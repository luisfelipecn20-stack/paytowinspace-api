from funciones_considerando_2 import (
    obtener_referencia_reclamante
)


def obtener_referencia_ausencia(
    datos_formato_2
):

    reclamante = datos_formato_2.get(
        "reclamante",
        ""
    )

    genero_reclamante = datos_formato_2.get(
        "genero_reclamante",
        ""
    )

    referencia = obtener_referencia_reclamante(
        reclamante,
        genero_reclamante
    )

    equivalencias = {
        "a la reclamante": "de la reclamante",
        "al reclamante": "del reclamante",
        "a la persona reclamante": (
            "de la persona reclamante"
        )
    }

    return equivalencias.get(
        referencia,
        "de la persona reclamante"
    )


def generar_considerando_5(
    datos_formato_2,
    validacion_formato_4
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return ""

    if not isinstance(
        validacion_formato_4,
        dict
    ):
        return ""

    if validacion_formato_4.get(
        "estado_validacion"
    ) != "VALIDADO":
        return ""

    if validacion_formato_4.get(
        "requiere_revision"
    ):
        return ""

    if not validacion_formato_4.get(
        "caso_soportado_v1"
    ):
        return ""

    resultado_audiencia = str(
        validacion_formato_4.get(
            "resultado_audiencia",
            ""
        )
    ).strip().upper()

    continua_reclamo = str(
        validacion_formato_4.get(
            "continua_reclamo",
            ""
        )
    ).strip().upper()

    fecha_audiencia = str(
        validacion_formato_4.get(
            "fecha_audiencia_final",
            ""
        )
    ).strip()

    if (
        not fecha_audiencia
        or continua_reclamo != "SI"
    ):
        return ""

    if resultado_audiencia == "AUSENTE":

        referencia = obtener_referencia_ausencia(
            datos_formato_2
        )

        return (
            f"Con fecha {fecha_audiencia} no se ha "
            "realizado la reunión de conciliación en la "
            f"hora programada, por ausencia {referencia}, "
            "continuando con el proceso de reclamo en la "
            "vía administrativa."
        )

    if resultado_audiencia == "SIN_ACUERDO":

        return (
            f"Con fecha {fecha_audiencia} se ha realizado "
            "la reunión de conciliación en la hora "
            "programada, no habiéndose llegado a ninguna "
            "fórmula de solución al reclamo, continuando "
            "con el proceso de reclamo en la vía "
            "administrativa."
        )

    return ""
