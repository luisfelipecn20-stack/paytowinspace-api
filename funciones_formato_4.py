import json
import re
import unicodedata

from funciones_pdf import convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from prompt_formato_4 import PROMPT_FORMATO_4


CAMPOS_TEXTO_ACTA = [
    "texto_propuesta_sedapal",
    "texto_propuesta_reclamante",
    "texto_puntos_acuerdo",
    "texto_puntos_desacuerdo",
    "texto_observaciones"
]


def limpiar_valor(valor):

    if valor is None:
        return ""

    return str(valor).strip()


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

        texto = "\n".join(
            lineas
        ).strip()

    inicio_json = texto.find("{")
    final_json = texto.rfind("}")

    if (
        inicio_json != -1
        and final_json != -1
        and final_json >= inicio_json
    ):

        texto = texto[
            inicio_json:final_json + 1
        ]

    return texto


def normalizar_texto(texto):

    texto = unicodedata.normalize(
        "NFD",
        limpiar_valor(texto)
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = texto.upper()

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


def limpiar_re(valor):

    coincidencia = re.search(
        r"\bRE\d+\b",
        limpiar_valor(valor),
        re.IGNORECASE
    )

    if coincidencia:
        return coincidencia.group(0).upper()

    return ""


def limpiar_fecha(valor):

    coincidencia = re.search(
        r"\b\d{2}/\d{2}/\d{4}\b",
        limpiar_valor(valor)
    )

    if coincidencia:
        return coincidencia.group(0)

    return ""


def obtener_texto_completo_acta(datos):

    textos = []

    for campo in CAMPOS_TEXTO_ACTA:

        valor = limpiar_valor(
            datos.get(
                campo,
                ""
            )
        )

        if valor:
            textos.append(
                valor
            )

    return " ".join(
        textos
    )


def contiene_ausencia(texto):

    texto = normalizar_texto(
        texto
    )

    patrones = [
        r"\bAUSENTE\b",
        r"\bAUSENCIA\b",
        r"\bINASISTENCIA\b",
        r"\bNO\s+ASISTIO\b",
        r"\bNO\s+SE\s+PRESENTO\b"
    ]

    return any(
        re.search(
            patron,
            texto
        )
        for patron in patrones
    )


def contiene_continuidad(texto):

    texto = normalizar_texto(
        texto
    )

    patrones = [
        r"\bCONTINUA\b",
        r"\bCONTINUAR\b",
        r"\bCONTINUANDO\b",
        r"\bSE\s+CONTINUA\b",
        r"\bSIGUE\s+SU\s+PROCESO\b",
        r"\bVIA\s+ADMINISTRATIVA\b",
        r"\bPROCESO\s+DEL\s+RECLAMO\b",
        r"\bPROCESO\s+DE\s+RECLAMO\b"
    ]

    return any(
        re.search(
            patron,
            texto
        )
        for patron in patrones
    )


def contiene_acuerdo(texto):

    texto = normalizar_texto(
        texto
    )

    patrones = [
        r"\bSE\s+LLEGO\s+A\s+UN\s+ACUERDO\b",
        r"\bLLEGARON\s+A\s+UN\s+ACUERDO\b",
        r"\bACUERDO\s+TOTAL\b",
        r"\bACEPTA\s+LA\s+PROPUESTA\b",
        r"\bACEPTO\s+LA\s+PROPUESTA\b"
    ]

    return any(
        re.search(
            patron,
            texto
        )
        for patron in patrones
    )


def detectar_solicitud_contraste(texto):

    texto = normalizar_texto(
        texto
    )

    patrones_negativos = [
        (
            r"\bNO\s+"
            r"(?:SOLICITA|SOLICITO|DESEA|REQUIERE)"
            r".{0,80}"
            r"(?:VERIFICACION|CONTRASTACION)"
        ),
        (
            r"\bNO\s+DESEA\s+REALIZAR"
            r".{0,80}"
            r"(?:VERIFICACION|CONTRASTACION)"
        )
    ]

    if any(
        re.search(
            patron,
            texto
        )
        for patron in patrones_negativos
    ):
        return "NO"

    patrones_positivos = [
        (
            r"\b"
            r"(?:SOLICITA|SOLICITO|DESEA|REQUIERE)"
            r".{0,80}"
            r"(?:VERIFICACION|CONTRASTACION)"
        ),
        (
            r"\b"
            r"(?:VERIFICACION|CONTRASTACION)"
            r".{0,80}"
            r"(?:SOLICITADA|SOLICITADO)"
        ),
        (
            r"\bSOLICITUD\s+DE\s+"
            r"(?:LA\s+)?"
            r"(?:VERIFICACION|CONTRASTACION)"
        )
    ]

    if any(
        re.search(
            patron,
            texto
        )
        for patron in patrones_positivos
    ):
        return "SI"

    return ""


def extraer_correo_desde_texto(texto):

    coincidencia = re.search(
        (
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}"
        ),
        limpiar_valor(texto)
    )

    if coincidencia:
        return coincidencia.group(0)

    return ""


def clasificar_resultado_audiencia(
    texto,
    subsiste_reclamo
):

    texto_normalizado = normalizar_texto(
        texto
    )

    # Si no se pudo leer información,
    # no se debe inventar un resultado.
    if (
        not texto_normalizado
        and subsiste_reclamo not in {
            "SI",
            "NO"
        }
    ):
        return ""

    # La ausencia se identifica por palabras
    # dentro de los recuadros del acta.
    if contiene_ausencia(texto):
        return "AUSENTE"

    if (
        subsiste_reclamo == "NO"
        or "DESISTIMIENTO" in texto_normalizado
        or "DESISTE" in texto_normalizado
    ):
        return "DESISTIMIENTO"

    if contiene_acuerdo(texto):
        return "ACUERDO"

    # Si no se indica ausencia, acuerdo ni
    # desistimiento, se entiende que el
    # reclamo continúa sin acuerdo.
    return "SIN_ACUERDO"


def determinar_continuidad(
    resultado_audiencia,
    subsiste_reclamo,
    solicita_contraste_acta,
    texto
):

    if resultado_audiencia in {
        "ACUERDO",
        "DESISTIMIENTO"
    }:
        return "NO"

    if subsiste_reclamo == "NO":
        return "NO"

    if resultado_audiencia in {
        "AUSENTE",
        "SIN_ACUERDO"
    }:
        return "SI"

    if solicita_contraste_acta == "SI":
        return "SI"

    if subsiste_reclamo == "SI":
        return "SI"

    if contiene_continuidad(texto):
        return "SI"

    return ""


def obtener_datos_formato_4(pdf):

    imagenes = convertir_pdf_a_imagenes(
        pdf
    )

    if not imagenes:

        return {
            "error": "NO_SE_PUDO_CONVERTIR_PDF"
        }

    respuesta_gpt = analizar_imagen(
        imagenes[:1],
        PROMPT_FORMATO_4
    )

    try:

        texto_json = limpiar_bloque_json(
            respuesta_gpt
        )

        datos = json.loads(
            texto_json
        )

    except (
        json.JSONDecodeError,
        TypeError,
        AttributeError
    ):

        return {
            "error": "JSON_INVALIDO",
            "respuesta_gpt": respuesta_gpt
        }

    subsiste_reclamo = normalizar_texto(
        datos.get(
            "subsiste_reclamo",
            ""
        )
    )

    if subsiste_reclamo not in {
        "SI",
        "NO"
    }:
        subsiste_reclamo = ""

    resultado = {
        "re": limpiar_re(
            datos.get(
                "re",
                ""
            )
        ),
        "fecha_audiencia": limpiar_fecha(
            datos.get(
                "fecha_audiencia",
                ""
            )
        ),
        "texto_propuesta_sedapal": limpiar_valor(
            datos.get(
                "texto_propuesta_sedapal",
                ""
            )
        ),
        "texto_propuesta_reclamante": limpiar_valor(
            datos.get(
                "texto_propuesta_reclamante",
                ""
            )
        ),
        "texto_puntos_acuerdo": limpiar_valor(
            datos.get(
                "texto_puntos_acuerdo",
                ""
            )
        ),
        "texto_puntos_desacuerdo": limpiar_valor(
            datos.get(
                "texto_puntos_desacuerdo",
                ""
            )
        ),
        "texto_observaciones": limpiar_valor(
            datos.get(
                "texto_observaciones",
                ""
            )
        ),
        "direccion_procesal_acta": limpiar_valor(
            datos.get(
                "direccion_procesal_acta",
                ""
            )
        ),
        "correo_electronico_acta": limpiar_valor(
            datos.get(
                "correo_electronico_acta",
                ""
            )
        ),
        "subsiste_reclamo": subsiste_reclamo
    }

    texto_acta = obtener_texto_completo_acta(
        resultado
    )

    solicita_contraste_acta = (
        detectar_solicitud_contraste(
            texto_acta
        )
    )

    resultado_audiencia = (
        clasificar_resultado_audiencia(
            texto_acta,
            resultado["subsiste_reclamo"]
        )
    )

    continua_reclamo = determinar_continuidad(
        resultado_audiencia,
        resultado["subsiste_reclamo"],
        solicita_contraste_acta,
        texto_acta
    )

    if not resultado["correo_electronico_acta"]:

        resultado["correo_electronico_acta"] = (
            extraer_correo_desde_texto(
                texto_acta
            )
        )

    resultado.update(
        {
            "resultado_audiencia": (
                resultado_audiencia
            ),
            "continua_reclamo": (
                continua_reclamo
            ),
            "solicita_contraste_acta": (
                solicita_contraste_acta
            ),
            "fuente": "VISION",
            "respuesta_gpt": respuesta_gpt
        }
    )

    return resultado
