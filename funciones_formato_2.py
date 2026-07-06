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

    coincidencia = re.search(
        r"^\s*([A-ZÁÉÍÓÚÑ]+)\s+([A-ZÁÉÍÓÚÑ]+)\s+NOMBRE DEL SOLICITANTE.*?RAZÓN SOCIAL\s+([A-ZÁÉÍÓÚÑ\s]+?)\s+\d{2}/\d{2}/\d{4}",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        apellido_paterno = coincidencia.group(1).strip()
        apellido_materno = coincidencia.group(2).strip()
        nombres = coincidencia.group(3).strip()

        return f"{apellido_paterno} {apellido_materno} {nombres}"

    return ""

def limpiar_espacios(texto):
    return re.sub(r"\s+", " ", texto).strip()


def extraer_direccion_suministro(texto):

    bloque = buscar(
        r"UBICACIÓN DEL PREDIO\s+(.*?)\s+DOMICILIO PROCESAL",
        texto
    )

    if not bloque:
        return ""

    lineas = [
        linea.strip()
        for linea in bloque.splitlines()
        if linea.strip()
    ]

    direccion = limpiar_espacios(" ".join(lineas))

    return direccion

def extraer_direccion_procesal(texto):

    bloque = buscar(
        r"DOMICILIO PROCESAL\s+(.*?)\s+O\. C\. CALLAO",
        texto
    )

    if not bloque:
        return ""

    lineas = [
        linea.strip()
        for linea in bloque.splitlines()
        if linea.strip()
    ]

    direccion = limpiar_espacios(" ".join(lineas))

    return direccion

def extraer_correo(texto):

    correo = buscar(
        r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        texto
    )

    return correo


def extraer_tiene_correo(texto):

    if extraer_correo(texto):
        return "SI"

    return "NO"

def extraer_tipo_reclamo(texto):

    tipo = buscar(
        r"TIPO DE RECLAMO.*?(Consumo Medido)",
        texto
    )

    return tipo

def extraer_fecha_reclamo(texto):

    fecha = buscar(
        r"RAZÓN SOCIAL.*?(\d{2}/\d{2}/\d{4})",
        texto
    )

    return fecha

def extraer_fecha_audiencia(texto):

    coincidencia = re.search(
        r"FECHA\s+(\d{2}/\d{2}/\d{4})\s+CITACI[ÓO]N\s+A\s+REUNI[ÓO]N",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    return ""

def extraer_solicita_contraste(texto):

    bloque = buscar(
        r"Solicito la realización de la prueba de contrastación.*?(Si\s+No|NO\s+SI|SI\s+NO)",
        texto
    )

    if not bloque:
        return ""

    if re.search(r"No\s+X|X\s+No", texto, re.IGNORECASE):
        return "NO"

    if re.search(r"Si\s+X|X\s+Si", texto, re.IGNORECASE):
        return "SI"

    return ""


def extraer_mes_reclamado(texto):

    coincidencia = re.search(
        r"recibo de\s+([A-ZÁÉÍÓÚÑ]+)\s+(\d{4})",
        texto,
        re.IGNORECASE
    )

    if coincidencia:
        return f"{coincidencia.group(1).upper()} {coincidencia.group(2)}"

    coincidencia = re.search(
        r"mes de\s+([A-ZÁÉÍÓÚÑ]+)\s+del\s+(\d{4})",
        texto,
        re.IGNORECASE
    )

    if coincidencia:
        return f"{coincidencia.group(1).upper()} {coincidencia.group(2)}"

    return ""

def extraer_datos_formato_3(texto):

    coincidencia = re.search(
        r"(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SETIEMBRE|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s+(\d{4}).*?Lectura\s+\d+(?:\.\d+)?\s+(\d+)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        mes = coincidencia.group(1).upper()
        anio = coincidencia.group(2)
        m3 = coincidencia.group(3)

        return {
            "mes_reclamado_formato_3": f"{mes} {anio}",
            "m3_reclamado": m3
        }

    return {
        "mes_reclamado_formato_3": "",
        "m3_reclamado": ""
    }

def obtener_datos(texto_formato_2, texto_formato_3):
    
    datos_formato_3 = extraer_datos_formato_3(texto_formato_3)

    datos = {

        # Identificación
        "re": extraer_re(texto_formato_2),

        "niss": extraer_niss(texto_formato_2),

        # Usuario
        "reclamante": extraer_reclamante(texto_formato_2),
        "fecha_reclamo": extraer_fecha_reclamo(texto_formato_2),
        
        # Direcciones
        "direccion_suministro": extraer_direccion_suministro(texto_formato_2),
        "direccion_procesal": extraer_direccion_procesal(texto_formato_2),

        # Correo
        "tiene_correo": extraer_tiene_correo(texto_formato_2),
        "correo_electronico": extraer_correo(texto_formato_2),

        # Reclamo
        "mes_reclamado": extraer_mes_reclamado(texto_formato_2),
        "mes_reclamado_formato_3": datos_formato_3["mes_reclamado_formato_3"],
        "m3_reclamado": datos_formato_3["m3_reclamado"],

        # Audiencia
        "canal_atencion": "",
        "fecha_audiencia": extraer_fecha_audiencia(texto_formato_2),

        # Contraste
        "solicita_contraste": extraer_solicita_contraste(texto_formato_2),
    
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
