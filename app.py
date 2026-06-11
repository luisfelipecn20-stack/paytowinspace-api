from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo que recibirá la información enviada desde Power Automate
class DatosEntrada(BaseModel):
    texto: str

# Ruta de prueba
@app.get("/")
def inicio():
    return {"mensaje": "Hola desde PaytowinSpace"}

# Ruta para recibir información desde Power Automate
@app.post("/procesar")
def procesar(datos: DatosEntrada):
    return {
        "mensaje": "Datos recibidos correctamente",
        "texto_recibido": datos.texto
    }
