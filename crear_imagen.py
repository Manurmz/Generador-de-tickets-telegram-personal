from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import subprocess

def crear_imagen(info):
    # Configuración base - tamaño fijo 400x800
    ancho = 400
    alto = 850
    
    # Crear imagen con fondo blanco
    img = Image.new('RGB', (ancho, alto), color='white')
    draw = ImageDraw.Draw(img)
    
    # Función mejorada para encontrar fuentes disponibles
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
            # Silenciar errores, simplemente continuar con otros métodos
            pass
        
        return None
    
    def cargar_fuente(nombres_familia, tamaño, estilo=None):
        """
        Versión mejorada para cargar fuentes
        """
        # Primero intentar con fc-match
        for nombre in nombres_familia:
            ruta = encontrar_fuente_por_nombre(nombre, estilo)
            if ruta:
                try:
                    return ImageFont.truetype(ruta, tamaño)
                except Exception:
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
            # Para nombres como "DejaVu Sans" también buscar "DejaVuSans"
            nombre_sin_espacios = nombre.replace(' ', '')
            patrones.extend([
                f"{nombre}.ttf",
                f"{nombre}.TTF",
                f"{nombre.lower()}.ttf",
                f"{nombre.upper()}.TTF",
                f"{nombre_sin_espacios}.ttf",
                f"{nombre_sin_espacios.lower()}.ttf",
            ])
        
        for ruta_base in rutas_comunes:
            if os.path.exists(ruta_base):
                for patron in patrones:
                    ruta_completa = os.path.join(ruta_base, patron)
                    if os.path.exists(ruta_completa):
                        try:
                            return ImageFont.truetype(ruta_completa, tamaño)
                        except Exception:
                            continue
        
        # Último recurso: fuente por defecto
        print("Advertencia: No se encontraron las fuentes específicas. Usando fuente por defecto.")
        return ImageFont.load_default()
    
    # Cargar fuentes - usando Times como primera opción (igual que el PDF)
    # Tamaños ajustados para imagen 400x800
    fuente_titulo = cargar_fuente(["Times New Roman", "Times", "DejaVu Serif"], 36, "Bold")
    fuente_normal = cargar_fuente(["Times New Roman", "Times", "DejaVu Serif"], 28)
    fuente_destacada = cargar_fuente(["Times New Roman", "Times", "DejaVu Serif"], 29, "Bold")
    fuente_pequena = cargar_fuente(["Times New Roman", "Times", "DejaVu Serif"], 21)
    
    # Posición inicial
    y_pos = 20
    
    # 1. Título "Miscelanea Emmanuel" (centrado, negrita)
    titulo = "Miscelanea Emmanuel"
    bbox_titulo = draw.textbbox((0, 0), titulo, font=fuente_titulo)
    ancho_titulo = bbox_titulo[2] - bbox_titulo[0]
    x_pos = (ancho - ancho_titulo) // 2
    draw.text((x_pos, y_pos), titulo, font=fuente_titulo, fill='black')
    y_pos += 60
    
    # 2. "CARGO EXITOSO" (centrado)
    servicio_texto = "CARGO EXITOSO"
    bbox_servicio = draw.textbbox((0, 0), servicio_texto, font=fuente_normal)
    ancho_servicio = bbox_servicio[2] - bbox_servicio[0]
    x_pos = (ancho - ancho_servicio) // 2
    draw.text((x_pos, y_pos), servicio_texto, font=fuente_normal, fill='black')
    y_pos += 37
    
    # 3. Nombre del servicio (centrado)
    if 'servicio' in info:
        bbox_nombre = draw.textbbox((0, 0), info['servicio'], font=fuente_destacada)
        ancho_nombre = bbox_nombre[2] - bbox_nombre[0]
        x_pos = (ancho - ancho_nombre) // 2
        draw.text((x_pos, y_pos), info['servicio'], font=fuente_destacada, fill='black')
        y_pos += 50
    
    # 4. Referencia (alineado a la izquierda)
    if 'referencia' in info:
        referencia_texto = f'Referencia: {info["referencia"]}'
        draw.text((20, y_pos), referencia_texto, font=fuente_normal, fill='black')
        y_pos += 60
    
    # 5. Monto, comisión y total
    if 'monto' in info:
        # Configurar comisión si no existe
        if 'comision' not in info:
            info['comision'] = 15
        info['total'] = info['monto'] + info['comision']
        
        # Monto (centrado)
        monto_texto = f"Monto: ${info['monto']}"
        bbox_monto = draw.textbbox((0, 0), monto_texto, font=fuente_normal)
        ancho_monto = bbox_monto[2] - bbox_monto[0]
        x_pos = (ancho - ancho_monto) // 2
        draw.text((x_pos, y_pos), monto_texto, font=fuente_normal, fill='black')
        y_pos += 37
        
        # Comisión (centrado)
        comision_texto = f"Comisión: ${info['comision']}"
        bbox_comision = draw.textbbox((0, 0), comision_texto, font=fuente_normal)
        ancho_comision = bbox_comision[2] - bbox_comision[0]
        x_pos = (ancho - ancho_comision) // 2
        draw.text((x_pos, y_pos), comision_texto, font=fuente_normal, fill='black')
        y_pos += 37
        
        # Total (con formato similar al PDF)
        total_texto = "Total: "
        bbox_total = draw.textbbox((0, 0), total_texto, font=fuente_normal)
        ancho_total = bbox_total[2] - bbox_total[0]
        
        # Calcular posición para "Total: " centrado
        x_pos_total = (ancho - ancho_total) // 2 - 15
        draw.text((x_pos_total, y_pos), total_texto, font=fuente_normal, fill='black')
        
        # Monto del total en negrita
        total_monto = f"${info['total']}"
        bbox_monto_total = draw.textbbox((0, 0), total_monto, font=fuente_destacada)
        x_pos_monto = x_pos_total + ancho_total + 5
        draw.text((x_pos_monto, y_pos), total_monto, font=fuente_destacada, fill='black')
        y_pos += 60
    
    # 6. Autorización y folio (si existe)
    if 'folio' in info and 'servicio' in info:
        autorizacion_texto = f"Autorización {info['servicio']}:"
        bbox_autorizacion = draw.textbbox((0, 0), autorizacion_texto, font=fuente_normal)
        ancho_autorizacion = bbox_autorizacion[2] - bbox_autorizacion[0]
        x_pos = (ancho - ancho_autorizacion) // 2
        draw.text((x_pos, y_pos), autorizacion_texto, font=fuente_normal, fill='black')
        y_pos += 40
        
        folio_texto = f"{info['folio']}"
        bbox_folio = draw.textbbox((0, 0), folio_texto, font=fuente_destacada)
        ancho_folio = bbox_folio[2] - bbox_folio[0]
        x_pos = (ancho - ancho_folio) // 2
        draw.text((x_pos, y_pos), folio_texto, font=fuente_destacada, fill='black')
        y_pos += 60
    
    # 7. Guía CIE (si existe)
    if 'guia' in info:
        guia_texto = "Guía CIE:"
        bbox_guia = draw.textbbox((0, 0), guia_texto, font=fuente_normal)
        ancho_guia = bbox_guia[2] - bbox_guia[0]
        x_pos = (ancho - ancho_guia) // 2
        draw.text((x_pos, y_pos), guia_texto, font=fuente_normal, fill='black')
        y_pos += 45
        
        guia_num_texto = f"{info['guia']}"
        bbox_guia_num = draw.textbbox((0, 0), guia_num_texto, font=fuente_destacada)
        ancho_guia_num = bbox_guia_num[2] - bbox_guia_num[0]
        x_pos = (ancho - ancho_guia_num) // 2
        draw.text((x_pos, y_pos), guia_num_texto, font=fuente_destacada, fill='black')
        y_pos += 60
    
    # 8. Hora (centrada)
    if 'hora' in info:
        hora_texto = info['hora']
        bbox_hora = draw.textbbox((0, 0), hora_texto, font=fuente_normal)
        ancho_hora = bbox_hora[2] - bbox_hora[0]
        x_pos = (ancho - ancho_hora) // 2
        draw.text((x_pos, y_pos), hora_texto, font=fuente_normal, fill='black')
        y_pos += 90
    
    # 9. Mensajes adicionales - separados en 2 arrays
    # Primer array: mensajes alineados a la izquierda
    mensajes_izquierda = [
        "El periodo para la aplicación de pago es de 24 a 36 horas.",
        "Conserve este comprobante para futuras aclaraciones."
    ]
    
    # Segundo array: mensaje centrado
    mensaje_centrado = ["ESTE NO ES UN COMPROBANTE FISCAL"]
    
    # Procesar mensajes alineados a la izquierda
    for mensaje in mensajes_izquierda:
        fuente_actual = fuente_pequena
        
        # Calcular si el texto es muy largo para el ancho
        bbox_mensaje = draw.textbbox((0, 0), mensaje, font=fuente_actual)
        ancho_mensaje = bbox_mensaje[2] - bbox_mensaje[0]
        
        # Si el texto es demasiado ancho, dividirlo en líneas
        if ancho_mensaje > (ancho - 40):
            palabras = mensaje.split()
            lineas = []
            linea_actual = ""
            
            for palabra in palabras:
                prueba_linea = f"{linea_actual} {palabra}".strip()
                bbox_prueba = draw.textbbox((0, 0), prueba_linea, font=fuente_actual)
                ancho_prueba = bbox_prueba[2] - bbox_prueba[0]
                
                if ancho_prueba <= (ancho - 40):
                    linea_actual = prueba_linea
                else:
                    if linea_actual:
                        lineas.append(linea_actual)
                    linea_actual = palabra
            
            if linea_actual:
                lineas.append(linea_actual)
            
            for linea in lineas:
                bbox_linea = draw.textbbox((0, 0), linea, font=fuente_actual)
                ancho_linea = bbox_linea[2] - bbox_linea[0]
                x_pos = 20  # Alineado a la izquierda con margen
                draw.text((x_pos, y_pos), linea, font=fuente_actual, fill='black')
                y_pos += 30
        else:
            # Texto cabe en una línea
            x_pos = 20  # Alineado a la izquierda con margen
            draw.text((x_pos, y_pos), mensaje, font=fuente_actual, fill='black')
            y_pos += 40
    y_pos += 20
    
    # Procesar mensaje centrado (en negrita)
    for mensaje in mensaje_centrado:
        fuente_actual = cargar_fuente(["Times New Roman", "Times", "DejaVu Serif"], 22, "Bold")
        
        # Calcular si el texto es muy largo para el ancho
        bbox_mensaje = draw.textbbox((0, 0), mensaje, font=fuente_actual)
        ancho_mensaje = bbox_mensaje[2] - bbox_mensaje[0]
        
        # Si el texto es demasiado ancho, dividirlo en líneas
        if ancho_mensaje > (ancho - 40):
            palabras = mensaje.split()
            lineas = []
            linea_actual = ""
            
            for palabra in palabras:
                prueba_linea = f"{linea_actual} {palabra}".strip()
                bbox_prueba = draw.textbbox((0, 0), prueba_linea, font=fuente_actual)
                ancho_prueba = bbox_prueba[2] - bbox_prueba[0]
                
                if ancho_prueba <= (ancho - 40):
                    linea_actual = prueba_linea
                else:
                    if linea_actual:
                        lineas.append(linea_actual)
                    linea_actual = palabra
            
            if linea_actual:
                lineas.append(linea_actual)
            
            for linea in lineas:
                bbox_linea = draw.textbbox((0, 0), linea, font=fuente_actual)
                ancho_linea = bbox_linea[2] - bbox_linea[0]
                x_pos = (ancho - ancho_linea) // 2  # Centrado
                draw.text((x_pos, y_pos), linea, font=fuente_actual, fill='black')
                y_pos += 30
        else:
            # Texto cabe en una línea
            bbox_mensaje = draw.textbbox((0, 0), mensaje, font=fuente_actual)
            ancho_mensaje = bbox_mensaje[2] - bbox_mensaje[0]
            x_pos = (ancho - ancho_mensaje) // 2  # Centrado
            draw.text((x_pos, y_pos), mensaje, font=fuente_actual, fill='black')
            y_pos += 40
    
    # Guardar la imagen
    nombre_archivo = f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    if 'hora' in info and ('folio' in info or 'guia' in info):
        identificador = info.get('folio', info.get('guia', ''))
        # Reemplazar caracteres problemáticos en el nombre del archivo
        hora_limpia = info['hora'].replace(':', '_').replace(' ', '_').replace('-', '_')
        nombre_archivo = f"ticket:{hora_limpia}__f:{identificador}.png"
    
    # Guardar en la carpeta imagenes_ticket
    ruta_completa = os.path.join("imagenes_ticket", nombre_archivo)
    img.save(ruta_completa)
    print(f"Imagen guardada como: {ruta_completa}")
    
    return nombre_archivo

if __name__ == "__main__":
    # Datos de ejemplo
    info = {
        "servicio": "MEGACABLE",
        "referencia": "5260001518",
        "monto": 201,
        "comision": 15,
        "total": 216,
        "folio": "515656639",
        "hora": "2025-12-09 07:37:00"
    }
    
    # También puedes probar con guía CIE
    info_con_guia = {
        "servicio": "AGUA POTABLE",
        "referencia": "987654321",
        "monto": 350,
        "comision": 10,
        "guia": "G123456789",
        "hora": "2025-12-10 10:15:00"
    }
    
    print("Creando ticket con datos de ejemplo...")
    nombre_archivo= crear_imagen(info)
    
    # Mostrar información sobre la imagen creada
    #print(f"Tamaño de la imagen: {imagen.size}")
    print(f"El nombre de la imagen es : {nombre_archivo}")
    
    # Mostrar la imagen (opcional)
    # imagen.show()
