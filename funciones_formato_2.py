# funciones_formato_2.py

from funciones_pdf import (
    buscar_paginas_documentos,
    extraer_texto_pagina
)

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

    paginas = buscar_paginas_documentos(
        pdf_formato_2
    )

    if paginas["formato_2"] is None:
        return {
            "error": "No se encontró el Formato 2 en el PDF."
        }

    if paginas["formato_3"] is None:
        return {
            "error": "No se encontró el Formato 3 en el PDF."
        }

    print("Páginas encontradas:", paginas)

    texto_formato_2 = extraer_texto_pagina(
        pdf_formato_2,
        paginas["formato_2"]
    )

    texto_formato_3 = extraer_texto_pagina(
        pdf_formato_2,
        paginas["formato_3"]
    )

    print("========== FORMATO 2 ==========")
    print(texto_formato_2)

    print("========== FORMATO 3 ==========")
    print(texto_formato_3)

    return {
        "paginas": paginas,
        "texto_formato_2": texto_formato_2,
        "texto_formato_3": texto_formato_3
    }
