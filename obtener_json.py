import re
from datetime import datetime

# --- Constantes y Mapeos ---
MESES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
}

BBVA_COMPROBANTE_SEQ = ['COMPROBANTE', 'DE', 'LA', 'OPERACIÓN', 'GENERAL']

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
        if (data_list[i].isdigit() and len(data_list[i]) <= 2 and # Ensure it's a potential day
            data_list[i+1].lower() == 'de' and
            data_list[i+2].lower() in meses_map):
            year_index = -1
            # Look for 'de YYYY' or just 'YYYY' after the month
            if i + 4 < len(data_list) and data_list[i+3].lower() == 'de': year_index = i + 4
            elif i + 3 < len(data_list): year_index = i + 3

            if year_index != -1:
                # Allow optional punctuation after year (like '.')
                year_match = re.match(r'(\d{4})\.?,?', data_list[year_index])
                if year_match:
                    day = data_list[i].zfill(2)
                    month_name = data_list[i+2].lower()
                    year = year_match.group(1)
                    date_found = True
                    break # Date found, stop searching

    # Scan for time parts: "HH:MM" or "HH:MM:SS" and AM/PM marker nearby
    time_found = False
    # Make seconds optional, handle potential extra chars like 'h' or '.' after time
    time_pattern = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')
    for i, item in enumerate(data_list):
        match_time = time_pattern.match(item)
        if match_time:
            hour_cand, minute_cand, second_cand = match_time.groups()
            # Use found seconds if available, default to 00 otherwise
            second = second_cand if second_cand else "00"
            hour = hour_cand
            minute = minute_cand
            time_found = True

            # Check for AM/PM marker *after* the time element
            # Look ahead a few elements for 'am' or 'pm' (case-insensitive, ignore dots)
            marker_area = ""
            lookahead_limit = min(i + 4, len(data_list)) # Look up to 3 elements ahead
            for j in range(i + 1, lookahead_limit):
                marker_area += data_list[j].lower().replace(".", "")
            
            if 'pm' in marker_area: is_pm = True
            elif 'am' in marker_area: is_am = True
            
            break # Time found, stop searching

    # Assemble the date and time
    if date_found and time_found:
        month = meses_map.get(month_name)
        if month:
            try:
                hour_int = int(hour)
                # Adjust hour for PM/AM
                if is_pm and hour_int != 12: hour_int += 12
                elif is_am and hour_int == 12: hour_int = 0 # Midnight case
                
                hour = str(hour_int).zfill(2)
                minute = minute.zfill(2)
                second = second.zfill(2) # Ensure seconds are also two digits

                dt_obj = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}:{second}", "%Y-%m-%d %H:%M:%S")
                return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError: return None # Handle potential datetime conversion errors
        else: return None # Month name wasn't valid
    else: return None # Date or time components not found

def _list_contains_sequence(data_list, sequence):
    """Checks if a list contains a specific sequence of elements."""
    seq_len = len(sequence)
    return any(data_list[i:i+seq_len] == sequence for i in range(len(data_list) - seq_len + 1))

# --- Funciones de Extracción por Tipo ---

def _extraer_datos_bbva(data_list, meses_map):
    """Extrae datos específicos de recibos tipo BBVA."""
    resultado_bbva = {"servicio": "SAPAO"} # Default service assumption

    # Check for the specific sequence (optional action)
    if _list_contains_sequence(data_list, BBVA_COMPROBANTE_SEQ):
         # print("DEBUG: BBVA Comprobante General sequence detected.") # For debugging
         pass # No specific action required based on sequence detection yet

    # Referencia (flexible, check if numeric after keyword)
    try:
        idx_ref = data_list.index("Referencia")
        # Check if the next element is a digit string (potentially long)
        if idx_ref + 1 < len(data_list) and re.match(r'^\d+$', data_list[idx_ref + 1]):
             resultado_bbva["referencia"] = data_list[idx_ref + 1]
    except ValueError: pass

    # --- CORRECCIÓN MONTO ---
    # Monto (Prioritize value after 'Importe', fallback to '$')
    monto_found = False
    try:
        # Find 'Importe' or 'IMPORTE' keyword
        idx_imp_kw = -1
        try:
            # Find the first occurrence of 'Importe' case-insensitively
            idx_imp_kw = next(i for i, x in enumerate(data_list) if x.upper() == "IMPORTE")
        except StopIteration: pass # Keyword not found

        # 1. Try element immediately after 'Importe' if keyword was found
        if idx_imp_kw != -1 and idx_imp_kw + 1 < len(data_list):
            potential_monto = data_list[idx_imp_kw + 1]
            # Use regex to check if it's a valid number format (int or float), ignore commas
            monto_match_direct = re.match(r'^(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?$', potential_monto)
            if monto_match_direct:
                value_str = potential_monto.replace(',', '') # Remove commas for float conversion
                try:
                    resultado_bbva["monto"] = int(float(value_str))
                    monto_found = True
                except ValueError: pass # Handle potential conversion errors if format is weird despite regex

        # 2. Fallback: Search for '$' followed by a number if not found via 'Importe'
        if not monto_found:
            for i in range(len(data_list) - 1): # Search entire list
                if data_list[i] == '$':
                    # Check the element *after* '$'
                    potential_monto_after_dollar = data_list[i+1]
                    # Regex allows optional sign, digits, optional comma separators, optional decimal part
                    monto_match_dollar = re.match(r'(-?)(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?', potential_monto_after_dollar)
                    if monto_match_dollar:
                        sign, integer_part, decimal_part = monto_match_dollar.groups()
                        # Reconstruct the number string without commas for conversion
                        value_str = integer_part.replace(',', '') + (decimal_part if decimal_part else '')
                        try:
                            resultado_bbva["monto"] = int(float(value_str))
                            monto_found = True
                            # IMPORTANT: Break *only* if we are reasonably sure this is the main amount.
                            # Heuristic: If 'Importe' was found earlier, the '$' amount might be commission.
                            # If 'Importe' was *not* found, this '$' amount is our best guess.
                            # Or, if the amount after '$' is substantial (not 0.00), likely the main amount.
                            if float(value_str) != 0.0:
                                break # Found a non-zero amount after '$', assume it's the one.
                        except ValueError: pass # Handle potential conversion errors

    except Exception as e:
        # print(f"DEBUG: Error extracting monto for BBVA: {e}") # Optional debug
        pass
    # --- FIN CORRECCIÓN MONTO ---


    # Convenio (fallback a Numero de convenio)
    convenio_found = False
    try:
         idx_conv_kw = -1
         # Find 'Número'/'Núm.', 'de', 'convenio' sequence (flexible)
         for i in range(len(data_list) - 2):
             # Allow 'Núm.' or 'Número'
             if (data_list[i].lower().startswith("núm") and
                 data_list[i+1].lower() == "de" and
                 data_list[i+2].lower() == "convenio"):
                 idx_conv_kw = i + 2; break
         if idx_conv_kw != -1 and idx_conv_kw + 1 < len(data_list) and re.match(r'^\d+$', data_list[idx_conv_kw+1]):
            resultado_bbva["convenio"] = data_list[idx_conv_kw+1]
            convenio_found = True
         # Add check for 'CIE', ':', 'convenio' pattern from new test case
         elif not convenio_found:
              for i in range(len(data_list) - 2):
                 # Look for CIE : <digits>
                 if (data_list[i].upper() == "CIE" and
                     data_list[i+1] == ":" and
                     re.match(r'^\d+$', data_list[i+2])):
                     resultado_bbva["convenio"] = data_list[i+2]
                     convenio_found = True; break

    except ValueError: pass

    # --- CORRECCIÓN GUIA CIE ---
    # Guia (based on Guía CIE)
    try:
        idx_guia = data_list.index("Guía") # Find the word "Guía"
        if idx_guia + 2 < len(data_list) and data_list[idx_guia + 1].upper() == "CIE":
            if re.match(r'^\d+$', data_list[idx_guia + 2]):
                resultado_bbva["guia"] = data_list[idx_guia + 2]
    except ValueError: pass # Guía CIE not found

    # Hora
    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_bbva["hora"] = fecha_hora_str

    return resultado_bbva

def _extraer_datos_ventamovil(data_list, meses_map):
    """Extrae datos específicos de recibos tipo Ventamovil."""
    resultado_ventamovil = {}
    idx_monto_val = -1
    idx_folio_kw = -1

    # 1. Encontrar Monto y su índice
    try:
        idx_monto_sym = data_list.index("$")
        if idx_monto_sym + 1 < len(data_list):
            # Handle potential '.00' and check if the result is digits
            monto_cand = data_list[idx_monto_sym + 1].replace('.00', '')
            if re.match(r'^\d+$', monto_cand):
               resultado_ventamovil["monto"] = int(monto_cand)
               idx_monto_val = idx_monto_sym + 1
    except ValueError: pass # '$' not found

    # 2. Encontrar Folio y el índice de la palabra "Folio"
    try:
        idx_folio_kw = data_list.index("Folio")
        # Expect ':' after 'Folio', then the number
        if idx_folio_kw + 2 < len(data_list) and data_list[idx_folio_kw + 1] == ':':
            if re.match(r'^\d+$', data_list[idx_folio_kw + 2]):
                resultado_ventamovil["folio"] = data_list[idx_folio_kw + 2]
    except ValueError: pass # 'Folio' not found

    # 3. Encontrar Servicio y Referencia (expected between monto value and Folio keyword)
    if idx_monto_val != -1 and idx_folio_kw != -1 and idx_monto_val < idx_folio_kw:
        service_parts = []
        ref_parts = []
        # Iterate through elements *between* the amount value and the 'Folio' keyword
        for i in range(idx_monto_val + 1, idx_folio_kw):
            elemento = data_list[i]
            # Assume long digit sequences are reference, others are service name parts
            if re.match(r'^\d{5,}$', elemento): # Heuristic: reference is usually long
                ref_parts.append(elemento)
            # Check for letters/spaces/common punctuation, ignore symbols/short numbers
            elif re.match(r'^[A-Za-zÁÉÍÓÚÑáéíóúñ\s./-]+$', elemento) and not elemento.isdigit():
                service_parts.append(elemento)
        if service_parts: resultado_ventamovil["servicio"] = " ".join(service_parts).strip()
        if ref_parts: resultado_ventamovil["referencia"] = "".join(ref_parts)

    # 4. Extraer Hora
    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_ventamovil["hora"] = fecha_hora_str

    return resultado_ventamovil

def _extraer_datos_cashi(data_list, meses_map):
    """Extrae datos específicos de recibos tipo Cashi/Otro (CSH...)."""
    resultado_cashi = {"servicio": "CFE"} # Default assumption for Cashi

    # Referencia (Look for a likely contract number - often 12 digits, but be flexible)
    # Prioritize longer digit sequences that aren't likely the folio or amount.
    ref_cand = None
    possible_refs = [item for item in data_list if re.match(r'^\d{10,}$', item)] # At least 10 digits
    if possible_refs:
        # Avoid picking something that looks like a folio if folio extraction works later
        # For now, just take the first long digit sequence found
        ref_cand = possible_refs[0] # Simple approach
        if ref_cand: resultado_cashi["referencia"] = ref_cand


    # Monto (positive, often preceded by '$')
    try:
        monto_str = None
        # Search backwards for '$' then grab the next element
        for i in range(len(data_list) - 1, 0, -1): # Start from end, go to index 1
             if data_list[i-1] == '$': # Check element before current index
                 potential_monto = data_list[i]
                 # Allow optional sign, digits, optional comma separators, optional decimal part
                 monto_match = re.match(r'(-?)(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?', potential_monto)
                 if monto_match:
                     sign, integer_part, decimal_part = monto_match.groups()
                     # Reconstruct the number string without commas
                     monto_str = integer_part.replace(',', '') + (decimal_part if decimal_part else '')
                     # Prefer the last '$' amount found when searching backwards
                     break
        if monto_str:
            resultado_cashi["monto"] = int(float(monto_str)) # Convert cleaned string
    except Exception: pass # Catch potential errors during search/conversion

    # Folio (Often near 'autorización' or 'No. de orden', or a specific length digit sequence)
    folio_cand = None
    try:
        # Strategy 1: Look for 'No.' 'de' 'autorización' followed by digits
        idx_aut_kw = -1
        for i in range(len(data_list) - 2):
            if (data_list[i].lower() == "no." and
                data_list[i+1].lower() == "de" and
                data_list[i+2].lower() == "autorización"):
                idx_aut_kw = i + 2
                # Look immediately after the sequence
                if idx_aut_kw + 1 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+1]):
                    folio_cand = data_list[idx_aut_kw+1]
                    break
                # Look further ahead if immediate doesn't match (sometimes separated by other words)
                elif idx_aut_kw + 3 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+3]):
                     folio_cand = data_list[idx_aut_kw+3]
                     break
                elif idx_aut_kw + 4 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_aut_kw+4]):
                     folio_cand = data_list[idx_aut_kw+4]
                     break

        # Strategy 2: Look for a 6-digit number between 'autorización' and 'CSH...' if Strategy 1 failed
        if not folio_cand:
            idx_aut = -1
            idx_csh = -1
            try:
                # Find last occurrence of 'autorización'
                idx_aut = max(i for i, item in enumerate(data_list) if item.lower() == "autorización")
                # Find first occurrence of 'CSH...' *after* 'autorización'
                idx_csh = next(i for i, item in enumerate(data_list) if item.startswith("CSH") and i > idx_aut)

                # Search between these indices for a 6-digit number (allow optional dots)
                for i in range(idx_aut + 1, idx_csh):
                     match_folio = re.match(r'^(\d{6})\.?$', data_list[i])
                     if match_folio:
                         folio_cand = match_folio.group(1)
                         break
            except (ValueError, StopIteration): pass # Indices not found

        # Strategy 3: Fallback - Look for 'No.' 'de' 'orden' followed by digits
        if not folio_cand:
            idx_ord_kw = -1
            for i in range(len(data_list) - 2):
                if (data_list[i].lower() == "no." and
                    data_list[i+1].lower() == "de" and
                    data_list[i+2].lower() == "orden"):
                    idx_ord_kw = i + 2
                    # Look immediately after
                    if idx_ord_kw + 1 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_ord_kw+1]):
                        folio_cand = data_list[idx_ord_kw+1]
                        break
                    # Look further ahead
                    elif idx_ord_kw + 3 < len(data_list) and re.match(r'^\d{6,}$', data_list[idx_ord_kw+3]):
                         folio_cand = data_list[idx_ord_kw+3]
                         break

        if folio_cand:
            resultado_cashi["folio"] = folio_cand
            # If reference wasn't found before, and folio looks different, update ref guess
            if "referencia" not in resultado_cashi and possible_refs:
                non_folio_refs = [p for p in possible_refs if p != folio_cand]
                if non_folio_refs:
                    resultado_cashi["referencia"] = non_folio_refs[0]


    except Exception: pass # Catch potential errors during folio search

    # Hora
    fecha_hora_str = _parsear_fecha_hora(data_list, meses_map)
    if fecha_hora_str:
        resultado_cashi["hora"] = fecha_hora_str

    return resultado_cashi


# --- Función Principal ---

def extraer_datos_recibo(datos_entrada: list[str]) -> dict | None:
    """
    Extrae información estructurada de una lista de strings proveniente de un recibo.
    Identifica el tipo de recibo y delega la extracción a funciones específicas.
    Retorna un diccionario con los datos o None si no se puede procesar.
    """
    resultado = {}
    datos_str_lower = " ".join(datos_entrada).lower() # For easier keyword checking

    # Identificar tipo y llamar a la función extractora correspondiente
    # Prioritize BBVA identification
    if "bbva" in datos_str_lower or "guía cie" in datos_str_lower:
        # print("DEBUG: Detected as BBVA")
        resultado = _extraer_datos_bbva(datos_entrada, MESES)
    elif "ventamovil" in datos_str_lower:
        # print("DEBUG: Detected as Ventamovil")
        resultado = _extraer_datos_ventamovil(datos_entrada, MESES)
    # Check for Cashi identifiers ('cashi', 'CSH...')
    elif "cashi" in datos_str_lower or any(item.startswith("CSH") for item in datos_entrada):
        # print("DEBUG: Detected as Cashi")
        resultado = _extraer_datos_cashi(datos_entrada, MESES)
    else:
        # Tipo desconocido o no identificable por palabras clave principales
        # print("DEBUG: Unknown type")
        return None # O retornar {} si prefieres un diccionario vacío

    # Limpieza final: Crear diccionario final solo con valores no nulos/vacíos
    final_result = {}
    if resultado: # Check if extraction function returned something
        for k, v in resultado.items():
            if v is not None and v != "":
                 final_result[k] = v

    # Asegurarse que el monto sea positivo si existe y es numérico
    if final_result.get("monto") is not None:
        try:
            # Ensure it's treated as a number before abs()
            numeric_monto = float(final_result["monto"])
            final_result["monto"] = abs(int(numeric_monto))
        except (ValueError, TypeError):
             # If monto is somehow not numeric, remove it or log error
             # print(f"WARN: Monto value '{final_result.get('monto')}' is not numeric.")
             final_result.pop("monto", None)


    # Retornar None si el diccionario resultante está vacío después de la limpieza
    # O si no contiene información mínima requerida (e.g., monto or folio/guia/ref)
    required_keys = ["monto", "folio", "guia", "referencia", "convenio"]
    if not final_result or not any(key in final_result for key in required_keys):
        # print("DEBUG: Final result empty or lacks essential keys.")
        return None

    return final_result

if __name__ == "__main__":
# --- Ejemplos de Test ---
    test_case_cashi = ['8:58', 'M', '№', '63', '%', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '679950709602', '15', 'de', 'abril', '2025.', '08:58', 'a', '.', 'm', '.', 'CSHOSURLKU643173323', '$', '330.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '330.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '788145', 'CSHOSURLKU643173323', '-', '$', '330.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.']
    test_case_ventamovil = ['TRANSACCION', 'EXITOSA', '11/04/2025', '11:25:37', '$', '222', 'CFE', '01679121155098250424000000222', '8', 'Folio', ':', '723241591', 'Whatsapp', 'Compartir', 'Imprimir', '+', ':', '=', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!']
    test_case_bbva = ['BBVA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Número', 'de', 'convenio', '000582122', 'Referencia', '3250130454645662219', 'Importe', '73', 'Comisión', '$', '00.00', 'Concepto', 'Pago', 'servicio', 'de', 'agua', 'Fecha', 'de', 'operación', '31', 'de', 'marzo', 'de', '2025', ',', '09:24', 'p.m.', 'h', 'Guía', 'CIE', '0980620', 'Folio', '2444532488', 'Número', 'de', 'operación', '2444532488', 'BBVA', 'Origin', 'Cuenta', 'de', 'Ahorro', 'Número', 'de', 'cuenta', '•', '9123']
    test_case_ventamovil_2 = ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!']
    test_case_cashi_2 = ['10:44', 'M.', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', 'OMIMI', '11', '%', '679160508372', '16', 'de', 'febrero', '2025', '•', '12:19', 'p', '.', 'm', '.', 'CSHOSRSG8Y707269475', '$', '66.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '66.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '354815', 'CSHOSRSG8Y707269475', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.', '-', '$', '66.00']
    # Test case BBVA 2, notice 'Importe' '$' '144.00' sequence and lack of time 'am/pm' marker
    test_case_bbva_2 = ['BBVA', 'PAGAR', 'SERVICIO', 'OPERACION', 'EXITOSA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Núm', '.', 'de', 'convenio', '000582122', 'Referencia', '3240362098244425201', 'Fecha', '10', 'diciembre', '2024', 'Hora', '23:42', 'h', 'Tipo', 'de', 'operación', 'Pagar', 'servicio', 'o', 'impuesto', 'Concepto', '3240362098244425201', 'Guía', 'CIE', '5973773', 'Folio', '2862930031', 'ORIGEN', 'Cuenta', 'corriente', '+9123', 'VALOR', 'Importe', '$', '144.00', 'Comisión', 'e', 'impuestos', '$', '0.00', 'Forma', 'de', 'pago', 'Cuenta', 'de', 'origen', 'Cuenta', 'corriente']

    # --- Ejecutar Tests ---
    print("--- Test Cashi ---")
    resultado_cashi = extraer_datos_recibo(test_case_cashi)
    print(resultado_cashi)

    print("\n--- Test Ventamovil ---")
    resultado_ventamovil = extraer_datos_recibo(test_case_ventamovil)
    print(resultado_ventamovil)

    print("\n--- Test BBVA ---")
    resultado_bbva = extraer_datos_recibo(test_case_bbva)
    print(resultado_bbva)

    print("\n--- Test Ventamovil 2---")
    resultado_ventamovil_2 = extraer_datos_recibo(test_case_ventamovil_2)
    print(resultado_ventamovil_2)

    print("\n--- Test Cashi 2---")
    resultado_cashi_2 = extraer_datos_recibo(test_case_cashi_2)
    print(resultado_cashi_2)

    print("\n--- Test BBVA 2---")
    resultado_bbva_2 = extraer_datos_recibo(test_case_bbva_2)
    print(resultado_bbva_2)