from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()


# Modelo que recibirá información desde Power Automate
class DatosEntrada(BaseModel):
    niss: str = ""
    inspeccion: str = ""
    gfmf: str = ""
    operacional: str = ""


# Ruta de prueba
@app.get("/")
def inicio():
    return {"mensaje": "Hola desde PaytowinSpace"}


# Ruta para procesar información enviada como JSON
@app.post("/procesar")
def procesar(datos: DatosEntrada):

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "inspeccion_recibida": datos.inspeccion,
        "gfmf_recibido": datos.gfmf,
        "operacional_recibido": datos.operacional
    }


# Ruta para recibir un PDF
@app.post("/subir_pdf")
async def subir_pdf(archivo: UploadFile = File(...)):

    contenido = await archivo.read()

    return {
        "resultado": "OK",
        "nombre_archivo": archivo.filename,
        "tamano_bytes": len(contenido)
    }
