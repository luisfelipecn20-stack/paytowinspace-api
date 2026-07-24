import pandas as pd
import base64
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
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

from funciones_formato_4 import (
    obtener_datos_formato_4,
    consolidar_formato_2_y_4
)

from funciones_considerando_5 import (
    generar_considerando_5
)

from funciones_considerando_6 import (
    generar_considerando_6
)

from funciones_articulos import (
    obtener_parrafo_base_legal,
    obtener_se_resuelve,
    generar_articulo_1,
    obtener_articulo_2,
    obtener_cierre,
    obtener_datos_firma_resolucion
)

from funciones_cruce_expedientes import (
    cruzar_data_open_inspecciones,
    cruzar_data_open_numero_documento
)

from funciones_ensamblaje import (
    buscar_registro_cruce,
    ensamblar_resolucion
)

from funciones_pdf_resolucion import (
    generar_pdf_resolucion
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

@app.post("/cruzar_data_open_inspecciones")
async def cruzar_data_open_inspecciones_api(
    archivo_data_open: UploadFile = File(...),
    archivo_inspecciones: UploadFile = File(...)
):

    contenido_data_open = (
        await archivo_data_open.read()
    )

    contenido_inspecciones = (
        await archivo_inspecciones.read()
    )

    try:

        resultado = (
            cruzar_data_open_inspecciones(
                archivo_data_open=BytesIO(
                    contenido_data_open
                ),
                archivo_inspecciones=BytesIO(
                    contenido_inspecciones
                )
            )
        )

    except ValueError as error:

        return {
            "estado": "ERROR_COLUMNAS",
            "detalle": str(error)
        }

    return resultado

@app.post("/generar_encabezados_resolucion")
async def generar_encabezados_resolucion_api(
    archivo_data_open: UploadFile = File(...),
    archivo_numero_documento: UploadFile = File(...)
):

    contenido_data_open = (
        await archivo_data_open.read()
    )

    contenido_numero_documento = (
        await archivo_numero_documento.read()
    )

    try:

        resultado = (
            cruzar_data_open_numero_documento(
                archivo_data_open=BytesIO(
                    contenido_data_open
                ),
                archivo_numero_documento=BytesIO(
                    contenido_numero_documento
                )
            )
        )

    except ValueError as error:

        return {
            "estado": "ERROR_COLUMNAS",
            "detalle": str(error)
        }

    return resultado

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

@app.post("/analizar_formato_4")
async def analizar_formato_4(
    archivo: UploadFile = File(...)
):

    contenido = await archivo.read()

    datos_formato_4 = obtener_datos_formato_4(
        contenido
    )

    return datos_formato_4

@app.post("/validar_formatos_2_y_4")
async def validar_formatos_2_y_4(
    archivo_formato_2: UploadFile = File(...),
    archivo_formato_4: UploadFile = File(...)
):

    contenido_formato_2 = (
        await archivo_formato_2.read()
    )

    contenido_formato_4 = (
        await archivo_formato_4.read()
    )

    datos_formato_2 = obtener_datos_formato_2(
        contenido_formato_2
    )

    datos_formato_4 = obtener_datos_formato_4(
        contenido_formato_4
    )

    validacion = consolidar_formato_2_y_4(
        datos_formato_2=datos_formato_2,
        datos_formato_4=datos_formato_4,
        nombre_archivo_formato_4=(
            archivo_formato_4.filename
            or ""
        )
    )

    return {
        "datos_formato_2": datos_formato_2,
        "datos_formato_4": datos_formato_4,
        "validacion": validacion
    }

@app.post("/generar_considerando_5")
async def generar_considerando_5_api(
    archivo_formato_2: UploadFile = File(...),
    archivo_formato_4: UploadFile = File(...)
):

    contenido_formato_2 = (
        await archivo_formato_2.read()
    )

    contenido_formato_4 = (
        await archivo_formato_4.read()
    )

    datos_formato_2 = obtener_datos_formato_2(
        contenido_formato_2
    )

    datos_formato_4 = obtener_datos_formato_4(
        contenido_formato_4
    )

    validacion = consolidar_formato_2_y_4(
        datos_formato_2=datos_formato_2,
        datos_formato_4=datos_formato_4,
        nombre_archivo_formato_4=(
            archivo_formato_4.filename
            or ""
        )
    )

    considerando_5 = generar_considerando_5(
        datos_formato_2=datos_formato_2,
        validacion_formato_4=validacion
    )

    if considerando_5:

        estado = "GENERADO"

    elif validacion.get(
        "requiere_revision"
    ):

        estado = "REQUIERE_REVISION"

    else:

        estado = "PENDIENTE_SIN_DATOS"

    return {
        "estado": estado,
        "re_final": validacion.get(
            "re_final",
            ""
        ),
        "fecha_audiencia": validacion.get(
            "fecha_audiencia_final",
            ""
        ),
        "resultado_audiencia": validacion.get(
            "resultado_audiencia",
            ""
        ),
        "continua_reclamo": validacion.get(
            "continua_reclamo",
            ""
        ),
        "caso_soportado_v1": validacion.get(
            "caso_soportado_v1",
            False
        ),
        "requiere_revision": validacion.get(
            "requiere_revision",
            True
        ),
        "validacion": validacion,
        "considerando_5": considerando_5
    }

@app.post("/generar_cierre_resolucion")
async def generar_cierre_resolucion_api(
    archivo_formato_2: UploadFile = File(...)
):

    contenido_formato_2 = (
        await archivo_formato_2.read()
    )

    datos_formato_2 = obtener_datos_formato_2(
        contenido_formato_2
    )

    if not isinstance(
        datos_formato_2,
        dict
    ):

        return {
            "estado": "ERROR_FORMATO_2"
        }

    considerando_6 = generar_considerando_6(
        datos_formato_2
    )

    parrafo_base_legal = (
        obtener_parrafo_base_legal()
    )

    se_resuelve = obtener_se_resuelve()

    articulo_1 = generar_articulo_1(
        datos_formato_2
    )

    articulo_2 = obtener_articulo_2()

    cierre = obtener_cierre()

    datos_firma = (
        obtener_datos_firma_resolucion()
    )
    
    if (
        considerando_6
        and articulo_1
    ):

        estado = "GENERADO"

    else:

        estado = "PENDIENTE_SIN_DATOS"

    return {
        "estado": estado,
        "re": datos_formato_2.get(
            "re",
            ""
        ),
        "tipo_reclamo": datos_formato_2.get(
            "tipo_reclamo",
            ""
        ),
        "meses_reclamados": datos_formato_2.get(
            "meses_reclamados",
            []
        ),
        "considerando_6": considerando_6,
        "parrafo_base_legal": (
            parrafo_base_legal
        ),
        "se_resuelve": se_resuelve,
        "articulo_1": articulo_1,
        "articulo_2": articulo_2,
        "cierre": cierre,
        "firma_resolucion": datos_firma
    }

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

@app.post("/ensamblar_resolucion")
async def ensamblar_resolucion_api(
    archivo_data_open: UploadFile = File(...),
    archivo_inspecciones: UploadFile = File(...),
    archivo_numero_documento: UploadFile = File(...),
    archivo_formato_2: UploadFile = File(...),
    archivo_informe: UploadFile = File(...),
    archivo_formato_4: UploadFile = File(...)
):

    contenido_data_open = (
        await archivo_data_open.read()
    )

    contenido_inspecciones = (
        await archivo_inspecciones.read()
    )

    contenido_numero_documento = (
        await archivo_numero_documento.read()
    )

    contenido_formato_2 = (
        await archivo_formato_2.read()
    )

    contenido_informe = (
        await archivo_informe.read()
    )

    contenido_formato_4 = (
        await archivo_formato_4.read()
    )

    datos_formato_2 = obtener_datos_formato_2(
        contenido_formato_2
    )

    if not isinstance(
        datos_formato_2,
        dict
    ):

        return {
            "estado": "ERROR_FORMATO_2"
        }

    re_formato_2 = datos_formato_2.get(
        "re",
        ""
    )

    niss_formato_2 = datos_formato_2.get(
        "niss",
        ""
    )

    try:

        cruce_inspecciones = (
            cruzar_data_open_inspecciones(
                archivo_data_open=BytesIO(
                    contenido_data_open
                ),
                archivo_inspecciones=BytesIO(
                    contenido_inspecciones
                )
            )
        )

        cruce_encabezados = (
            cruzar_data_open_numero_documento(
                archivo_data_open=BytesIO(
                    contenido_data_open
                ),
                archivo_numero_documento=BytesIO(
                    contenido_numero_documento
                )
            )
        )

    except ValueError as error:

        return {
            "estado": "ERROR_COLUMNAS_EXCEL",
            "detalle": str(error)
        }

    expediente_inspeccion = buscar_registro_cruce(
        resultado_cruce=cruce_inspecciones,
        nombre_lista="expedientes",
        re_buscado=re_formato_2,
        niss_buscado=niss_formato_2
    )

    encabezado = buscar_registro_cruce(
        resultado_cruce=cruce_encabezados,
        nombre_lista="encabezados",
        re_buscado=re_formato_2,
        niss_buscado=niss_formato_2
    )

    if not expediente_inspeccion:

        return {
            "estado": "SIN_CRUCE_INSPECCION",
            "re": re_formato_2,
            "niss": niss_formato_2
        }

    if expediente_inspeccion.get(
        "estado_cruce"
    ) != "VALIDADO":

        return {
            "estado": "INSPECCION_REQUIERE_REVISION",
            "detalle": expediente_inspeccion
        }

    if not encabezado:

        return {
            "estado": "SIN_CRUCE_ENCABEZADO",
            "re": re_formato_2,
            "niss": niss_formato_2
        }

    if encabezado.get(
        "estado_cruce"
    ) != "VALIDADO":

        return {
            "estado": "ENCABEZADO_REQUIERE_REVISION",
            "detalle": encabezado
        }

    datos_inspeccion = expediente_inspeccion.get(
        "datos_inspeccion",
        {}
    )

    datos_informe = (
        obtener_datos_informe_facturacion(
            contenido_informe
        )
    )

    datos_formato_4 = obtener_datos_formato_4(
        contenido_formato_4
    )

    validacion_formato_4 = (
        consolidar_formato_2_y_4(
            datos_formato_2=datos_formato_2,
            datos_formato_4=datos_formato_4,
            nombre_archivo_formato_4=(
                archivo_formato_4.filename
                or ""
            )
        )
    )

    resultado = ensamblar_resolucion(
        datos_formato_2=datos_formato_2,
        datos_inspeccion=datos_inspeccion,
        datos_informe=datos_informe,
        validacion_formato_4=(
            validacion_formato_4
        ),
        encabezado=encabezado
    )

    resultado["origenes"] = {
        "archivo_formato_2": (
            archivo_formato_2.filename
        ),
        "archivo_informe": (
            archivo_informe.filename
        ),
        "archivo_formato_4": (
            archivo_formato_4.filename
        ),
        "num_os": expediente_inspeccion.get(
            "num_os",
            ""
        ),
        "fecha_inspeccion": (
            expediente_inspeccion.get(
                "fecha_inspeccion",
                ""
            )
        )
    }

    return resultado

@app.post("/generar_pdf_resolucion")
async def generar_pdf_resolucion_api(
    archivo_data_open: UploadFile = File(...),
    archivo_inspecciones: UploadFile = File(...),
    archivo_numero_documento: UploadFile = File(...),
    archivo_formato_2: UploadFile = File(...),
    archivo_informe: UploadFile = File(...),
    archivo_formato_4: UploadFile = File(...)
):

    resultado = await ensamblar_resolucion_api(
        archivo_data_open=archivo_data_open,
        archivo_inspecciones=(
            archivo_inspecciones
        ),
        archivo_numero_documento=(
            archivo_numero_documento
        ),
        archivo_formato_2=archivo_formato_2,
        archivo_informe=archivo_informe,
        archivo_formato_4=archivo_formato_4
    )

    if not isinstance(
        resultado,
        dict
    ):

        return {
            "estado": "ERROR_ENSAMBLAJE"
        }

    if resultado.get(
        "estado"
    ) != "GENERADO":

        return resultado

    try:

        contenido_pdf = generar_pdf_resolucion(
            resultado
        )

    except (
        ValueError,
        FileNotFoundError
    ) as error:

        return {
            "estado": "ERROR_GENERACION_PDF",
            "detalle": str(error)
        }

    re_final = resultado.get(
        "datos_expediente",
        {}
    ).get(
        "re",
        ""
    )

    nombre_archivo = (
        f"Resolucion_{re_final}.pdf"
    )

    return StreamingResponse(
        BytesIO(
            contenido_pdf
        ),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                f'filename="{nombre_archivo}"'
            )
        }
    )


@app.post("/generar_pdfs_lote")
async def generar_pdfs_lote_api(
    archivo_data_open: UploadFile = File(...),
    archivo_inspecciones: UploadFile = File(...),
    archivo_numero_documento: UploadFile = File(...),
    archivos_formato_2: list[UploadFile] = File(...),
    archivos_informe: list[UploadFile] = File(...),
    archivos_formato_4: list[UploadFile] = File(...)
):

    cantidades = {
        "formatos_2": len(
            archivos_formato_2
        ),
        "informes": len(
            archivos_informe
        ),
        "formatos_4": len(
            archivos_formato_4
        )
    }

    if any(
        cantidad != 3
        for cantidad in cantidades.values()
    ):

        return {
            "estado": "CANTIDAD_ARCHIVOS_INVALIDA",
            "detalle": (
                "Para esta prueba deben cargarse "
                "exactamente 3 archivos de cada tipo."
            ),
            "cantidades_recibidas": cantidades
        }

    resultados = []
    resoluciones_pdf = []

    expedientes = zip(
        archivos_formato_2,
        archivos_informe,
        archivos_formato_4
    )

    for posicion, expediente in enumerate(
        expedientes,
        start=1
    ):

        archivo_formato_2 = expediente[0]
        archivo_informe = expediente[1]
        archivo_formato_4 = expediente[2]

        await archivo_data_open.seek(0)
        await archivo_inspecciones.seek(0)
        await archivo_numero_documento.seek(0)

        resultado = await ensamblar_resolucion_api(
            archivo_data_open=archivo_data_open,
            archivo_inspecciones=(
                archivo_inspecciones
            ),
            archivo_numero_documento=(
                archivo_numero_documento
            ),
            archivo_formato_2=archivo_formato_2,
            archivo_informe=archivo_informe,
            archivo_formato_4=archivo_formato_4
        )

        if not isinstance(
            resultado,
            dict
        ):

            resultados.append(
                {
                    "posicion": posicion,
                    "estado": "ERROR_ENSAMBLAJE"
                }
            )

            continue

        estado = resultado.get(
            "estado",
            ""
        )

        re_final = resultado.get(
            "datos_expediente",
            {}
        ).get(
            "re",
            ""
        )

        registro_resultado = {
            "posicion": posicion,
            "re": re_final,
            "estado": estado,
            "archivo_formato_2": (
                archivo_formato_2.filename
            ),
            "archivo_informe": (
                archivo_informe.filename
            ),
            "archivo_formato_4": (
                archivo_formato_4.filename
            )
        }

        if estado != "GENERADO":

            registro_resultado[
                "componentes_faltantes"
            ] = resultado.get(
                "componentes_faltantes",
                []
            )

            resultados.append(
                registro_resultado
            )

            continue

        try:

            contenido_pdf = generar_pdf_resolucion(
                resultado
            )

        except (
            ValueError,
            FileNotFoundError
        ) as error:

            registro_resultado[
                "estado"
            ] = "ERROR_GENERACION_PDF"

            registro_resultado[
                "detalle"
            ] = str(error)

            resultados.append(
                registro_resultado
            )

            continue

        nombre_pdf = (
            f"Resolucion_{re_final}.pdf"
        )

        resoluciones_pdf.append(
            (
                nombre_pdf,
                contenido_pdf
            )
        )

        resultados.append(
            registro_resultado
        )

    tiene_errores = any(
        resultado.get(
            "estado"
        ) != "GENERADO"
        for resultado in resultados
    )

    if tiene_errores:

        return {
            "estado": "LOTE_REQUIERE_REVISION",
            "total_solicitados": 3,
            "total_generados": len(
                resoluciones_pdf
            ),
            "resultados": resultados
        }

    memoria_zip = BytesIO()

    with ZipFile(
        memoria_zip,
        mode="w",
        compression=ZIP_DEFLATED
    ) as archivo_zip:

        for nombre_pdf, contenido_pdf in (
            resoluciones_pdf
        ):

            archivo_zip.writestr(
                nombre_pdf,
                contenido_pdf
            )

    memoria_zip.seek(0)

    return StreamingResponse(
        memoria_zip,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="Resoluciones_lote.zip"'
            )
        }
    )
