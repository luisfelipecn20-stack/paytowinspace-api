```python
from openai import OpenAI
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generar_considerando_1(datos_inspeccion):

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un especialista en resoluciones de reclamos por consumo de agua de Sedapal.

Tu tarea es redactar únicamente el Considerando Primero.

Utiliza exclusivamente la información recibida.

No inventes información.

Redacta en lenguaje administrativo y en un solo párrafo.
"""
            },
            {
                "role": "user",
                "content": str(datos_inspeccion)
            }
        ]
    )

    return respuesta.choices[0].message.content
```
