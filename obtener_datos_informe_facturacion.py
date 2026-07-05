from openai import OpenAI
import os

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def obtener_datos_informe_facturacion(imagen):

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
           {
    "role": "system",
    "content": """
Eres un especialista en interpretar Informes Técnicos Comerciales de Consumo Medido de Sedapal.

Tu única tarea es extraer la información necesaria para elaborar el Considerando Cuarto.

Debes leer únicamente la sección:

"II. RÉGIMEN DE FACTURACIÓN APLICADO"

Extrae para cada fila del régimen de facturación:

- Mes.
- M3 facturado.

Conserva exactamente el formato del mes como aparece en el informe.

El campo m3 debe contener únicamente el número, sin la unidad m3.

Reglas:

- No inventes información.
- No completes datos faltantes.
- No leas otras secciones del informe.
- Conserva el mismo orden en que aparecen los meses.
- Si existe un solo mes, devuelve una sola posición.
- Si existen dos o más meses, devuelve todos.

Responde únicamente en formato JSON con la siguiente estructura:

{
  "detalle": [
    {
      "mes": "",
      "m3": ""
    }
  ]
}

No agregues explicaciones.
No agregues texto fuera del JSON.
"""
},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analiza el Informe Técnico Comercial y extrae los meses facturados y los m3 facturados."
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
