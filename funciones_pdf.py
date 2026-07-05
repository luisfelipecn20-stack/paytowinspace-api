import fitz


def contar_paginas_pdf(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")

    return len(pdf)


def convertir_pdf_a_imagenes(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")

    imagenes = []

    for pagina in pdf:

        pix = pagina.get_pixmap()

        imagen = pix.tobytes("png")

        imagenes.append(imagen)

    return imagenes

def extraer_texto_pdf(contenido_pdf):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    texto = ""

    for pagina in pdf:

        texto += pagina.get_text()

    return texto
