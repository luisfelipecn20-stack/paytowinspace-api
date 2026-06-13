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
        "asistio_audiencia": True,
        "hubo_acuerdo": False,

        # RESULTADO
        "resultado": "INFUNDADO"

    }

    return expediente


def generar_considerando_1(datos_inspeccion):

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

    return respuesta.choices[0].message.content
