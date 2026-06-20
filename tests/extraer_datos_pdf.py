import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root, "src"))

import fitz
from paths import PDF_PRUEBA_DIR
from obtener_json_pdf import procesar_array
import json


def extraer_datos_de_pdf(archivo_pdf: str) -> list:
    """
    Extrae texto y coordenadas de un PDF en disco.
    """
    data = []
    doc = fitz.open(archivo_pdf)
    pagina = doc[0]
    contenido_detallado = pagina.get_text("dict")

    for bloque in contenido_detallado["blocks"]:
        if "lines" in bloque:
            for linea in bloque["lines"]:
                for span in linea["spans"]:
                    extraido = {
                        "text": span["text"],
                        "coordenadas": span["bbox"]
                    }
                    data.append(extraido)
    doc.close()
    return data


def main():
    if not os.path.exists(PDF_PRUEBA_DIR):
        print(f"Error: La carpeta '{PDF_PRUEBA_DIR}' no existe")
        return

    pdfs = [f for f in os.listdir(PDF_PRUEBA_DIR) if f.lower().endswith(".pdf")]

    if not pdfs:
        print(f"No se encontraron PDFs en '{PDF_PRUEBA_DIR}'")
        return

    print(f"\n=== PDFs disponibles ({len(pdfs)}) ===")
    for i, pdf in enumerate(sorted(pdfs), 1):
        print(f"{i}. {pdf}")
    print("==================================")
    print("0. Procesar todos")
    print("----------------------------------")

    try:
        sel = input("Selecciona el número del PDF: ").strip()
        if sel == "0":
            for pdf_file in sorted(pdfs):
                _procesar_pdf(pdf_file)
        else:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(pdfs):
                print("Selección inválida")
                return
            _procesar_pdf(sorted(pdfs)[idx])
    except ValueError:
        print("Debes ingresar un número")


def _procesar_pdf(pdf_file):
    ruta_pdf = os.path.join(PDF_PRUEBA_DIR, pdf_file)
    print(f"\n>>> Procesando: {pdf_file}")
    try:
        array_datos = extraer_datos_de_pdf(ruta_pdf)
        print(f"    {len(array_datos)} elementos extraidos")
        resultado = procesar_array(array_datos)
        if resultado:
            print(f"    Resultado JSON:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        else:
            print("    No se pudieron extraer datos")
    except Exception as e:
        print(f"    Error: {e}")


if __name__ == "__main__":
    main()
