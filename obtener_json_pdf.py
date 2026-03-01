import json
from typing import List, Dict, Any
import obtener_json  # Importamos el módulo existente

def extraer_datos_mercado_pago(textos: List[str]) -> Dict[str, Any]:
    """
    Extrae datos específicos de recibos tipo Mercado Pago.
    Devuelve solo los campos: servicio, monto, referencia, folio, hora.
    """
    resultado = {}
    
    # Identificar servicio (buscando después de "Pagaste a")
    try:
        idx_pagaste = textos.index("Pagaste a")
        if idx_pagaste + 1 < len(textos):
            resultado["servicio"] = textos[idx_pagaste + 1].upper()
    except ValueError:
        pass
    
    # Monto (buscar texto que contenga '$' y extraer número)
    for texto in textos:
        if "$" in texto:
            # Extraer números y puntos del texto
            import re
            # Buscar patrones como $ 250.00, $250.00, etc.
            match = re.search(r'\$?\s*(\d+\.?\d*)', texto)
            if match:
                monto_str = match.group(1)
                try:
                    # Convertir a float y luego a int (eliminar decimales)
                    resultado["monto"] = int(float(monto_str))
                    break
                except ValueError:
                    pass
    
    # Referencia (buscar "número de suscriptor" o "suscriptor")
    try:
        idx_suscriptor = next(i for i, texto in enumerate(textos) 
                             if "suscriptor" in texto.lower())
        if idx_suscriptor + 1 < len(textos):
            resultado["referencia"] = textos[idx_suscriptor + 1]
    except StopIteration:
        pass
    
    # Folio (buscar "Número de transacción")
    try:
        idx_transaccion = textos.index("Número de transacción")
        if idx_transaccion + 1 < len(textos):
            resultado["folio"] = textos[idx_transaccion + 1]
    except ValueError:
        pass
    
    # Hora (buscar "Fecha de pago" y convertir formato)
    try:
        idx_fecha = textos.index("Fecha de pago")
        if idx_fecha + 1 < len(textos):
            fecha_str = textos[idx_fecha + 1]
            # Convertir de DD/MM/YYYY HH:MM:SS a YYYY-MM-DD HH:MM:SS
            try:
                from datetime import datetime
                dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M:%S")
                resultado["hora"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                resultado["hora"] = fecha_str  # mantener original si falla
    except ValueError:
        pass
    
    return resultado

def procesar_array(array: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Procesa un array de diccionarios con texto y coordenadas.
    Extrae los textos y aplica la extracción de datos.
    """
    # Extraer solo los textos
    textos = [item["text"] for item in array]
    
    # Primero intentar con el extractor general de obtener_json
    resultado = obtener_json.extraer_datos_recibo(textos)
    
    # Si no se pudo extraer, intentar con el extractor de Mercado Pago
    if resultado is None:
        resultado = extraer_datos_mercado_pago(textos)
    
    # Si aún no hay resultado, devolver diccionario vacío
    if resultado is None:
        resultado = {}
    
    return resultado

def procesar_arrays_multiples(arrays: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Procesa múltiples arrays y devuelve una lista de resultados.
    """
    resultados = []
    for i, array in enumerate(arrays):
        print(f"Procesando array {i+1}...")
        resultado = procesar_array(array)
        resultados.append(resultado)
    return resultados

def main():
    """
    Función principal para pruebas.
    """
    # Ejemplos de arrays proporcionados por el usuario
    ejemplo1 = [
        {'text': 'Comprobante de pago', 'coordenadas': (246.6840057373047, 19.916013717651367, 366.0, 37.13601303100586)},
        {'text': '#140688791563', 'coordenadas': (278.86798095703125, 37.135986328125, 365.9999694824219, 54.35598373413086)},
        {'text': 'Pagaste a', 'coordenadas': (177.79200744628906, 75.00001525878906, 212.2080078125, 86.48001861572266)},
        {'text': 'Megacable', 'coordenadas': (145.3000030517578, 86.47999572753906, 244.02000427246094, 115.18000030517578)},
        {'text': 'Total pagado', 'coordenadas': (172.27999877929688, 120.82002258300781, 217.94400024414062, 132.30003356933594)},
        {'text': '$ 250.00', 'coordenadas': (144.92401123046875, 132.29998779296875, 244.64401245117188, 166.739990234375)},
        {'text': 'Detalle de operación', 'coordenadas': (24.0, 184.5079803466797, 116.20000457763672, 198.85797119140625)},
        {'text': 'Valor del recibo', 'coordenadas': (24.0, 198.85801696777344, 93.4800033569336, 213.2080078125)},
        {'text': '$ 250.00', 'coordenadas': (325.3599853515625, 198.85801696777344, 366.80999755859375, 213.2080078125)},
        {'text': 'Total pagado', 'coordenadas': (24.0, 235.70799255371094, 81.08000183105469, 250.0579833984375)},
        {'text': '$ 250.00', 'coordenadas': (325.3599853515625, 235.70799255371094, 366.80999755859375, 250.0579833984375)},
        {'text': 'número de suscriptor', 'coordenadas': (30.0, 286.0580139160156, 123.34001159667969, 300.40802001953125)},
        {'text': '5230001518', 'coordenadas': (30.0, 300.4079895019531, 85.7699966430664, 314.75799560546875)},
        {'text': 'Número de transacción', 'coordenadas': (30.0, 327.7580871582031, 132.25999450683594, 342.10809326171875)},
        {'text': '525961449', 'coordenadas': (30.0, 342.1080627441406, 81.43000030517578, 356.45806884765625)},
        {'text': 'Pagador', 'coordenadas': (30.0, 369.4580383300781, 66.72000122070312, 383.80804443359375)},
        {'text': 'EMMANUEL', 'coordenadas': (30.0, 383.8080139160156, 84.23999786376953, 398.15802001953125)},
        {'text': 'Fecha de pago', 'coordenadas': (201.0, 369.4580383300781, 266.9200134277344, 383.80804443359375)},
        {'text': '09/01/2026 11:28:37', 'coordenadas': (201.0, 383.8080139160156, 291.010009765625, 398.15802001953125)},
        {'text': 'Para cualquier duda o aclaración con tu pago, comunícate al servicio de atención a clientes de la ', 'coordenadas': (24.0, 415.1580505371094, 365.572021484375, 426.6380310058594)},
        {'text': 'empresa. Puedes consultar este comprobante en cualquier momento en la sección Actividades ', 'coordenadas': (24.0, 424.7580261230469, 365.2360534667969, 436.2380065917969)},
        {'text': 'de la app de Mercado Pago Standard.Mercado Pago Standard cobra la comisión detallada en el ', 'coordenadas': (24.0, 434.3580017089844, 366.3559265136719, 445.8379821777344)},
        {'text': 'comprobante por el uso de su app en la gestión de pagos de servicios.', 'coordenadas': (24.0, 443.9580993652344, 273.15203857421875, 455.4380798339844)}
    ]
    
    ejemplo2 = [
        {'text': 'Comprobante de pago', 'coordenadas': (246.6840057373047, 19.916013717651367, 366.0, 37.13601303100586)},
        {'text': '#141400236127', 'coordenadas': (281.58001708984375, 37.135986328125, 366.0000305175781, 54.35598373413086)},
        {'text': 'Pagaste a', 'coordenadas': (177.79200744628906, 75.00001525878906, 212.2080078125, 86.48001861572266)},
        {'text': 'Megacable', 'coordenadas': (145.3000030517578, 86.47999572753906, 244.02000427246094, 115.18000030517578)},
        {'text': 'Total pagado', 'coordenadas': (172.27999877929688, 120.82002258300781, 217.94400024414062, 132.30003356933594)},
        {'text': '$ 350.00', 'coordenadas': (145.0800018310547, 132.29998779296875, 244.36801147460938, 166.739990234375)},
        {'text': 'Detalle de operación', 'coordenadas': (24.0, 184.5079803466797, 116.20000457763672, 198.85797119140625)},
        {'text': 'Valor del recibo', 'coordenadas': (24.0, 198.85801696777344, 93.4800033569336, 213.2080078125)},
        {'text': '$ 350.00', 'coordenadas': (325.66998291015625, 198.85801696777344, 366.9399719238281, 213.2080078125)},
        {'text': 'Total pagado', 'coordenadas': (24.0, 235.70799255371094, 81.08000183105469, 250.0579833984375)},
        {'text': '$ 350.00', 'coordenadas': (325.66998291015625, 235.70799255371094, 366.9399719238281, 250.0579833984375)},
        {'text': 'número de suscriptor', 'coordenadas': (30.0, 286.0580139160156, 123.34001159667969, 300.40802001953125)},
        {'text': '5230019571', 'coordenadas': (30.0, 300.4079895019531, 85.0, 314.75799560546875)},
        {'text': 'Número de transacción', 'coordenadas': (30.0, 327.7580871582031, 132.25999450683594, 342.10809326171875)},
        {'text': '527879369', 'coordenadas': (30.0, 342.1080627441406, 82.05000305175781, 356.45806884765625)},
        {'text': 'Pagador', 'coordenadas': (30.0, 369.4580383300781, 66.72000122070312, 383.80804443359375)},
        {'text': 'EMMANUEL', 'coordenadas': (30.0, 383.8080139160156, 84.23999786376953, 398.15802001953125)},
        {'text': 'Fecha de pago', 'coordenadas': (201.0, 369.4580383300781, 266.9200134277344, 383.80804443359375)},
        {'text': '14/01/2026 17:46:57', 'coordenadas': (201.0, 383.8080139160156, 290.0600280761719, 398.15802001953125)},
        {'text': 'Para cualquier duda o aclaración con tu pago, comunícate al servicio de atención a clientes de la ', 'coordenadas': (24.0, 415.1580505371094, 365.572021484375, 426.6380310058594)},
        {'text': 'empresa. Puedes consultar este comprobante en cualquier momento en la sección Actividades ', 'coordenadas': (24.0, 424.7580261230469, 365.2360534667969, 436.2380065917969)},
        {'text': 'de la app de Mercado Pago Standard.Mercado Pago Standard cobra la comisión detallada en el ', 'coordenadas': (24.0, 434.3580017089844, 366.3559265136719, 445.8379821777344)},
        {'text': 'comprobante por el uso de su app en la gestión de pagos de servicios.', 'coordenadas': (24.0, 443.9580993652344, 273.15203857421875, 455.4380798339844)}
    ]
    
    arrays = [ejemplo1, ejemplo2]
    
    print("Procesando arrays de ejemplo...")
    resultados = procesar_arrays_multiples(arrays)
    
    for i, resultado in enumerate(resultados):
        print(f"\nResultado array {i+1}:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
