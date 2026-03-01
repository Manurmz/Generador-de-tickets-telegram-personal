# Generador de Tickets Telegram Personal 🤖

Un bot de Telegram inteligente que genera tickets/receipts a partir de imágenes de recibos o datos manuales, con capacidades de OCR, procesamiento de PDFs e impresión térmica.

## 📋 Características Principales

- **Procesamiento de imágenes**: Extrae texto de recibos usando Google Cloud Vision OCR
- **Procesamiento de PDFs**: Analiza documentos PDF para extraer datos estructurados
- **Generación automática de tickets**: Crea tickets en formato PDF con diseño optimizado para impresión térmica
- **Interacción por Telegram**: Comandos simples y flujos conversacionales intuitivos
- **Impresión térmica**: Integración con impresoras térmicas para tickets físicos
- **Modo manual**: Creación de tickets personalizados mediante comandos paso a paso

## 🏗️ Arquitectura del Proyecto

### Archivos Principales

- **`bot_ticket.py`** - Bot principal de Telegram con manejo de estados y flujos de conversación
- **`crear_pdf.py`** - Generación de tickets PDF con formato específico para impresión térmica
- **`OCR_imagen.py`** - Integración con Google Cloud Vision para reconocimiento de texto en imágenes
- **`crear_imagen.py`** - Conversión de datos a imágenes para impresión térmica
- **`impresora_termica.py`** - Control de impresoras térmicas
- **`obtener_json.py`** - Extracción de datos estructurados de arrays OCR
- **`obtener_json_pdf.py`** - Procesamiento de arrays de datos extraídos de PDFs
- **`extraer_datos_pdf.py`** - Extracción de texto y coordenadas de archivos PDF

### Dependencias Clave

- **`pyTelegramBotAPI`** - Framework para el bot de Telegram
- **`google-cloud-vision`** - API de Google Cloud Vision para OCR
- **`fpdf2`** - Generación de archivos PDF
- **`pillow`** - Procesamiento de imágenes
- **`python-dotenv`** - Manejo de variables de entorno

## 🚀 Instalación y Configuración

### Requisitos Previos

1. Python 3.8 o superior
2. Cuenta de Google Cloud con API de Vision habilitada
3. Bot de Telegram creado a través de [@BotFather](https://t.me/botfather)
4. Impresora térmica compatible (opcional)

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Manurmz/Generador-de-tickets-telegram-personal.git
   cd Generador-de-tickets-telegram-personal
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Crear un archivo `.env` con las siguientes variables:
   ```
   TOKEN=tu_token_de_telegram_bot
   USER_ID_TELEGRAM=tu_id_de_usuario_telegram
   GOOGLE_APPLICATION_CREDENTIALS=ruta/a/tu/credenciales.json
   ```

4. **Configurar credenciales de Google Cloud:**
   - Habilitar la API de Cloud Vision
   - Descargar el archivo JSON de credenciales de servicio
   - Establecer la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`

## 📖 Uso del Bot

### Comandos Disponibles

- **`/start`** - Iniciar el bot (mensaje de bienvenida)
- **`/status`** - Verificar estado del bot
- **`/ticket`** - Crear un ticket personalizado manualmente

### Flujos de Trabajo

#### 1. Generación Automática desde Imágenes/PDFs
1. Envía una foto de un recibo o un documento PDF al bot
2. El bot procesa la imagen usando OCR
3. Extrae automáticamente: monto, referencia, servicio, etc.
4. Confirma los datos detectados
5. Genera y envía el ticket PDF
6. Imprime automáticamente en la impresora térmica (si está configurada)

#### 2. Creación Manual de Tickets
1. Usa el comando `/ticket`
2. Sigue el flujo conversacional:
   - Nombre del servicio
   - Número de referencia
   - Monto del pago
   - Folio/autorización
3. El bot genera el ticket con los datos proporcionados

## 🖨️ Impresión Térmica

El sistema incluye integración con impresoras térmicas a través del módulo `impresora_termica.py`. Características:

- Soporte para múltiples modelos de impresoras térmicas
- Conversión automática de PDF a formato de imagen optimizado
- Control de parámetros de impresión (densidad, velocidad, etc.)
- Manejo de errores y reintentos

## 🔧 Estructura de Datos

Los tickets generados incluyen la siguiente información:

```python
{
    "servicio": "Nombre del servicio (CFE, Agua, Teléfono, etc.)",
    "referencia": "Número de referencia del pago",
    "monto": "Cantidad pagada",
    "comision": "Comisión aplicada (default: 15)",
    "total": "Monto total (monto + comisión)",
    "folio": "Número de folio/autorización",
    "hora": "Fecha y hora de la transacción",
    "guia": "Guía CIE (para pagos de agua)"
}
```

## 🧪 Pruebas

El proyecto incluye archivos de prueba:
- `prueba.py` - Scripts de prueba para diferentes funcionalidades
- Imágenes de ejemplo para testing de OCR

## 📁 Estructura del Proyecto

```
Generador-de-tickets-telegram-personal/
├── bot_ticket.py              # Bot principal de Telegram
├── crear_pdf.py               # Generador de PDFs
├── crear_imagen.py            # Conversor a imágenes para impresión
├── impresora_termica.py       # Control de impresora térmica
├── OCR_imagen.py              # Integración con Google Cloud Vision
├── obtener_json.py            # Procesamiento de datos OCR
├── obtener_json_pdf.py        # Procesamiento de datos PDF
├── extraer_datos_pdf.py       # Extracción de datos de PDFs
├── prueba.py                  # Scripts de prueba
├── requirements.txt           # Dependencias de Python
├── README.md                  # Este archivo
└── .gitignore                 # Archivos ignorados por Git
```

## ⚠️ Consideraciones Importantes

1. **Credenciales de Google Cloud**: Necesitas una cuenta activa con facturación habilitada para usar la API de Vision
2. **Límites de OCR**: Google Cloud Vision tiene límites de uso gratuito y tarifas por uso excesivo
3. **Formato de recibos**: El OCR funciona mejor con recibos claros y bien iluminados
4. **Impresora térmica**: La funcionalidad de impresión es opcional, el bot funciona sin ella

## 🔄 Mantenimiento y Mejoras

### Monitoreo
- El bot envía un mensaje de inicio al usuario configurado
- Manejo de errores con mensajes descriptivos al usuario
- Logging de errores en consola para debugging

### Posibles Mejoras Futuras
- Soporte para más formatos de documentos
- Integración con bases de datos para historial de tickets
- Panel web de administración
- Estadísticas y reportes
- Soporte multi-idioma

## 📄 Licencia

Este proyecto es de uso personal. Para uso comercial o distribución, contactar al autor.

## 👤 Autor

**Manurmz** - [GitHub](https://github.com/Manurmz)

---

*Última actualización: Marzo 2026*