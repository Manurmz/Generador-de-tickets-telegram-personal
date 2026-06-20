import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TICKETS_PDF_DIR = os.path.join(PROJECT_ROOT, "tickets")
TICKETS_IMG_DIR = os.path.join(PROJECT_ROOT, "imagenes_ticket")
PRUEBA_IMG_DIR = os.path.join(PROJECT_ROOT, "imagenes_prueba")
PDF_PRUEBA_DIR = os.path.join(PROJECT_ROOT, "pdf_prueba")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")


def ensure_dirs():
    for d in (TICKETS_PDF_DIR, TICKETS_IMG_DIR, PRUEBA_IMG_DIR, PDF_PRUEBA_DIR):
        os.makedirs(d, exist_ok=True)
