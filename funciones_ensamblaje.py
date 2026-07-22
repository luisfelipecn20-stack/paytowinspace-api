from funciones_visto import generar_visto

from funciones_considerando_1 import (
    generar_considerando_1
)

from funciones_considerando_2 import (
    generar_considerando_2
)

from funciones_considerando_3 import (
    generar_considerando_3
)

from funciones_considerando_4 import (
    generar_considerando_4,
    combinar_datos_facturacion
)

from funciones_considerando_5 import (
    generar_considerando_5
)

from funciones_considerando_6 import (
    generar_considerando_6
)

from funciones_articulos import (
    obtener_parrafo_base_legal,
    obtener_se_resuelve,
    generar_articulo_1,
    obtener_articulo_2,
    obtener_cierre,
    obtener_datos_firma_resolucion
)

from funciones_cruce_expedientes import (
    normalizar_re,
    normalizar_numero
)


def buscar_registro_cruce(
    resultado_cruce,
    nombre_lista,
    re_buscado,
    niss_buscado
):

    if not isinstance(
        resultado_cruce,
        dict
    ):
        return {}

    registros = resultado_cruce.get(
        nombre_lista,
        []
    )

    re_buscado = normalizar_re(
        re_buscado
    )

    niss_buscado = normalizar_numero(
        niss_buscado
    )

    for registro in registros:

        re_registro = normalizar_re(
            registro.get(
                "re",
                ""
            )
        )

        niss_registro = normalizar_numero(
            registro.get(
                "niss",
                ""
            )
        )

        if (
            re_registro == re_buscado
            and niss_registro == niss_buscado
        ):
            return registro

    return {}


def ensamblar_resolucion(
    datos_formato_2,
    datos_inspeccion,
    datos_informe,
    validacion_formato_4,
    encabezado
):

    if not isinstance(
        datos_formato_2,
        dict
    ):
        return {
            "estado": "ERROR_FORMATO_2"
        }

    if not isinstance(
        datos_inspeccion,
        dict
    ):
        datos_inspeccion = {}

    if not isinstance(
        datos_informe,
        dict
    ):
        datos_informe = {}

    if not isinstance(
        validacion_formato_4,
        dict
    ):
        validacion_formato_4 = {}

    if not isinstance(
        encabezado,
        dict
    ):
        encabezado = {}

    re_final = normalizar_re(
        datos_formato_2.get(
            "re",
            ""
        )
    )

    niss_final = normalizar_numero(
        datos_formato_2.get(
            "niss",
            ""
        )
    )

    visto = datos_formato_2.get(
        "visto",
        ""
    )

    if not visto:

        visto = generar_visto(
            datos_formato_2
        )

    considerando_1 = generar_considerando_1(
        datos_inspeccion
    )

    considerando_2 = generar_considerando_2(
        datos_formato_2
    )

    considerando_3 = generar_considerando_3()

    regimen_facturacion = datos_informe.get(
        "regimen_facturacion",
        []
    )

    recibos_formato_3 = datos_formato_2.get(
        "recibos_formato_3",
        []
    )

    validacion_facturacion = (
        combinar_datos_facturacion(
            regimen_facturacion=regimen_facturacion,
            recibos_formato_3=recibos_formato_3
        )
    )

    tiene_diferencias_facturacion = any(
        str(
            registro.get(
                "estado_validacion",
                ""
            )
        ).startswith(
            "DIFERENCIA"
        )
        for registro in validacion_facturacion
    )

    considerando_4 = generar_considerando_4(
        regimen_facturacion=regimen_facturacion,
        recibos_formato_3=recibos_formato_3
    )

    considerando_5 = generar_considerando_5(
        datos_formato_2=datos_formato_2,
        validacion_formato_4=(
            validacion_formato_4
        )
    )

    considerando_6 = generar_considerando_6(
        datos_formato_2
    )

    parrafo_base_legal = (
        obtener_parrafo_base_legal()
    )

    se_resuelve = obtener_se_resuelve()

    articulo_1 = generar_articulo_1(
        datos_formato_2
    )

    articulo_2 = obtener_articulo_2()

    cierre = obtener_cierre()

    firma_resolucion = (
        obtener_datos_firma_resolucion()
    )

    componentes_obligatorios = {
        "linea_resolucion": encabezado.get(
            "linea_resolucion",
            ""
        ),
        "linea_fecha": encabezado.get(
            "linea_fecha",
            ""
        ),
        "re": re_final,
        "niss": niss_final,
        "visto": visto,
        "considerando_1": considerando_1,
        "considerando_2": considerando_2,
        "considerando_3": considerando_3,
        "considerando_4": considerando_4,
        "considerando_5": considerando_5,
        "considerando_6": considerando_6,
        "articulo_1": articulo_1
    }

    componentes_faltantes = [
        nombre
        for nombre, contenido
        in componentes_obligatorios.items()
        if not contenido
    ]

    acta_validada = (
        validacion_formato_4.get(
            "estado_validacion"
        )
        == "VALIDADO"
        and not validacion_formato_4.get(
            "requiere_revision",
            True
        )
        and validacion_formato_4.get(
            "caso_soportado_v1",
            False
        )
    )

    encabezado_validado = (
        encabezado.get(
            "estado_cruce"
        )
        == "VALIDADO"
    )

    if not acta_validada:

        estado = "REQUIERE_REVISION_ACTA"

    elif not encabezado_validado:

        estado = "REQUIERE_REVISION_ENCABEZADO"

    elif tiene_diferencias_facturacion:

        estado = "REQUIERE_REVISION_FACTURACION"

    elif componentes_faltantes:

        estado = "PENDIENTE_SIN_DATOS"

    else:

        estado = "GENERADO"

    return {
        "estado": estado,
        "componentes_faltantes": (
            componentes_faltantes
        ),
        "encabezado": {
            "numero_resolucion": encabezado.get(
                "numero_resolucion",
                ""
            ),
            "fecha_emision": encabezado.get(
                "fecha_emision",
                ""
            ),
            "linea_resolucion": encabezado.get(
                "linea_resolucion",
                ""
            ),
            "linea_fecha": encabezado.get(
                "linea_fecha",
                ""
            )
        },
        "datos_expediente": {
            "re": re_final,
            "niss": niss_final,
            "reclamante": datos_formato_2.get(
                "reclamante",
                ""
            ),
            "direccion_suministro": (
                datos_formato_2.get(
                    "direccion_suministro",
                    ""
                )
            ),
            "direccion_procesal": (
                validacion_formato_4.get(
                    "direccion_procesal_final",
                    ""
                )
            ),
            "correo_electronico": (
                validacion_formato_4.get(
                    "correo_final",
                    ""
                )
            ),
            "tipo_reclamo": datos_formato_2.get(
                "tipo_reclamo",
                ""
            ),
            "meses_reclamados": (
                datos_formato_2.get(
                    "meses_reclamados",
                    []
                )
            )
        },
        "visto": visto,
        "considerando_1": considerando_1,
        "considerando_2": considerando_2,
        "considerando_3": considerando_3,
        "considerando_4": considerando_4,
        "considerando_5": considerando_5,
        "considerando_6": considerando_6,
        "parrafo_base_legal": (
            parrafo_base_legal
        ),
        "se_resuelve": se_resuelve,
        "articulo_1": articulo_1,
        "articulo_2": articulo_2,
        "cierre": cierre,
        "firma_resolucion": firma_resolucion,
        "controles": {
            "acta_validada": acta_validada,
            "encabezado_validado": (
                encabezado_validado
            ),
            "tiene_diferencias_facturacion": (
                tiene_diferencias_facturacion
            ),
            "validacion_facturacion": (
                validacion_facturacion
            ),
            "resultado_audiencia": (
                validacion_formato_4.get(
                    "resultado_audiencia",
                    ""
                )
            ),
            "continua_reclamo": (
                validacion_formato_4.get(
                    "continua_reclamo",
                    ""
                )
            )
        }
    }
