CASOS_RECIBO = {
    "Ventamovil": {
        "input": ['TRANSACCION', 'EXITOSA', '11/04/2025', '11:25:37', '$', '222', 'CFE', '01679121155098250424000000222', '8', 'Folio', ':', '723241591', 'Whatsapp', 'Compartir', 'Imprimir', '+', ':', '=', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "esperado": {"servicio": "CFE", "referencia": "01679121155098250424000000222", "monto": 222, "folio": "723241591"}
    },
    # "BBVA": {
    #     "input": ['BBVA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Número', 'de', 'convenio', '000582122', 'Referencia', '3250130454645662219', 'Importe', '73', 'Comisión', '$', '00.00', 'Concepto', 'Pago', 'servicio', 'de', 'agua', 'Fecha', 'de', 'operación', '31', 'de', 'marzo', 'de', '2025', ',', '09:24', 'p.m.', 'h', 'Guía', 'CIE', '0980620', 'Folio', '2444532488', 'Número', 'de', 'operación', '2444532488', 'BBVA', 'Origin', 'Cuenta', 'de', 'Ahorro', 'Número', 'de', 'cuenta', '•', '9123'],
    #     "esperado": {"servicio": "SAPAO", "referencia": "3250130454645662219", "monto": 73, "folio": "2444532488", "convenio": "000582122", "guia": "0980620"}
    # },
    "Ventamovil 2": {
        "input": ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "esperado": {"servicio": "IZZI TELECOM", "referencia": "0372847228", "monto": 370, "folio": "105798858"}
    },
    # "BBVA 2": {
    #     "input": ['BBVA', 'PAGAR', 'SERVICIO', 'OPERACION', 'EXITOSA', 'Servicio', 'GOB', 'EDO', 'OAX', '/', 'SRIA', '.', 'DE', 'FINANZAS', '/', 'Núm', '.', 'de', 'convenio', '000582122', 'Referencia', '3240362098244425201', 'Fecha', '10', 'diciembre', '2024', 'Hora', '23:42', 'h', 'Tipo', 'de', 'operación', 'Pagar', 'servicio', 'o', 'impuesto', 'Concepto', '3240362098244425201', 'Guía', 'CIE', '5973773', 'Folio', '2862930031', 'ORIGEN', 'Cuenta', 'corriente', '+9123', 'VALOR', 'Importe', '$', '144.00', 'Comisión', 'e', 'impuestos', '$', '0.00', 'Forma', 'de', 'pago', 'Cuenta', 'de', 'origen', 'Cuenta', 'corriente'],
    #     "esperado": {"servicio": "SAPAO", "referencia": "3240362098244425201", "monto": 144, "folio": "2862930031", "guia": "5973773"}
    # },
    "Megacable": {
        "input": ['TRANSACCION', 'EXITOSA', '17/04/2025', '05:12:40', '$', '370', 'IZZI', 'TELECOM', '0372847228', 'Folio', ':', '105798858', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'Π', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'Ventamovil', '!'],
        "esperado": {"servicio": "IZZI TELECOM", "referencia": "0372847228", "monto": 370, "folio": "105798858"}
    },
    "Vetv": {
        "input": ['TRANSACCION', 'EXITOSA', '04/01/2026', '01:37:17', '$', '269', 'VETV', '501247026120', 'Folio', ':', '3138313033', 'Whatsapp', 'Compartir', 'Imprimir', '+', 'NUEVA', 'INICIO', 'TRANSAC', '.', '¡', 'Gracias', 'por', 'formar', 'parte', 'de', 'la', 'familia', 'recargame', '-', 'app', '!'],
        "esperado": {"servicio": "VETV", "referencia": "501247026120", "monto": 269, "folio": "3138313033"}
    },
    "Izzi": {
        "input": ['7:52', '<', '.izz', '!', 'Contrato', 'Izzi', 'Izzi', 'M.', 'Recibo', 'MIMI', '18', '%', 'O', '0372847228', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', '14', 'de', 'enero', '2026', '07:50', 'p.m.', 'CSHOT8VUGZ250138436', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '$', '470.00', 'Gratis', '-', '$', '470.00', 'Saldo', 'principal', 'cashi', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '818353', 'CSHOT8VUGZ250138436', '-', '$', '470.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "IZZI", "referencia": "0372847228", "monto": 470, "folio": "818353"}
    },
    "SAPAO": {
        "input": ['BBVA', 'COMPROBANTE', 'DE', 'LA', 'OPERACIÓN', 'GENERAL', 'Tipo', 'de', 'operación', '62219', 'CIE', ':', '0582122', 'Fecha', 'de', 'operación', '31', 'marzo', '2025', ',', '21:15:00', 'h', 'Fecha', 'de', 'aplicación', '31', 'marzo', '2025', ',', '00:00:00', 'h', 'Número', 'de', 'convenio', '0582122', 'Referencia', '03250130454645662219', 'Guía', 'CIE', '0980620', 'IMPORTE', 'Importe', '$', '-73.00', 'ORIGEN', 'Cuenta', 'de', 'retiro', '⚫9123'],
        "esperado": {"servicio": "SAPAO", "referencia": "03250130454645662219", "monto": 73, "convenio": "0582122", "guia": "0980620"}
    },
    "Cashi 3": {
        "input": ['Г', '.izz', '!', 'Izzi', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '15', 'de', 'febrero', '2026', '04:42', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAIV3G566157329', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '470.00', '0372847228', '$', '470,00', 'Gratis', '-', '$', '470.00', '892790', 'CSHOTAIV3G566157329', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "IZZI", "referencia": "0372847228", "monto": 470, "folio": "892790"}
    },
    "Cashi 4": {
        "input": ['Г', 'Contrato', 'Megacable', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '15', 'de', 'febrero', '2026', '06:24', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAIZTF051154440', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '350.00', '5230019571', '$', '350.00', 'Gratis', '-', '$', '350.00', '383386', 'CSHOTAIZTF051154440', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "MEGACABLE", "referencia": "5230019571", "monto": 350, "folio": "383386"}
    },
    "Cashi 5": {
        "input": ['<', 'CFE', 'CFE', 'Contrato', 'Detalles', 'de', 'la', 'transacción', 'Recibo', '-', '$', '216.00', '016791211550982506240000001884', '18', 'de', 'febrero', '2026', '09:30', 'a', '.', 'm', '.', 'ID', ':', 'CSHOTANV2X810163320', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '$', '216.00', 'Gratis', '-', '$', '216.00', '719831', 'CSHOTANV2X810163320', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "CFE", "referencia": "016791211550982506240000001884", "monto": 216, "folio": "719831"}
    },
    "Cashi 6": {
        "input": ['J', 'CFE', 'CFE', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '18', 'de', 'febrero', '2026', '03:28', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAOBNZ929150380', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '362.00', '679090107863', '$', '362.00', 'Gratis', '-', '$', '362.00', '404243', 'CSHOTAOBNZ929150380', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "CFE", "referencia": "679090107863", "monto": 362, "folio": "404243"}
    },
    "Cashi 7": {
        "input": ['CFE', 'CFE', 'Contrato', 'Recibo', 'Detalles', 'de', 'la', 'transacción', '19', 'de', 'febrero', '2026', '01:13', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAQ02J263151409', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '-', '$', '149.00', '679090416742', '$', '149.00', 'Gratis', '-', '$', '149.00', '996851', 'CSHOTAQ02J263151409', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "CFE", "referencia": "679090416742", "monto": 149, "folio": "996851"}
    },
    "Cashi 8": {
        "input": ['CFE', 'CFE', 'Contrato', 'Recibo', '-', '$', '168.00', '016799507099392506240000002370', 'Detalles', 'de', 'la', 'transacción', '19', 'de', 'febrero', '2026', '09:01', 'p', '.', 'm', '.', 'ID', ':', 'CSHOTAQLQB263153254', 'Detalles', 'del', 'pago', 'Importe', 'Comisión', 'Pagaste', 'con', 'cashi', 'Saldo', 'principal', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', '$', '168.00', 'Gratis', '-', '$', '168.00', '067274', 'CSHOTAQLQB263153254', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.'],
        "esperado": {"servicio": "CFE", "referencia": "016799507099392506240000002370", "monto": 168, "folio": "067274"}
    },
}
