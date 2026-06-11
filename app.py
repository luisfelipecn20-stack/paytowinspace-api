from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import fitz  # PyMuPDF

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

    # Abrir PDF
    pdf = fitz.open(stream=contenido, filetype="pdf")

    total_paginas = len(pdf)

    return {
        "resultado": "OK",
        "nombre_archivo": archivo.filename,
        "paginas": total_paginas
    }
