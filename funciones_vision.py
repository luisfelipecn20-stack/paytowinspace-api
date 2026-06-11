from openai import OpenAI
import base64

cliente = OpenAI()


def analizar_imagen(imagen_png):

    imagen_base64 = base64.b64encode(imagen_png).decode("utf-8")

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extrae todo el texto visible de esta imagen."
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
