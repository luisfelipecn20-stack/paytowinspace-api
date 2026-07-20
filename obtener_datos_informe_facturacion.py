import json

from funciones_pdf import convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from prompt_informe_facturacion import (
    PROMPT_INFORME_FACTURACION
)


def limpiar_bloque_json(respuesta):

    texto = respuesta.strip()

    if texto.startswith("```"):

        lineas = texto.splitlines()

        if lineas and lineas[0].startswith("```"):
            lineas = lineas[1:]

        if lineas and lineas[-1].strip() == "```":
            lineas = lineas[:-1]

        texto = "\n".join(lineas).strip()

    return texto


def obtener_datos_informe_facturacion(pdf):

    imagenes = convertir_pdf_a_imagenes(
        pdf
    )

    resultado = analizar_imagen(
        imagenes,
        PROMPT_INFORME_FACTURACION
    )

    try:

        texto_json = limpiar_bloque_json(
            resultado
        )

        datos = json.loads(
            texto_json
        )

        regimen_facturacion = datos.get(
            "regimen_facturacion",
            []
        )

        if not isinstance(
            regimen_facturacion,
            list
        ):
            regimen_facturacion = []

    except (
        json.JSONDecodeError,
        TypeError,
        AttributeError
    ):

        regimen_facturacion = []

    return {
        "regimen_facturacion": (
            regimen_facturacion
        ),
        "respuesta_gpt": resultado
    }
