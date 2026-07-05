# funciones_formato_2.py

from funciones_pdf import extraer_texto_pagina


def obtener_datos_formato_2(pdf_formato_2):

    texto_formato_2 = extraer_texto_pagina(
        pdf_formato_2,
        0
    )

    texto_formato_3 = extraer_texto_pagina(
        pdf_formato_2,
        2
    )

    print("========== FORMATO 2 ==========")
    print(texto_formato_2)

    print("========== FORMATO 3 ==========")
    print(texto_formato_3)

    return {
        "texto_formato_2": texto_formato_2,
        "texto_formato_3": texto_formato_3
    }
