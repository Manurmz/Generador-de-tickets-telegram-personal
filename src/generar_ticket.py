import os

from paths import TICKETS_PDF_DIR
from crear_pdf import crear_pdf
from crear_imagen import crear_imagen
from impresora_termica import print_image_file


def generar_ticket(data: dict) -> dict:
    nombre_pdf = crear_pdf(data)
    nombre_imagen = crear_imagen(data)
    print_image_file(nombre_imagen)
    ruta_pdf = os.path.join(TICKETS_PDF_DIR, nombre_pdf)

    return {
        "pdf_path": ruta_pdf,
        "pdf_nombre": nombre_pdf,
        "imagen_nombre": nombre_imagen
    }
