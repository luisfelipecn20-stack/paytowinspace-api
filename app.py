from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# Modelo que recibirá la información desde Power Automate
class DatosEntrada(BaseModel):
    niss: str = ""
    inspeccion: str = ""
    gfmf: str = ""
    operacional: str = ""


# Ruta de prueba
@app.get("/")
def inicio():
    return {"mensaje": "Hola desde PaytowinSpace"}


# Ruta para procesar la información
@app.post("/procesar")
def procesar(datos: DatosEntrada):

    return {
        "resultado": "OK",
        "niss_recibido": datos.niss,
        "inspeccion_recibida": datos.inspeccion,
        "gfmf_recibido": datos.gfmf,
        "operacional_recibido": datos.operacional
    }
