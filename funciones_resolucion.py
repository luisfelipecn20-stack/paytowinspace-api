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
```
