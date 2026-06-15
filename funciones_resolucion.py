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


def generar_considerando_1(datos_inspeccion):

    inicio_gpt = time.time()

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un especialista en resoluciones de reclamos comerciales de Sedapal.

Tu tarea es redactar únicamente el Considerando Primero.

Utiliza exclusivamente la información proporcionada.

No inventes información.

Prohibido inferir hechos no expresamente indicados.

Prohibido completar información faltante.

Prohibido asumir distribución de pisos o viviendas.

Redacta en un solo párrafo y con lenguaje administrativo.

Debes seguir el estilo utilizado por el Equipo Comercial Callao.

Si se realizó inspección interna y externa, indícalo expresamente.

Si la inspección interna no se realizó, precisa la razón correspondiente.

Describe las unidades de uso ocupadas y desocupadas.

Si existen unidades domésticas y comerciales, señala que se trata de un predio mixto.

Si existe una sola unidad doméstica ocupada y no existen otras unidades, señala que se trata de un predio unifamiliar.

Incorpora las observaciones encontradas durante la inspección.

Menciona el número del medidor y la lectura registrada al momento de la inspección.

Si existe fuga en caja, indícalo expresamente.

No cites normas.

No emitas conclusiones.

No indiques si el reclamo es fundado o infundado.

Devuelve únicamente el texto del Considerando Primero.
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
