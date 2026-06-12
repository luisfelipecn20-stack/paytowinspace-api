import pandas as pd

# Columnas que necesita la resolución
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

    df_maestro = df_bruto.reindex(columns=COLUMNAS_RESOLUCION)

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


def obtener_datos_resolucion(excel_bruto):

    df_bruto = pd.read_excel(excel_bruto)

    df_resolucion = df_bruto.reindex(columns=COLUMNAS_RESOLUCION)

    return df_resolucion.to_dict(orient="records")
    
