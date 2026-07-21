import re
import unicodedata


MESES = {
    "ene": 1,
    "enero": 1,
    "feb": 2,
    "febrero": 2,
    "mar": 3,
    "marzo": 3,
    "abr": 4,
    "abril": 4,
    "may": 5,
    "mayo": 5,
    "jun": 6,
    "junio": 6,
    "jul": 7,
    "julio": 7,
    "ago": 8,
    "agosto": 8,
    "sep": 9,
    "set": 9,
    "septiembre": 9,
    "setiembre": 9,
    "oct": 10,
    "octubre": 10,
    "nov": 11,
    "noviembre": 11,
    "dic": 12,
    "diciembre": 12
}


NOMBRES_MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre"
}


def quitar_tildes(texto):

    texto = unicodedata.normalize(
        "NFD",
        str(texto)
    )

    return "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )


def obtener_clave_mes(mes):

    texto = quitar_tildes(
        mes
    ).lower().strip()

    coincidencia = re.search(
        r"([a-z]+)[\s./-]+(\d{2,4})",
        texto
    )

    if not coincidencia:
        return texto

    nombre_mes = coincidencia.group(1)
    anio = int(coincidencia.group(2))

    numero_mes = MESES.get(
        nombre_mes
    )

    if not numero_mes:
        return texto

    if anio < 100:
        anio += 2000

    return anio, numero_mes


def limpiar_m3(valor):

    if valor is None:
        return ""

    coincidencia = re.search(
        r"\d+(?:[.,]\d+)?",
        str(valor)
    )

    if not coincidencia:
        return ""

    resultado = coincidencia.group(0)

    if resultado.endswith(".0"):
        resultado = resultado[:-2]

    return resultado


def ordenar_registros(registros):

    def clave_orden(registro):

        clave = registro["clave_mes"]

        if isinstance(clave, tuple):
            return clave

        return 9999, 99

    return sorted(
        registros,
        key=clave_orden
    )


def combinar_datos_facturacion(
    regimen_facturacion=None,
    recibos_formato_3=None
):

    regimen_facturacion = (
        regimen_facturacion
        if isinstance(
            regimen_facturacion,
            list
        )
        else []
    )

    recibos_formato_3 = (
        recibos_formato_3
        if isinstance(
            recibos_formato_3,
            list
        )
        else []
    )

    registros = {}

    # Formato 3:
    # fuente de respaldo.
    for fila in recibos_formato_3:

        if not isinstance(fila, dict):
            continue

        mes = str(
            fila.get("mes", "")
        ).strip()

        m3 = limpiar_m3(
            fila.get(
                "m3",
                fila.get(
                    "m3_facturado",
                    ""
                )
            )
        )

        if not mes or not m3:
            continue

        clave_mes = obtener_clave_mes(
            mes
        )

        registros[clave_mes] = {
            "clave_mes": clave_mes,
            "mes_original": mes,
            "m3": m3,
            "fuente": "FORMATO_3"
        }

    # Informe de Facturación:
    # tiene prioridad sobre el Formato 3.
    for fila in regimen_facturacion:

        if not isinstance(fila, dict):
            continue

        mes = str(
            fila.get("mes", "")
        ).strip()

        m3 = limpiar_m3(
            fila.get(
                "m3_facturado",
                ""
            )
        )

        if not mes or not m3:
            continue

        clave_mes = obtener_clave_mes(
            mes
        )

        registros[clave_mes] = {
            "clave_mes": clave_mes,
            "mes_original": mes,
            "m3": m3,
            "fuente": "INFORME_FACTURACION"
        }

    return ordenar_registros(
        list(
            registros.values()
        )
    )


def unir_elementos(elementos):

    if not elementos:
        return ""

    if len(elementos) == 1:
        return elementos[0]

    if len(elementos) == 2:
        return (
            elementos[0]
            + " y "
            + elementos[1]
        )

    return (
        ", ".join(elementos[:-1])
        + " y "
        + elementos[-1]
    )


def construir_texto_meses(registros):

    claves = [
        registro["clave_mes"]
        for registro in registros
    ]

    if all(
        isinstance(clave, tuple)
        for clave in claves
    ):

        anios = {
            clave[0]
            for clave in claves
        }

        if len(anios) == 1:

            anio = claves[0][0]

            nombres = [
                NOMBRES_MESES[clave[1]]
                for clave in claves
            ]

            return (
                unir_elementos(nombres)
                + f" de {anio}"
            )

        meses = [
            (
                f"{NOMBRES_MESES[clave[1]]} "
                f"de {clave[0]}"
            )
            for clave in claves
        ]

        return unir_elementos(
            meses
        )

    return unir_elementos(
        [
            registro["mes_original"]
            for registro in registros
        ]
    )


def generar_considerando_4(
    regimen_facturacion=None,
    recibos_formato_3=None
):

    registros = combinar_datos_facturacion(
        regimen_facturacion,
        recibos_formato_3
    )

    if not registros:
        return ""

    texto_meses = construir_texto_meses(
        registros
    )

    volumenes = [
        f'{registro["m3"]} m³'
        for registro in registros
    ]

    texto_volumenes = unir_elementos(
        volumenes
    )

    inicio = (
        "Con informe técnico del Grupo "
        "Funcional de Medición y Facturación"
    )

    if len(registros) == 1:

        return (
            f"{inicio}, se precisa que el volumen "
            f"real consumido en el mes de "
            f"{texto_meses} es de {texto_volumenes}, "
            f"en base a las diferencias de lecturas "
            f"registradas por el medidor."
        )

    return (
        f"{inicio}, se precisa que los volúmenes "
        f"reales consumidos en los meses de "
        f"{texto_meses} son de {texto_volumenes}, "
        f"respectivamente, en base a las diferencias "
        f"de lecturas registradas por el medidor."
    )
