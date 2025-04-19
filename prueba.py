def process_payment_data(arr):
    def parse_date(date_str, case):
        month_dict = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }
        
        if case == 'BBVA' or case == 'CSH':
            parts = date_str.replace(',', '').replace('.', '').split()
            day = parts[0].zfill(2)
            month = month_dict[parts[2].lower()]
            year = parts[3]
            time_part = parts[4]
            am_pm = parts[5].lower()
            
            time_split = time_part.split(':')
            hour = time_split[0].zfill(2)
            minute = time_split[1].zfill(2)
            
            if 'p.m.' in am_pm and hour != '12':
                hour = str(int(hour) + 12)
            elif 'a.m.' in am_pm and hour == '12':
                hour = '00'
                
            return f"{year}-{month}-{day} {hour}:{minute}:00"
        
        elif case == 'Ventamovil':
            date_part, time_part = date_str.split(' ')
            day, month, year = date_part.split('/')
            return f"{year}-{month}-{day} {time_part}"
    
    case = None
    if any("BBVA" in s for s in arr):
        case = "BBVA"
    elif any(s.startswith("CSH") for s in arr):
        case = "CSH"
    elif "Ventamovil" in arr:
        case = "Ventamovil"
    else:
        return None

    result = {
        "servicio": "SAPAO" if case == "BBVA" else "CFE",
        "referencia": "",
        "monto": 0,
        "folio": "",
        "hora": ""
    }

    if case == "BBVA":
        result["convenio"] = ""
        for i, s in enumerate(arr):
            if s == "Guía" and arr[i+1] == "CIE":
                result["convenio"] = arr[i+2]
            if s == "Referencia":
                result["referencia"] = arr[i+1]
            if s == "Folio":
                result["folio"] = arr[i+1].replace(':', '')
            if s == "Importe":
                result["monto"] = int(arr[i+1])
        
        date_str = ' '.join([s for s in arr if 'de' in s and ('a.m.' in s or 'p.m.' in s)][0].split()[:6])
        result["hora"] = parse_date(date_str, case)
    
    elif case == "CSH":
        for i, s in enumerate(arr):
            if s.startswith("CSH"):
                for j in range(i-1, 0, -1):
                    if arr[j].isdigit() and len(arr[j]) == 12:
                        result["referencia"] = arr[j]
                        break
            if "autorización" in s:
                for j in range(i+1, len(arr)):
                    if arr[j].isdigit():
                        result["folio"] = arr[j]
                        break
                    if arr[j].startswith("CSH"):
                        break
            if "$" == s:
                result["monto"] = int(float(arr[i+1].replace(',', '')))
        
        date_str = ' '.join([s for s in arr if 'de' in s and ('a. m.' in s or 'p. m.' in s)][0].split()[:5])
        result["hora"] = parse_date(date_str, case)
    
    elif case == "Ventamovil":
        cfe_index = max([i for i, s in enumerate(arr) if s == "CFE"])
        folio_index = arr.index("Folio")
        result["referencia"] = ''.join([s for s in arr[cfe_index+1:folio_index] if s.isdigit()])
        result["folio"] = arr[folio_index+1].replace(':', '')
        result["monto"] = int(arr[arr.index("$")+1])
        date_str = [s for s in arr if '/' in s and ':' in s][0]
        result["hora"] = parse_date(date_str, case)
    
    if case != "BBVA":
        result.pop("convenio", None)
    
    return result

# Test cases
test_case_1 = ['8:58', 'M', '№', '63', '%', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '679950709602', '15', 'de', 'abril', '2025.', '08:58', 'a.', 'm.', 'CSHOSURLKU643173323', '$', '330.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '330.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '788145', 'CSHOSURLKU643173323', '-', '$', '330.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.']
test_case_2 = ['TRANSACCION', 'EXITOSA', '11/04/2025', '11:25:37', '$', '222', 'CFE', '01679121155098250424000000222', '8', 'Folio', ':', '723241591', 'Whatsapp', 'Compartir', 'Imprimir', '+', ':', '=', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!']
test_case_3 = ['BBVA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Número', 'de', 'convenio', '000582122', 'Referencia', '3250130454645662219', 'Importe', '73', 'Comisión', '$', '00.00', 'Concepto', 'Pago', 'servicio', 'de', 'agua', 'Fecha', 'de', 'operación', '31', 'de', 'marzo', 'de', '2025', ',', '09:24', 'p.m.', 'h', 'Guía', 'CIE', '0980620', 'Folio', '2444532488', 'Número', 'de', 'operación', '2444532488', 'BBVA', 'Origin', 'Cuenta', 'de', 'Ahorro', 'Número', 'de', 'cuenta', '•', '9123']

print(process_payment_data(test_case_1))
print(process_payment_data(test_case_2))
print(process_payment_data(test_case_3))

if __name__ == "__main__":
# --- Ejemplos de Test ---
    test_case_cashi = ['8:58', 'M', '№', '63', '%', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '679950709602', '15', 'de', 'abril', '2025.', '08:58', 'a', '.', 'm', '.', 'CSHOSURLKU643173323', '$', '330.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '330.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '788145', 'CSHOSURLKU643173323', '-', '$', '330.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.']
    test_case_ventamovil = ['TRANSACCION', 'EXITOSA', '11/04/2025', '11:25:37', '$', '222', 'CFE', '01679121155098250424000000222', '8', 'Folio', ':', '723241591', 'Whatsapp', 'Compartir', 'Imprimir', '+', ':', '=', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!']
    test_case_bbva = ['BBVA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Número', 'de', 'convenio', '000582122', 'Referencia', '3250130454645662219', 'Importe', '73', 'Comisión', '$', '00.00', 'Concepto', 'Pago', 'servicio', 'de', 'agua', 'Fecha', 'de', 'operación', '31', 'de', 'marzo', 'de', '2025', ',', '09:24', 'p.m.', 'h', 'Guía', 'CIE', '0980620', 'Folio', '2444532488', 'Número', 'de', 'operación', '2444532488', 'BBVA', 'Origin', 'Cuenta', 'de', 'Ahorro', 'Número', 'de', 'cuenta', '•', '9123']
    test_case_ventamovil_2 = ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!']
    test_case_cashi_2 = ['10:44', 'M.', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', 'OMIMI', '11', '%', '679160508372', '16', 'de', 'febrero', '2025', '•', '12:19', 'p', '.', 'm', '.', 'CSHOSRSG8Y707269475', '$', '66.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '66.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '354815', 'CSHOSRSG8Y707269475', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.', '-', '$', '66.00']
    test_case_bbva_2 = ['BBVA', 'PAGAR', 'SERVICIO', 'OPERACION', 'EXITOSA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Núm', '.', 'de', 'convenio', '000582122', 'Referencia', '3240362098244425201', 'Fecha', '10', 'diciembre', '2024', 'Hora', '23:42', 'h', 'Tipo', 'de', 'operación', 'Pagar', 'servicio', 'o', 'impuesto', 'Concepto', '3240362098244425201', 'Guía', 'CIE', '5973773', 'Folio', '2862930031', 'ORIGEN', 'Cuenta', 'corriente', '+9123', 'VALOR', 'Importe', '$', '144.00', 'Comisión', 'e', 'impuestos', '$', '0.00', 'Forma', 'de', 'pago', 'Cuenta', 'de', 'origen', 'Cuenta', 'corriente']
    test_case_bbva_3 = ['BBVA', 'COMPROBANTE', 'DE', 'LA', 'OPERACIÓN', 'GENERAL', 'Tipo', 'de', 'operación', '62219', 'CIE', ':', '0582122', 'Fecha', 'de', 'operación', '31', 'marzo', '2025', ',', '21:15:00', 'h', 'Fecha', 'de', 'aplicación', '31', 'marzo', '2025', ',', '00:00:00', 'h', 'Número', 'de', 'convenio', '0582122', 'Referencia', '03250130454645662219', 'Guía', 'CIE', '0980620', 'IMPORTE', 'Importe', '$', '-73.00', 'ORIGEN', 'Cuenta', 'de', 'retiro', '⚫9123']
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

    print("\n--- Test BBVA 3---")
    resultado_bbva_3 = extraer_datos_recibo(test_case_bbva_3)
    print(resultado_bbva_3)