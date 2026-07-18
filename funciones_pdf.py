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

        ancho = pagina.rect.width
        alto = pagina.rect.height

        # Recorte superior: identificación y reclamante.
        recorte_superior = fitz.Rect(
            0,
            alto * 0.05,
            ancho,
            alto * 0.43
        )

        # Recorte inferior: casillas de contraste.
        recorte_inferior = fitz.Rect(
            0,
            alto * 0.71,
            ancho,
            alto * 0.79
        )

        pix_superior = pagina.get_pixmap(
            matrix=matriz,
            clip=recorte_superior,
            alpha=False
        )

        pix_inferior = pagina.get_pixmap(
            matrix=matriz,
            clip=recorte_inferior,
            alpha=False
        )

        imagen_superior = pix_superior.tobytes("png")
        imagen_inferior = pix_inferior.tobytes("png")

        prompt = """
Las dos imágenes pertenecen a la primera página de un Formato 2.

La primera imagen contiene la parte superior del formulario.
La segunda imagen contiene la parte inferior.

Lee directamente las celdas visibles. No inventes información y no
utilices el orden de una transcripción OCR.

Extrae los siguientes campos por separado:

1. niss:
   Lee únicamente los dígitos de la celda ubicada junto a
   "N° DE SUMINISTRO".

2. Datos del reclamante:
   Lee las tres columnas ubicadas bajo
   "NOMBRE DEL SOLICITANTE O REPRESENTANTE":

   - apellido_paterno
   - apellido_materno
   - nombres

   No unas las columnas.
   No omitas el apellido paterno.
   No incluyas etiquetas.

3. direccion_suministro:
   Lee por separado las celdas de "UBICACIÓN DEL PREDIO":

   - via
   - numero
   - manzana
   - lote
   - urbanizacion
   - provincia
   - distrito

4. direccion_procesal:
   Lee por separado las celdas de "DOMICILIO PROCESAL":

   - via
   - numero
   - manzana
   - lote
   - urbanizacion
   - provincia
   - distrito

   No incluyas teléfono, correo, código postal, declaraciones,
   casillas ni etiquetas.

5. solicita_contraste:
   Revisa exclusivamente la sección:

   "DECLARACIÓN DEL RECLAMANTE
   (aplicable a reclamos por consumo medido)
   Solicito la realización de la prueba de contrastación..."

   Devuelve:
   - "SI" si la X está junto a Sí.
   - "NO" si la X está junto a No.
   - "" si no puede determinarse.

   No confundas esta sección con la entrega de cartilla,
   la autorización de correo ni otra casilla.

Devuelve exclusivamente JSON válido con esta estructura:

{
  "niss": "",
  "apellido_paterno": "",
  "apellido_materno": "",
  "nombres": "",
  "direccion_suministro": {
    "via": "",
    "numero": "",
    "manzana": "",
    "lote": "",
    "urbanizacion": "",
    "provincia": "",
    "distrito": ""
  },
  "direccion_procesal": {
    "via": "",
    "numero": "",
    "manzana": "",
    "lote": "",
    "urbanizacion": "",
    "provincia": "",
    "distrito": ""
  },
  "solicita_contraste": ""
}

No agregues explicaciones.
No utilices Markdown.
"""

        respuesta = analizar_imagen(
            [
                imagen_superior,
                imagen_inferior
            ],
            prompt,
            modelo="gpt-4o"
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

        apellido_paterno = limpiar_respuesta_visual(
            datos.get("apellido_paterno", "")
        )

        apellido_materno = limpiar_respuesta_visual(
            datos.get("apellido_materno", "")
        )

        nombres = limpiar_respuesta_visual(
            datos.get("nombres", "")
        )

        reclamante = limpiar_respuesta_visual(
            " ".join(
                valor
                for valor in [
                    apellido_paterno,
                    apellido_materno,
                    nombres
                ]
                if valor
            )
        )

        def construir_direccion(nombre_campo):

            direccion = datos.get(
                nombre_campo,
                {}
            )

            if not isinstance(direccion, dict):
                return ""

            partes = [
                direccion.get("via", ""),
                direccion.get("numero", ""),
                direccion.get("manzana", ""),
                direccion.get("lote", ""),
                direccion.get("urbanizacion", ""),
                direccion.get("provincia", ""),
                direccion.get("distrito", "")
            ]

            partes_limpias = [
                limpiar_respuesta_visual(parte)
                for parte in partes
                if limpiar_respuesta_visual(parte)
            ]

            return " ".join(partes_limpias)

        direccion_suministro = construir_direccion(
            "direccion_suministro"
        )

        direccion_procesal = construir_direccion(
            "direccion_procesal"
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
