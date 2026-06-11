from openai import OpenAI
import base64
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analizar_imagen(imagen_png):

    imagen_base64 = base64.b64encode(imagen_png).decode("utf-8")

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un experto en análisis de actas de inspección de Sedapal.

IMPORTANTE:

- Analiza cuidadosamente tanto el texto impreso como las anotaciones manuscritas.
- Da prioridad a la información escrita a mano cuando exista.
- Revisa casillas marcadas, observaciones, tablas y notas del inspector.
- Si existe contradicción entre texto impreso y manuscrito, prioriza la anotación manuscrita.
- No inventes información.
- Si un dato no existe, déjalo vacío.
- Devuelve únicamente JSON válido.

Presta especial atención a:

- Tipo de predio.
- Número de unidades de uso.
- Presencia de fuga en las instalaciones internas del predio.
- Presencia de fuga en la caja del medidor.
- Lectura actual del medidor, incluso si está escrita a mano.
- Estado del medidor.
- Hallazgos y observaciones del inspector.
- Casillas marcadas o seleccionadas.

Utiliza las siguientes claves:

{
    "niss":"",
    "medidor":"",
    "fecha_inspeccion":"",
    "tipo_predio":"",
    "unidades_uso":"",
    "fuga_predio":"",
    "fuga_caja":"",
    "lectura_actual":"",
    "estado_medidor":"",
    "hallazgos":"",
    "observaciones":""
}

Reglas:

- Para "fuga_predio", responde únicamente "SI" o "NO".
- Para "fuga_caja", responde únicamente "SI" o "NO".
- Para "estado_medidor", responde únicamente "FUNCIONA" o "NO FUNCIONA".
- Interpreta las casillas marcadas.
- No agregues explicaciones ni texto fuera del JSON.
"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analiza esta imagen."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{imagen_base64}"
                        }
                    }
                ]
            }
        ]
    )

    return respuesta.choices[0].message.content
