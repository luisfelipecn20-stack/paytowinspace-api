from funciones_pdf import (
    extraer_texto_pagina,
    extraer_campos_visuales_formato_2,
    pagina_es_escaneada,
    contar_paginas_pdf
)

from funciones_visto import generar_visto

import re
import unicodedata

TIPOLOGIAS_RECLAMO = {
    "CR118": "Asignación de consumo",
    "CR120": "Conceptos emitidos",
    "CR129": "Consumo Atribuible a Otro Suministro",
    "CR128": "Consumo Atribuible a Usuario Anterior del Suministro",
    "CR125": "Consumo Medido",
    "CR132": "Consumo Medido - Desproporcional",
    "CR126": "Consumo No Facturado Oportunamente",
    "CR127": "Consumo No Realizado por Servicio Cerrado",
    "CR102": "Consumo por promedio",
    "CR137": "F.P. Categoría de Usuario",
    "CR139": "F.P. Consumo no realizado",
    "CR138": "F.P. Importe Facturado por el Servicio",
    "CR136": "F.P. VAF (Volumen de Agua Facturado - m³)",
    "CR123": "Número de Unidades de Uso",
    "CR106": "Pagos no procesados",
    "CR130": "Tipo de Tarifa",
    "CR151": "Uso de la Red de Desagüe",
    "CR134": "VMA - Cargo por suspensión y reapertura",
    "CR133": "VMA - Conceptos por prueba, análisis y laboratorio",
    "CR180": "VMA - Factor de ajuste",
    "CR181": "VMA - Factor de ajuste e importe de alcantarillado",
    "CR135": "VMA - Importe por Alcantarillado"
}

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

def normalizar_texto(texto):
    texto = unicodedata.normalize(
        "NFD",
        texto or ""
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return limpiar_espacios(texto).upper()

def extraer_recibos_y_formato_3(pdf):

    total_paginas = contar_paginas_pdf(pdf)

    texto_recibos = ""
    texto_formato_3 = ""

    # Índices 2 a 5 equivalen a las páginas 3 a 6.
    limite = min(
        total_paginas,
        6
    )

    for indice in range(2, limite):

        texto_pagina = extraer_texto_pagina(
            pdf,
            indice
        )

        texto_normalizado = normalizar_texto(
            texto_pagina
        )

        if (
            not texto_recibos
            and "RECIBOS RECLAMADOS" in texto_normalizado
        ):
            texto_recibos = texto_pagina

        if (
            not texto_formato_3
            and "FORMATO 3" in texto_normalizado
            and "DATOS DE LA FACTURACION" in texto_normalizado
        ):
            texto_formato_3 = texto_pagina

        # Se detiene inmediatamente cuando encuentra ambos.
        if texto_recibos and texto_formato_3:
            break

    return texto_recibos, texto_formato_3

def limpiar_direccion(direccion):
    if not direccion:
        return ""

    direccion = limpiar_espacios(direccion)

    # Eliminar encabezados correspondientes a las columnas del formulario
    direccion = re.sub(
        r"\(\s*Calle\s*,?\s*Jir[oó]n\s*,?\s*Avenida\s*\)"
        r"\s*N[°º]?\s*Mz\s*Lote",
        " ",
        direccion,
        flags=re.IGNORECASE
    )

    direccion = re.sub(
        r"\(\s*Urbanizaci[oó]n\s*,?\s*Barrio\s*\)"
        r"\s*Provincia\s*Distrito",
        " ",
        direccion,
        flags=re.IGNORECASE
    )

    # Respaldo por si las etiquetas aparecen separadas
    direccion = re.sub(
        r"\(\s*Calle\s*,?\s*Jir[oó]n\s*,?\s*Avenida\s*\)",
        " ",
        direccion,
        flags=re.IGNORECASE
    )

    direccion = re.sub(
        r"\(\s*Urbanizaci[oó]n\s*,?\s*Barrio\s*\)",
        " ",
        direccion,
        flags=re.IGNORECASE
    )

    direccion = re.sub(
        r"\bProvincia\b|\bDistrito\b",
        " ",
        direccion,
        flags=re.IGNORECASE
    )

    # Eliminar símbolo suelto producido por N°
    direccion = re.sub(r"(?<!\w)[°º](?!\w)", " ", direccion)

    # Eliminar correos capturados accidentalmente
    direccion = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        " ",
        direccion
    )

    # Eliminar teléfonos o códigos capturados al final
    direccion = re.sub(
        r"\s+\d{6,}(?:\s*/\s*\d{6,})*\s*$",
        "",
        direccion
    )

    return limpiar_espacios(direccion)

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

    re_formato_2 = extraer_re(
        texto_formato_2
    )

    re_recibos = extraer_re(
        texto_recibos
    )

    re_formato_3 = extraer_re(
        texto_formato_3
    )

    valores = [
        valor
        for valor in [
            re_formato_2,
            re_recibos,
            re_formato_3
        ]
        if valor
    ]

    if not valores:
        return ""

    # Si un RE aparece dos o más veces,
    # se considera validado por mayoría.
    for valor in valores:

        if valores.count(valor) >= 2:
            return valor

    # Si no existe mayoría, se prioriza la lista
    # de Recibos Reclamados por ser más legible.
    if re_recibos:
        return re_recibos

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

    # Respaldo para OCR escaneado cuando todo el nombre
    # aparece en una línea antes de las tres etiquetas.
    coincidencia_fila_completa = re.search(
        r"^\s*"
        r"([A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+)+)"
        r"\s*$"
        r"\s*Apellido Paterno"
        r"\s+Apellido Materno"
        r"\s+Nombres",
        bloque,
        re.IGNORECASE | re.MULTILINE
    )

    if coincidencia_fila_completa:
        return limpiar_espacios(
            coincidencia_fila_completa.group(1)
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

    return limpiar_direccion(direccion)

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

    return limpiar_direccion(direccion)

def extraer_correo(texto):

    # Elimina tildes introducidas por el OCR.
    texto_sin_tildes = unicodedata.normalize(
        "NFD",
        texto or ""
    )

    texto_sin_tildes = "".join(
        caracter
        for caracter in texto_sin_tildes
        if unicodedata.category(caracter) != "Mn"
    )

    correo = buscar(
        r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
        texto_sin_tildes
    )

    return correo.lower()

def extraer_tiene_correo(texto):

    if extraer_correo(texto):
        return "SI"

    return "NO"

def extraer_tipo_reclamo(texto):

    bloque = buscar(
        r"TIPO DE RECLAMO"
        r"(.*?)"
        r"BREVE DESCRIPCI[ÓO]N",
        texto
    )

    if not bloque:
        return ""

    bloque_normalizado = normalizar_texto(bloque)

    # Se revisan primero los nombres más largos para evitar
    # confundir Consumo Medido - Desproporcional con Consumo Medido.
    tipologias_ordenadas = sorted(
        TIPOLOGIAS_RECLAMO.items(),
        key=lambda elemento: len(elemento[1]),
        reverse=True
    )

    for codigo, nombre in tipologias_ordenadas:

        if normalizar_texto(nombre) in bloque_normalizado:
            return nombre

    return ""

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

    def validar_fecha_numerica(valor):

        partes = valor.split("/")

        if len(partes) != 3:
            return ""

        try:
            dia = int(partes[0])
            mes = int(partes[1])
            anio = int(partes[2])
        except ValueError:
            return ""

        if not 1 <= dia <= 31:
            return ""

        if not 1 <= mes <= 12:
            return ""

        return f"{dia:02d}/{mes:02d}/{anio:04d}"

    meses_numero = {
        "ENE": "01",
        "FEB": "02",
        "MAR": "03",
        "ABR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AGO": "08",
        "SET": "09",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DIC": "12"
    }

    # Localiza la sección final del Formato 2.
    marcas_firma = list(
        re.finditer(
            r"(?:Firma|Firm[eé])\s+del Reclamante"
            r"|Huella digital",
            texto,
            re.IGNORECASE
        )
    )

    if marcas_firma:

        inicio = max(
            0,
            marcas_firma[-1].start() - 300
        )

        bloque_fecha = texto[inicio:]

    else:
        # Respaldo: revisa únicamente el tramo final.
        bloque_fecha = texto[-1200:]

    candidatos = []

    # Fechas numéricas ubicadas en el pie.
    for coincidencia in re.finditer(
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        bloque_fecha
    ):

        # Revisa solamente el texto situado desde
        # la fecha numérica anterior.
        inicio_contexto = max(
            0,
            coincidencia.start() - 200
        )

        contexto_previo = bloque_fecha[
            inicio_contexto:coincidencia.start()
        ]

        fechas_previas = list(
            re.finditer(
                r"\b\d{1,2}/\d{1,2}/\d{4}\b",
                contexto_previo
            )
        )

        if fechas_previas:
            contexto_previo = contexto_previo[
                fechas_previas[-1].end():
            ]

        contexto_normalizado = normalizar_texto(
            contexto_previo
        )

        etiquetas_excluidas = [
            "FECHA MAXIMA DE NOTIFICACION",
            "CITACION A REUNION",
            "INSPECCION INTERNA Y EXTERNA"
        ]

        if any(
            etiqueta in contexto_normalizado
            for etiqueta in etiquetas_excluidas
        ):
            continue

        fecha = validar_fecha_numerica(
            coincidencia.group(0)
        )

        if fecha:
            candidatos.append((
                coincidencia.start(),
                fecha
            ))

    # Fechas con mes abreviado ubicadas en el pie.
    for coincidencia in re.finditer(
        r"\b(0?[1-9]|[12]\d|3[01])\s+"
        r"(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SET|SEP|OCT|NOV|DIC)"
        r"\.?\s+"
        r"(\d{4})\b",
        bloque_fecha,
        re.IGNORECASE
    ):

        dia = int(coincidencia.group(1))
        mes = meses_numero[
            coincidencia.group(2).upper()
        ]
        anio = coincidencia.group(3)

        fecha = f"{dia:02d}/{mes}/{anio}"

        candidatos.append((
            coincidencia.start(),
            fecha
        ))

    if candidatos:

        # Utiliza la última fecha válida encontrada
        # dentro de la sección de firma.
        return max(
            candidatos,
            key=lambda elemento: elemento[0]
        )[1]

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
        rf"(?:"
        rf"Lectura|"
        rf"Promedio|"
        rf"Asignado|"
        rf"Asignaci[oó]n|"
        rf"Asig\.?\s*Consumo|"
        rf"CM"
        rf")\s+"
        rf"\d+(?:[.,]\d+)?\s+"
        rf"(\d+(?:[.,]\d+)?)\b",
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

    tipo_reclamo = extraer_tipo_reclamo(
        texto_formato_2
    )

    codigo_tipo_reclamo = next(
        (
            codigo
            for codigo, nombre in TIPOLOGIAS_RECLAMO.items()
            if nombre == tipo_reclamo
        ),
        ""
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
        "codigo_tipo_reclamo": codigo_tipo_reclamo,
        "tipo_reclamo": tipo_reclamo,

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

    # Busca Recibos Reclamados y Formato 3
    # entre las páginas 3 y 6.
    texto_recibos, texto_formato_3 = (
        extraer_recibos_y_formato_3(
            pdf_formato_2
        )
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

            # En documentos escaneados, Vision tiene
            # prioridad para obtener el reclamante completo.
            if campos_visuales.get("reclamante"):
                datos["reclamante"] = (
                    campos_visuales["reclamante"]
                )

            # Las direcciones visuales siguen teniendo
            # prioridad temporalmente en los escaneados.
            for campo in [
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

        # En documentos escaneados, Vision tiene prioridad
        # para determinar visualmente dónde está la X.
        if (
            campos_visuales.get("solicita_contraste")
            and (
                es_escaneado
                or not datos.get("solicita_contraste")
            )
        ):
            datos["solicita_contraste"] = (
                campos_visuales["solicita_contraste"]
            )

    datos["reclamante"] = limpiar_espacios(
        datos.get("reclamante", "")
    ).upper()

    datos["direccion_suministro"] = limpiar_direccion(
        datos.get("direccion_suministro", "")
    )

    datos["direccion_procesal"] = limpiar_direccion(
        datos.get("direccion_procesal", "")
    )

    datos["visto"] = generar_visto(
        datos
    )
    
    print(datos)

    return datos
