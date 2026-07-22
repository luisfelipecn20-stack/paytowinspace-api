import re
import pandas as pd

from funciones_excel import (
    COLUMNAS_RESOLUCION
)


COLUMNAS_DATA_OPEN = {
    "num_re",
    "nis_rad",
    "f_ire",
    "f_uce",
    "desc_tipo"
}


COLUMNAS_CONTROL_INSPECCION = {
    "nis_rad",
    "num_os",
    "tip_os",
    "fec_emis",
    "fec_vis",
    "nreclamo"
}


def normalizar_re(valor):

    coincidencia = re.search(
        r"\bRE\d+\b",
        str(valor).strip(),
        re.IGNORECASE
    )

    if coincidencia:
        return coincidencia.group(0).upper()

    return ""


def normalizar_numero(valor):

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if re.fullmatch(
        r"\d+\.0+",
        texto
    ):
        texto = texto.split(".")[0]

    return re.sub(
        r"\D",
        "",
        texto
    )


def formatear_fecha(valor):

    fecha = pd.to_datetime(
        valor,
        errors="coerce"
    )

    if pd.isna(fecha):
        return ""

    return fecha.strftime(
        "%d/%m/%Y"
    )


def limpiar_valor_json(valor):

    if pd.isna(valor):
        return ""

    if isinstance(
        valor,
        pd.Timestamp
    ):
        return valor.strftime(
            "%d/%m/%Y"
        )

    if hasattr(
        valor,
        "item"
    ):

        try:
            return valor.item()

        except ValueError:
            pass

    return valor


def validar_columnas(
    dataframe,
    columnas_requeridas,
    nombre_archivo
):

    columnas_faltantes = (
        columnas_requeridas
        - set(dataframe.columns)
    )

    if columnas_faltantes:

        faltantes = ", ".join(
            sorted(columnas_faltantes)
        )

        raise ValueError(
            f"{nombre_archivo}: faltan columnas: "
            f"{faltantes}"
        )


def obtener_columnas_inspeccion():

    columnas = list(
        COLUMNAS_RESOLUCION
    )

    for columna in COLUMNAS_CONTROL_INSPECCION:

        if columna not in columnas:
            columnas.append(
                columna
            )

    return columnas


def cruzar_data_open_inspecciones(
    archivo_data_open,
    archivo_inspecciones
):

    dataframe_open = pd.read_excel(
        archivo_data_open
    )

    columnas_inspeccion = (
        obtener_columnas_inspeccion()
    )

    dataframe_inspecciones = pd.read_excel(
        archivo_inspecciones,
        usecols=lambda columna: (
            str(columna).strip()
            in columnas_inspeccion
        )
    )

    dataframe_open.columns = [
        str(columna).strip()
        for columna in dataframe_open.columns
    ]

    dataframe_inspecciones.columns = [
        str(columna).strip()
        for columna in dataframe_inspecciones.columns
    ]

    validar_columnas(
        dataframe_open,
        COLUMNAS_DATA_OPEN,
        "DATA_OPEN"
    )

    validar_columnas(
        dataframe_inspecciones,
        COLUMNAS_CONTROL_INSPECCION,
        "INSPECCIONES"
    )

    dataframe_inspecciones[
        "_niss_normalizado"
    ] = dataframe_inspecciones[
        "nis_rad"
    ].apply(
        normalizar_numero
    )

    dataframe_inspecciones[
        "_re_inspeccion"
    ] = dataframe_inspecciones[
        "nreclamo"
    ].apply(
        normalizar_re
    )

    dataframe_inspecciones[
        "_fec_emis"
    ] = pd.to_datetime(
        dataframe_inspecciones[
            "fec_emis"
        ],
        errors="coerce"
    )

    dataframe_inspecciones[
        "_fec_vis"
    ] = pd.to_datetime(
        dataframe_inspecciones[
            "fec_vis"
        ],
        errors="coerce"
    )

    dataframe_inspecciones[
        "_tipo_os"
    ] = dataframe_inspecciones[
        "tip_os"
    ].astype(str).str.strip().str.upper()

    # Para Consumo Medido únicamente se utilizan
    # las inspecciones de tipo TO821.
    dataframe_inspecciones = (
        dataframe_inspecciones[
            dataframe_inspecciones[
                "_tipo_os"
            ]
            == "TO821"
        ].copy()
    )

    expedientes = []
    claves_data_open = set()

    for _, fila_open in dataframe_open.iterrows():

        re_open = normalizar_re(
            fila_open.get(
                "num_re",
                ""
            )
        )

        niss_open = normalizar_numero(
            fila_open.get(
                "nis_rad",
                ""
            )
        )

        fecha_ingreso = pd.to_datetime(
            fila_open.get(
                "f_ire",
                ""
            ),
            errors="coerce"
        )

        clave_data_open = (
            re_open,
            niss_open
        )

        expediente = {
            "re": re_open,
            "niss": niss_open,
            "tipo_reclamo": str(
                fila_open.get(
                    "desc_tipo",
                    ""
                )
            ).strip(),
            "fecha_ingreso_reclamo": (
                formatear_fecha(
                    fila_open.get(
                        "f_ire",
                        ""
                    )
                )
            ),
            "fecha_limite": (
                formatear_fecha(
                    fila_open.get(
                        "f_uce",
                        ""
                    )
                )
            ),
            "num_os": "",
            "fecha_inspeccion": "",
            "re_inspeccion": "",
            "coincide_re_inspeccion": False,
            "cantidad_inspecciones_candidatas": 0,
            "regla_seleccion": "",
            "estado_cruce": "",
            "datos_inspeccion": {}
        }

        if not re_open or not niss_open:

            expediente["estado_cruce"] = (
                "DATOS_CLAVE_INVALIDOS"
            )

            expedientes.append(
                expediente
            )

            continue

        if pd.isna(fecha_ingreso):

            expediente["estado_cruce"] = (
                "FECHA_INGRESO_INVALIDA"
            )

            expedientes.append(
                expediente
            )

            continue

        if clave_data_open in claves_data_open:

            expediente["estado_cruce"] = (
                "DUPLICADO_DATA_OPEN"
            )

            expedientes.append(
                expediente
            )

            continue

        claves_data_open.add(
            clave_data_open
        )

        candidatas = dataframe_inspecciones[
            (
                dataframe_inspecciones[
                    "_niss_normalizado"
                ]
                == niss_open
            )
            & (
                dataframe_inspecciones[
                    "_fec_emis"
                ]
                >= fecha_ingreso
            )
        ].copy()

        cantidad_candidatas = len(
            candidatas
        )

        expediente[
            "cantidad_inspecciones_candidatas"
        ] = cantidad_candidatas

        if candidatas.empty:

            expediente["estado_cruce"] = (
                "SIN_INSPECCION_TO821"
            )

            expedientes.append(
                expediente
            )

            continue

        candidatas_con_fecha = candidatas[
            candidatas[
                "_fec_vis"
            ].notna()
        ].copy()

        if candidatas_con_fecha.empty:

            expediente["estado_cruce"] = (
                "INSPECCION_SIN_FECHA"
            )

            expedientes.append(
                expediente
            )

            continue

        fecha_mas_reciente = (
            candidatas_con_fecha[
                "_fec_vis"
            ].max()
        )

        inspecciones_mas_recientes = (
            candidatas_con_fecha[
                candidatas_con_fecha[
                    "_fec_vis"
                ]
                == fecha_mas_reciente
            ]
        )

        if len(
            inspecciones_mas_recientes
        ) > 1:

            expediente["estado_cruce"] = (
                "EMPATE_INSPECCION_REQUIERE_REVISION"
            )

            expedientes.append(
                expediente
            )

            continue

        fila_inspeccion = (
            inspecciones_mas_recientes.iloc[0]
        )

        num_os = normalizar_numero(
            fila_inspeccion.get(
                "num_os",
                ""
            )
        )

        if not num_os:

            expediente["estado_cruce"] = (
                "INSPECCION_SIN_NUM_OS"
            )

            expedientes.append(
                expediente
            )

            continue

        re_inspeccion = normalizar_re(
            fila_inspeccion.get(
                "nreclamo",
                ""
            )
        )

        datos_inspeccion = {}

        for columna in COLUMNAS_RESOLUCION:

            datos_inspeccion[columna] = (
                limpiar_valor_json(
                    fila_inspeccion.get(
                        columna,
                        ""
                    )
                )
            )

        if cantidad_candidatas == 1:

            regla_seleccion = (
                "INSPECCION_UNICA"
            )

        else:

            regla_seleccion = (
                "FECHA_VISITA_MAS_RECIENTE"
            )

        expediente.update(
            {
                "num_os": num_os,
                "fecha_inspeccion": (
                    formatear_fecha(
                        fila_inspeccion.get(
                            "fec_vis",
                            ""
                        )
                    )
                ),
                "re_inspeccion": re_inspeccion,
                "coincide_re_inspeccion": (
                    re_inspeccion == re_open
                ),
                "regla_seleccion": (
                    regla_seleccion
                ),
                "estado_cruce": "VALIDADO",
                "datos_inspeccion": (
                    datos_inspeccion
                )
            }
        )

        expedientes.append(
            expediente
        )

    total_solicitados = len(
        expedientes
    )

    total_validados = sum(
        expediente["estado_cruce"]
        == "VALIDADO"
        for expediente in expedientes
    )

    total_observados = (
        total_solicitados
        - total_validados
    )

    if total_solicitados == 0:

        estado = "SIN_CASOS"

    elif total_observados == 0:

        estado = "VALIDADO"

    else:

        estado = (
            "VALIDADO_CON_OBSERVACIONES"
        )

    return {
        "estado": estado,
        "total_solicitados": (
            total_solicitados
        ),
        "total_validados": (
            total_validados
        ),
        "total_observados": (
            total_observados
        ),
        "expedientes": expedientes
    }
