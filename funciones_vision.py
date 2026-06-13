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
    "unidades_domesticas":"",
    "unidades_comerciales":"",
    "unidades_industriales":"",
    "unidades_estatales":"",
    "ocupacion_predio":"",
    "observaciones_inspeccion":"",
    "medidor":"",
    "lectura_actual":"",
    "fuga_caja":""
}

Reglas:

1. Busca el N° de suministro y extrae el NISS.

2. La fecha de inspección se encuentra en la primera hoja del Formato 5.

Busca la fecha impresa ubicada junto a "Fec.Res.".

No utilices la fecha manuscrita ubicada al pie del documento.

Devuelve la fecha en formato AAAA-MM-DD.

No inventes fechas.

3. Ubica el cuadro situado a la derecha de "TIPO DE UNIDADES DE USO" y "N° de conexiones asociadas" en la primera hoja.

Identifica cuántas unidades existen de cada tipo.

Extrae por separado:

- unidades_domesticas
- unidades_comerciales
- unidades_industriales
- unidades_estatales

Si una categoría no existe, devuelve 0.

Identifica también cuál es el tipo predominante y devuélvelo en la clave "tipo_unidad_uso".

No utilices las observaciones para determinar el tipo de unidad.

No infieras información que no sea visible.

4. Determina si el predio se encuentra:

- OCUPADO
- DESOCUPADO

Devuelve únicamente uno de esos dos valores en la clave "ocupacion_predio".

5. Busca las observaciones manuscritas ubicadas debajo de "DETALLE DE LA INSPECCIÓN DE LAS INSTALACIONES SANITARIAS INTERIORES".

No inventes palabras.

No asumas que existe una fuga.

No es necesario comprender completamente toda la escritura.

Solo registra información si las palabras son claramente visibles.

Si no es posible determinar con certeza el contenido, deja la observación vacía.

La incertidumbre es preferible a inventar información.

Guarda las observaciones encontradas en la clave "observaciones_inspeccion".

6. El número del medidor se encuentra en la segunda hoja.

Busca el cuadro "Medidor N°" ubicado en la parte superior.

El valor puede contener letras y números.

Nunca utilices la lectura ni el diámetro como número de medidor.

No utilices el medidor impreso del bloque "Datos Registrados" de la primera hoja.

Copia exactamente los caracteres visibles.

7. La lectura actual se encuentra en la segunda hoja.

Busca el número manuscrito situado encima del cuadro "Lectura".

No utilices "Ult.Lect." del bloque "Datos Registrados" de la primera hoja.

No confundas la lectura con el diámetro.

Devuelve únicamente el valor numérico.

8. Busca la sección "FUGA EN LA CAJA".

Interpreta la casilla marcada.

Devuelve únicamente:

- SI
- NO

en la clave "fuga_caja".

9. No inventes información.

10. Si un dato no existe, déjalo vacío.

11. La sección "Datos Registrados" de la primera hoja es únicamente referencial.

No utilices esa sección para determinar:

- medidor;
- lectura actual;
- fuga en caja.

Da prioridad a la información observada por el inspector en la segunda hoja.

Ignora el diámetro y la última lectura del bloque "Datos Registrados".

Todo lo que aparece desde "CIERRES Y REAPERTURAS / INSPECCIÓN SERVICIOS CERRADOS" hacia abajo en la segunda hoja puede ignorarse.

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

def analizar_expediente_comercial(imagen_png):

    imagen_base64 = base64.b64encode(imagen_png).decode("utf-8")

    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un especialista en expedientes comerciales de Sedapal.

Analiza cuidadosamente el documento.

Toda la información es mecanografiada.

No inventes información.

Si un dato no existe, déjalo vacío.

Devuelve únicamente JSON válido.

Extrae las siguientes claves:

{
"medio_presentacion":"",
"fecha_reclamo":"",
"tipo_reclamo":"",
"direccion_procesal":"",
"correo_autorizado":"",
"fecha_inspeccion":"",
"fecha_audiencia":"",
"meses_reclamados":"",
"volumen_real":"",
"lecturas_historicas":""
}

Reglas:

1. Identifica si el reclamo fue presentado:

- TELEFONICO
- WEB
- FORMATO_2

2. Extrae la fecha del reclamo.

3. Extrae el tipo de reclamo.

4. Extrae la dirección procesal.

5. Determina si existe autorización para notificación por correo electrónico.

Devuelve únicamente:

- SI
- NO

6. Extrae la fecha de inspección.

7. Extrae la fecha de audiencia.

8. Identifica los meses reclamados.

9. Extrae el volumen reclamado o volumen real si aparece.

10. Extrae las lecturas históricas del medidor si se encuentran visibles.

11. No inventes información.

12. Devuelve únicamente JSON válido y ningún texto adicional.
"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analiza este expediente comercial."
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
