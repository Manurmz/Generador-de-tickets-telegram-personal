from dotenv import dotenv_values
import telebot
import os
from datetime import datetime
from collections import defaultdict
import io

from crear_pdf import crear_pdf
from OCR_imagen import detect_text
from obtener_json import extraer_datos_recibo
from obtener_json_pdf import procesar_array

from crear_imagen import crear_imagen
from impresora_termica import print_image_file

# Cargar token como variable
env_vars = dotenv_values(".env")
TOKEN = env_vars.get("TOKEN")

bot = telebot.TeleBot(TOKEN)
InlineKeyboardMarkup = telebot.types.InlineKeyboardMarkup
InlineKeyboardButton = telebot.types.InlineKeyboardButton

# Estados posibles
STATES = {
    "PROCESSING_RECEIPT": "processing_receipt",
    "WAITING_AMOUNT": "waiting_amount",
    "PROCESSING_DOCUMENT": "processing_document"
}

class UserStateManager:
    def __init__(self):
        self.user_data = defaultdict(dict)
    
    def set_state(self, chat_id, state, data=None):
        self.user_data[chat_id] = {
            "state": state,
            "data": data or {},
            "timestamp": datetime.now()
        }
    
    def get_state(self, chat_id):
        return self.user_data.get(chat_id, {})
    
    def clear_state(self, chat_id):
        if chat_id in self.user_data:
            del self.user_data[chat_id]
    
    def update_data(self, chat_id, key, value):
        if chat_id in self.user_data:
            self.user_data[chat_id]["data"][key] = value

def extraer_datos_de_pdf(pdf_bytes: bytes) -> list:
    """
    Extrae texto y coordenadas de un PDF en memoria.
    Similar a extraer_datos_pdf.py pero trabaja con bytes.
    """
    try:
        import fitz  # PyMuPDF
        data = []
        # Abrir PDF desde bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Procesar solo la primera página
        pagina = doc[0]
        contenido_detallado = pagina.get_text("dict")
        
        for bloque in contenido_detallado["blocks"]:
            if "lines" in bloque:
                for linea in bloque["lines"]:
                    for span in linea["spans"]:
                        extraido = {
                            "text": span['text'],
                            "coordenadas": span['bbox']
                        }
                        data.append(extraido)
        doc.close()
        return data
    except Exception as e:
        print(f"Error en extraer_datos_de_pdf: {e}")
        return []

def procesar_documento_pdf(pdf_bytes: bytes, file_extension: str) -> dict:
    """
    Procesa un documento PDF y extrae datos estructurados.
    """
    # Si es PDF, extraer array y procesar
    if file_extension.lower() == '.pdf':
        array_datos = extraer_datos_de_pdf(pdf_bytes)
        if array_datos:
            return procesar_array(array_datos)
    # Para imágenes, usar el procesamiento existente (OCR)
    else:
        # Usar OCR_imagen para imágenes
        try:
            array_datos = detect_text(pdf_bytes)
            return extraer_datos_recibo(array_datos)
        except Exception as e:
            print(f"Error procesando imagen en procesar_documento_pdf: {e}")
    return {}

# Inicializar el manager
state_manager = UserStateManager()

def generar_y_enviar_ticket(chat_id, data):
    """Función reutilizable para generar y enviar tickets"""
    try:
        nombre_pdf = crear_pdf(data)
        nombre_imagen = crear_imagen(data)
        print_image_file(nombre_imagen)
        directorio_script = os.path.dirname(os.path.realpath(__file__))
        ruta_pdf = os.path.join(directorio_script, nombre_pdf)
        
        if os.path.exists(ruta_pdf):
            with open(ruta_pdf, 'rb') as pdf_file:
                bot.send_document(chat_id, pdf_file)
                bot.send_message(chat_id, "✅ Ticket generado exitosamente")
        else:
            bot.send_message(chat_id, "❌ Error: No se pudo generar el PDF")
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error generando el ticket: {str(e)}")
        print(f"Error en generar_y_enviar_ticket: {e}")

# Maneja el comando '/status'
@bot.message_handler(commands=['status'])
def send_welcome(message):
    print("comando /status")
    bot.reply_to(message, "✅ Bot activo y funcionando")

# Maneja el comando '/ticket'
@bot.message_handler(commands=['ticket'])
def ticket_personalizado(message):
    """
    Inicia el proceso para crear un ticket personalizado solicitando el primer dato.
    """
    chat_id = message.chat.id
    state_manager.clear_state(chat_id)
    
    print('Comando /ticket recibido')
    info_personalizada = {}
    msg = bot.send_message(chat_id, "🤖 Creación de Ticket Personalizado 🤖\n\nPor favor, dime el nombre del servicio:")
    bot.register_next_step_handler(msg, obtener_servicio, info_personalizada)


#inicia a generar el ticket cuando recibe una imagen
@bot.message_handler(content_types=['photo'])
def handle_photo(mensaje):
    chat_id = mensaje.chat.id
    
    # Limpiar estado previo si existe
    state_manager.clear_state(chat_id)
    
    markUp = InlineKeyboardMarkup()
    btn_si = InlineKeyboardButton('🟢Sí', callback_data='confirm_yes')
    btn_no = InlineKeyboardButton('🔴No', callback_data='confirm_no')
    markUp.add(btn_si, btn_no)
    
    bot.send_message(chat_id, '📸 Procesando imagen del recibo...')
    
    try:
        # Obtener la foto
        file_info = bot.get_file(mensaje.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Procesar imagen
        array_datos = detect_text(downloaded_file)
        data = extraer_datos_recibo(array_datos)
        
        # Guardar datos en estado del usuario
        state_manager.set_state(
            chat_id, 
            STATES["PROCESSING_RECEIPT"], 
            data
        )
        
        # Mostrar confirmación
        precio_recibo = data.get('monto', 'No detectado')
        respuesta = f"¿El valor del recibo es de ${precio_recibo} MXN?"
        bot.send_message(chat_id, respuesta, reply_markup=markUp)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error procesando la imagen: {str(e)}")
        print(f"Error en handle_photo: {e}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """
    Maneja documentos enviados (PDFs, imágenes, etc.)
    """
    chat_id = message.chat.id
    
    # Verificar si es un PDF u otro documento soportado
    document = message.document
    file_name = document.file_name.lower() if document.file_name else ""
    
    # Extensiones soportadas
    extensiones_soportadas = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    if not any(file_name.endswith(ext) for ext in extensiones_soportadas):
        bot.send_message(chat_id, "❌ Formato no soportado. Envía un PDF o imagen (JPG, PNG, etc.)")
        return
    
    bot.send_message(chat_id, f"📄 Procesando documento: {document.file_name}")
    
    try:
        # Obtener el archivo
        file_info = bot.get_file(document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Determinar la extensión
        file_extension = os.path.splitext(file_name)[1] if file_name else '.pdf'
        
        # Procesar documento
        state_manager.set_state(chat_id, STATES["PROCESSING_DOCUMENT"])
        
        # Usar función para procesar documentos
        datos_extraidos = procesar_documento_pdf(downloaded_file, file_extension)
        
        if datos_extraidos:
            # Guardar datos en estado del usuario
            state_manager.set_state(
                chat_id, 
                STATES["PROCESSING_RECEIPT"], 
                datos_extraidos
            )
            
            # Mostrar confirmación
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
        # Cambiar estado a esperando monto
        state_manager.set_state(chat_id, STATES["WAITING_AMOUNT"])
        bot.send_message(chat_id, '💵 ¿Cuál es el valor correcto del pago? (Solo el número)')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_state = state_manager.get_state(chat_id)
    
    # Si el usuario está en estado de espera de monto
    if user_state.get("state") == STATES["WAITING_AMOUNT"]:
        handle_amount_correction(message, user_state)
    
    # Si no, verificar si es un comando
    elif message.text and message.text.startswith('/'):
        bot.process_new_messages([message])
    
    # Si es un mensaje normal y no hay estado activo
    else:
        bot.send_message(chat_id, "Envía una foto de un recibo o usa /ticket para crear uno manualmente")

def handle_amount_correction(message, user_state):
    chat_id = message.chat.id
    
    if message.text and message.text.isdigit():
        monto_correcto = int(message.text)
        
        # Actualizar datos
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
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

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
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

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
        bot.reply_to(message, '❌ Ocurrió un error. Por favor, intenta de nuevo con /ticket.')

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

        # Usar función reutilizable para generar PDF
        generar_y_enviar_ticket(message.chat.id, info_personalizada)

    except Exception as e:
        print(f"Error en obtener_folio_y_generar: {e}")
        bot.reply_to(message, '❌ Ocurrió un error final al generar el ticket. Por favor, intenta de nuevo.')

# Inicio del bot
print('🚀 Ejecutando bot...')

# Enviar mensaje de inicio
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

# Iniciar polling
print("📡 Iniciando polling...")
bot.infinity_polling()
