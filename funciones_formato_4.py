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

def extraer_re_nombre_archivo(
    nombre_archivo
):

    return limpiar_re(
        nombre_archivo
    )

def obtener_re_formato_2(
    datos_formato_2
):

    campos_posibles = [
        "re",
        "numero_re",
        "numero_reclamo",
        "numero_reclamacion"
    ]

    for campo in campos_posibles:

        re_encontrado = limpiar_re(
            datos_formato_2.get(
                campo,
                ""
            )
        )

        if re_encontrado:
            return re_encontrado

    return ""

def consolidar_formato_2_y_4(
    datos_formato_2,
    datos_formato_4,
    nombre_archivo_formato_4=""
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        datos_formato_2 = {}

    if not isinstance(
        datos_formato_4,
        dict
    ):
        datos_formato_4 = {}

    # ==========================
    # VALIDACIÓN DEL RE
    # ==========================

    re_formato_2 = obtener_re_formato_2(
        datos_formato_2
    )

    re_formato_4_vision = limpiar_re(
        datos_formato_4.get(
            "re",
            ""
        )
    )

    re_archivo_formato_4 = (
        extraer_re_nombre_archivo(
            nombre_archivo_formato_4
        )
    )

    error_formato_4 = datos_formato_4.get(
        "error",
        ""
    )

    acta_corresponde_expediente = False

    if error_formato_4:

        validacion_re = (
            "ERROR_LECTURA_FORMATO_4"
        )

    elif not re_formato_2:

        validacion_re = (
            "SIN_RE_FORMATO_2"
        )

    elif re_archivo_formato_4:

        if (
            re_archivo_formato_4
            != re_formato_2
        ):

            validacion_re = (
                "ARCHIVO_NO_CORRESPONDE"
            )

        elif (
            re_formato_4_vision
            == re_formato_2
        ):

            validacion_re = "COINCIDE"
            acta_corresponde_expediente = True

        elif re_formato_4_vision:

            validacion_re = (
                "COINCIDE_ARCHIVO_"
                "DIFERENCIA_VISION"
            )

            acta_corresponde_expediente = True

        else:

            validacion_re = (
                "COINCIDE_ARCHIVO_"
                "SIN_RE_VISION"
            )

            acta_corresponde_expediente = True

    elif (
        re_formato_4_vision
        == re_formato_2
    ):

        validacion_re = (
            "COINCIDE_VISION"
        )

        acta_corresponde_expediente = True

    elif re_formato_4_vision:

        validacion_re = (
            "DIFERENCIA_RE_"
            "REQUIERE_REVISION"
        )

    else:

        validacion_re = (
            "SIN_RE_FORMATO_4"
        )

    # El RE definitivo siempre proviene
    # del Formato 2.
    re_final = re_formato_2

    # ==========================
    # VALIDACIÓN DE LA FECHA
    # ==========================

    fecha_formato_2 = limpiar_fecha(
        datos_formato_2.get(
            "fecha_audiencia",
            ""
        )
    )

    fecha_formato_4 = limpiar_fecha(
        datos_formato_4.get(
            "fecha_audiencia",
            ""
        )
    )

    if fecha_formato_2 and fecha_formato_4:

        if fecha_formato_2 == fecha_formato_4:

            validacion_fecha = "COINCIDE"

        else:

            validacion_fecha = "DIFERENCIA"

    elif fecha_formato_2:

        validacion_fecha = (
            "SIN_FECHA_FORMATO_4"
        )

    elif fecha_formato_4:

        validacion_fecha = (
            "SIN_FECHA_FORMATO_2"
        )

    else:

        validacion_fecha = (
            "SIN_FECHAS"
        )

    # La fecha principal continúa siendo
    # la programada en el Formato 2.
    fecha_audiencia_final = (
        fecha_formato_2
        or fecha_formato_4
    )

    # ==========================
    # DIRECCIÓN PROCESAL
    # ==========================

    direccion_formato_2 = limpiar_valor(
        datos_formato_2.get(
            "direccion_procesal",
            ""
        )
    )

    direccion_formato_4 = limpiar_valor(
        datos_formato_4.get(
            "direccion_procesal_acta",
            ""
        )
    )

    if (
        acta_corresponde_expediente
        and direccion_formato_4
    ):

        direccion_procesal_final = (
            direccion_formato_4
        )

        fuente_direccion_procesal = (
            "FORMATO_4"
        )

    else:

        direccion_procesal_final = (
            direccion_formato_2
        )

        if direccion_formato_2:

            fuente_direccion_procesal = (
                "FORMATO_2"
            )

        else:

            fuente_direccion_procesal = ""

    # ==========================
    # CORREO ELECTRÓNICO
    # ==========================

    correo_formato_2 = limpiar_valor(
        datos_formato_2.get(
            "correo_electronico",
            ""
        )
    )

    correo_formato_4 = limpiar_valor(
        datos_formato_4.get(
            "correo_electronico_acta",
            ""
        )
    )

    if (
        acta_corresponde_expediente
        and correo_formato_4
    ):

        correo_final = correo_formato_4
        fuente_correo = "FORMATO_4"

    else:

        correo_final = correo_formato_2

        if correo_formato_2:
            fuente_correo = "FORMATO_2"
        else:
            fuente_correo = ""

    # ==========================
    # CONTRASTACIÓN
    # ==========================

    contraste_formato_2 = normalizar_texto(
        datos_formato_2.get(
            "solicita_contraste",
            ""
        )
    )

    contraste_formato_4 = normalizar_texto(
        datos_formato_4.get(
            "solicita_contraste_acta",
            ""
        )
    )

    if contraste_formato_2 not in {
        "SI",
        "NO"
    }:
        contraste_formato_2 = ""

    if contraste_formato_4 not in {
        "SI",
        "NO"
    }:
        contraste_formato_4 = ""

    if (
        acta_corresponde_expediente
        and contraste_formato_4
    ):

        solicita_contraste_final = (
            contraste_formato_4
        )

        fuente_solicita_contraste = (
            "FORMATO_4"
        )

    else:

        solicita_contraste_final = (
            contraste_formato_2
        )

        if contraste_formato_2:

            fuente_solicita_contraste = (
                "FORMATO_2"
            )

        else:

            fuente_solicita_contraste = ""

    # ==========================
    # RESULTADO DE LA AUDIENCIA
    # ==========================

    if acta_corresponde_expediente:

        resultado_audiencia = limpiar_valor(
            datos_formato_4.get(
                "resultado_audiencia",
                ""
            )
        )

        continua_reclamo = normalizar_texto(
            datos_formato_4.get(
                "continua_reclamo",
                ""
            )
        )

    else:

        resultado_audiencia = ""
        continua_reclamo = ""

    # ==========================
    # ESTADO GENERAL
    # ==========================

    requiere_revision = (
        not acta_corresponde_expediente
        or validacion_fecha == "DIFERENCIA"
    )

    if not acta_corresponde_expediente:

        estado_validacion = (
            "ACTA_NO_VALIDADA"
        )

    elif validacion_fecha == "DIFERENCIA":

        estado_validacion = (
            "VALIDADO_CON_DIFERENCIA_FECHA"
        )

    else:

        estado_validacion = "VALIDADO"

    return {
        "estado_validacion": estado_validacion,
        "requiere_revision": requiere_revision,

        "re_formato_2": re_formato_2,
        "re_formato_4_vision": (
            re_formato_4_vision
        ),
        "re_archivo_formato_4": (
            re_archivo_formato_4
        ),
        "validacion_re": validacion_re,
        "re_final": re_final,

        "fecha_audiencia_formato_2": (
            fecha_formato_2
        ),
        "fecha_audiencia_formato_4": (
            fecha_formato_4
        ),
        "validacion_fecha_audiencia": (
            validacion_fecha
        ),
        "fecha_audiencia_final": (
            fecha_audiencia_final
        ),

        "direccion_procesal_formato_2": (
            direccion_formato_2
        ),
        "direccion_procesal_formato_4": (
            direccion_formato_4
        ),
        "direccion_procesal_final": (
            direccion_procesal_final
        ),
        "fuente_direccion_procesal": (
            fuente_direccion_procesal
        ),

        "correo_formato_2": correo_formato_2,
        "correo_formato_4": correo_formato_4,
        "correo_final": correo_final,
        "fuente_correo": fuente_correo,

        "solicita_contraste_formato_2": (
            contraste_formato_2
        ),
        "solicita_contraste_formato_4": (
            contraste_formato_4
        ),
        "solicita_contraste_final": (
            solicita_contraste_final
        ),
        "fuente_solicita_contraste": (
            fuente_solicita_contraste
        ),

        "resultado_audiencia": (
            resultado_audiencia
        ),
        "continua_reclamo": continua_reclamo
    }
