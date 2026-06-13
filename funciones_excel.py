import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from funciones_pdf import contar_paginas_pdf, convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from funciones_resolucion import generar_considerando_1

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

# El Excel se carga UNA sola vez al iniciar la API
df_bruto = pd.read_excel("excel sin depurar.xlsx")


def obtener_datos_resolucion(niss):

    df_filtrado = df_bruto[
        df_bruto["nis_rad"] == int(niss)
    ]

    df_resolucion = df_filtrado.reindex(
        columns=COLUMNAS_RESOLUCION
    )

    return df_resolucion.to_dict(
        orient="records"
    )


app = FastAPI()


class DatosEntrada(BaseModel):
    niss: str = ""
    inspeccion: str = ""
    gfmf: str = ""
    operacional: str = ""


@app.get("/")
def inicio():
    return {"mensaje": "Hola desde PaytowinSpace"}


@app.post("/procesar")
def procesar(datos: DatosEntrada):

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "inspeccion_recibida": datos.inspeccion,
        "gfmf_recibido": datos.gfmf,
        "operacional_recibido": datos.operacional
    }


@app.post("/subir_pdf")
async def subir_pdf(archivo: UploadFile = File(...)):

    contenido = await archivo.read()

    total_paginas = contar_paginas_pdf(contenido)

    return {
        "resultado": "OK",
        "nombre_archivo": archivo.filename,
        "paginas": total_paginas
    }


@app.post("/subir_imagen")
async def subir_imagen(archivo: UploadFile = File(...)):

    contenido = await archivo.read()

    texto_extraido = analizar_imagen(contenido)

    return {
        "resultado": "OK",
        "nombre_archivo": archivo.filename,
        "texto_extraido": texto_extraido
    }


@app.post("/analizar_inspeccion")
async def analizar_inspeccion(archivo: UploadFile = File(...)):

    contenido = await archivo.read()

    if archivo.filename.lower().endswith(".pdf"):

        imagenes = convertir_pdf_a_imagenes(contenido)

        resultados = []

        for imagen in imagenes:

            resultado = analizar_imagen(imagen)

            resultados.append(resultado)

        return resultados

    else:

        datos_inspeccion = analizar_imagen(contenido)

        return datos_inspeccion


@app.post("/generar_considerando_1")
async def generar_considerando_1_api(
    niss: str = ""
):

    datos_resolucion = obtener_datos_resolucion(
        niss
    )

    return {
        "datos_resolucion": datos_resolucion
    }
