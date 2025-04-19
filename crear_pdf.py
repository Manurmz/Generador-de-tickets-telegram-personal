from fpdf import FPDF, XPos, YPos

def crear_pdf(info):
    fuente = "Times"
    if 'comision' not in info:
        info['comision'] = 15
    info['total'] = info['monto'] + info['comision']
    
    # Crear el objeto PDF con el tamaño personalizado
    pdf = FPDF(unit='mm', format=(56, 100))
    pdf.set_auto_page_break(auto=False, margin=0)  # Desactivar salto de página automático
    pdf.set_margins(left=3, top=4, right=3)  # Establecer márgenes
    pdf.add_page()

    # Título
    pdf.set_font(fuente, size=13, style="B")
    pdf.cell(0, 4, "Miscelanea Emmanuel", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(4)

    # Información del servicio
    pdf.set_font(fuente, size=9)
    pdf.cell(0, 4, "CARGO EXITOSO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 4, f"{info['servicio']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.multi_cell(0, 4, f'Referencia: {info["referencia"]}', align='L')
    pdf.ln(4)

    # Monto, comisión y total
    pdf.cell(0, 4, f"Monto: ${info['monto']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(1)
    pdf.cell(0, 4, f"Comisión: ${info['comision']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(1)
    pdf.cell(0, 4, "Total: ", new_x=XPos.LMARGIN, align='C')
    pdf.set_font(fuente, size=10, style="B")
    pdf.set_x(32)
    pdf.cell(0, 4, f"${info['total']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2)
    pdf.set_font(fuente, size=9)
    # Autorización y folio
    if 'folio' in info:
        
        pdf.cell(0, 4, f"Autorización {info['servicio']}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(0, 4, f"{info['folio']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(1)

    #convenio CIE agua
    if 'guia' in info:
        pdf.cell(0, 4, f"Guia CIE :", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(0, 4, f"{info['guia']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')        
        pdf.ln(1)

    # Hora
    pdf.cell(0, 4, info['hora'], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(4)

    # Mensajes adicionales
    pdf.multi_cell(0, 4, "El periodo para la aplicacion de pago es de 24 a 36 horas.")
    pdf.ln(1)
    pdf.multi_cell(0, 4, "Conserve este comprobante para futuras aclaraciones.", align="C")
    pdf.ln(1)
    pdf.multi_cell(0, 4, "ESTE NO ES UN COMPROBANTE FISCAL", align="C")
    pdf.ln(4)
    nombre = f"ticket:{info['hora']}__f:{info['folio'] if 'folio' in info else info['guia']}.pdf"
    # Guardar el PDF
    with open(nombre, "wb") as archivo:
        archivo.write(pdf.output())
    return nombre

if __name__ == "__main__":
    info = {
        "servicio": "CFE",
        "referencia": "2934492229344922293449222934492",
        "monto": 1564,
        "guia":"3456789",
        "folio": "440653",
        "hora": "2024-10-20 13:20:04"
    }
    resultado = crear_pdf(info)
    nombre = "ticket.pdf"