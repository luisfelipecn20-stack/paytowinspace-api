from openai import OpenAI
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def obtener_datos_considerando_4(imagen):

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                
                """

            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extrae la información solicitada."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imagen
                        }
                    }
                ]
            }
        ]
    )

    return respuesta.choices[0].message.content
