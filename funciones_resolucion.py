from openai import OpenAI
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def crear_expediente_maestro():

    expediente = {

        # RESOLUCIÓN
        "numero_resolucion": "",
        "fecha_resolucion": "",

        # USUARIO
        "suministro": "",
        "reclamante": "",
        "sexo_reclamante": "",

        # DIRECCIONES
        "direccion_suministro": "",
        "direccion_procesal": "",
        "correo_autorizado": False,

        # FORMATO 2
        "direccion_formato_2": "",
        "correo_formato_2": "",

        # FORMATO 4
        "existe_formato_4": False,
        "direccion_formato_4": "",
        "correo_formato_4": "",

        # RECLAMO
        "codigo_reclamo": "",
        "medio_presentacion": "",
        "tipo_reclamo": "",
        "fecha_reclamo": "",
        "meses_reclamados": [],

        # INSPECCIÓN
        "fecha_inspeccion": "",
        "medidor": "",
        "lectura_actual": "",
        "fuga_caja": "",
        "ocupacion_predio": "",
        "unidades_domesticas": 0,
        "unidades_comerciales": 0,
        "unidades_industriales": 0,
        "unidades_estatales": 0,
        "observaciones_inspeccion": "",

        # FACTURACIÓN
        "volumen_real": "",
        "lecturas_historicas": [],

        # AUDIENCIA
        "fecha_audiencia": "",
        "hubo_audiencia": False,
        "asistio_audiencia": True,
        "hubo_acuerdo": False,

        # REGLAS DE REDACCIÓN
        "tipo_predio": "",
        "texto_mes": "",
        "texto_usuario": "",
        "texto_notificacion": "",

        # RESULTADO
        "resultado": "INFUNDADO"

    }

    return expediente


def determinar_tipo_predio(
        unidades_domesticas,
        unidades_comerciales,
        unidades_industriales,
        unidades_estatales):

    total_unidades = (
        unidades_domesticas
        + unidades_comerciales
        + unidades_industriales
        + unidades_estatales
    )

    if (
        unidades_domesticas == 1
        and unidades_comerciales == 0
        and unidades_industriales == 0
        and unidades_estatales == 0
    ):
        return "UNIFAMILIAR"

    if (
        unidades_domesticas > 0
        and (
            unidades_comerciales > 0
            or unidades_industriales > 0
            or unidades_estatales > 0
        )
    ):
        return "MIXTO"

    if total_unidades > 1:
        return "MULTIFAMILIAR"

    return ""


def determinar_texto_mes(
        cantidad_meses):

    if cantidad_meses == 1:
        return "mes cuestionado"

    return "meses cuestionados"


def determinar_texto_audiencia(
        hubo_acuerdo):

    if hubo_acuerdo:
        return (
            "habiéndose arribado a una fórmula de solución "
            "al reclamo por acuerdo entre las partes."
        )

    return (
        "no habiéndose llegado a ninguna fórmula de solución "
        "al reclamo, por falta de consenso entre las partes, "
        "continuando con el proceso de reclamo en la vía administrativa."
    )


import time
from datetime import datetime

def generar_considerando_1(datos_inspeccion):

    inicio_gpt = time.time()

    # Normalizar lectura
    lectura = datos_inspeccion.get("lec")

    if isinstance(lectura, float) and lectura.is_integer():
        datos_inspeccion["lec"] = int(lectura)

    # Normalizar fecha
    fecha = datos_inspeccion.get("fec_vis")

    if fecha:

        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(
                fecha.replace("Z", "")
            )

        datos_inspeccion["fec_vis"] = fecha.strftime("%d/%m/%Y")

    # Determinar estado de fuga
    observacion = datos_inspeccion.get("observ", "").upper()

    if "NO REGISTRA CONSUMO" in observacion:
        datos_inspeccion["estado_fuga"] = "SIN FUGA"

    elif "FUGA" in observacion:
        datos_inspeccion["estado_fuga"] = "CON FUGA"

    else:
        datos_inspeccion["estado_fuga"] = ""
    
    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un especialista en resoluciones de reclamos comerciales de Sedapal perteneciente al Equipo Comercial Callao.

Tu tarea es redactar únicamente el Considerando Primero.

Debes imitar el estilo utilizado por el Equipo Comercial Callao.

La redacción debe realizarse en un solo párrafo y con lenguaje administrativo.

Debes utilizar exclusivamente la información proporcionada.

No inventes información.

No infieras hechos no expresamente indicados.

No completes información faltante.

No asumas distribución de pisos, ambientes, viviendas o niveles.

No agregues detalles que no aparezcan en los datos recibidos.

No cites normas.

No emitas conclusiones.

No indiques si el reclamo es fundado o infundado.

No hagas recomendaciones.

No menciones aspectos que correspondan a otros considerandos.

Devuelve únicamente el texto del Considerando Primero.

La redacción debe iniciar obligatoriamente con:

"Con fecha ... se llevó a cabo la inspección ..."

La fecha debe expresarse obligatoriamente en formato DD/MM/AAAA.

No debes utilizar expresiones como:

"29 de junio de 2026"

"29 de mayo de 2026"

Debes conservar exactamente la fecha recibida y expresarla únicamente en formato numérico.

Si se realizó inspección interna y externa, debes indicar:

"se llevó a cabo la inspección interna y externa al predio"

Si solo se realizó inspección externa, debes indicar:

"se llevó a cabo la inspección externa al predio"

Luego debes señalar que:

"se verificó que la caja de control de la conexión domiciliaria de agua potable se encuentra vigente en buen estado"

Si existe fuga en caja debes indicar:

"y con fuga de agua"

Si no existe fuga en caja debes indicar:

"y sin fuga de agua"

Debes indicar:

"Que el medidor (número de medidor) registra al momento de la inspección la lectura de (lectura) m3."

No utilices expresiones como:

"habiéndose registrado un número de medidor"

o similares.

Cuando corresponda, utiliza las siguientes expresiones:

* "la conexión domiciliaria abastece a un predio unifamiliar"
* "la conexión domiciliaria abastece a un predio multifamiliar"
* "la conexión domiciliaria abastece a un predio mixto"
* "la conexión domiciliaria abastece a un predio comercial en actividad"
* "la conexión domiciliaria abastece a un predio doméstico desocupado"

Si existen unidades ocupadas y desocupadas, debes describirlas siguiendo el estilo:

"conformado por 01 doméstico habitado, 03 comerciales en actividad y 01 doméstico desocupado"

o

"conformado por 06 unidades de uso doméstico habitadas"

o

"conformado por 01 doméstico habitado y 01 comercial en actividad"

No inventes cantidades.

Si no existen datos suficientes, omite la descripción de las unidades.

Respecto a las instalaciones internas, no debes describir pruebas hidráulicas ni copiar literalmente las observaciones.

Debes incorporar el estado de fuga consignado en el campo "estado_fuga".

Si el campo "estado_fuga" contiene:

"SIN FUGA"

debes incorporar expresamente la frase:

"sin fuga".

Si el campo "estado_fuga" contiene:

"CON FUGA"

debes incorporar expresamente la frase:

"con fuga".

La conclusión sobre la existencia o inexistencia de fuga es obligatoria y no debe omitirse.

No debes describir pruebas hidráulicas.

No debes copiar literalmente las observaciones.

No debes precisar el lugar específico de la fuga.

La expresión "sin fuga" o "con fuga" debe aparecer en el Considerando Primero aun cuando las observaciones hayan sido resumidas.

La frase "sin fuga" o "con fuga" debe incorporarse al final del párrafo correspondiente a la inspección interna.

No debes omitir dicha conclusión bajo ninguna circunstancia.

Si el campo "estado_fuga" está vacío, no debes hacer referencia a las instalaciones internas.

No utilices expresiones como:

"cerrando todos los puntos de agua"

"el medidor no registra consumo"

"no se detectó fuga de agua en las instalaciones internas"

"fuga en inodoro"

"fuga en válvula"

"fuga en tanque"

Debes resumir dichas situaciones únicamente como:

"sin fuga"

o

"con fuga"

según corresponda.

Si la inspección interna no se realizó, debes indicar expresamente la causa consignada en la información recibida, por ejemplo:

* "por ausencia del reclamante"
* "por oposición del reclamante"
* "por ausencia de la reclamante"
* "por oposición de la reclamante"

Debes incorporar las observaciones encontradas durante la inspección únicamente si aparecen expresamente en la información recibida.

No reformules innecesariamente.

La estructura y redacción deben ser similares a las resoluciones emitidas por el Equipo Comercial Callao.

"""
            },
            {
                "role": "user",
                "content": str(datos_inspeccion)
            }
        ]
    )

    print(
        "Tiempo OpenAI:",
        round(time.time() - inicio_gpt, 2),
        "segundos"
    )

    return respuesta.choices[0].message.content
