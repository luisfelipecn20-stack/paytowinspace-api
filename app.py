import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from funciones_pdf import contar_paginas_pdf, convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from funciones_excel import obtener_datos_resolucion
from funciones_resolucion import generar_considerando_1

app = FastAPI()


class DatosEntrada(BaseModel):
    niss: str = ""
    inspeccion: str = ""
    gfmf: str = ""
    operacional: str = ""
    excel_sin_depurar: str = ""


@app.get("/")
def inicio():
    return {"mensaje": "Hola desde PaytowinSpace"}


@app.post("/procesar")
def procesar(datos: DatosEntrada):

    excel_bytes = base64.b64decode(
        datos.excel_sin_depurar
    )

    excel_stream = BytesIO(
        excel_bytes
    )

    df_bruto = pd.read_excel(
        excel_stream
    )

    df_filtrado = df_bruto[
        df_bruto["nis_rad"].astype(str)
        == str(datos.niss)
    ]

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "filas_encontradas": len(df_filtrado),
        "datos_encontrados": df_filtrado.to_dict(
            orient="records"
        )
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
    archivo: UploadFile = File(...),
    niss: str = ""
):

    datos_resolucion = obtener_datos_resolucion(
        archivo.file,
        niss
    )

    return {
        "datos_resolucion": datos_resolucion
    }
