import fitz  # PyMuPDF

# 1. Abrir el documento
archivo_pdf = "comprobante.pdf"
doc = fitz.open(archivo_pdf)

# 2. Seleccionar la primera página (índice 0)
pagina = doc[0]
data = []
# 3. Extraer el texto simple
# Extraer texto como un diccionario de objetos
contenido_detallado = pagina.get_text("dict")

# # Esto te permite navegar por bloques de texto
# for bloque in contenido_detallado["blocks"]:
#     if "lines" in bloque:
#         for linea in bloque["lines"]:
#             for span in linea["spans"]:
#                 print(f"Texto: {span['text']}")
#                 print(f"Fuente: {span['font']}, Tamaño: {span['size']}")
#                 print(f"Coordenadas: {span['bbox']}") # (x0, y0, x1, y1)
#                 print("-" * 10)
# print(contenido_detallado)
extraido = {}
for bloque in contenido_detallado["blocks"]:
    if "lines" in bloque:
        for linea in bloque["lines"]:
            for span in linea["spans"]:
                extraido["text"] = span['text']
                extraido["coordenadas"] = span['bbox']
                data.append(extraido)
                extraido = {}

print(data)
