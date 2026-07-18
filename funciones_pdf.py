import re
import fitz
import json

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

def pagina_es_escaneada(
    contenido_pdf,
    numero_pagina=0
):

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    try:
        pagina = pdf[numero_pagina]

        texto_digital = pagina.get_text(
            "text",
            sort=True
        ).strip()

        return not texto_es_suficiente(
            texto_digital
        )

    finally:
        pdf.close()

def limpiar_respuesta_visual(valor):

    if not isinstance(valor, str):
        return ""

    return re.sub(
        r"\s+",
        " ",
        valor
    ).strip().upper()

def extraer_campos_visuales_formato_2(contenido_pdf):

    campos_vacios = {
        "niss": "",
        "reclamante": "",
        "direccion_suministro": "",
        "direccion_procesal": "",
        "solicita_contraste": ""
    }

    pdf = fitz.open(
        stream=contenido_pdf,
        filetype="pdf"
    )

    try:
        pagina = pdf[0]

        escala = 300 / 72

        matriz = fitz.Matrix(
            escala,
            escala
        )

        pix = pagina.get_pixmap(
            matrix=matriz,
            alpha=False
        )

        imagen = pix.tobytes("png")

        prompt = """
Observa únicamente la primera página del Formato 2.

Lee directamente las celdas visibles de la imagen. No utilices el
orden de una transcripción OCR y no inventes información.

Extrae estos cinco campos:

1. niss:
   Lee todos los dígitos de la celda ubicada junto a
   "N° DE SUMINISTRO".
   Devuelve únicamente los números.

2. reclamante:
   Lee por separado las tres columnas ubicadas bajo
   "NOMBRE DEL SOLICITANTE O REPRESENTANTE":

   - Apellido Paterno
   - Apellido Materno
   - Nombres

   Une los tres valores respetando exactamente este orden:
   APELLIDO PATERNO + APELLIDO MATERNO + NOMBRES.

   No omitas el apellido paterno aunque esté tenue.
   No incluyas las etiquetas del formulario.

3. direccion_suministro:
   Lee todas las celdas de "UBICACIÓN DEL PREDIO":

   - Calle, jirón, avenida o pasaje
   - Número
   - Manzana
   - Lote
   - Urbanización o barrio
   - Provincia
   - Distrito

   Une solamente los valores visibles, en ese orden.
   No incluyas palabras impresas como:
   "Calle, Jirón, Avenida", "N°", "Mz", "Lote",
   "Urbanización, barrio", "Provincia" o "Distrito".

4. direccion_procesal:
   Lee todas las celdas de "DOMICILIO PROCESAL":

   - Calle, jirón, avenida o pasaje
   - Número
   - Manzana
   - Lote
   - Urbanización o barrio
   - Provincia
   - Distrito

   Une solamente los valores visibles, en ese orden.
   No incluyas teléfono, correo electrónico, código postal,
   declaraciones, casillas ni etiquetas del formulario.

5. solicita_contraste:
   Revisa exclusivamente la sección inferior que comienza con:

   "DECLARACIÓN DEL RECLAMANTE
   (aplicable a reclamos por consumo medido)
   Solicito la realización de la prueba de contrastación..."

   No confundas esta sección con:
   - la entrega de cartilla informativa;
   - la autorización para recibir correos;
   - la confirmación de contrastación ubicada junto al correo.

   Devuelve:
   - "SI" si la X está en la opción Sí;
   - "NO" si la X está en la opción No;
   - "" si no puede determinarse.

Devuelve exclusivamente JSON válido:

{
  "niss": "",
  "reclamante": "",
  "direccion_suministro": "",
  "direccion_procesal": "",
  "solicita_contraste": ""
}

No agregues explicaciones.
No utilices Markdown.
"""

        respuesta = analizar_imagen(
            [imagen],
            prompt
        )

        if not isinstance(respuesta, str):
            return campos_vacios

        respuesta = respuesta.strip()

        if respuesta.startswith("```"):
            respuesta = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                respuesta,
                flags=re.IGNORECASE
            ).strip()

        try:
            datos = json.loads(respuesta)
        except json.JSONDecodeError:
            return campos_vacios

        niss = re.sub(
            r"\D",
            "",
            str(datos.get("niss", ""))
        )

        if not 6 <= len(niss) <= 10:
            niss = ""

        reclamante = limpiar_respuesta_visual(
            datos.get("reclamante", "")
        )

        direccion_suministro = limpiar_respuesta_visual(
            datos.get("direccion_suministro", "")
        )

        direccion_procesal = limpiar_respuesta_visual(
            datos.get("direccion_procesal", "")
        )

        solicita_contraste = limpiar_respuesta_visual(
            datos.get("solicita_contraste", "")
        )

        if solicita_contraste not in ["SI", "NO"]:
            solicita_contraste = ""

        return {
            "niss": niss,
            "reclamante": reclamante,
            "direccion_suministro": direccion_suministro,
            "direccion_procesal": direccion_procesal,
            "solicita_contraste": solicita_contraste
        }

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
