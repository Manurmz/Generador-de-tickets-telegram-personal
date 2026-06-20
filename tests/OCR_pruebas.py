from google.cloud import vision
def detect_text(imagen):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with open(imagen, "rb") as image_file:
        content = image_file.read()
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

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from paths import PRUEBA_IMG_DIR

    imagenes = [
        "izzi.jpg", "izzi_viejo.jpg", "cfe_viejo.jpg",
        "megacable_nuevo.jpg", "megacable_nuevo_2.jpg",
        "vtv.jpg", "izzi_c.jpg", "agua.jpg", "cashi_6.jpg"
    ]
    for img in imagenes:
        ruta = os.path.join(PRUEBA_IMG_DIR, img)
        if os.path.exists(ruta):
            print(f"--- {img} ---")
            array = detect_text(ruta)
            print(array)
            break
