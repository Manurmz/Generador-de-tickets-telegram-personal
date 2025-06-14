from dotenv import dotenv_values
import telebot
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from datetime import datetime

from crear_pdf import crear_pdf
from OCR_imagen import detect_text
from obtener_json import extraer_datos_recibo

# Cargar token como variable
env_vars = dotenv_values(".env")
TOKEN = env_vars.get("TOKEN")

bot = telebot.TeleBot(TOKEN)
InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup
InlineKeyboardButton = telebot.types.InlineKeyboardButton


esperando_respuesta = False
print('ejecutando bot')

# Definir data como una variable global inicializada como None
data = None

@bot.message_handler(content_types=['photo'])
def handle_photo(mensaje):
    global esperando_respuesta, data  # Declarar que estamos usando la variable global
    esperando_respuesta = True
    markUp = InlineKeyboardMarkup()
    btn_si = InlineKeyboardButton('🟢Sí', callback_data='si')
    btn_no = InlineKeyboardButton('🔴No', callback_data='no')
    markUp.add(btn_si, btn_no)
    bot.send_message(mensaje.chat.id,'Archivo recibido')
    # Obtener la foto
    file_info = bot.get_file(mensaje.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    array_datos = detect_text(downloaded_file)
    #print(array_datos)
    #generar json con los datos a inyectar
    data = extraer_datos_recibo(array_datos)
    #print(data)
    # Enviar mensaje
    precio_recibo = data['monto']
    respuesta = f"¿El valor del recibo es de {precio_recibo}?"
    bot.send_message(mensaje.chat.id, respuesta, reply_markup=markUp)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    global esperando_respuesta, data  # Declarar que estamos usando la variable global
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    if call.data == 'si':
        bot.send_message(call.message.chat.id, 'Generando ticket')
        esperando_respuesta = False
        nombre_pdf = crear_pdf(data)
        directorio_script = os.path.dirname(os.path.realpath(__file__))
        ruta_pdf = os.path.join(directorio_script, nombre_pdf)
        with open(ruta_pdf,'rb') as pdf_file:
            bot.send_document(call.message.chat.id,pdf_file)
        print('recibo enviado')
        # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, '¿Cuál es el valor de el pago?')
        # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.message_handler(func=lambda message: esperando_respuesta)
def handle_message(message):
    global esperando_respuesta, data
    if message.text.isdigit():  # Verificar si el mensaje del usuario es un número
        esperando_respuesta = False
        monto_correcto = int(message.text)
        data["monto"] = monto_correcto
        bot.send_message(message.chat.id, f"El monto ha sido actualizado a {monto_correcto} MXN.")
        bot.send_message(message.chat.id, "creando ticket")
        nombre_pdf = crear_pdf(data)
        directorio_script = os.path.dirname(os.path.realpath(__file__))
        ruta_pdf = os.path.join(directorio_script, nombre_pdf)
        bot.send_message(message.chat.id,'Recibo generado')
        with open(ruta_pdf,'rb') as pdf_file:
            bot.send_document(message.chat.id,pdf_file)
        print('recivo enviado')
    else:
        bot.send_message(message.chat.id, "Por favor, introduce un valor numérico válido.")

# Maneja el comando '/status'
@bot.message_handler(commands=['status'])
def send_welcome(message):
    bot.reply_to(message, "Estado activo")

# Maneja el comando '/ticket'
@bot.message_handler(commands=['ticket'])
def ticket_personalizado(message):
    """
    Inicia el proceso para crear un ticket personalizado solicitando el primer dato.
    """
    print('Comando /ticket recibido')
    # Se crea un diccionario vacío para almacenar los datos del ticket
    info_personalizada = {}
    msg = bot.send_message(message.chat.id, "🤖 Creación de Ticket Personalizado 🤖\n\nPor favor, dime el nombre del servicio:")
    # Se registra el siguiente paso para que la función obtener_servicio maneje la respuesta
    bot.register_next_step_handler(msg, obtener_servicio, info_personalizada)

def obtener_servicio(message, info_personalizada):
    """
    Recibe el nombre del servicio y solicita el número de referencia.
    """
    try:
        servicio = message.text
        info_personalizada['servicio'] = servicio
        msg = bot.send_message(message.chat.id, f"✅ Servicio: {servicio}\n\nAhora, introduce la referencia:")
        bot.register_next_step_handler(msg, obtener_referencia, info_personalizada)
    except Exception as e:
        print(f"Error en obtener_servicio: {e}")
        bot.reply_to(message, 'Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

def obtener_referencia(message, info_personalizada):
    """
    Recibe la referencia y solicita el monto.
    """
    try:
        referencia = message.text
        info_personalizada['referencia'] = referencia
        msg = bot.send_message(message.chat.id, f"✅ Referencia: {referencia}\n\nAhora, introduce el monto (ej. 1564):")
        bot.register_next_step_handler(msg, obtener_monto, info_personalizada)
    except Exception as e:
        print(f"Error en obtener_referencia: {e}")
        bot.reply_to(message, 'Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

def obtener_monto(message, info_personalizada):
    """
    Recibe y valida el monto, luego solicita la guía.
    """
    try:
        # Valida que el monto sea un número
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
        bot.reply_to(message, 'Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

# def obtener_guia(message, info_personalizada):
#     """
#     Recibe la guía y solicita el folio.
#     """
#     try:
#         guia = message.text
#         info_personalizada['guia'] = guia
#         msg = bot.send_message(message.chat.id, f"✅ Guía: {guia}\n\nPor último, introduce el folio:")
#         bot.register_next_step_handler(msg, obtener_folio_y_generar, info_personalizada)
#     except Exception as e:
#         print(f"Error en obtener_guia: {e}")
#         bot.reply_to(message, 'Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

def obtener_folio_y_generar(message, info_personalizada):
    """
    Recibe el folio, completa los datos, genera el PDF y lo envía.
    """
    try:
        folio = message.text
        info_personalizada['folio'] = folio

        # Agrega la hora actual del sistema
        info_personalizada['hora'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        bot.send_message(message.chat.id, f"✅ Folio: {folio}\n\nTodos los datos han sido recibidos. Generando tu ticket...")

        # Llama a la función para crear el PDF con los datos recolectados
        nombre_pdf = crear_pdf(info_personalizada)
        directorio_script = os.path.dirname(os.path.realpath(__file__))
        ruta_pdf = os.path.join(directorio_script, nombre_pdf)

        # Envía el documento PDF generado
        with open(ruta_pdf, 'rb') as pdf_file:
            bot.send_document(message.chat.id, pdf_file)
        print('Ticket personalizado enviado exitosamente.')

    except Exception as e:
        print(f"Error en obtener_folio_y_generar: {e}")
        bot.reply_to(message, 'Ocurrió un error final al generar el ticket. Por favor, intenta de nuevo.')


bot.infinity_polling()
