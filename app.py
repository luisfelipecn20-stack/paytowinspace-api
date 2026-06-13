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
    excel_url: str = ""


@app.get("/")
def inicio():

    return {
        "mensaje": "Hola desde PaytowinSpace"
    }


@app.post("/procesar")
def procesar(datos: DatosEntrada):

    datos_resolucion = obtener_datos_resolucion(
        datos.excel_url,
        datos.niss
    )

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "datos_resolucion": datos_resolucion
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
