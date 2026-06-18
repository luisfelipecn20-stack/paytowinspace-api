from openai import OpenAI
import base64
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analizar_imagen(imagenes_png, prompt_sistema):

    contenido = [
        {
            "type": "text",
            "text": "Analiza las siguientes imágenes."
        }
    ]

    for imagen_png in imagenes_png:

        imagen_base64 = base64.b64encode(
            imagen_png
        ).decode("utf-8")

        contenido.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{imagen_base64}"
                }
            }
        )

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": prompt_sistema
            },
            {
                "role": "user",
                "content": contenido
            }
        ]
    )

    return respuesta.choices[0].message.content
