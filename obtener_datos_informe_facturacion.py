import json
import re

from funciones_pdf import (
    convertir_pdf_a_imagenes,
    extraer_texto_pdf
)
from funciones_vision import analizar_imagen
from prompt_informe_facturacion import (
    PROMPT_INFORME_FACTURACION
)


def limpiar_bloque_json(respuesta):

    if not isinstance(respuesta, str):
        return ""

    texto = respuesta.strip()

    if texto.startswith("```"):

        lineas = texto.splitlines()

        if lineas and lineas[0].startswith("```"):
            lineas = lineas[1:]

        if lineas and lineas[-1].strip() == "```":
            lineas = lineas[:-1]

        texto = "\n".join(lineas).strip()

    return texto


def normalizar_regimen_facturacion(regimen):

    resultado = []

    if not isinstance(regimen, list):
        return resultado

    for fila in regimen:

        if not isinstance(fila, dict):
            continue

        mes = str(
            fila.get("mes", "")
        ).strip()

        m3 = fila.get(
            "m3_facturado",
            ""
        )

        if m3 is None:
            m3 = ""
        else:
            m3 = str(m3).strip()

        if mes:
            resultado.append(
                {
                    "mes": mes,
                    "m3_facturado": m3
                }
            )

    return resultado


def extraer_regimen_desde_texto(texto):

    if not isinstance(texto, str):
        return []

    inicio = re.search(
        (
            r"II\.\s*"
            r"R[ÉE]GIMEN\s+DE\s+"
            r"FACTURACI[ÓO]N\s+APLICADO"
        ),
        texto,
        re.IGNORECASE
    )

    if not inicio:
        return []

    seccion = texto[
        inicio.end():
    ]

    fin = re.search(
        r"III\.",
        seccion,
        re.IGNORECASE
    )

    if fin:
        seccion = seccion[
            :fin.start()
        ]

    seccion = re.sub(
        r"\s+",
        " ",
        seccion
    ).strip()

    patron_fila = re.compile(
        (
            r"\b"
            r"([A-Za-zÁÉÍÓÚÑáéíóúñ]{3,12}"
            r"-\d{2,4})"
            r"\s+"
            r"([A-Za-z0-9./-]+)"
            r"\s+"
            r"(\d{2}/\d{2}/\d{4})"
            r"\s+"
            r"(\d+(?:[.,]\d+)?)"
            r"\s+"
            r"(\d+(?:[.,]\d+)?)"
            r"\b"
        ),
        re.IGNORECASE
    )

    regimen = []

    for coincidencia in patron_fila.finditer(
        seccion
    ):

        mes = coincidencia.group(1)

        # Grupo 4: Lectura acumulada.
        # Grupo 5: M3 facturado.
        m3_facturado = coincidencia.group(5)

        regimen.append(
            {
                "mes": mes,
                "m3_facturado": m3_facturado
            }
        )

    return regimen


def extraer_regimen_con_vision(pdf):

    imagenes = convertir_pdf_a_imagenes(
        pdf
    )

    respuesta = analizar_imagen(
        imagenes,
        PROMPT_INFORME_FACTURACION
    )

    try:

        texto_json = limpiar_bloque_json(
            respuesta
        )

        datos = json.loads(
            texto_json
        )

        regimen = normalizar_regimen_facturacion(
            datos.get(
                "regimen_facturacion",
                []
            )
        )

    except (
        json.JSONDecodeError,
        TypeError,
        AttributeError
    ):

        regimen = []

    return regimen, respuesta


def obtener_datos_informe_facturacion(pdf):

    # Primer intento:
    # extracción directa del texto digital.
    texto_pdf = extraer_texto_pdf(
        pdf
    )

    regimen = extraer_regimen_desde_texto(
        texto_pdf
    )

    if regimen:

        return {
            "regimen_facturacion": regimen,
            "fuente": "PDF_TEXTO",
            "respuesta_gpt": ""
        }

    # Segundo intento:
    # Vision únicamente para informes escaneados.
    regimen, respuesta_gpt = (
        extraer_regimen_con_vision(pdf)
    )

    if regimen:
        fuente = "VISION"
    else:
        fuente = "NO_ENCONTRADO"

    return {
        "regimen_facturacion": regimen,
        "fuente": fuente,
        "respuesta_gpt": respuesta_gpt
    }
