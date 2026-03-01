#!/usr/bin/python3
from escpos.printer import Usb
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

# --- CONFIGURACIÓN ---
IMAGES_FOLDER = "imagenes_ticket"
VENDOR_ID = int(env_vars.get("VENDOR_ID"), 0)
PRODUCT_ID = int(env_vars.get("PRODUCT_ID"), 0)
SHIFT_LEFT = 40  # Píxeles a desplazar hacia la izquierda
# --------------------

def print_image(printer, image_path):
    """Imprime una imagen desplazada hacia la izquierda"""
    # Mover posición de impresión hacia la izquierda
    # Calcular bytes para el desplazamiento (en puntos)
    nL = SHIFT_LEFT % 256
    nH = SHIFT_LEFT // 256
    
    # Enviar comando de desplazamiento
    printer._raw(b'\x1B\x24' + bytes([nL, nH]))  # ESC $ - Set absolute print position
    
    # Imprimir imagen
    printer.image(image_path, impl="bitImageRaster", fragment_height=1024)

def print_image_file(filename):
    """
    Imprime un archivo específico de la carpeta IMAGES_FOLDER
    
    Args:
        filename: Nombre del archivo a imprimir (ej: "ticket.png")
    
    Returns:
        bool: True si la impresión fue exitosa, False si hubo error
    """
    # Construir la ruta completa del archivo
    image_path = os.path.join(IMAGES_FOLDER, filename)
    
    # Verificar que el archivo existe
    if not os.path.exists(image_path):
        print(f"!!! ERROR: El archivo '{filename}' no existe en '{IMAGES_FOLDER}'")
        return False
    
    # Verificar que es un archivo PNG
    if not filename.lower().endswith('.png'):
        print(f"!!! ERROR: El archivo debe ser PNG")
        return False
    
    try:
        # Inicializar impresora
        p = Usb(VENDOR_ID, PRODUCT_ID)
        print(f">>> Imprimiendo archivo: {filename}")
        
        # Configurar impresora
        p._raw(b'\x1B\x40')  # Reset
        
        # Imprimir la imagen
        print_image(p, image_path)
        
        #p.cut()  # Descomentar si quieres cortar el papel
        print(">>> Impresión completada con éxito!")
        
        # Cerrar conexión
        p.close()
        return True
        
    except Exception as e:
        print(f"!!! ERROR de impresión: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_all_images():
    """Imprime todas las imágenes de la carpeta (función original)"""
    import glob
    
    image_files = sorted(glob.glob(os.path.join(IMAGES_FOLDER, "*.png")))
    
    if not image_files:
        print("!!! No se encontraron imágenes para imprimir")
        return False
    
    try:
        p = Usb(VENDOR_ID, PRODUCT_ID)
        print(f">>> Imprimiendo {len(image_files)} imágenes...")
        
        # Configurar impresora
        p._raw(b'\x1B\x40')  # Reset
        
        for i, img_path in enumerate(image_files):
            filename = os.path.basename(img_path)
            print(f">>> Página {i+1}: {filename}")
            print_image(p, img_path)
            if i < len(image_files) - 1:
                p.text("\n")  # Espacio entre páginas
        
        #p.cut()
        print(">>> Impresión completada con éxito!")
        p.close()
        return True
    
    except Exception as e:
        print(f"!!! ERROR de impresión: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    if not os.path.exists(IMAGES_FOLDER):
        print(f"Error: La carpeta '{IMAGES_FOLDER}' no existe")
        exit(1)
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        # Imprimir archivo específico
        filename = sys.argv[1]
        success = print_image_file(filename)
        exit(0 if success else 1)
    else:
        # Imprimir todas las imágenes (comportamiento original)
        print(f">>> Buscando imágenes en: {IMAGES_FOLDER}")
        print(f"Desplazando impresión {SHIFT_LEFT}px hacia la izquierda")
        success = print_all_images()
        exit(0 if success else 1)