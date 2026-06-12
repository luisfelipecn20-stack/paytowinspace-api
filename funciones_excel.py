import pandas as pd


def crear_excel_maestro(excel_bruto, excel_plantilla):

    df_bruto = pd.read_excel(excel_bruto)

    df_plantilla = pd.read_excel(excel_plantilla)

    encabezados_maestros = df_plantilla.columns.tolist()

    return encabezados_maestros
