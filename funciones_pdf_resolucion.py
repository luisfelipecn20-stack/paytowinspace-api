from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_JUSTIFY,
    TA_LEFT
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


ANCHO_PAGINA, ALTO_PAGINA = A4

MARGEN_IZQUIERDO = 28.2 * mm
ANCHO_CONTENIDO = 154.8 * mm


def preparar_texto(valor):

    texto = escape(
        str(valor or "")
    )

    return texto.replace(
        "\n",
        "<br/>"
    )


def dibujar_primera_pagina(
    lienzo,
    documento
):

    ruta_base = Path(
        __file__
    ).resolve().parent

    ruta_logo = (
        ruta_base
        / "logo_sedapal.png"
    )

    ruta_pie = (
        ruta_base
        / "pie_institucional.png"
    )

    lienzo.saveState()

    lienzo.drawImage(
        str(ruta_logo),
        30 * mm,
        264.7 * mm,
        width=38.6 * mm,
        height=15.5 * mm,
        preserveAspectRatio=True,
        mask="auto"
    )

    lienzo.setFont(
        "Helvetica",
        8
    )

    lienzo.drawString(
        30 * mm,
        260.7 * mm,
        "Servicio de Agua Potable y Alcantarillado de Lima"
    )

    lienzo.drawImage(
        str(ruta_pie),
        MARGEN_IZQUIERDO,
        7 * mm,
        width=ANCHO_CONTENIDO,
        height=20.1 * mm,
        preserveAspectRatio=True,
        mask="auto"
    )

    lienzo.restoreState()


def crear_estilos():

    cuerpo = ParagraphStyle(
        "CuerpoResolucion",
        fontName="Helvetica",
        fontSize=9.7,
        leading=11.6,
        alignment=TA_JUSTIFY,
        textColor=colors.black,
        spaceAfter=0
    )

    return {
        "cuerpo": cuerpo,
        "titulo": ParagraphStyle(
            "TituloResolucion",
            parent=cuerpo,
            alignment=TA_CENTER,
            fontSize=10,
            leading=11.5
        ),
        "fecha": ParagraphStyle(
            "FechaResolucion",
            parent=cuerpo,
            alignment=TA_CENTER,
            fontSize=10,
            leading=11.5
        ),
        "seccion": ParagraphStyle(
            "SeccionResolucion",
            parent=cuerpo,
            alignment=TA_LEFT,
            fontSize=9.7,
            leading=11.6
        ),
        "datos": ParagraphStyle(
            "DatosResolucion",
            parent=cuerpo,
            alignment=TA_LEFT,
            fontSize=9.7,
            leading=11.4
        ),
        "numero": ParagraphStyle(
            "NumeroConsiderando",
            parent=cuerpo,
            alignment=TA_LEFT,
            fontSize=9.7,
            leading=11.6
        ),
        "centrado": ParagraphStyle(
            "CentradoResolucion",
            parent=cuerpo,
            alignment=TA_CENTER,
            fontSize=9.7,
            leading=11.6
        ),
        "codigo": ParagraphStyle(
            "CodigoResolucion",
            parent=cuerpo,
            alignment=TA_LEFT,
            fontSize=8,
            leading=9
        )
    }


def crear_tabla_datos(
    datos_expediente,
    estilos
):

    filas = [
        (
            "Suministro",
            datos_expediente.get(
                "niss",
                ""
            )
        ),
        (
            "Reclamante",
            datos_expediente.get(
                "reclamante",
                ""
            )
        ),
        (
            "Reclamo",
            datos_expediente.get(
                "re",
                ""
            )
        ),
        (
            "Dirección del suministro",
            datos_expediente.get(
                "direccion_suministro",
                ""
            )
        ),
        (
            "Dirección Procesal",
            datos_expediente.get(
                "direccion_procesal",
                ""
            )
        )
    ]

    contenido = []

    correo_electronico = str(
        datos_expediente.get(
            "correo_electronico",
            ""
        )
    ).strip()

    if correo_electronico:

        filas.append(
            (
                "Correo electrónico",
                correo_electronico
            )
        )

    for etiqueta, valor in filas:

        contenido.append(
            [
                Paragraph(
                    preparar_texto(
                        etiqueta
                    ),
                    estilos["datos"]
                ),
                Paragraph(
                    ":",
                    estilos["datos"]
                ),
                Paragraph(
                    preparar_texto(
                        valor
                    ),
                    estilos["datos"]
                )
            ]
        )

    tabla = Table(
        contenido,
        colWidths=[
            49.3 * mm,
            4 * mm,
            101.5 * mm
        ],
        hAlign="LEFT"
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0.7
                )
            ]
        )
    )

    return tabla


def crear_considerando(
    numero,
    texto,
    estilos
):

    tabla = Table(
        [
            [
                Paragraph(
                    f"{numero}.",
                    estilos["numero"]
                ),
                Paragraph(
                    preparar_texto(
                        texto
                    ),
                    estilos["cuerpo"]
                )
            ]
        ],
        colWidths=[
            6.5 * mm,
            148.3 * mm
        ],
        hAlign="LEFT",
        splitByRow=1
    )

    tabla.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0
                )
            ]
        )
    )

    return tabla


def preparar_articulo_2(texto):

    texto_seguro = preparar_texto(
        texto
    )

    return texto_seguro.replace(
        "www.sedapal.com.pe",
        (
            '<u><font color="#0000FF">'
            "www.sedapal.com.pe"
            "</font></u>"
        )
    )


def generar_pdf_resolucion(
    datos_resolucion
):

    if not isinstance(
        datos_resolucion,
        dict
    ):
        raise ValueError(
            "Los datos de la resolución no son válidos."
        )

    if datos_resolucion.get(
        "estado"
    ) != "GENERADO":
        raise ValueError(
            "La resolución todavía no está validada."
        )

    ruta_base = Path(
        __file__
    ).resolve().parent

    for nombre_recurso in (
        "logo_sedapal.png",
        "pie_institucional.png"
    ):

        if not (
            ruta_base
            / nombre_recurso
        ).exists():

            raise FileNotFoundError(
                f"No se encontró {nombre_recurso}."
            )

    memoria_pdf = BytesIO()

    documento = BaseDocTemplate(
        memoria_pdf,
        pagesize=A4,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=(
            datos_resolucion.get(
                "encabezado",
                {}
            ).get(
                "linea_resolucion",
                "Resolución"
            )
        ),
        author="SEDAPAL"
    )

    marco_primera = Frame(
        MARGEN_IZQUIERDO,
        29.5 * mm,
        ANCHO_CONTENIDO,
        224.8 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="marco_primera"
    )

    marco_segunda = Frame(
        MARGEN_IZQUIERDO,
        29.5 * mm,
        ANCHO_CONTENIDO,
        224.8 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="marco_segunda"
    )

    plantilla_primera = PageTemplate(
        id="PrimeraPagina",
        frames=[marco_primera],
        onPage=dibujar_primera_pagina,
        autoNextPageTemplate=(
            "SegundaPagina"
        )
    )

    plantilla_segunda = PageTemplate(
        id="SegundaPagina",
        frames=[marco_segunda],
        onPage=dibujar_primera_pagina
    )

    documento.addPageTemplates(
        [
            plantilla_primera,
            plantilla_segunda
        ]
    )

    estilos = crear_estilos()

    encabezado = datos_resolucion.get(
        "encabezado",
        {}
    )

    datos_expediente = datos_resolucion.get(
        "datos_expediente",
        {}
    )

    historia = []

    historia.append(
        Paragraph(
            (
                "<u>"
                + preparar_texto(
                    encabezado.get(
                        "linea_resolucion",
                        ""
                    )
                )
                + "</u>"
            ),
            estilos["titulo"]
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                encabezado.get(
                    "linea_fecha",
                    ""
                )
            ),
            estilos["fecha"]
        )
    )

    historia.append(
        Spacer(
            1,
            3 * mm
        )
    )

    historia.append(
        crear_tabla_datos(
            datos_expediente,
            estilos
        )
    )

    historia.append(
        Spacer(
            1,
            3 * mm
        )
    )

    historia.append(
        Paragraph(
            "Visto",
            estilos["seccion"]
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_resolucion.get(
                    "visto",
                    ""
                )
            ),
            estilos["cuerpo"]
        )
    )

    historia.append(
        Spacer(
            1,
            3 * mm
        )
    )

    historia.append(
        Paragraph(
            "Considerando",
            estilos["seccion"]
        )
    )

    for numero in range(
        1,
        7
    ):

        historia.append(
            crear_considerando(
                numero,
                datos_resolucion.get(
                    f"considerando_{numero}",
                    ""
                ),
                estilos
            )
        )

        if numero < 6:

            historia.append(
                Spacer(
                    1,
                    4.1 * mm
                )
            )

    historia.append(
        Spacer(
            1,
            6.4 * mm
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_resolucion.get(
                    "parrafo_base_legal",
                    ""
                )
            ),
            estilos["cuerpo"]
        )
    )

    historia.append(
        Spacer(
            1,
            7.2 * mm
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_resolucion.get(
                    "se_resuelve",
                    ""
                )
            ),
            estilos["seccion"]
        )
    )

    historia.append(
        Spacer(
            1,
            2 * mm
        )
    )

    historia.append(
        KeepTogether(
            [
                Paragraph(
                    preparar_texto(
                        datos_resolucion.get(
                            "articulo_1",
                            ""
                        )
                    ),
                    estilos["cuerpo"]
                )
            ]
        )
    )

    historia.append(
        PageBreak()
    )

    historia.append(
        Paragraph(
            preparar_articulo_2(
                datos_resolucion.get(
                    "articulo_2",
                    ""
                )
            ),
            estilos["cuerpo"]
        )
    )

    historia.append(
        Spacer(
            1,
            4 * mm
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_resolucion.get(
                    "cierre",
                    ""
                )
            ),
            estilos["centrado"]
        )
    )

    historia.append(
        Spacer(
            1,
            17 * mm
        )
    )

    datos_firma = datos_resolucion.get(
        "firma_resolucion",
        {}
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_firma.get(
                    "nombre_jefe",
                    ""
                )
            ),
            estilos["centrado"]
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_firma.get(
                    "cargo_jefe",
                    ""
                )
            ),
            estilos["centrado"]
        )
    )

    historia.append(
        Spacer(
            1,
            14 * mm
        )
    )

    historia.append(
        Paragraph(
            preparar_texto(
                datos_firma.get(
                    "codigo_elaborador",
                    ""
                )
            ),
            estilos["codigo"]
        )
    )

    documento.build(
        historia
    )

    memoria_pdf.seek(0)

    return memoria_pdf.getvalue()
