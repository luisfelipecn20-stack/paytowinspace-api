from funciones_visto import formatear_periodos


PARRAFO_BASE_LEGAL = (
    "Estando en las consideraciones expuestas y de "
    "conformidad con el Reglamento de Reclamos "
    "Comerciales de Usuarios de Servicios de "
    "Saneamiento aprobado por la Resolución de Consejo "
    "Directivo 066-2006-SUNASS-CD, modificado por la "
    "Resolución de Consejo Directivo "
    "088-2007-SUNASS-CD, y de conformidad a lo "
    "dispuesto en la Resolución de Gerencia General "
    "750-2005-GG. del 13.12.2005."
)


ARTICULO_2 = (
    "Art. 2° Comunicar al usuario que de estimarlo "
    "pertinente le asisten recursos administrativos que "
    "podrá interponer, opcionalmente de manera virtual "
    "ingresando a www.sedapal.com.pe dentro del plazo "
    "de quince (15) días útiles desde la recepción de "
    "la presente resolución, siendo estos: (i) El "
    "Recurso de Reconsideración (Formato N°08), que "
    "debe ser sustentado necesariamente en nueva prueba "
    "instrumental y será resuelto por la misma autoridad "
    "que emitió la resolución a impugnar o (ii) el "
    "Recurso de Apelación (Formato N° 09), que se "
    "sustenta en cuestiones de puro derecho o diferente "
    "interpretación de las pruebas actuadas y será "
    "resuelto por el Tribunal Administrativo de "
    "Solución de Reclamos de la Superintendencia "
    "Nacional de Servicio de Saneamiento."
)


def obtener_parrafo_base_legal():

    return PARRAFO_BASE_LEGAL


def generar_articulo_1(
    datos_formato_2
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return ""

    tipo_reclamo = str(
        datos_formato_2.get(
            "tipo_reclamo",
            ""
        )
    ).strip().upper()

    if tipo_reclamo != "CONSUMO MEDIDO":
        return ""

    meses_reclamados = datos_formato_2.get(
        "meses_reclamados",
        []
    )

    periodos = formatear_periodos(
        meses_reclamados
    )

    if not periodos:
        return ""

    return (
        "Art. 1° Declarar Infundado el reclamo, "
        "respecto al Consumo Medido facturado en "
        f"{periodos}, en base a las consideraciones "
        "expuestas en la presente resolución."
    )


def obtener_articulo_2():

    return ARTICULO_2


def obtener_cierre():

    return (
        "Regístrese, comuníquese y archívese"
    )
