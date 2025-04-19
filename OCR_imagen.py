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

if __name__ == "__main__":
    imagen1 = "pago izzi.jpg"
    imagen2 = "cfe pago cashi 2.jpg"
    imagen3 = "pago agua bbva instantaneo.jpg"
    array = detect_text(imagen3)
    print(array)