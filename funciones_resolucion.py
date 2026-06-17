from openai import OpenAI
import os
import time
from datetime import datetime

cliente = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def crear_expediente_maestro():

    expediente = {

        # RESOLUCIÓN
        "numero_resolucion": "",
        "fecha_resolucion": "",

        # USUARIO
        "suministro": "",
        "reclamante": "",
        "sexo_reclamante": "",

        # DIRECCIONES
        "direccion_suministro": "",
        "direccion_procesal": "",
        "correo_autorizado": False,

        # FORMATO 2
        "direccion_formato_2": "",
        "correo_formato_2": "",

        # FORMATO 4
        "existe_formato_4": False,
        "direccion_formato_4": "",
        "correo_formato_4": "",

        # RECLAMO
        "codigo_reclamo": "",
        "medio_presentacion": "",
        "tipo_reclamo": "",
        "fecha_reclamo": "",
        "meses_reclamados": [],

        # INSPECCIÓN
        "fecha_inspeccion": "",
        "medidor": "",
        "lectura_actual": "",
        "fuga_caja": "",
        "ocupacion_predio": "",
        "unidades_domesticas": 0,
        "unidades_comerciales": 0,
        "unidades_industriales": 0,
        "unidades_estatales": 0,
        "observaciones_inspeccion": "",

        # FACTURACIÓN
        "volumen_real": "",
        "lecturas_historicas": [],

        # AUDIENCIA
        "fecha_audiencia": "",
        "hubo_audiencia": False,
        "asistio_audiencia": True,
        "hubo_acuerdo": False,

        # REGLAS DE REDACCIÓN
        "tipo_predio": "",
        "texto_mes": "",
        "texto_usuario": "",
        "texto_notificacion": "",

        # RESULTADO
        "resultado": "INFUNDADO"

    }

    return expediente


def determinar_tipo_predio(
        unidades_domesticas,
        unidades_comerciales,
        unidades_industriales,
        unidades_estatales):

    total_unidades = (
        unidades_domesticas
        + unidades_comerciales
        + unidades_industriales
        + unidades_estatales
    )

    if (
        unidades_domesticas == 1
        and unidades_comerciales == 0
        and unidades_industriales == 0
        and unidades_estatales == 0
    ):
        return "UNIFAMILIAR"

    if (
        unidades_domesticas > 0
        and (
            unidades_comerciales > 0
            or unidades_industriales > 0
            or unidades_estatales > 0
        )
    ):
        return "MIXTO"

    if total_unidades > 1:
        return "MULTIFAMILIAR"

    return ""


def determinar_texto_mes(cantidad_meses):

    if cantidad_meses == 1:
        return "mes cuestionado"

    return "meses cuestionados"


def determinar_texto_audiencia(hubo_acuerdo):

    if hubo_acuerdo:
        return (
            "habiéndose arribado a una fórmula de solución "
            "al reclamo por acuerdo entre las partes."
        )

    return (
        "no habiéndose llegado a ninguna fórmula de solución "
        "al reclamo, por falta de consenso entre las partes, "
        "continuando con el proceso de reclamo en la vía administrativa."
    )

def determinar_descripcion_unidades(datos_inspeccion):

    partes = []

    # DOMÉSTICAS OCUPADAS
    dom_ocup = int(datos_inspeccion.get("dom_ocup", 0))

    if dom_ocup > 0:
        if dom_ocup == 1:
            partes.append("01 doméstico habitado")
        else:
            partes.append(
                f"{dom_ocup:02d} unidades de uso doméstico habitadas"
            )

    # COMERCIALES OCUPADAS
    com_ocup = int(datos_inspeccion.get("com_ocup", 0))

    if com_ocup > 0:
        if com_ocup == 1:
            partes.append("01 comercial en actividad")
        else:
            partes.append(
                f"{com_ocup:02d} comerciales en actividad"
            )

    # INDUSTRIALES OCUPADAS
    ind_ocup = int(datos_inspeccion.get("ind_ocup", 0))

    if ind_ocup > 0:
        if ind_ocup == 1:
            partes.append("01 industrial en actividad")
        else:
            partes.append(
                f"{ind_ocup:02d} industriales en actividad"
            )

    # ESTATALES OCUPADAS
    est_ocup = int(datos_inspeccion.get("est_ocup", 0))

    if est_ocup > 0:
        if est_ocup == 1:
            partes.append("01 estatal en actividad")
        else:
            partes.append(
                f"{est_ocup:02d} estatales en actividad"
            )

    # DOMÉSTICAS DESOCUPADAS
    dom_desc = int(datos_inspeccion.get("dom_desc", 0))

    if dom_desc > 0:
        if dom_desc == 1:
            partes.append("01 doméstico desocupado")
        else:
            partes.append(
                f"{dom_desc:02d} domésticos desocupados"
            )

    return ", ".join(partes)
    
def determinar_texto_inspeccion(datos_inspeccion):
    
    observ = (
        datos_inspeccion.get("observ", "")
        + " "
        + datos_inspeccion.get("observm1", "")
        + " "
        + datos_inspeccion.get("observm2", "")
    ).upper()

    if (
        "OPOSICION" in observ
        or "OPOSICIÓN" in observ
    ):

        return (
            "se llevó a cabo la inspección externa al predio, "
            "no habiéndose efectuado la inspección interna por oposición del usuario"
        )

    elif (
        "NO SE INSPECCIONO" in observ
    ):

        return (
            "se llevó a cabo la inspección interna y externa de manera parcial al predio"
        )

    elif (
        "AUSENTE" in observ
        or "AUSENCIA" in observ
    ):

        return (
            "se llevó a cabo la inspección externa al predio, "
            "no habiéndose efectuado la inspección interna por ausencia del usuario"
        )

    else:

        return (
            "se llevó a cabo la inspección interna y externa al predio"
        )

def generar_considerando_1(datos_inspeccion):

    inicio_gpt = time.time()

    # Normalizar lectura
    lectura = datos_inspeccion.get("lec")

    if (
        isinstance(lectura, float)
        and lectura.is_integer()
    ):
        datos_inspeccion["lec"] = int(lectura)

    # Normalizar fecha
    fecha = datos_inspeccion.get("fec_vis")

    if fecha:

        if isinstance(fecha, str):

            fecha = datetime.fromisoformat(
                fecha.replace("Z", "")
            )

        datos_inspeccion["fec_vis"] = (
            fecha.strftime("%d/%m/%Y")
        )

    # Determinar estado de las instalaciones internas

    if datos_inspeccion.get("estado_instalaciones"):

        datos_inspeccion["estado_fuga"] = (
            datos_inspeccion["estado_instalaciones"]
        )

    elif datos_inspeccion.get("fuga_caj") == "S/F/CAJA":

        datos_inspeccion["estado_fuga"] = "SIN FUGA"

    elif datos_inspeccion.get("fuga_caj") == "C/F/CAJA":

        datos_inspeccion["estado_fuga"] = "CON FUGA"

    else:

        datos_inspeccion["estado_fuga"] = ""

    # Determinar tipo de inspección
    datos_inspeccion["texto_inspeccion"] = (
        determinar_texto_inspeccion(
            datos_inspeccion
        )
    )

    # Construir inicio obligatorio del considerando
    datos_inspeccion["inicio_considerando"] = (
        f"Con fecha {datos_inspeccion['fec_vis']}, "
        f"{datos_inspeccion['texto_inspeccion']},"
)

    datos_inspeccion["tipo_predio"] = determinar_tipo_predio(
        datos_inspeccion.get("dom_ocup", 0),
        datos_inspeccion.get("com_ocup", 0),
        datos_inspeccion.get("ind_ocup", 0),
        datos_inspeccion.get("est_ocup", 0)
)

    datos_inspeccion["descripcion_unidades"] = (
        determinar_descripcion_unidades(datos_inspeccion)
    )
    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
Eres un especialista en resoluciones de reclamos comerciales de Sedapal perteneciente al Equipo Comercial Callao.

Tu tarea es redactar únicamente el Considerando Primero.

Debes imitar el estilo utilizado por el Equipo Comercial Callao.

La redacción debe realizarse en un solo párrafo y con lenguaje administrativo.

Debes utilizar exclusivamente la información proporcionada.

No inventes información.

No infieras hechos no expresamente indicados.

No completes información faltante.

No asumas distribución de pisos, ambientes, viviendas o niveles.

No agregues detalles que no aparezcan en los datos recibidos.

No cites normas.

No emitas conclusiones.

No indiques si el reclamo es fundado o infundado.

No hagas recomendaciones.

No menciones aspectos que correspondan a otros considerandos.

Devuelve únicamente el texto del Considerando Primero.

La redacción debe iniciar obligatoriamente con el contenido del campo "inicio_considerando".

Debes reproducirlo exactamente como fue recibido.

No debes modificarlo.

No debes resumirlo.

No debes omitir ninguna palabra.

No debes cambiar la redacción recibida.

La fecha debe conservarse exactamente como fue recibida y expresarse únicamente en formato DD/MM/AAAA.

No debes utilizar expresiones como:

"29 de junio de 2026"

"29 de mayo de 2026"

Bajo ninguna circunstancia puedes reemplazar expresiones equivalentes.

La frase inicial del considerando es obligatoria y debe conservarse íntegramente.

Si el contenido del campo "inicio_considerando" incluye:

"no habiéndose efectuado la inspección interna por oposición del usuario"

debes conservar dicha expresión completa.

Si incluye:

"no habiéndose efectuado la inspección interna por ausencia del usuario"

debes conservar dicha expresión completa.

Si incluye:

"se llevó a cabo la inspección interna y externa al predio"

debes conservar dicha expresión completa.

Si incluye:

"se llevó a cabo la inspección externa al predio"

debes conservar dicha expresión completa.

Bajo ninguna circunstancia debes sustituir una inspección externa por una inspección interna y externa.

No debes inferir que existió inspección interna si ello no aparece expresamente en el campo "inicio_considerando".

Si incluye:

"se llevó a cabo la inspección interna y externa de manera parcial al predio"

debes conservar dicha expresión completa.

Luego debes señalar que:

"se verificó que la caja de control de la conexión domiciliaria de agua potable se encuentra vigente en buen estado"

Si existe fuga en caja debes indicar:

"y con fuga de agua"

Si no existe fuga en caja debes indicar:

"y sin fuga de agua"

Si el valor recibido para fuga_caj es:

"S/F/CAJA"

debes indicar obligatoriamente:

"y sin fuga de agua"

No debes omitir dicha expresión.

No debes inferir la existencia de fuga de agua en la caja cuando el valor recibido sea "S/F/CAJA".

Debes indicar:

"Que el medidor (número de medidor) registra al momento de la inspección la lectura de (lectura) m3."

No utilices expresiones como:

"habiéndose registrado un número de medidor"

o similares.

Cuando corresponda, utiliza las siguientes expresiones:

* "la conexión domiciliaria abastece a un predio unifamiliar"
* "la conexión domiciliaria abastece a un predio multifamiliar"
* "la conexión domiciliaria abastece a un predio mixto"
* "la conexión domiciliaria abastece a un predio comercial en actividad"
* "la conexión domiciliaria abastece a un predio doméstico desocupado"

La clasificación del predio debe realizarse exclusivamente utilizando el campo "tipo_predio".

Si el campo "tipo_predio" es:

"UNIFAMILIAR"

debes indicar:

"la conexión domiciliaria abastece a un predio unifamiliar"

Si el campo "tipo_predio" es:

"MULTIFAMILIAR"

debes indicar:

"la conexión domiciliaria abastece a un predio multifamiliar"

Si el campo "tipo_predio" es:

"MIXTO"

debes indicar:

"la conexión domiciliaria abastece a un predio mixto"

No debes utilizar las observaciones para modificar la clasificación del predio.

Las observaciones solo pueden utilizarse como información complementaria.

La clasificación determinada por el campo "tipo_predio" prevalece sobre cualquier descripción contenida en las observaciones.

Si existen unidades ocupadas y desocupadas, debes describirlas siguiendo el estilo:

"conformado por 01 doméstico habitado, 03 comerciales en actividad y 01 doméstico desocupado"

o

"conformado por 06 unidades de uso doméstico habitadas"

o

"conformado por 01 doméstico habitado y 01 comercial en actividad"

No inventes cantidades.

Si no existen datos suficientes, omite la descripción de las unidades.

No debes crear unidades domésticas, comerciales, industriales o estatales que no hayan sido proporcionadas.

No debes asumir la existencia de unidades domésticas habitadas.

No debes convertir un predio comercial en un predio mixto.

Si únicamente existen unidades comerciales, debes describir únicamente las unidades comerciales.

Si únicamente existe una unidad comercial ocupada, debes indicar:

"la conexión domiciliaria abastece a un predio comercial en actividad"

No debes agregar unidades domésticas ni predios mixtos salvo que ello aparezca expresamente en la información recibida.

Si no existe información suficiente para describir las unidades de uso, debes omitir dicha descripción.

Respecto a las instalaciones internas, no debes describir pruebas hidráulicas ni copiar literalmente las observaciones.

No debes omitir dicha conclusión bajo ninguna circunstancia.

Si el campo "estado_fuga" está vacío, no debes hacer referencia a las instalaciones internas.

Si el valor recibido para "fuga_caj" es:

"S/F/CAJA"

debes indicar obligatoriamente:

"y sin fuga de agua"

No debes omitir dicha expresión.

No debes inferir la existencia de fuga de agua en la caja cuando el valor recibido sea "S/F/CAJA".

Interpretación obligatoria del campo fuga_caj:

"S/F/CAJA" significa que la caja de control se encuentra sin fuga de agua.

"C/F/CAJA" significa que la caja de control presenta fuga de agua.

Debes respetar obligatoriamente dicha interpretación.

La interpretación del campo fuga_caj prevalece sobre cualquier observación consignada en la inspección.

No debes inferir la existencia de fuga de agua cuando el valor recibido sea "S/F/CAJA".

No debes utilizar expresiones contenidas en las observaciones para modificar la interpretación del campo fuga_caj.

La sola presencia de la palabra "fuga" en las observaciones no significa necesariamente que exista fuga.

Expresiones como:

"NO SE DETECTÓ FUGA"

"NO SE DETECTO FUGA"

"NO PRESENTA FUGA"

"NO EXISTE FUGA"

deben interpretarse como ausencia de fuga.

No utilices expresiones como:

"cerrando todos los puntos de agua"

"el medidor no registra consumo"

"no se detectó fuga de agua en las instalaciones internas"

"fuga en inodoro"

"fuga en válvula"

"fuga en tanque"

Debes resumir dichas situaciones únicamente como:

"sin fuga"

o

"con fuga"

según corresponda.

Debes incorporar las observaciones encontradas durante la inspección únicamente si aparecen expresamente en la información recibida.

No reformules innecesariamente.

La estructura y redacción deben ser similares a las resoluciones emitidas por el Equipo Comercial Callao.

"""

            },
            {
                "role": "user",
                "content": str(datos_inspeccion)
            }
        ]
    )

    print(
        "Tiempo OpenAI:",
        round(time.time() - inicio_gpt, 2),
        "segundos"
    )

    considerando = (
        respuesta.choices[0]
        .message
        .content
    )

    considerando = considerando.replace(
        "Considerando Primero:",
        ""
    ).strip()

    if (
        datos_inspeccion.get("estado_fuga") == "SIN FUGA"
        and "oposición del usuario" not in datos_inspeccion["texto_inspeccion"]
        and "ausencia del usuario" not in datos_inspeccion["texto_inspeccion"]
    ):

        considerando += (
            " Asimismo, se verificó que las instalaciones internas se encuentran sin fuga."
        )

    elif (
        datos_inspeccion.get("estado_fuga") == "CON FUGA"
        and "oposición del usuario" not in datos_inspeccion["texto_inspeccion"]
        and "ausencia del usuario" not in datos_inspeccion["texto_inspeccion"]
    ):

        considerando += (
            " Asimismo, se verificó que las instalaciones internas se encuentran con fuga."
        )
    return considerando
