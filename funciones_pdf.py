import fitz


def contar_paginas_pdf(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")

    total_paginas = len(pdf)

    pdf.close()

    return total_paginas


def convertir_pdf_a_imagenes(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")

    imagenes = []

    for pagina in pdf:

        pix = pagina.get_pixmap()

        imagen = pix.tobytes("png")

        imagenes.append(imagen)

    pdf.close()

    return imagenes


def extraer_texto_pdf(contenido_pdf):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    texto = ""

    for pagina in pdf:

        texto += pagina.get_text()

    pdf.close()

    return texto


def buscar_paginas_documentos(contenido_pdf):

    pdf = fitz.open(stream=contenido_pdf, filetype="pdf")

    paginas = {
        "formato_2": None,
        "formato_3": None,
    }

    for numero, pagina in enumerate(pdf):

        texto = pagina.get_text().upper()

        if paginas["formato_2"] is None and "FORMATO 2" in texto:
            paginas["formato_2"] = numero

        if paginas["formato_3"] is None and "FORMATO 3" in texto:
            paginas["formato_3"] = numero

    pdf.close()

    return paginas
