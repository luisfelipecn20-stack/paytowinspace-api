def generar_considerando_6(
    datos_formato_2
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return ""

    meses_reclamados = datos_formato_2.get(
        "meses_reclamados",
        []
    )

    if not isinstance(
        meses_reclamados,
        list
    ):
        return ""

    meses_validos = [
        str(mes).strip()
        for mes in meses_reclamados
        if str(mes).strip()
    ]

    if not meses_validos:
        return ""

    if len(meses_validos) == 1:

        periodo_cuestionado = (
            "el mes cuestionado"
        )

    else:

        periodo_cuestionado = (
            "los meses cuestionados"
        )

    return (
        "Habiéndose acreditado la existencia de "
        "condiciones técnicas operacionales adecuadas "
        "para la facturación por diferencia de lecturas, "
        "la secuencia correcta de registros del medidor, "
        "y al no detectarse defectos imputables a "
        "Sedapal, se concluye que el reclamo presentado "
        f"por {periodo_cuestionado} deviene en infundado."
    )
