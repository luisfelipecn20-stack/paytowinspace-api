import pandas as pd
import time

COLUMNAS_RESOLUCION = [
    "medidor",
    "nis_rad",
    "num_os",
    "fec_vis",
    "serv",
    "cx_c_dt",
    "lec",
    "fuga_caj",
    "uu_ocup",
    "soc_ocup",
    "dom_ocup",
    "com_ocup",
    "ind_ocup",
    "est_ocup",
    "uu_docup",
    "soc_desc",
    "dom_desc",
    "com_desc",
    "ind_desc",
    "est_desc",
    "observ",
    "observm1"
]


def crear_excel_maestro(excel_bruto):

    df_bruto = pd.read_excel(excel_bruto)

    df_maestro = df_bruto.reindex(
        columns=COLUMNAS_RESOLUCION
    )

    return df_maestro


def guardar_excel_maestro(
        excel_bruto,
        ruta_salida):

    df_maestro = crear_excel_maestro(
        excel_bruto
    )

    df_maestro.to_excel(
        ruta_salida,
        index=False
    )


def obtener_datos_resolucion(
        df_bruto,
        niss):

    # ---------- FILTRO ----------
    inicio_filtro = time.time()

    df_filtrado = df_bruto[
        df_bruto["nis_rad"] == int(niss)
    ]

    print(
        "Tiempo filtro:",
        round(time.time() - inicio_filtro, 2),
        "segundos"
    )

    if df_filtrado.empty:
        return {}

    # ---------- OBTENER FILA ----------
    inicio_fila = time.time()

    fila = df_filtrado.iloc[0]

    print(
        "Tiempo iloc:",
        round(time.time() - inicio_fila, 2),
        "segundos"
    )

    # ---------- DICCIONARIO ----------
    inicio_dict = time.time()

    resultado = fila.reindex(
        COLUMNAS_RESOLUCION
    ).to_dict()

    print(
        "Tiempo to_dict:",
        round(time.time() - inicio_dict, 2),
        "segundos"
    )

    return resultado
