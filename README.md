# Telebot Tickets

Bot de Telegram que genera tickets/comprobantes de pago. Recibe una foto o PDF de un recibo, extrae los datos automáticamente mediante OCR con Google Cloud Vision, reconoce distintos formatos (BBVA, Cashi, Ventamovil, Mercado Pago) y genera un ticket PDF e imagen PNG para enviar al usuario e imprimir en una impresora térmica.

## Estructura del proyecto

```
├── main.py                    # Punto de entrada: ejecuta el bot
├── src/                       # Código fuente activo
│   ├── nuevo_bot_tickets.py   # Bot principal (Telegram)
│   ├── paths.py               # Rutas de carpetas (project-root relativas)
│   ├── crear_pdf.py           # Genera el ticket en PDF
│   ├── crear_imagen.py        # Genera el ticket en PNG
│   ├── OCR_imagen.py          # OCR con Google Cloud Vision
│   ├── obtener_json.py        # Extrae datos de recibos (BBVA, Cashi, Ventamovil)
│   ├── obtener_json_pdf.py    # Extrae datos de recibos (Mercado Pago, PDFs)
│   └── impresora_termica.py   # Imprime tickets en impresora térmica
├── legacy/                    # Código obsoleto/duplicado (referencia)
├── tests/                     # Scripts y datos de prueba
│   ├── fixtures_recibos.py     # 12 casos de prueba con datos esperados
│   ├── test_obtener_json.py   # Tests pytest para extraer_datos_recibo
│   ├── test_fuentes.py
│   ├── OCR_pruebas.py
│   └── extraer_datos_pdf.py   # Test harness para PDFs de pdf_prueba/
├── pdf_prueba/                 # PDFs de Mercado Pago para pruebas
├── imagenes_prueba/           # Imágenes de recibo para pruebas (entrada)
├── imagenes_ticket/           # Tickets generados en PNG (salida)
├── tickets/                   # Tickets generados en PDF (salida)
├── .env                       # Variables de entorno (Token, IDs) — NO SUBIR A GIT
├── .env.example               # Plantilla de variables de entorno
└── pyproject.toml             # Dependencias del proyecto
```

## Requisitos

- **Python** 3.13+ (compatible con 3.14)
- **Pip** o **[uv](https://docs.astral.sh/uv/)** para instalar dependencias
- **Google Cloud Vision API** habilitada y credenciales configuradas

## Configuración

1. **Clonar el repositorio** y entrar al directorio:
   ```bash
   cd "telebot tickets"
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
   o con uv:
   ```bash
   uv sync
   ```

3. **Configurar variables de entorno** (`./.env`):
   ```env
   TOKEN=tu_token_de_telegram
   USER_ID_TELEGRAM=tu_user_id
   VENDOR_ID=0x6868
   PRODUCT_ID=0x0200
   GOOGLE_APPLICATION_CREDENTIALS=/ruta/completa/a/permisos-personales.json
   ```

4. **Configurar credenciales de Google Cloud**:
   - Coloca tu archivo JSON de service account en una ruta segura
   - Configura la variable `GOOGLE_APPLICATION_CREDENTIALS` en `.env` o como variable de entorno del sistema

## Uso

Ejecutar el bot:
```bash
python main.py
```

## Pruebas

Ejecutar tests con pytest:
```bash
pytest tests/
pytest tests/test_obtener_json.py -v
```

Menú interactivo de pruebas:
```bash
python prueba.py
```
Este menú permite probar individualmente cada módulo del proyecto.

**Comandos del bot en Telegram:**
| Comando/Acción | Descripción |
|---|---|
| `/status` | Verifica que el bot esté activo |
| `/ticket` | Crea un ticket manual paso a paso |
| Enviar foto | Envía una foto de un recibo para extraer datos automáticamente |
| Enviar PDF | Envía un PDF de recibo (Mercado Pago, etc.) |

## Formatos de recibo soportados

- **BBVA** — Comprobantes de pago de servicios (agua SAPAO, etc.)
- **Cashi** — Pagos desde la app Cashi (CFE, Izzi, Megacable, etc.)
- **Ventamovil** — Recibos de Ventamovil/Recargame (CFE, Izzi, VETV, etc.)
- **Mercado Pago** — Comprobantes de pago desde Mercado Pago (PDF)

## Notas y problemas conocidos

1. **Credenciales de Google Cloud**: El archivo `permisos-personales.json` contiene una clave privada de service account. **No debe subirse a git.** Ya está en `.gitignore`.
2. **Impresora térmica**: Requiere una impresora USB conectada. Los Vendor/Product IDs se configuran en `.env`. Verifica que las rutas USB coincidan con las de tu sistema.
3. **Versión de Python**: `.python-version` indica 3.14, pero el proyecto funciona correctamente con 3.13. Se recomienda alinear ambas versiones.
4. **Dos entornos virtuales**: Existen `venv/` y `.venv/`. Se recomienda eliminar uno y mantener solo el que uses.
5. **Sin commits en git**: El proyecto está sin commits iniciales. Se recomienda hacer `git add` y `git commit` tras verificar que todo funciona.
