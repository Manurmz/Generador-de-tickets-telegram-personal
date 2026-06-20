#!/usr/bin/env python3
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tests"))

def menu_principal():
    print("\n===== MENU DE PRUEBAS =====")
    print("1. Crear PDF de ticket")
    print("2. Crear imagen de ticket")
    print("3. Impresora térmica")
    print("4. Extraer datos de recibos (fixtures)")
    print("5. Arrays Mercado Pago (formato antiguo)")
    print("6. Extraer PDFs de pdf_prueba/")
    print("7. OCR imagen individual")
    print("8. OCR todas las imágenes de prueba")
    print("9. Verificar fuentes")
    print("0. Salir")
    print("============================")

def opcion1():
    from crear_pdf import main as crear_pdf_main
    crear_pdf_main()

def opcion2():
    from crear_imagen import main as crear_imagen_main
    crear_imagen_main()

def opcion3():
    from impresora_termica import main as impresora_main
    impresora_main()

def opcion4():
    from obtener_json import extraer_datos_recibo
    from fixtures_recibos import CASOS_RECIBO
    for nombre, caso in CASOS_RECIBO.items():
        resultado = extraer_datos_recibo(caso["input"])
        print(f"\n--- {nombre} ---")
        print(resultado)

def opcion5():
    from obtener_json import extraer_datos_mercado_pago
    print("Ejemplo con arrays de formato antiguo.")
    print("Usa la opción 4 para ver todos los casos.")

def opcion6():
    from extraer_datos_pdf import main as extraer_main
    extraer_main()

def opcion7():
    from OCR_imagen import main as ocr_main
    ocr_main()

def opcion8():
    from OCR_imagen import procesar_todas_las_imagenes
    procesar_todas_las_imagenes()

def opcion9():
    from test_fuentes import cargar_fuente_mejorada
    print("Probando carga de fuentes...")
    fuentes_a_probar = [
        (["Arial", "Liberation Sans", "DejaVu Sans"], 20, "Regular"),
        (["Times New Roman", "Liberation Serif", "DejaVu Serif"], 20, "Regular"),
        (["DejaVu Sans", "Arial"], 20, "Bold"),
        (["Verdana", "Tahoma"], 20, None),
    ]
    for nombres, tamaño, estilo in fuentes_a_probar:
        print(f"\nIntentando cargar: {nombres[0]} (tamaño: {tamaño}, estilo: {estilo})")
        fuente = cargar_fuente_mejorada(nombres, tamaño, estilo)
        if fuente:
            print(f"✓ Fuente cargada exitosamente")
            print(f"  Tipo: {type(fuente)}")
        else:
            print("✗ No se pudo cargar la fuente")

def main():
    opciones = {
        "1": opcion1,
        "2": opcion2,
        "3": opcion3,
        "4": opcion4,
        "5": opcion5,
        "6": opcion6,
        "7": opcion7,
        "8": opcion8,
        "9": opcion9,
    }

    while True:
        menu_principal()
        choix = input("Selecciona una opción: ").strip()
        if choix == "0":
            print("Salir.")
            break
        elif choix in opciones:
            try:
                opciones[choix]()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
