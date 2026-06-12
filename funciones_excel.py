import pandas as pd

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
        excel_bruto,
        niss):

    df_bruto = pd.read_excel(excel_bruto)

    print(df_bruto.columns.tolist())

    return {
        "columnas": df_bruto.columns.tolist()
    }
