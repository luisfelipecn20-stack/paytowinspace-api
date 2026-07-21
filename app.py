import pandas as pd
import base64
from io import BytesIO
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from funciones_pdf import (
    contar_paginas_pdf,
    convertir_pdf_a_imagenes,
    extraer_texto_pdf,
    buscar_paginas_documentos
)
from funciones_vision import analizar_imagen
from funciones_excel import obtener_datos_resolucion
from funciones_considerando_1 import generar_considerando_1
from funciones_considerando_3 import generar_considerando_3
from funciones_formato_2 import obtener_datos_formato_2
from obtener_datos_informe_facturacion import obtener_datos_informe_facturacion
from sharepoint import probar_conexion
from typing import Optional
from funciones_considerando_4 import (
    generar_considerando_4,
    combinar_datos_facturacion
)

from funciones_considerando_2 import (
    generar_considerando_2,
    obtener_referencia_reclamante
)

app = FastAPI()


class DatosEntrada(BaseModel):
    niss: str = ""
    num_os: str = ""
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
    datos.num_os
    )

    return {
        "resultado": "OK",
        "num_os_recibido": datos.num_os,
        "datos_resolucion": datos_resolucion
    }


@app.post("/resolver")
def resolver(datos: DatosEntrada):

    return {
        "resultado": "OK",
        "num_os": datos.num_os,
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
    num_os: str = ""
):

    contenido_excel = await archivo.read()

    excel_stream = BytesIO(
        contenido_excel
    )

    datos_resolucion = obtener_datos_resolucion(
    excel_stream,
    num_os
    )

    if not datos_resolucion:
        return {
            "error": f"No se encontró la O/S {num_os} en el Excel."
    }

    considerando_1 = generar_considerando_1(
        datos_resolucion
    )

    return {
        "datos_resolucion": datos_resolucion,
        "considerando_1": considerando_1
    }

@app.post("/analizar_formato_2")
async def analizar_formato_2(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    datos_formato_2 = obtener_datos_formato_2(
        contenido
    )

    return datos_formato_2

@app.post("/generar_considerando_2")
async def generar_considerando_2_api(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    datos_formato_2 = obtener_datos_formato_2(
        contenido
    )

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return {
            "estado": "ERROR_FORMATO_2",
            "considerando_2": ""
        }

    reclamante = datos_formato_2.get(
        "reclamante",
        ""
    )

    genero_reclamante = datos_formato_2.get(
        "genero_reclamante",
        ""
    )

    referencia_reclamante = (
        obtener_referencia_reclamante(
            reclamante,
            genero_reclamante
        )
    )

    considerando_2 = generar_considerando_2(
        datos_formato_2
    )

    if considerando_2:
        estado = "GENERADO"
    else:
        estado = "PENDIENTE_SIN_DATOS"

    return {
        "estado": estado,
        "reclamante": reclamante,
        "canal_atencion": datos_formato_2.get(
            "canal_atencion",
            ""
        ),
        "solicita_contraste": datos_formato_2.get(
            "solicita_contraste",
            ""
        ),
        "referencia_reclamante": referencia_reclamante,
        "considerando_2": considerando_2
    }

@app.get("/generar_considerando_3")
def generar_considerando_3_api():

    considerando_3 = generar_considerando_3()

    return {
        "considerando_3": considerando_3
    }

@app.post("/analizar_informe_facturacion")
async def analizar_informe_facturacion(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    datos_informe = (
        obtener_datos_informe_facturacion(
            contenido
        )
    )

    return datos_informe

@app.post("/extraer_texto_pdf")
async def extraer_texto_pdf_api(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    texto = extraer_texto_pdf(
        contenido
    )

    return {
        "texto": texto
    }

@app.post("/generar_considerando_4")
async def generar_considerando_4_api(
    archivo_informe: Optional[UploadFile] = File(None),
    archivo_formato_2: Optional[UploadFile] = File(None)
):

    datos_informe = {}
    datos_formato_2 = {}

    regimen_facturacion = []
    recibos_formato_3 = []

    # Datos del Informe Técnico.
    if archivo_informe is not None:

        contenido_informe = (
            await archivo_informe.read()
        )

        datos_informe = (
            obtener_datos_informe_facturacion(
                contenido_informe
            )
        )

        if isinstance(datos_informe, dict):

            regimen_facturacion = (
                datos_informe.get(
                    "regimen_facturacion",
                    []
                )
            )

    # Datos del Formato 3.
    if archivo_formato_2 is not None:

        contenido_formato_2 = (
            await archivo_formato_2.read()
        )

        datos_formato_2 = (
            obtener_datos_formato_2(
                contenido_formato_2
            )
        )

        if isinstance(datos_formato_2, dict):

            recibos_formato_3 = (
                datos_formato_2.get(
                    "recibos_formato_3",
                    []
                )
            )

    # Comparación entre las dos fuentes.
    registros_validados = (
        combinar_datos_facturacion(
            regimen_facturacion=regimen_facturacion,
            recibos_formato_3=recibos_formato_3
        )
    )

    validacion_facturacion = [
        {
            "mes": registro["mes_original"],
            "m3_informe": registro["m3_informe"],
            "m3_formato_3": registro["m3_formato_3"],
            "m3_utilizado": registro["m3"],
            "estado": registro["estado_validacion"]
        }
        for registro in registros_validados
    ]

    tiene_diferencias = any(
        registro["estado_validacion"].startswith(
            "DIFERENCIA"
        )
        for registro in registros_validados
    )

    considerando_4 = generar_considerando_4(
        regimen_facturacion=regimen_facturacion,
        recibos_formato_3=recibos_formato_3
    )

    if considerando_4:
        estado = "GENERADO"
    else:
        estado = "PENDIENTE_SIN_DATOS"

    return {
        "estado": estado,
        "regimen_facturacion": regimen_facturacion,
        "recibos_formato_3": recibos_formato_3,
        "validacion_facturacion": validacion_facturacion,
        "tiene_diferencias": tiene_diferencias,
        "considerando_4": considerando_4,
        "datos_informe": datos_informe
    }
    
@app.post("/buscar_documentos_pdf")
async def buscar_documentos_pdf_api(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    paginas = buscar_paginas_documentos(
        contenido
    )

    return paginas
