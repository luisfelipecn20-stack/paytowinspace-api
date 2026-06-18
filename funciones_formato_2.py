# funciones_formato_2.py
import json

from funciones_pdf import convertir_pdf_a_imagenes
from funciones_vision import analizar_imagen
from prompt_formato_2 import PROMPT_FORMATO_2

def obtener_datos_formato_2(pdf_formato_2):

    datos_formato_2 = {
        
        # Identificación del expediente
        "re": "",
        "niss": "",

        # Usuario
        "reclamante": "",

        # Direcciones
        "direccion_suministro": "",
        "direccion_procesal": "",

        # Correo electrónico
        "tiene_correo": "",
        "correo_electronico": "",

        # Reclamo
        "tipo_reclamo": "",
        "mes_reclamado": "",

        # Canal de atención
        "canal_atencion": "",

        # Audiencia
        "fecha_audiencia": "",

        # Contraste
        "solicita_contraste": ""

    }

    imagenes = convertir_pdf_a_imagenes(
        pdf_formato_2
    )

    resultado = analizar_imagen(
        imagenes[:8],
        PROMPT_FORMATO_2
    )    

    print(resultado)

    return {
        "respuesta_gpt": resultado
    }

def tiene_correo(correo_electronico):

    if correo_electronico.strip() == "":
        return "NO"

    return "SI"


def solicita_contraste(opcion):

    if opcion.strip().upper() == "SI":
        return "SI"

    return "NO"
