import pandas as pd
import base64
from io import BytesIO
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from funciones_pdf import contar_paginas_pdf, convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from funciones_excel import obtener_datos_resolucion
from funciones_resolucion import generar_considerando_1

app = FastAPI()


class DatosEntrada(BaseModel):
    niss: str = ""
    re: str = ""
    inspeccion: str = ""
    gfmf: str = ""
    operacional: str = ""
    excel_sin_depurar: str = ""
    numero_documento: str = ""
    pdfs: list[str] = []


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

    datos_resolucion = obtener_datos_resolucion(
        excel_stream,
        datos.niss
    )

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "datos_resolucion": datos_resolucion
    }


@app.post("/resolver")
def resolver(datos: DatosEntrada):

    return {
        "resultado": "OK",
        "niss": datos.niss,
        "re": datos.re,
        "cantidad_pdfs": len(datos.pdfs),
        "pdfs": datos.pdfs
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

    contenido_excel = await archivo.read()

    excel_stream = BytesIO(
        contenido_excel
    )

    datos_resolucion = obtener_datos_resolucion(
        excel_stream,
        niss
    )

    if not datos_resolucion:
        return {
            "error": "No se encontró el NISS en el Excel."
        }

    considerando_1 = generar_considerando_1(
        datos_resolucion
    )

    return {
        "datos_resolucion": datos_resolucion,
        "considerando_1": considerando_1
    }
