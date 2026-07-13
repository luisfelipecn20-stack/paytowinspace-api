import re
import fitz

from funciones_vision import analizar_imagen


MINIMO_CARACTERES_TEXTO = 80

PROMPT_OCR = """
Actúa únicamente como un sistema OCR.

Transcribe literalmente todo el texto visible de la imagen.

Reglas obligatorias:

- No analices el documento.
- No resumas.
- No expliques.
- No corrijas nombres, direcciones, fechas, códigos ni números.
- No inventes información.
- Conserva los saltos de línea en lo posible.
- Conserva las marcas X de las opciones seleccionadas.
- Lee el documento de arriba hacia abajo y de izquierda a derecha.
- No utilices Markdown.
- No generes tablas Markdown.
- No devuelvas JSON.
- Devuelve exclusivamente el texto transcrito.
"""


def texto_es_suficiente(texto):

    if not texto:
        return False

    texto_sin_espacios = re.sub(
        r"\s+",
        "",
        texto
    )

    return (
        len(texto_sin_espacios)
        >= MINIMO_CARACTERES_TEXTO
    )


def convertir_pagina_a_imagen_ocr(pagina):

    # Renderiza la página aproximadamente a 300 DPI.
    escala = 300 / 72

    matriz = fitz.Matrix(
        escala,
        escala
    )

    pix = pagina.get_pixmap(
        matrix=matriz,
        alpha=False
    )

    return pix.tobytes("png")


def contar_paginas_pdf(contenido_pdf):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    total_paginas = len(pdf)

    pdf.close()

    return total_paginas


def convertir_pdf_a_imagenes(contenido_pdf):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

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


def extraer_texto_pagina(
    contenido_pdf,
    numero_pagina
):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    try:

        pagina = pdf[numero_pagina]

        # Primer intento: extraer texto digital con PyMuPDF.
        texto = pagina.get_text(
            "text",
            sort=True
        ).strip()

        if texto_es_suficiente(texto):
            return texto

        # Segundo intento: usar OCR si la página está escaneada.
        imagen = convertir_pagina_a_imagen_ocr(
            pagina
        )

        texto_ocr = analizar_imagen(
            [imagen],
            PROMPT_OCR
        )

        if isinstance(texto_ocr, str):
            return texto_ocr.strip()

        return ""

    finally:

        pdf.close()


def buscar_paginas_documentos(contenido_pdf):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    paginas = {
        "formato_2": None,
        "formato_3": None,
    }

    for numero, pagina in enumerate(pdf):

        texto = pagina.get_text().upper()

        if (
            paginas["formato_2"] is None
            and "FORMATO 2" in texto
        ):
            paginas["formato_2"] = numero

        if (
            paginas["formato_3"] is None
            and "FORMATO 3" in texto
        ):
            paginas["formato_3"] = numero

    pdf.close()

    return paginas
