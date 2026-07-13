from funciones_pdf import (
    extraer_texto_pagina,
    extraer_contraste_desde_imagen
)
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

def limpiar_espacios(texto):
    return re.sub(r"\s+", " ", texto).strip()

# ==========================
# EXTRACTORES
# ==========================

def extraer_re(texto):
    return buscar(
        r"(RE\d+)",
        texto
    )

def extraer_re_validado(texto_formato_2, texto_formato_3):

    re_formato_2 = extraer_re(texto_formato_2)
    re_formato_3 = extraer_re(texto_formato_3)

    if re_formato_3:
        return re_formato_3

    return re_formato_2

def extraer_niss(texto):

    coincidencia = re.search(
        r"N[°º]?\s*DE\s+SUMINISTRO\s+(\d{6,10})",
        texto,
        re.IGNORECASE
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    return ""


def extraer_reclamante(texto):

    coincidencia = re.search(
        r"NOMBRE DEL SOLICITANTE O REPRESENTANTE"
        r".*?"
        r"Apellido Paterno\s+([A-ZÁÉÍÓÚÑ]+)"
        r".*?"
        r"Apellido Materno\s*([A-ZÁÉÍÓÚÑ]*)"
        r".*?"
        r"Nombres\s+([A-ZÁÉÍÓÚÑ\s]+?)"
        r"\s+N[ÚU]MERO DE DOCUMENTO",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        apellido_paterno = coincidencia.group(1).strip()
        apellido_materno = coincidencia.group(2).strip()
        nombres = limpiar_espacios(
            coincidencia.group(3)
        )

        partes = [
            apellido_paterno,
            apellido_materno,
            nombres
        ]

        return " ".join(
            parte
            for parte in partes
            if parte
        )

    return ""


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

def extraer_canal_atencion(texto):

    coincidencia = re.search(
        r"MODALIDAD DE ATENCI[ÓO]N DE LA SOLICITUD"
        r"\s*\([^)]*\)\s*"
        r"([^\n]+)",
        texto,
        re.IGNORECASE
    )

    modalidad = ""

    if coincidencia:
        modalidad = coincidencia.group(1).strip().upper()

    if (
        "EN PERSONA" in modalidad
        or "VERBAL" in modalidad
        or "PRESENCIAL" in modalidad
    ):
        return "PRESENCIAL"

    if (
        "POR TELEFONO" in modalidad
        or "POR TELÉFONO" in modalidad
        or "TELEFONICO" in modalidad
        or "TELEFÓNICO" in modalidad
    ):
        return "TELEFÓNICO"

    if "VIRTUAL" in modalidad or "WEB" in modalidad:
        return "VIRTUAL"

    # Respaldo usando solo el fundamento.
    fundamento = buscar(
        r"FUNDAMENTO DEL RECLAMO.*?(.*?)RELACIÓN DE PRUEBAS",
        texto
    ).upper()

    if "PRESENCIAL" in fundamento:
        return "PRESENCIAL"

    if "VIRTUAL" in fundamento or "WEB" in fundamento:
        return "VIRTUAL"

    if "TELEFON" in fundamento:
        return "TELEFÓNICO"

    return ""

def extraer_fecha_reclamo(texto):

    # La fecha de presentación aparece al pie del Formato 2.
    coincidencia = re.search(
        r"(\d{2}/\d{2}/\d{4})\s+Fecha\s*$",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    # Respaldo: toma la última fecha encontrada.
    fechas = re.findall(
        r"\b\d{2}/\d{2}/\d{4}\b",
        texto
    )

    if fechas:
        return fechas[-1]

    return ""

def extraer_fecha_audiencia(texto):

    coincidencia = re.search(
        r"CITACI[ÓO]N\s+A\s+REUNI[ÓO]N"
        r".{0,80}?"
        r"FECHA\s+(\d{2}/\d{2}/\d{4})",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    return ""

def extraer_solicita_contraste(texto):

    coincidencia = re.search(
        r"Solicito la realización de la prueba de "
        r"(?:contrastación|contracertificación|contrarrestación)"
        r".{0,500}?"
        r"(Si.{0,120}?No.{0,120}?X|No.{0,120}?X|X.{0,120}?No)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if not coincidencia:
        return ""

    bloque = coincidencia.group(1)

    if re.search(
        r"No\s*X|X\s*No",
        bloque,
        re.IGNORECASE | re.DOTALL
    ):
        return "NO"

    if re.search(
        r"Si\s*X|X\s*Si",
        bloque,
        re.IGNORECASE | re.DOTALL
    ):
        return "SI"

    return ""

def extraer_mes_reclamado(texto):

    coincidencia = re.search(
        r"(?:mes|recibo)\s+de\s+"
        r"([A-ZÁÉÍÓÚÑ]+)\s+"
        r"(?:del\s+)?"
        r"(\d{4})",
        texto,
        re.IGNORECASE
    )

    if coincidencia:
        mes = coincidencia.group(1).upper()
        anio = coincidencia.group(2)

        return f"{mes} {anio}"

    return ""

def extraer_datos_formato_3(texto):

    meses = (
        r"ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|"
        r"JULIO|AGOSTO|SETIEMBRE|SEPTIEMBRE|"
        r"OCTUBRE|NOVIEMBRE|DICIEMBRE"
    )

    # Lee la fila superior de DATOS DE LA FACTURACIÓN.
    coincidencia = re.search(
        rf"DATOS DE LA FACTURACI[ÓO]N"
        rf".*?\b({meses})\b"
        rf"\s+(\d{{4}})"
        rf"\s+\d{{2}}/\d{{2}}/\d{{4}}"
        rf"\s+\w+"
        rf"\s+\d+(?:\.\d+)?"
        rf"\s+(\d+)",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if coincidencia:
        mes = coincidencia.group(1).upper()
        anio = coincidencia.group(2)
        m3 = coincidencia.group(3)

        recibo = {
            "mes": f"{mes} {anio}",
            "m3": m3
        }

        return {
            "mes_reclamado_formato_3": recibo["mes"],
            "m3_reclamado": recibo["m3"],
            "recibos_formato_3": [recibo]
        }

    return {
        "mes_reclamado_formato_3": "",
        "m3_reclamado": "",
        "recibos_formato_3": []
    }

def obtener_datos(texto_formato_2, texto_formato_3):
    
    datos_formato_3 = extraer_datos_formato_3(texto_formato_3)

    datos = {

        # Identificación
        "re": extraer_re_validado(
            texto_formato_2,
            texto_formato_3
        ),

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
        "recibos_formato_3": datos_formato_3["recibos_formato_3"],

        # Audiencia
        "canal_atencion": extraer_canal_atencion(texto_formato_2),
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
        3
    )

    datos = obtener_datos(
        texto_formato_2,
        texto_formato_3
    )

    # Si el texto no permitió reconocer la opción,
    # se hace una lectura visual específica.
    if not datos["solicita_contraste"]:
        datos["solicita_contraste"] = (
            extraer_contraste_desde_imagen(
                pdf_formato_2
            )
        )

    print(datos)

    return datos
