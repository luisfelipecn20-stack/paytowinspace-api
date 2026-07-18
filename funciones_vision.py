from openai import OpenAI
import base64
import os


cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analizar_imagen(
    imagenes_png,
    prompt_sistema,
    modelo="gpt-4o-mini"
):

    contenido = [
        {
            "type": "text",
            "text": (
                "Analiza las imágenes siguiendo exactamente "
                "las instrucciones del mensaje del sistema. "
                "Devuelve exclusivamente el formato solicitado."
            )
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
                    "url": (
                        "data:image/png;base64,"
                        f"{imagen_base64}"
                    ),
                    "detail": "high"
                }
            }
        )

    respuesta = cliente.chat.completions.create(
        model=modelo,
        temperature=0,
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
