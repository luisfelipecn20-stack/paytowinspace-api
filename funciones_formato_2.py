from funciones_pdf import (
    extraer_texto_pagina,
    extraer_campos_visuales_formato_2,
    pagina_es_escaneada
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

def extraer_re_validado(
    texto_formato_2,
    texto_recibos,
    texto_formato_3
):

    valores = [
        extraer_re(texto_formato_2),
        extraer_re(texto_recibos),
        extraer_re(texto_formato_3)
    ]

    valores = [
        valor
        for valor in valores
        if valor
    ]

    if not valores:
        return ""

    return max(
        valores,
        key=valores.count
    )
    
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

    bloque = buscar(
        r"NOMBRE DEL SOLICITANTE O REPRESENTANTE"
        r"(.*?)"
        r"N[ÚU]MERO DE DOCUMENTO",
        texto
    )

    if not bloque:
        return ""

    lineas = [
        linea.strip()
        for linea in bloque.splitlines()
        if linea.strip()
    ]

    # Caso de PDF con texto nativo:
    # APELLIDO PATERNO | APELLIDO MATERNO | NOMBRES
    for linea in lineas:

        linea_mayuscula = linea.upper()

        if (
            "APELLIDO PATERNO" in linea_mayuscula
            or "APELLIDO MATERNO" in linea_mayuscula
            or "NOMBRES" in linea_mayuscula
            or "TELÉFONO" in linea_mayuscula
            or "TELEFONO" in linea_mayuscula
        ):
            continue

        columnas = re.split(
            r"[ \t]{2,}",
            linea
        )

        columnas = [
            limpiar_espacios(columna)
            for columna in columnas
            if limpiar_espacios(columna)
        ]

        if len(columnas) >= 3:

            apellido_paterno = columnas[0]
            apellido_materno = columnas[1]
            nombres = columnas[2]

            return " ".join([
                apellido_paterno,
                apellido_materno,
                nombres
            ])

    # Caso de PDF escaneado: los dos apellidos aparecen
    # juntos antes de las etiquetas del formulario.
    for linea in lineas:

        linea_mayuscula = linea.upper()

        if (
            "APELLIDO" in linea_mayuscula
            or "TELÉFONO" in linea_mayuscula
            or "TELEFONO" in linea_mayuscula
        ):
            continue

        columnas = re.split(
            r"[ \t]{2,}",
            linea
        )

        columnas = [
            limpiar_espacios(columna)
            for columna in columnas
            if limpiar_espacios(columna)
        ]

        if len(columnas) == 2:

            coincidencia_nombres = re.search(
                r"\bNombres\s+"
                r"([A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+)*)",
                bloque,
                re.IGNORECASE
            )

            if coincidencia_nombres:

                apellido_paterno = columnas[0]
                apellido_materno = columnas[1]

                nombres = limpiar_espacios(
                    coincidencia_nombres.group(1)
                )

                return " ".join([
                    apellido_paterno,
                    apellido_materno,
                    nombres
                ])

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

    coincidencia = re.search(
        r"DOMICILIO PROCESAL\s+"
        r"(.*?)"
        r"(?="
        r"\s+C[oó]digo Postal|"
        r"\s+\d{9}\b|"
        r"\s+[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|"
        r"\s+Tel[eé]fono\s*/\s*Celular|"
        r"\s+DECLARACI[ÓO]N DEL RECLAMANTE"
        r")",
        texto,
        re.IGNORECASE | re.DOTALL
    )

    if not coincidencia:
        return ""

    direccion = coincidencia.group(1)

    # Elimina las etiquetas impresas del formulario,
    # pero conserva los valores de la dirección.
    etiquetas = [
        r"\(Calle,\s*Jir[oó]n,\s*Avenida\)",
        r"\(Urbanizaci[oó]n,\s*[Bb]arrio\)",
        r"\bN[°º]?\b",
        r"\bMz\b",
        r"\bLote\b",
        r"\bProvincia\b",
        r"\bDistrito\b"
    ]

    for etiqueta in etiquetas:
        direccion = re.sub(
            etiqueta,
            " ",
            direccion,
            flags=re.IGNORECASE
        )

    return limpiar_espacios(direccion)

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

def extraer_meses_reclamados(texto_formato_2, texto_recibos):

    meses = (
        r"ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|"
        r"JULIO|AGOSTO|SETIEMBRE|SEPTIEMBRE|"
        r"OCTUBRE|NOVIEMBRE|DICIEMBRE"
    )

    coincidencias = re.findall(
        rf"\b({meses})\b\s+(\d{{4}})\s+\d+(?:[.,]\d+)?",
        texto_recibos,
        re.IGNORECASE
    )

    meses_reclamados = []

    for mes, anio in coincidencias:

        periodo = f"{mes.upper()} {anio}"

        if periodo not in meses_reclamados:
            meses_reclamados.append(periodo)

        # Por ahora, PEIAD procesará como máximo tres meses.
        if len(meses_reclamados) == 3:
            break

    if meses_reclamados:
        return meses_reclamados

    # Respaldo para expedientes con un solo mes.
    mes_formato_2 = extraer_mes_reclamado(texto_formato_2)

    if mes_formato_2:
        return [mes_formato_2]

    return []

def extraer_datos_formato_3(
    texto,
    meses_reclamados
):

    meses = (
        r"ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|"
        r"JULIO|AGOSTO|SETIEMBRE|SEPTIEMBRE|"
        r"OCTUBRE|NOVIEMBRE|DICIEMBRE"
    )

    patron_fila = re.compile(
        rf"\b\d+\s+"
        rf"({meses})\s+"
        rf"(\d{{4}})\s+"
        rf".*?"
        rf"\d{{2}}/\d{{2}}/\d{{4}}\s+"
        rf"(?:Lectura|Promedio|Asignado|CM)\s+"
        rf"\d+(?:[.,]\d+)?\s+"
        rf"(\d+)\b",
        re.IGNORECASE
    )

    recibos_encontrados = {}

    for coincidencia in patron_fila.finditer(texto):

        mes = coincidencia.group(1).upper()
        anio = coincidencia.group(2)
        m3 = coincidencia.group(3)

        periodo = f"{mes} {anio}"

        recibos_encontrados[periodo] = {
            "mes": periodo,
            "m3": m3
        }

    recibos_reclamados = []

    for periodo in meses_reclamados:

        if periodo in recibos_encontrados:
            recibos_reclamados.append(
                recibos_encontrados[periodo]
            )
        else:
            recibos_reclamados.append({
                "mes": periodo,
                "m3": ""
            })

    if recibos_reclamados:
        primer_recibo = recibos_reclamados[0]

        return {
            "mes_reclamado_formato_3": primer_recibo["mes"],
            "m3_reclamado": primer_recibo["m3"],
            "recibos_formato_3": recibos_reclamados
        }

    return {
        "mes_reclamado_formato_3": "",
        "m3_reclamado": "",
        "recibos_formato_3": []
    }

def obtener_datos(
    texto_formato_2,
    texto_recibos,
    texto_formato_3
):

    meses_reclamados = extraer_meses_reclamados(
        texto_formato_2,
        texto_recibos
    )

    datos_formato_3 = extraer_datos_formato_3(
        texto_formato_3,
        meses_reclamados
    )

    datos = {

        # Identificación
        "re": extraer_re_validado(
            texto_formato_2,
            texto_recibos,
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
        "mes_reclamado": (
        meses_reclamados[0]
        if meses_reclamados
        else ""
        ),

        "meses_reclamados": meses_reclamados,
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
        "texto_recibos_reclamados": texto_recibos,
        "texto_formato_3": texto_formato_3

    }

    return datos

def obtener_datos_formato_2(pdf_formato_2):

    # Determina si la primera página contiene texto digital
    # o si corresponde a un documento escaneado.
    es_escaneado = pagina_es_escaneada(
        pdf_formato_2,
        0
    )

    # Página 1: Formato 2
    texto_formato_2 = extraer_texto_pagina(
        pdf_formato_2,
        0
    )

    # Página 3: lista de recibos reclamados
    texto_recibos = extraer_texto_pagina(
        pdf_formato_2,
        2
    )

    # Página 4: Formato 3
    texto_formato_3 = extraer_texto_pagina(
        pdf_formato_2,
        3
    )

    datos = obtener_datos(
        texto_formato_2,
        texto_recibos,
        texto_formato_3
    )

    campos_visuales_necesarios = [
        "niss",
        "reclamante",
        "direccion_suministro",
        "direccion_procesal",
        "solicita_contraste"
    ]

    debe_usar_vision = (
        es_escaneado
        or any(
            not datos.get(campo)
            for campo in campos_visuales_necesarios
        )
    )

    if debe_usar_vision:

        campos_visuales = extraer_campos_visuales_formato_2(
            pdf_formato_2
        )

        # NISS: Vision solo completa si el OCR no lo obtuvo.
        if (
            not datos.get("niss")
            and campos_visuales.get("niss")
        ):
            datos["niss"] = campos_visuales["niss"]

        # En documentos escaneados, Vision estructurada
        # tiene prioridad para reclamante y direcciones.
        if es_escaneado:

            for campo in [
                "reclamante",
                "direccion_suministro",
                "direccion_procesal"
            ]:

                valor_visual = campos_visuales.get(
                    campo,
                    ""
                )

                if valor_visual:
                    datos[campo] = valor_visual

        # En documentos digitales, Vision únicamente
        # completa reclamante o direcciones vacías.
        else:

            for campo in [
                "reclamante",
                "direccion_suministro",
                "direccion_procesal"
            ]:

                if (
                    not datos.get(campo)
                    and campos_visuales.get(campo)
                ):
                    datos[campo] = campos_visuales[campo]

        # El contraste obtenido por regex nunca se reemplaza.
        # Vision solo se utiliza cuando está vacío.
        if (
            not datos.get("solicita_contraste")
            and campos_visuales.get("solicita_contraste")
        ):
            datos["solicita_contraste"] = (
                campos_visuales["solicita_contraste"]
            )

    print(datos)

    return datos
