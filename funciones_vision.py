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
Eres un experto en análisis de documentos.

Extrae la información relevante y responde únicamente en formato JSON.

Utiliza las siguientes claves:

{
    "niss":"",
    "medidor":"",
    "fecha_inspeccion":"",
    "direccion":"",
    "lectura_actual":"",
    "lectura_anterior":"",
    "hallazgos":"",
    "observaciones":""
}

Si un dato no existe, déjalo vacío.

No agregues explicaciones ni texto fuera del JSON.
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
