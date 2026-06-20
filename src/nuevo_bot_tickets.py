from dotenv import dotenv_values
import telebot
import os
from datetime import datetime
import io

from paths import TICKETS_PDF_DIR, ENV_PATH, ensure_dirs
from estado_usuario import STATES, UserStateManager
from procesar_recibo import procesar_imagen, procesar_documento
from generar_ticket import generar_ticket

ensure_dirs()

env_vars = dotenv_values(ENV_PATH)
TOKEN = env_vars.get("TOKEN")

bot = telebot.TeleBot(TOKEN)
InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup
InlineKeyboardButton = telebot.types.InlineKeyboardButton

state_manager = UserStateManager()

def generar_y_enviar_ticket(chat_id, data):
    try:
        resultado = generar_ticket(data)
        ruta_pdf = resultado["pdf_path"]

        if os.path.exists(ruta_pdf):
            with open(ruta_pdf, 'rb') as pdf_file:
                bot.send_document(chat_id, pdf_file)
                bot.send_message(chat_id, "✅ Ticket generado exitosamente")
        else:
            bot.send_message(chat_id, "❌ Error: No se pudo generar el PDF")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error generando el ticket: {str(e)}")
        print(f"Error en generar_y_enviar_ticket: {e}")


@bot.message_handler(commands=['status'])
def send_welcome(message):
    bot.reply_to(message, "✅ Bot activo y funcionando")


@bot.message_handler(commands=['ticket'])
def ticket_personalizado(message):
    chat_id = message.chat.id
    state_manager.clear_state(chat_id)

    print('Comando /ticket recibido')
    info_personalizada = {}
    msg = bot.send_message(chat_id, "🤖 Creación de Ticket Personalizado 🤖\n\nPor favor, dime el nombre del servicio:")
    bot.register_next_step_handler(msg, obtener_servicio, info_personalizada)


@bot.message_handler(content_types=['photo'])
def handle_photo(mensaje):
    chat_id = mensaje.chat.id

    state_manager.clear_state(chat_id)

    markUp = InlineKeyboardMarkup()
    btn_si = InlineKeyboardButton('🟢Sí', callback_data='confirm_yes')
    btn_no = InlineKeyboardButton('🔴No', callback_data='confirm_no')
    markUp.add(btn_si, btn_no)

    bot.send_message(chat_id, '📸 Procesando imagen del recibo...')

    try:
        file_info = bot.get_file(mensaje.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        data = procesar_imagen(downloaded_file)

        state_manager.set_state(
            chat_id,
            STATES["PROCESSING_RECEIPT"],
            data
        )

        precio_recibo = data.get('monto', 'No detectado')
        respuesta = f"¿El valor del recibo es de ${precio_recibo} MXN?"
        bot.send_message(chat_id, respuesta, reply_markup=markUp)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error procesando la imagen: {str(e)}")
        print(f"Error en handle_photo: {e}")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id

    document = message.document
    file_name = document.file_name.lower() if document.file_name else ""

    extensiones_soportadas = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']

    if not any(file_name.endswith(ext) for ext in extensiones_soportadas):
        bot.send_message(chat_id, "❌ Formato no soportado. Envía un PDF o imagen (JPG, PNG, etc.)")
        return

    bot.send_message(chat_id, f"📄 Procesando documento: {document.file_name}")

    try:
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        state_manager.set_state(chat_id, STATES["PROCESSING_DOCUMENT"])

        datos_extraidos = procesar_documento(downloaded_file, file_name)

        if datos_extraidos:
            state_manager.set_state(
                chat_id,
                STATES["PROCESSING_RECEIPT"],
                datos_extraidos
            )

            markUp = InlineKeyboardMarkup()
            btn_si = InlineKeyboardButton('🟢Sí', callback_data='confirm_yes')
            btn_no = InlineKeyboardButton('🔴No', callback_data='confirm_no')
            markUp.add(btn_si, btn_no)

            precio_recibo = datos_extraidos.get('monto', 'No detectado')
            respuesta = f"¿El valor del recibo es de ${precio_recibo} MXN?"
            bot.send_message(chat_id, respuesta, reply_markup=markUp)
        else:
            bot.send_message(chat_id, "❌ No se pudieron extraer datos del documento. Intenta con una imagen más clara.")
            state_manager.clear_state(chat_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Error procesando el documento: {str(e)}")
        print(f"Error en handle_document: {e}")
        state_manager.clear_state(chat_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    user_state = state_manager.get_state(chat_id)

    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)

    if call.data == 'confirm_yes':
        data = user_state.get("data", {})
        if data:
            bot.send_message(chat_id, '🔄 Generando ticket...')
            generar_y_enviar_ticket(chat_id, data)
            state_manager.clear_state(chat_id)
        else:
            bot.send_message(chat_id, '❌ No se encontraron datos del recibo')

    elif call.data == 'confirm_no':
        state_manager.set_state(chat_id, STATES["WAITING_AMOUNT"])
        bot.send_message(chat_id, '💵 ¿Cuál es el valor correcto del pago? (Solo el número)')


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_state = state_manager.get_state(chat_id)

    if user_state.get("state") == STATES["WAITING_AMOUNT"]:
        handle_amount_correction(message, user_state)

    elif message.text and message.text.startswith('/'):
        bot.process_new_messages([message])

    else:
        bot.send_message(chat_id, "Envía una foto de un recibo o usa /ticket para crear uno manualmente")


def handle_amount_correction(message, user_state):
    chat_id = message.chat.id

    if message.text and message.text.isdigit():
        monto_correcto = int(message.text)

        data = user_state.get("data", {})
        data["monto"] = monto_correcto
        state_manager.update_data(chat_id, "monto", monto_correcto)

        bot.send_message(chat_id, f"✅ Monto actualizado a ${monto_correcto:,} MXN")
        bot.send_message(chat_id, "🔄 Generando ticket...")

        generar_y_enviar_ticket(chat_id, data)
        state_manager.clear_state(chat_id)

    else:
        bot.send_message(chat_id, "Por favor, introduce solo números (ej: 1500)")


def obtener_servicio(message, info_personalizada):
    try:
        servicio = message.text
        info_personalizada['servicio'] = servicio
        msg = bot.send_message(message.chat.id, f"✅ Servicio: {servicio}\n\nAhora, introduce la referencia:")
        bot.register_next_step_handler(msg, obtener_referencia, info_personalizada)
    except Exception as e:
        print(f"Error en obtener_servicio: {e}")
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')


def obtener_referencia(message, info_personalizada):
    try:
        referencia = message.text
        info_personalizada['referencia'] = referencia
        msg = bot.send_message(message.chat.id, f"✅ Referencia: {referencia}\n\nAhora, introduce el monto (ej. 1564):")
        bot.register_next_step_handler(msg, obtener_monto, info_personalizada)
    except Exception as e:
        print(f"Error en obtener_referencia: {e}")
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')


def obtener_monto(message, info_personalizada):
    try:
        if not message.text.isdigit():
            msg = bot.send_message(message.chat.id, "❌ Error: El monto debe ser un valor numérico.\nPor favor, introduce el monto de nuevo:")
            bot.register_next_step_handler(msg, obtener_monto, info_personalizada)
            return

        monto = int(message.text)
        info_personalizada['monto'] = monto
        msg = bot.send_message(message.chat.id, f"✅ Monto: ${monto:,.2f} MXN\n\nAhora, introduce el folio:")
        bot.register_next_step_handler(msg, obtener_folio_y_generar, info_personalizada)
    except Exception as e:
        print(f"Error en obtener_monto: {e}")
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')


def obtener_folio_y_generar(message, info_personalizada):
    try:
        folio = message.text
        info_personalizada['folio'] = folio

        info_personalizada['hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        bot.send_message(message.chat.id, f"✅ Folio: {folio}\n\nTodos los datos han sido recibidos. Generando tu ticket...")

        generar_y_enviar_ticket(message.chat.id, info_personalizada)

    except Exception as e:
        print(f"Error en obtener_folio_y_generar: {e}")
        bot.reply_to(message, '❌ Ocurrió un error final al generar el ticket. Por favor, intenta de nuevo.')


print('🚀 Ejecutando bot...')

user_id = env_vars.get("USER_ID_TELEGRAM")
if user_id:
    try:
        bot.send_message(
            chat_id=user_id,
            text="🤖 ¡Bot iniciado correctamente! Estoy online y listo para ayudar 😊"
        )
        print("✅ Mensaje de inicio enviado exitosamente!")
    except telebot.apihelper.ApiTelegramException as e:
        if e.result.status_code == 403:
            print("⚠️  Advertencia: Usuario bloqueó el bot o nunca inició chat")
        elif e.result.status_code == 400:
            print("⚠️  Advertencia: ID de usuario inválido")
        else:
            print(f"⚠️  Error enviando mensaje de inicio: {e}")

print("📡 Iniciando polling...")
bot.infinity_polling()
