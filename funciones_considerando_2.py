import re
import unicodedata


NOMBRES_FEMENINOS = {
    "MARIA",
    "ROSA",
    "ANA",
    "LUZ",
    "CARMEN",
    "ELENA",
    "TERESA",
    "NORMA",
    "PATRICIA",
    "GLORIA",
    "HERLINDA",
    "CONSUELO",
    "JULIA",
    "JUANA",
    "MERCEDES",
    "SANDRA",
    "CLAUDIA",
    "MARGARITA",
    "LUCIA",
    "SOFIA",
    "ELIZABETH",
    "ELSA",
    "NANCY",
    "YOLANDA",
    "VILMA",
    "CECILIA",
    "BEATRIZ",
    "DIANA",
    "MILAGROS",
    "FIORELLA",
    "KARLA",
    "VERONICA",
    "MARIELA",
    "ROCIO",
    "ALEJANDRA",
    "ANDREA",
    "PAOLA"
}


NOMBRES_MASCULINOS = {
    "JOSE",
    "JUAN",
    "LUIS",
    "CARLOS",
    "MIGUEL",
    "JORGE",
    "PEDRO",
    "MANUEL",
    "JESUS",
    "SABINO",
    "RICARDO",
    "FERNANDO",
    "EDUARDO",
    "VICTOR",
    "OSCAR",
    "CESAR",
    "JULIO",
    "MARIO",
    "ROBERTO",
    "ALBERTO",
    "ANGEL",
    "DIEGO",
    "RENATO",
    "RAUL",
    "FELIPE",
    "MARCO",
    "MARCOS",
    "FRANCISCO",
    "ANTONIO",
    "DAVID",
    "DANIEL",
    "ALEJANDRO",
    "JHON",
    "JOHN"
}


def normalizar_texto(texto):

    texto = unicodedata.normalize(
        "NFD",
        str(texto)
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return re.sub(
        r"[^A-ZÑ ]",
        " ",
        texto.upper()
    )


def obtener_referencia_reclamante(
    reclamante,
    genero_reclamante=""
):

    genero = normalizar_texto(
        genero_reclamante
    ).strip()

    if genero in {
        "F",
        "FEMENINO",
        "MUJER"
    }:
        return "a la reclamante"

    if genero in {
        "M",
        "MASCULINO",
        "HOMBRE"
    }:
        return "al reclamante"

    nombre_normalizado = normalizar_texto(
        reclamante
    )

    palabras = nombre_normalizado.split()

    # Los nombres aparecen al final porque
    # el Formato 2 entrega primero los apellidos.
    posibles_nombres = palabras[-2:]

    es_femenino = any(
        nombre in NOMBRES_FEMENINOS
        for nombre in posibles_nombres
    )

    es_masculino = any(
        nombre in NOMBRES_MASCULINOS
        for nombre in posibles_nombres
    )

    if es_femenino and not es_masculino:
        return "a la reclamante"

    if es_masculino and not es_femenino:
        return "al reclamante"

    return "a la persona reclamante"


def generar_considerando_2(
    datos_formato_2
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return ""

    canal = normalizar_texto(
        datos_formato_2.get(
            "canal_atencion",
            ""
        )
    ).strip()

    solicita_contraste = normalizar_texto(
        datos_formato_2.get(
            "solicita_contraste",
            ""
        )
    ).strip()

    reclamante = datos_formato_2.get(
        "reclamante",
        ""
    )

    genero_reclamante = datos_formato_2.get(
        "genero_reclamante",
        ""
    )

    if solicita_contraste not in {
        "SI",
        "NO"
    }:
        return ""

    referencia = obtener_referencia_reclamante(
        reclamante,
        genero_reclamante
    )

    if canal == "PRESENCIAL":

        if solicita_contraste == "SI":
            decision = "manifestó aceptar dicha prueba"
        else:
            decision = "manifestó no aceptar dicha prueba"

        return (
            "Al momento de la presentación del reclamo, "
            f"se ha informado {referencia} acerca de su "
            "derecho a solicitar la verificación posterior "
            "en laboratorio del medidor, respecto al cual "
            f"{decision}."
        )

    if canal in {
        "TELEFONICO",
        "TELEFÓNICO"
    }:

        if solicita_contraste == "SI":
            solicitud = "ha sido solicitada"
        else:
            solicitud = "no ha sido solicitada"

        return (
            f"Mediante Carta se ha notificado {referencia} "
            "sobre su derecho de solicitar verificación "
            "posterior en laboratorio del medidor, la misma "
            f"que a la fecha {solicitud}."
        )

    if canal in {
        "WEB",
        "VIRTUAL"
    }:

        if solicita_contraste == "SI":
            solicitud = "ha sido solicitada"
        else:
            solicitud = "no ha sido solicitada"

        return (
            f"Mediante correo electrónico se ha notificado "
            f"{referencia} sobre su derecho de solicitar "
            "verificación posterior en laboratorio del "
            "medidor, la misma que a la fecha "
            f"{solicitud}."
        )

    return ""
