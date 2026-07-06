from funciones_pdf import extraer_texto_pagina
import re


def buscar(patron, texto):

    coincidencia = re.search(
        patron,
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    return ""


# ==========================
# EXTRACTORES
# ==========================

def extraer_re(texto):
    return buscar(
        r"(RE\d+)",
        texto
    )


def extraer_niss(texto):
    return buscar(
        r"N° DE SUMINISTRO\s+CÓDIGO DE RECLAMO N°:\s+RE\d+\s+(\d+)",
        texto
    )


def extraer_reclamante(texto):
    return buscar(
        r"Apellido Paterno\s+Apellido Materno\s+Nombres\s+([A-ZÁÉÍÓÚÑ\s]+?)\s+X",
        texto
    )


def obtener_datos(texto_formato_2, texto_formato_3):

    datos = {

        # Identificación
        "re": extraer_re(texto_formato_2),

        "niss": extraer_niss(texto_formato_2),

        # Usuario
        "reclamante": extraer_reclamante(texto_formato_2),

        # Direcciones
        "direccion_suministro": "",
        "direccion_procesal": "",

        # Correo
        "tiene_correo": "",
        "correo_electronico": "",

        # Reclamo
        "tipo_reclamo": "",

        # Formato 3
        "mes_reclamado": "",
        "m3_reclamado": "",

        # Audiencia
        "canal_atencion": "",
        "fecha_audiencia": "",

        # Contraste
        "solicita_contraste": "",

        # Temporal (para depuración)
        "texto_formato_2": texto_formato_2,
        "texto_formato_3": texto_formato_3

    }

    return datos


def obtener_datos_formato_2(pdf_formato_2):

    texto_formato_2 = extraer_texto_pagina(
        pdf_formato_2,
        0
    )

    texto_formato_3 = extraer_texto_pagina(
        pdf_formato_2,
        2
    )

    datos = obtener_datos(
        texto_formato_2,
        texto_formato_3
    )

    print(datos)

    return datos
