#!/usr/bin/env python3
from PIL import ImageFont
import os
import subprocess

def encontrar_fuente_por_nombre(nombre_familia, estilo=None):
    """
    Encuentra la ruta de una fuente usando fc-match
    """
    try:
        # Construir el patrón de búsqueda
        patron = nombre_familia
        if estilo:
            patron += f":{estilo}"
        
        # Ejecutar fc-match
        resultado = subprocess.run(
            ['fc-match', '-v', patron],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if resultado.returncode == 0:
            # Buscar la línea que contiene el archivo
            for linea in resultado.stdout.split('\n'):
                if 'file:' in linea:
                    ruta = linea.split('"')[1]
                    if os.path.exists(ruta):
                        return ruta
    except Exception as e:
        print(f"Error buscando fuente {nombre_familia}: {e}")
    
    return None

def cargar_fuente_mejorada(nombres_familia, tamaño, estilo=None):
    """
    Versión mejorada para cargar fuentes
    """
    # Primero intentar con fc-match
    for nombre in nombres_familia:
        ruta = encontrar_fuente_por_nombre(nombre, estilo)
        if ruta:
            try:
                return ImageFont.truetype(ruta, tamaño)
            except Exception as e:
                print(f"Error cargando fuente {ruta}: {e}")
                continue
    
    # Si no funciona, intentar con búsqueda directa en rutas comunes
    rutas_comunes = [
        "/usr/share/fonts/",
        "/usr/local/share/fonts/",
        "/home/manus-pc/.fonts/",
        "/home/manus-pc/.local/share/fonts/",
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/TTF/",
        "/usr/share/fonts/liberation/",
    ]
    
    # Patrones de nombres a buscar
    patrones = []
    for nombre in nombres_familia:
        patrones.extend([
            f"{nombre}.ttf",
            f"{nombre}.TTF",
            f"{nombre.lower()}.ttf",
            f"{nombre.upper()}.TTF",
            f"{nombre.replace(' ', '')}.ttf",
        ])
    
    for ruta_base in rutas_comunes:
        if os.path.exists(ruta_base):
            for patron in patrones:
                ruta_completa = os.path.join(ruta_base, patron)
                if os.path.exists(ruta_completa):
                    try:
                        return ImageFont.truetype(ruta_completa, tamaño)
                    except Exception as e:
                        print(f"Error cargando {ruta_completa}: {e}")
                        continue
    
    # Último recurso: fuente por defecto
    print("Advertencia: No se encontraron las fuentes específicas. Usando fuente por defecto.")
    return ImageFont.load_default()

# Prueba de la función
if __name__ == "__main__":
    print("Probando carga de fuentes...")
    
    # Probar con diferentes fuentes
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
