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

Utiliza las siguientes claves:

{
    "niss":"",
    "fecha_inspeccion":"",
    "tipo_unidad_uso":"",
    "ocupacion_predio":"",
    "observaciones_inspeccion":"",
    "medidor":"",
    "lectura_actual":"",
    "fuga_caja":""
}

Reglas:

1. Busca el N° de suministro y extrae el NISS.

2. Busca la fecha de inspección ubicada junto a la palabra "FECHA" al pie del Formato 5 o Formato 6.

- Ignora fechas de reclamo, orden de servicio y encabezados.
- Si el año aparece con dos dígitos, conviértelo a cuatro dígitos.
- No inventes fechas.

3. Busca la tabla "TIPO DE UNIDADES DE USO" e identifica cuál casilla está marcada:

- Dom = DOMESTICO
- Com = COMERCIAL
- Ind = INDUSTRIAL
- Est = ESTATAL

Devuelve únicamente uno de esos cuatro valores en la clave "tipo_unidad_uso".

4. Determina si el predio se encuentra:

- OCUPADO
- DESOCUPADO

Devuelve únicamente uno de esos dos valores en la clave "ocupacion_predio".

5. Busca la sección "Observaciones" ubicada debajo de "DETALLE DE LA INSPECCIÓN DE LAS INSTALACIONES SANITARIAS INTERIORES".

- Transcribe las observaciones de la forma más fiel posible.
- La fidelidad es más importante que la gramática.
- Si una palabra es ilegible, utiliza [ilegible].
- No inventes información.
- No es necesario interpretar si el predio es unifamiliar, multifamiliar o mixto.
- La información más relevante es la relacionada con fugas interiores, anomalías y estado del medidor.

Conserva las palabras tal como aparecen en el documento y guárdalas en la clave "observaciones_inspeccion".

6. Busca el campo "Medidor N°".

- El medidor puede contener letras y números.
- Copia exactamente los caracteres visibles.
- Nunca agregues dígitos.
- Nunca completes caracteres faltantes.
- No confundas el medidor con la lectura ni con el diámetro.

7. Busca el campo "Lectura".

- Devuelve únicamente el valor numérico.
- No confundas la lectura con el diámetro.
- La lectura corresponde al número situado debajo de la palabra "Lectura".

8. Busca la sección "FUGA EN LA CAJA".

Interpreta la casilla marcada.

Devuelve únicamente:

- SI
- NO

en la clave "fuga_caja".

9. No confundas la lectura con el diámetro del medidor.

La lectura corresponde al número manuscrito ubicado debajo de la palabra "Lectura".

10. No inventes información.

11. Si un dato no existe, déjalo vacío.

11.5 Si existen varias fechas, varios números o varias anotaciones, utiliza únicamente la información correspondiente al campo solicitado.

Nunca infieras ni completes información faltante.

12. Devuelve únicamente JSON válido y ningún texto adicional.
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
