import re
from datetime import datetime

# --- Constantes y Mapeos ---
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
}

BBVA_COMPROBANTE_SEQ = ['COMPROBANTE', 'DE', 'LA', 'OPERACIÓN', 'GENERAL']

# Palabras vacías que no deben considerarse como nombre de servicio
PALABRAS_VACIAS = {'DE', 'LA', 'DEL', 'Y', 'E', 'EL', 'LOS', 'LAS', 'UN', 'UNA',
                   'POR', 'PARA', 'CON', 'SIN', 'SOBRE', 'ENTRE', 'MEDIANTE',
                   'CONTRA', 'HASTA', 'DESDE', 'EN', 'A', 'O', 'U', 'QUE', 'COMO',
                   'CUANDO', 'DONDE', 'QUIEN', 'CUAL', 'CUYO', 'ESTE', 'ESTA',
                   'ESTOS', 'ESTAS', 'ESE', 'ESA', 'ESOS', 'ESAS', 'AQUEL',
                   'AQUELLA', 'AQUELLOS', 'AQUELLAS', 'MI', 'TU', 'SU', 'NUESTRO',
                   'VUESTRO', 'SUS', 'MIS', 'TUS', 'MI', 'TU', 'TE', 'SE', 'LE',
                   'LES', 'NOS', 'OS', 'LO', 'LA', 'LOS', 'LAS'}

# --- Funciones Auxiliares ---

def _parsear_fecha_hora(data_list, meses_map):
    """Parsea fecha y hora desde diferentes formatos en la lista."""
    # 1. Try Ventamovil format first (DD/MM/YYYY HH:MM:SS)
    for i, item in enumerate(data_list):
        match_fecha = re.match(r'(\d{2})/(\d{2})/(\d{4})', item)
        if match_fecha and i + 1 < len(data_list):
            match_hora = re.match(r'(\d{2}):(\d{2}):(\d{2})', data_list[i+1])
            if match_hora:
                day, month, year = match_fecha.groups()
                hour, minute, second = match_hora.groups()
                try:
                    dt_obj = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
                    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError: continue

    # 2. If not found, try scattered format (DD de mes [de] YYYY, HH:MM[:SS] am/pm)
    day, month_name, year = None, None, None
    hour, minute, second = None, None, "00"
    is_pm = False
    is_am = False
    date_found = False
    # Scan for date parts: "DD de mes [de] YYYY"
    for i in range(len(data_list) - 2):
        if (data_list[i].isdigit() and len(data_list[i]) <= 2 and
            data_list[i+1].lower() == 'de' and
            data_list[i+2].lower() in meses_map):
            year_index = -1
            if i + 4 < len(data_list) and data_list[i+3].lower() == 'de': year_index = i + 4
            elif i + 3 < len(data_list): year_index = i + 3

            if year_index != -1:
                year_match = re.match(r'(\d{4})\.?,?', data_list[year_index])
                if year_match:
                    day = data_list[i].zfill(2)
                    month_name = data_list[i+2].lower()
                    year = year_match.group(1)
                    date_found = True
                    break

    time_found = False
    time_pattern = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')
    for i, item in enumerate(data_list):
        match_time = time_pattern.match(item)
        if match_time:
            hour_cand, minute_cand, second_cand = match_time.groups()
            second = second_cand if second_cand else "00"
            hour = hour_cand
            minute = minute_cand
            time_found = True

            marker_area = ""
            lookahead_limit = min(i + 4, len(data_list))
            for j in range(i + 1, lookahead_limit):
                marker_area += data_list[j].lower().replace(".", "")
            
            if 'pm' in marker_area: is_pm = True
            elif 'am' in marker_area: is_am = True
            
            break

    if date_found and time_found:
        month = meses_map.get(month_name)
        if month:
            try:
                hour_int = int(hour)
                if is_pm and hour_int != 12: hour_int += 12
                elif is_am and hour_int == 12: hour_int = 0
                
                hour = str(hour_int).zfill(2)
                minute = minute.zfill(2)
                second = second.zfill(2)

                dt_obj = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
                return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError: return None
        else: return None
    else: return None

def _list_contains_sequence(data_list, sequence):
    """Checks if a list contains a specific sequence of elements."""
    seq_len = len(sequence)
    return any(data_list[i:i+seq_len] == sequence for i in range(len(data_list) - seq_len + 1))

# --- Funciones de Extracción por Tipo ---

def _extraer_datos_bbva(data_list, meses_map):
    """Extrae datos específicos de recibos tipo BBVA."""
    resultado_bbva = {"servicio": "SAPAO"} # Default service assumption

    if _list_contains_sequence(data_list, BBVA_COMPROBANTE_SEQ):
         pass

    try:
        idx_ref = data_list.index("Referencia")
        if idx_ref + 1 < len(data_list) and re.match(r'^\d+$', data_list[idx_ref + 1]):
             resultado_bbva["referencia"] = data_list[idx_ref + 1]
    except ValueError: pass

    monto_found = False
    try:
        idx_imp_kw = -1
        try:
            idx_imp_kw = next(i for i, x in enumerate(data_list) if x.upper() == "IMPORTE")
        except StopIteration: pass

        if idx_imp_kw != -1 and idx_imp_kw + 1 < len(data_list):
            potential_monto = data_list[idx_imp_kw + 1]
            monto_match_direct = re.match(r'^(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?$', potential_monto)
            if monto_match_direct:
                value_str = potential_monto.replace(',', '')
                try:
                    resultado_bbva["monto"] = int(float(value_str))
                    monto_found = True
                except ValueError: pass

        if not monto_found:
            for i in range(len(data_list) - 1):
                if data_list[i] == '$':
                    potential_monto_after_dollar = data_list[i+1]
                    monto_match_dollar = re.match(r'(-?)(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?', potential_monto_after_dollar)
                    if monto_match_dollar:
                        sign, integer_part, decimal_part = monto_match_dollar.groups()
                        value_str = integer_part.replace(',', '') + (decimal_part if decimal_part else '')
                        try:
                            resultado_bbva["monto"] = int(float(value_str))
                            monto_found = True
                            if float(value_str) != 0.0:
                                break
                        except ValueError: pass
    except Exception: pass

    convenio_found = False
    try:
         idx_conv_kw = -1
         for i in range(len(data_list) - 2):
             if (data_list[i].lower().startswith("núm") and
                 data_list[i+1].lower() == "de" and
                 data_list[i+2].lower() == "convenio"):
                 idx_conv_kw = i + 2; break
         if idx_conv_kw != -1 and idx_conv_kw + 1 < len(data_list) and re.match(r'^\d+$', data_list[idx_conv_kw+1]):
            resultado_bbva["convenio"] = data_list[idx_conv_kw+1]
            convenio_found = True
         elif not convenio_found:
              for i in range(len(data_list) - 2):
                 if (data_list[i].upper() == "CIE" and
                     data_list[i+1] == ":" and
                     re.match(r'^\d+$', data_list[i+2])):
                     resultado_bbva["convenio"] = data_list[i+2]
                     convenio_found = True; break
    except ValueError: pass

    try:
        idx_guia = data_list.index("Guía")
        if idx_guia + 2 < len(data_list) and data_list[idx_guia + 1].upper() == "CIE":
            if re.match(r'^\d+$', data_list[idx_guia + 2]):
                resultado_bbva["guia"] = data_list[idx_guia + 2]
    except ValueError: pass

    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_bbva["hora"] = fecha_hora_str

    return resultado_bbva

def _extraer_datos_ventamovil(data_list, meses_map):
    """Extrae datos específicos de recibos tipo Ventamovil."""
    resultado_ventamovil = {}
    idx_monto_val = -1
    idx_folio_kw = -1

    try:
        idx_monto_sym = data_list.index("$")
        if idx_monto_sym + 1 < len(data_list):
            monto_cand = data_list[idx_monto_sym + 1].replace('.00', '')
            if re.match(r'^\d+$', monto_cand):
               resultado_ventamovil["monto"] = int(monto_cand)
               idx_monto_val = idx_monto_sym + 1
    except ValueError: pass

    try:
        idx_folio_kw = data_list.index("Folio")
        if idx_folio_kw + 2 < len(data_list) and data_list[idx_folio_kw + 1] == ':':
            if re.match(r'^\d+$', data_list[idx_folio_kw + 2]):
                resultado_ventamovil["folio"] = data_list[idx_folio_kw + 2]
    except ValueError: pass

    if idx_monto_val != -1 and idx_folio_kw != -1 and idx_monto_val < idx_folio_kw:
        service_parts = []
        ref_parts = []
        for i in range(idx_monto_val + 1, idx_folio_kw):
            elemento = data_list[i]
            if re.match(r'^\d{5,}$', elemento):
                ref_parts.append(elemento)
            elif re.match(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ\s./-]+$', elemento) and not elemento.isdigit():
                service_parts.append(elemento)
        if service_parts: resultado_ventamovil["servicio"] = " ".join(service_parts).strip()
        if ref_parts: resultado_ventamovil["referencia"] = "".join(ref_parts)

    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_ventamovil["hora"] = fecha_hora_str

    return resultado_ventamovil

def _extraer_datos_cashi(data_list, meses_map):
    """
    Extrae datos específicos de recibos tipo Cashi.
    Mejorada para extraer servicio usando la palabra clave 'Contrato'.
    """
    resultado_cashi = {}

    # --- Servicio: buscar basado en 'Contrato' ---
    servicio = None
    try:
        idx_contrato = data_list.index("Contrato")
        # Mirar elemento anterior
        if idx_contrato > 0:
            anterior = data_list[idx_contrato - 1].strip().upper()
            # Limpiar posibles caracteres no alfabéticos (p.ej., puntos)
            anterior_limpio = re.sub(r'[^A-ZÁÉÍÓÚÑ]', '', anterior)
            if (anterior_limpio and len(anterior_limpio) >= 2 and
                anterior_limpio not in PALABRAS_VACIAS):
                servicio = anterior_limpio
        # Si no, mirar elemento siguiente
        if not servicio and idx_contrato + 1 < len(data_list):
            siguiente = data_list[idx_contrato + 1].strip().upper()
            siguiente_limpio = re.sub(r'[^A-ZÁÉÍÓÚÑ]', '', siguiente)
            if (siguiente_limpio and len(siguiente_limpio) >= 2 and
                siguiente_limpio not in PALABRAS_VACIAS):
                servicio = siguiente_limpio
    except ValueError:
        pass

    # Si no se encontró con 'Contrato', buscar servicios conocidos
    if not servicio:
        servicios_conocidos = {"CFE", "IZZI", "MEGACABLE", "VETV", "TELECOM", "TOTALPLAY", "DISH", "SKY"}
        for elem in data_list:
            elem_up = elem.upper()
            if elem_up in servicios_conocidos:
                servicio = elem_up
                break

    # Último recurso: contar repeticiones en primeros 14, excluyendo palabras vacías
    if not servicio:
        primeros_14 = data_list[:14]
        frec = {}
        for elem in primeros_14:
            elem_up = elem.upper()
            if elem_up in PALABRAS_VACIAS or not re.match(r'^[A-ZÁÉÍÓÚÑ]+$', elem_up):
                continue
            frec[elem_up] = frec.get(elem_up, 0) + 1
        if frec:
            servicio = max(frec, key=frec.get)

    if servicio:
        resultado_cashi["servicio"] = servicio

    # --- Referencia: números largos (>=10 dígitos) ---
    ref_cand = None
    possible_refs = [item for item in data_list if re.match(r'^\d{10,}$', item)]
    if possible_refs:
        ref_cand = possible_refs[0]
        resultado_cashi["referencia"] = ref_cand

    # --- Monto ---
    try:
        monto_str = None
        for i in range(len(data_list) - 1, 0, -1):
            if data_list[i-1] == '$':
                potential_monto = data_list[i]
                monto_match = re.match(r'(-?)(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?', potential_monto)
                if monto_match:
                    sign, integer_part, decimal_part = monto_match.groups()
                    monto_str = integer_part.replace(',', '') + (decimal_part if decimal_part else '')
                    break
        if monto_str:
            resultado_cashi["monto"] = int(float(monto_str))
    except Exception: pass

    # --- Folio ---
    folio_cand = None
    try:
        # Estrategia 1: cerca de 'autorización'
        idx_aut_kw = -1
        for i in range(len(data_list) - 2):
            if (data_list[i].lower() == "no." and
                data_list[i+1].lower() == "de" and
                data_list[i+2].lower() == "autorización"):
                idx_aut_kw = i + 2
                if idx_aut_kw + 1 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+1]):
                    folio_cand = data_list[idx_aut_kw+1]
                    break
                elif idx_aut_kw + 3 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+3]):
                    folio_cand = data_list[idx_aut_kw+3]
                    break
                elif idx_aut_kw + 4 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+4]):
                    folio_cand = data_list[idx_aut_kw+4]
                    break

        # Estrategia 2: número de 6 dígitos entre 'autorización' y 'CSH...'
        if not folio_cand:
            idx_aut = -1
            idx_csh = -1
            try:
                idx_aut = max(i for i, item in enumerate(data_list) if item.lower() == "autorización")
                idx_csh = next(i for i, item in enumerate(data_list) if item.startswith("CSH") and i > idx_aut)
                for i in range(idx_aut + 1, idx_csh):
                    match_folio = re.match(r'^(\d{6})\.?$', data_list[i])
                    if match_folio:
                        folio_cand = match_folio.group(1)
                        break
            except (ValueError, StopIteration): pass

        # Estrategia 3: cerca de 'orden'
        if not folio_cand:
            idx_ord_kw = -1
            for i in range(len(data_list) - 2):
                if (data_list[i].lower() == "no." and
                    data_list[i+1].lower() == "de" and
                    data_list[i+2].lower() == "orden"):
                    idx_ord_kw = i + 2
                    if idx_ord_kw + 1 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_ord_kw+1]):
                        folio_cand = data_list[idx_ord_kw+1]
                        break
                    elif idx_ord_kw + 3 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_ord_kw+3]):
                        folio_cand = data_list[idx_ord_kw+3]
                        break

        if folio_cand:
            resultado_cashi["folio"] = folio_cand
            # Si la referencia coincide con el folio, buscar otra
            if "referencia" in resultado_cashi and resultado_cashi["referencia"] == folio_cand:
                # Tomar el siguiente número largo diferente
                otros_refs = [r for r in possible_refs if r != folio_cand]
                if otros_refs:
                    resultado_cashi["referencia"] = otros_refs[0]
                else:
                    del resultado_cashi["referencia"]  # No hay otra candidata

    except Exception: pass

    # --- Hora ---
    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_cashi["hora"] = fecha_hora_str

    return resultado_cashi

def extraer_servicio(array):
    """
    Versión original (se mantiene por compatibilidad, pero ya no se usa en cashi).
    """
    primeros_14 = array[:14]
    frecuencia = {}
    for elemento in primeros_14:
        if elemento in frecuencia:
            frecuencia[elemento] += 1
        else:
            frecuencia[elemento] = 1
    repetidos = {k: v for k, v in frecuencia.items() if v > 1}
    if repetidos:
        return list(repetidos.keys())[0]
    return None

# --- Función Principal ---

def extraer_datos_recibo(datos_entrada: list[str]) -> dict | None:
    """
    Extrae información estructurada de una lista de strings proveniente de un recibo.
    Retorna un diccionario con los datos ordenados como se solicita.
    """
    resultado = {}
    datos_str_lower = " ".join(datos_entrada).lower()

    if "bbva" in datos_str_lower or "guía cie" in datos_str_lower:
        resultado = _extraer_datos_bbva(datos_entrada, MESES)
    elif "ventamovil" in datos_str_lower or "recargame" in datos_str_lower:
        resultado = _extraer_datos_ventamovil(datos_entrada, MESES)
    elif "cashi" in datos_str_lower or any(item.startswith("CSH") for item in datos_entrada):
        resultado = _extraer_datos_cashi(datos_entrada, MESES)
    else:
        return None

    # Limpiar valores vacíos y asegurar monto positivo
    final_result = {}
    for k, v in resultado.items():
        if v is not None and v != "":
            final_result[k] = v

    if final_result.get("monto") is not None:
        try:
            numeric_monto = float(final_result["monto"])
            final_result["monto"] = abs(int(numeric_monto))
        except (ValueError, TypeError):
            final_result.pop("monto", None)

    # Ordenar según el formato deseado (servicio, referencia, monto, folio, hora)
    orden = ["servicio", "referencia", "monto", "folio", "hora"]
    resultado_ordenado = {}
    for key in orden:
        if key in final_result:
            resultado_ordenado[key] = final_result[key]
    # Agregar cualquier otra clave que pueda existir (ej. convenio, guia) al final
    for key, value in final_result.items():
        if key not in resultado_ordenado:
            resultado_ordenado[key] = value

    # Validar que tenga al menos un campo esencial
    required_keys = ["monto", "folio", "guia", "referencia", "convenio"]
    if not resultado_ordenado or not any(key in resultado_ordenado for key in required_keys):
        return None

    return resultado_ordenado

if __name__ == "__main__":
    tests = {
        "Ventamovil": ['TRANSACCION', 'EXITOSA', '11/04/2025', '11:25:37', '$', '222', 'CFE', '01679121155098250424000000222', '8', 'Folio', ':', '723241591', 'Whatsapp', 'Compartir', 'Imprimir', '+', ':', '=', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "BBVA": ['BBVA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Número', 'de', 'convenio', '000582122', 'Referencia', '3250130454645662219', 'Importe', '73', 'Comisión', '$', '00.00', 'Concepto', 'Pago', 'servicio', 'de', 'agua', 'Fecha', 'de', 'operación', '31', 'de', 'marzo', 'de', '2025', ',', '09:24', 'p.m.', 'h', 'Guía', 'CIE', '0980620', 'Folio', '2444532488', 'Número', 'de', 'operación', '2444532488', 'BBVA', 'Origin', 'Cuenta', 'de', 'Ahorro', 'Número', 'de', 'cuenta', '•', '9123'],
        "Ventamovil 2": ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "BBVA 2": ['BBVA', 'PAGAR', 'SERVICIO', 'OPERACION', 'EXITOSA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Núm', '.', 'de', 'convenio', '000582122', 'Referencia', '3240362098244425201', 'Fecha', '10', 'diciembre', '2024', 'Hora', '23:42', 'h', 'Tipo', 'de', 'operación', 'Pagar', 'servicio', 'o', 'impuesto', 'Concepto', '3240362098244425201', 'Guía', 'CIE', '5973773', 'Folio', '2862930031', 'ORIGEN', 'Cuenta', 'corriente', '+9123', 'VALOR', 'Importe', '$', '144.00', 'Comisión', 'e', 'impuestos', '$', '0.00', 'Forma', 'de', 'pago', 'Cuenta', 'de', 'origen', 'Cuenta', 'corriente'],
        "Megacable": ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "Vetv": ['TRANSACCION', 'EXITOSA', '04/01/2026', '01:37:17', '$', '269', 'VETV', '501247026120', 'Folio', ':', '3138313033', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'recargame', '-', 'app', '!'],
        "Izzi": ['7:52', '<', '.izz', '!', 'Contrato', 'Izzi', 'Izzi', 'M.', 'Recibo', 'MIMI', '18', '%', 'O', '0372847228', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', '14', 'de', 'enero', '2026', '07:50', 'p.m.', 'CSHOT8VUGZ250138436', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '$', '470.00', 'Gratis', '-', '$', '470.00', 'Saldo', 'principal', 'cashi', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '818353', 'CSHOT8VUGZ250138436', '-', '$', '470.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "SAPAO": ['BBVA', 'COMPROBANTE', 'DE', 'LA', 'OPERACIÓN', 'GENERAL', 'Tipo', 'de', 'operación', '62219', 'CIE', ':', '0582122', 'Fecha', 'de', 'operación', '31', 'marzo', '2025', ',', '21:15:00', 'h', 'Fecha', 'de', 'aplicación', '31', 'marzo', '2025', ',', '00:00:00', 'h', 'Número', 'de', 'convenio', '0582122', 'Referencia', '03250130454645662219', 'Guía', 'CIE', '0980620', 'IMPORTE', 'Importe', '$', '-73.00', 'ORIGEN', 'Cuenta', 'de', 'retiro', '⚫9123'],
        "Cashi 3": ['Г', '.izz', '!', 'Izzi', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '15', 'de', 'febrero', '2026', '04:42', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAIV3G566157329', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '470.00', '0372847228', '$', '470,00', 'Gratis', '-', '$', '470.00', '892790', 'CSHOTAIV3G566157329', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "Cashi 4": ['Г', 'Contrato', 'Megacable', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '15', 'de', 'febrero', '2026', '06:24', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAIZTF051154440', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '350.00', '5230019571', '$', '350.00', 'Gratis', '-', '$', '350.00', '383386', 'CSHOTAIZTF051154440', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "Cashi 5": ['<', 'CFE', 'CFE', 'Contrato', 'Detalles', 'de', 'la', 'transacción', 'Recibo', '-', '$', '216.00', '016791211550982506240000001884', '18', 'de', 'febrero', '2026', '09:30', 'a', '.', 'm', '.', 'ID', ':', 'CSHOTANV2X810163320', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '$', '216.00', 'Gratis', '-', '$', '216.00', '719831', 'CSHOTANV2X810163320', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "Cashi 6": ['J', 'CFE', 'CFE', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '18', 'de', 'febrero', '2026', '03:28', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAOBNZ929150380', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '362.00', '679090107863', '$', '362.00', 'Gratis', '-', '$', '362.00', '404243', 'CSHOTAOBNZ929150380', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "Cashi 7": ['CFE', 'CFE', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '19', 'de', 'febrero', '2026', '01:13', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAQ02J263151409', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '149.00', '679090416742', '$', '149.00', 'Gratis', '-', '$', '149.00', '996851', 'CSHOTAQ02J263151409', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "Cashi 8": ['CFE', 'CFE', 'Contrato', 'Recibo', '-', '$', '168.00', '016799507099392506240000002370', 'Detalles', 'de', 'la', 'transacción', '19', 'de', 'febrero', '2026', '09:01', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAQLQB263153254', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '$', '168.00', 'Gratis', '-', '$', '168.00', '067274', 'CSHOTAQLQB263153254', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
    }

    for test_name, test_data in tests.items():
        print(f"\n--- Test {test_name} ---")
        resultado = extraer_datos_recibo(test_data)
        print(resultado)