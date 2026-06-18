# funciones_formato_2.py

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

    return datos_formato_2

def determinar_canal_atencion(re):

    if re.startswith("RE111"):
        return "TELEFONICO"

    elif re.startswith("RE211"):
        return "WEB"

    else:
        return ""

def tiene_correo(correo_electronico):

    if correo_electronico.strip() == "":
        return "NO"

    return "SI"
    
def solicita_contraste(opcion):

    if opcion.strip().upper() == "SI":
        return "SI"

    return "NO"
