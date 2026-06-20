import os

from OCR_imagen import detect_text
from obtener_json import extraer_datos_recibo
from obtener_json_pdf import procesar_array


def extraer_datos_de_pdf(pdf_bytes: bytes) -> list:
    try:
        import fitz
        data = []
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
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


def procesar_documento(file_bytes: bytes, file_name: str) -> dict:
    ext = os.path.splitext(file_name)[1].lower() if file_name else ""

    if ext == '.pdf':
        array_datos = extraer_datos_de_pdf(file_bytes)
        if array_datos:
            return procesar_array(array_datos)
        return {}

    try:
        array_texto = detect_text(file_bytes)
        return extraer_datos_recibo(array_texto)
    except Exception as e:
        print(f"Error procesando archivo {file_name}: {e}")
        return {}


def procesar_imagen(image_bytes: bytes) -> dict:
    try:
        array_texto = detect_text(image_bytes)
        return extraer_datos_recibo(array_texto)
    except Exception as e:
        print(f"Error en procesar_imagen: {e}")
        return {}
