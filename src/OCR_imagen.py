from google.cloud import vision
def detect_text(imagen):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    # with open(imagen, "rb") as image_file:
    #     content = image_file.read()
    content = imagen
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    ocr = []
    # print("Texts:")
    #arrayExeption = ['TRANSACCION', 'EXITOSA','Whatsapp', 'Compartir', 'Imprimir']

    for text in texts:
        # print(f'\n"{text.description}"')

        # vertices = [
        #     f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        # ]

        # print("bounds: {}".format(",".join(vertices)))
        # if text.description not in arrayExeption:
        #     ocr.append(text.description)
        ocr.append(text.description)

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return ocr[1:]

def procesar_todas_las_imagenes():
    import os
    from paths import PRUEBA_IMG_DIR
    if not os.path.exists(PRUEBA_IMG_DIR):
        print(f"La carpeta '{PRUEBA_IMG_DIR}' no existe")
        return
    archivos = os.listdir(PRUEBA_IMG_DIR)
    if not archivos:
        print("No hay imágenes en la carpeta de prueba")
        return
    for img in archivos:
        ruta = os.path.join(PRUEBA_IMG_DIR, img)
        if os.path.isfile(ruta):
            with open(ruta, "rb") as f:
                array = detect_text(f.read())
                print(f"\n--- {img} ---")
                print(array)

def main():
    import os
    from paths import PRUEBA_IMG_DIR
    if not os.path.exists(PRUEBA_IMG_DIR):
        print(f"La carpeta '{PRUEBA_IMG_DIR}' no existe")
        return
    archivos = [f for f in os.listdir(PRUEBA_IMG_DIR) if os.path.isfile(os.path.join(PRUEBA_IMG_DIR, f))]
    if not archivos:
        print("No hay imágenes en la carpeta de prueba")
        return
    print("\n=== Imágenes disponibles ===")
    for i, img in enumerate(archivos, 1):
        print(f"{i}. {img}")
    print("============================")
    try:
        sel = int(input("Selecciona el número de la imagen: ")) - 1
        if sel < 0 or sel >= len(archivos):
            print("Selección inválida")
            return
        img = archivos[sel]
        ruta = os.path.join(PRUEBA_IMG_DIR, img)
        with open(ruta, "rb") as f:
            array = detect_text(f.read())
            print(f"\n--- {img} ---")
            print(array)
    except ValueError:
        print("Debes ingresar un número")

if __name__ == "__main__":
    main()