import fitz


def contar_paginas_pdf(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")



  
    return len(pdf)
