# ==========================
# CONFIGURACIÓN DEL VISTO
# ==========================

CANALES_VISTO = {
    "PRESENCIAL": "mediante Formato 2",
    "VIRTUAL": "vía web",
    "TELEFÓNICO": "vía telefónica",
    "TELEFONICO": "vía telefónica"
}


# Por ahora PEIAD generará resoluciones
# para Consumo Medido.
# Posteriormente agregaremos las plantillas
# correspondientes a las demás tipologías.
PLANTILLAS_VISTO = {
    "CR125": (
        "por {tipo_reclamo} facturado en {periodos}"
    ),
    "CR132": (
        "por {tipo_reclamo} facturado en {periodos}"
    )
}


# ==========================
# FORMATO DE LOS PERIODOS
# ==========================

def separar_periodo(periodo):

    partes = periodo.strip().split()

    if len(partes) < 2:
        return "", ""

    mes = " ".join(
        partes[:-1]
    ).lower()

    anio = partes[-1]

    return mes, anio


def unir_elementos(elementos):

    if not elementos:
        return ""

    if len(elementos) == 1:
        return elementos[0]

    if len(elementos) == 2:
        return (
            f"{elementos[0]} "
            f"y {elementos[1]}"
        )

    return (
        ", ".join(elementos[:-1])
        + f" y {elementos[-1]}"
    )


def formatear_periodos(meses_reclamados):

    if not meses_reclamados:
        return ""

    periodos = [
        separar_periodo(periodo)
        for periodo in meses_reclamados
    ]

    periodos = [
        (mes, anio)
        for mes, anio in periodos
        if mes and anio
    ]

    if not periodos:
        return ""

    # Un solo mes
    if len(periodos) == 1:

        mes, anio = periodos[0]

        return (
            f"el mes de {mes} "
            f"de {anio}"
        )

    anios = {
        anio
        for _, anio in periodos
    }

    # Varios meses del mismo año
    if len(anios) == 1:

        anio = periodos[0][1]

        meses = [
            mes
            for mes, _ in periodos
        ]

        return (
            f"los meses de "
            f"{unir_elementos(meses)} "
            f"de {anio}"
        )

    # Meses pertenecientes a años diferentes
    periodos_completos = [
        f"{mes} de {anio}"
        for mes, anio in periodos
    ]

    return (
        "los meses de "
        + unir_elementos(
            periodos_completos
        )
    )


# ==========================
# GENERADOR DEL VISTO
# ==========================

def generar_visto(datos):

    canal = datos.get(
        "canal_atencion",
        ""
    ).upper()

    fecha_reclamo = datos.get(
        "fecha_reclamo",
        ""
    )

    codigo_tipo_reclamo = datos.get(
        "codigo_tipo_reclamo",
        ""
    )

    tipo_reclamo = datos.get(
        "tipo_reclamo",
        ""
    )

    meses_reclamados = datos.get(
        "meses_reclamados",
        []
    )

    frase_canal = CANALES_VISTO.get(
        canal,
        ""
    )

    periodos = formatear_periodos(
        meses_reclamados
    )

    plantilla = PLANTILLAS_VISTO.get(
        codigo_tipo_reclamo
    )

    if (
        not frase_canal
        or not fecha_reclamo
        or not tipo_reclamo
        or not periodos
        or not plantilla
    ):
        return ""

    detalle_reclamo = plantilla.format(
        tipo_reclamo=tipo_reclamo,
        periodos=periodos
    )

    return (
        f"El reclamo interpuesto "
        f"{frase_canal} "
        f"de fecha {fecha_reclamo}, "
        f"{detalle_reclamo}."
    )
