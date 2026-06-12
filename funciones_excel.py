import pandas as pd


def crear_excel_maestro(excel_bruto, excel_plantilla):

    df_bruto = pd.read_excel(excel_bruto)

    df_plantilla = pd.read_excel(excel_plantilla)

    encabezados_maestros = df_plantilla.columns.tolist()

    equivalencias = {

        "medidor": "medidor",
        "nis_rad": "nis_rad",
        "num_os": "num_os",
        "fec_vis": "fec_vis",
        "serv": "serv",
        "cx_c_dt": "cx_c_dt",
        "lec": "lec",
        "fuga_caj": "fuga_caj",
        "uu_ocup": "uu_ocup",
        "soc_ocup": "soc_ocup",
        "dom_ocup": "dom_ocup",
        "com_ocup": "com_ocup",
        "ind_ocup": "ind_ocup",
        "est_ocup": "est_ocup",
        "uu_docup": "uu_docup",
        "soc_desc": "soc_desc",
        "dom_desc": "dom_desc",
        "com_desc": "com_desc",
        "ind_desc": "ind_desc",
        "est_desc": "est_desc",
        "observ": "observ",
        "observm1": "observm1"

    }

    df_maestro = df_bruto.rename(columns=equivalencias)

    df_maestro = df_maestro[encabezados_maestros]
    
    return df_maestro

def guardar_excel_maestro(
        excel_bruto,
        excel_plantilla,
        ruta_salida):

    df_maestro = crear_excel_maestro(
        excel_bruto,
        excel_plantilla
    )

    df_maestro.to_excel(
        ruta_salida,
        index=False
    )
