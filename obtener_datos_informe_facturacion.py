from funciones_pdf import convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from prompt_informe_facturacion import PROMPT_INFORME_FACTURACION

    def obtener_datos_informe_facturacion(pdf):

    imagenes = convertir_pdf_a_imagenes(
        pdf
    )

    resultado = analizar_imagen(
        imagenes,
        PROMPT_INFORME_FACTURACION
    )

    return {
        "respuesta_gpt": resultado
    }
