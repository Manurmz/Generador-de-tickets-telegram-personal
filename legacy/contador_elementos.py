def contar_elementos_repetidos(array):
    """
    Toma los primeros 14 elementos de un array y cuenta cuántos se repiten.
    
    Args:
        array: Lista de elementos (pueden ser strings, números, etc.)
    
    Returns:
        dict: Diccionario con los elementos como claves y su frecuencia como valores
    """
    # Tomar los primeros 14 elementos
    primeros_14 = array[:14]
    
    # Crear un diccionario para contar las frecuencias
    frecuencia = {}
    
    # Contar la frecuencia de cada elemento
    for elemento in primeros_14:
        if elemento in frecuencia:
            frecuencia[elemento] += 1
        else:
            frecuencia[elemento] = 1
    
    repetidos = {k: v for k, v in frecuencia.items() if v > 1}
    #print(f"\nElementos que se repiten ({len(repetidos)}):", repetidos)
    return repetidos

# Ejemplo de uso con tus datos
Cashi = ['8:58', 'M', '№', '63', '%', '←', 'Recibo', 'CFE', 'CFE', 'CFE', 'Contrato', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '679950709602', '15', 'de', 'abril', '2025.', '08:58', 'a', '.', 'm', '.', 'CSHOSURLKU643173323', '$', '330.00', 'Gratis', 'cashi', 'Saldo', 'principal', '-', '$', '330.00', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '788145', 'CSHOSURLKU643173323', '-', '$', '330.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.']

Izzi = ['7:52', '<', '.izz', '!', 'Contrato', 'Izzi', 'Izzi', 'M.', 'Recibo', 'MIMI', '18', '%', 'O', '0372847228', 'DETALLES', 'DE', 'LA', 'TRANSACCIÓN', 'Fecha', 'y', 'hora', 'ID', '14', 'de', 'enero', '2026', '07:50', 'p.m.', 'CSHOT8VUGZ250138436', 'DETALLES', 'DEL', 'PAGO', 'Importe', 'Comisión', 'PAGASTE', 'CON', '$', '470.00', 'Gratis', '-', '$', '470.00', 'Saldo', 'principal', 'cashi', 'No.', 'de', 'autorización', 'No.', 'de', 'orden', 'Total', '818353', 'CSHOT8VUGZ250138436', '-', '$', '470.00', 'Tu', 'comprobante', 'quedará', 'guardado', 'en', 'tu', 'historial', 'de', 'movimientos', '.']

# Analizar el array Cashi
print("=== Análisis del array Cashi ===")
frecuencia_cashi = contar_elementos_repetidos(Izzi)
#print("Primeros 14 elementos:", Cashi[:14])
print("\nFrecuencia de elementos:")
print(frecuencia_cashi)
# for elemento, count in frecuencia_cashi.items():
#     print(f"  '{elemento}': {count} vez(ces)")
    
# Encontrar elementos que se repiten
# repetidos_cashi = {k: v for k, v in frecuencia_cashi.items() if v > 1}
# print(f"\nElementos que se repiten ({len(repetidos_cashi)}):", repetidos_cashi)

# Analizar el array Izzi
# print("\n=== Análisis del array Izzi ===")
# frecuencia_izzi = contar_elementos_repetidos(Izzi)
# print("Primeros 14 elementos:", Izzi[:14])
# print("\nFrecuencia de elementos:")
# for elemento, count in frecuencia_izzi.items():
#     print(f"  '{elemento}': {count} vez(ces)")

# Encontrar elementos que se repiten
# repetidos_izzi = {k: v for k, v in frecuencia_izzi.items() if v > 1}
# print(f"\nElementos que se repiten ({len(repetidos_izzi)}):", repetidos_izzi)

# Versión alternativa que también muestra el porcentaje
def contar_y_mostrar(array, nombre="Array"):
    """
    Versión más completa que muestra estadísticas detalladas
    """
    primeros_14 = array[:14]
    frecuencia = {}
    
    for elemento in primeros_14:
        frecuencia[elemento] = frecuencia.get(elemento, 0) + 1
    
    print(f"\n{'='*50}")
    print(f"Análisis detallado de {nombre}")
    print(f"{'='*50}")
    print(f"Total de elementos analizados: {len(primeros_14)}")
    print(f"Elementos únicos: {len(frecuencia)}")
    
    repetidos = {k: v for k, v in frecuencia.items() if v > 1}
    print(f"Elementos repetidos: {len(repetidos)}")
    
    if repetidos:
        print("\nDetalle de repeticiones:")
        for elemento, count in repetidos.items():
            porcentaje = (count / len(primeros_14)) * 100
            print(f"  '{elemento}': {count} veces ({porcentaje:.1f}%)")
    
    return frecuencia

# Usar la versión más completa
# contar_y_mostrar(Cashi, "Cashi")
# contar_y_mostrar(Izzi, "Izzi")