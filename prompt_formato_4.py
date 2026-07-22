PROMPT_FORMATO_4 = """
Analiza visualmente esta Acta de Reunión de Conciliación
de SEDAPAL denominada FORMATO 4.

El documento puede estar impreso, escaneado, inclinado,
tener baja calidad o contener texto escrito manualmente.

Tu función es únicamente leer y transcribir información.
No determines el resultado de la audiencia.
La clasificación será realizada posteriormente con Python.

Devuelve solamente un JSON válido con esta estructura:

{
  "re": "",
  "fecha_audiencia": "",
  "texto_propuesta_sedapal": "",
  "texto_propuesta_reclamante": "",
  "texto_puntos_acuerdo": "",
  "texto_puntos_desacuerdo": "",
  "texto_observaciones": "",
  "direccion_procesal_acta": "",
  "correo_electronico_acta": "",
  "subsiste_reclamo": ""
}

REGLAS:

1. re:
Extrae el código ubicado en “CÓDIGO DE RECLAMO N°”.

Debe comenzar con RE.

Copia solamente el código completo.
No extraigas el número de suministro.

2. fecha_audiencia:
Extrae la fecha ubicada en la parte inferior del acta,
junto a la firma del representante de SEDAPAL.

Devuelve únicamente una fecha con formato DD/MM/AAAA.

No extraigas las horas.
No inventes la fecha si no puede leerse claramente.

3. texto_propuesta_sedapal:
Transcribe íntegramente el contenido del recuadro
“PROPUESTA DE SEDAPAL”.

4. texto_propuesta_reclamante:
Transcribe íntegramente el contenido del recuadro
“PROPUESTA DEL RECLAMANTE”.

5. texto_puntos_acuerdo:
Transcribe íntegramente el contenido del recuadro
“PUNTOS DE ACUERDO”.

6. texto_puntos_desacuerdo:
Transcribe íntegramente el contenido del recuadro
“PUNTOS DE DESACUERDO”.

7. texto_observaciones:
Transcribe íntegramente el contenido del recuadro
“OBSERVACIONES DEL RECLAMANTE O DE SEDAPAL”.

En los cinco recuadros anteriores presta especial atención
a expresiones relacionadas con:

- ausente
- ausencia
- inasistencia
- no asistió
- no se presentó
- no se llegó a ninguna fórmula de solución
- no hubo acuerdo
- continuación del reclamo
- continúa con el proceso de reclamo
- proceso por la vía administrativa
- nueva dirección procesal
- nuevo domicilio procesal
- dirección para notificaciones
- dirección de correo electrónico

Transcribe las expresiones exactamente como aparecen.

No resumas.
No interpretes.
No corrijas el contenido.

8. direccion_procesal_acta:
Extrae una dirección únicamente cuando en alguno de los
cinco recuadros se indique expresamente una nueva:

- dirección procesal
- domicilio procesal
- dirección para notificaciones

Copia la dirección completa exactamente como aparece.

No copies direcciones de otras partes del documento.
No completes datos faltantes.
No corrijas la dirección.

Si no existe una nueva dirección procesal, devuelve "".

9. correo_electronico_acta:
Extrae un correo electrónico únicamente cuando aparezca
en alguno de los cinco recuadros.

Copia el correo exactamente como aparece.

No corrijas letras.
No corrijas números.
No corrijas el dominio.
No inventes caracteres faltantes.

Si no existe un correo electrónico, devuelve "".

10. subsiste_reclamo:
Observa únicamente las casillas de
“¿SUBSISTE EL RECLAMO?”.

Devuelve:

- "SI" si la X está en la casilla Sí.
- "NO" si la X está en la casilla No.
- "" si no puede determinarse claramente.

No confundas esta casilla con otras opciones Sí/No
que puedan aparecer en el documento.

REGLAS GENERALES:

Si un recuadro está vacío, devuelve "".

No extraigas:

- NISS
- número de suministro
- nombre del reclamante
- DNI
- representante de SEDAPAL
- horas de la audiencia
- meses reclamados
- montos reclamados

No inventes información.
No agregues explicaciones fuera del JSON.
No uses Markdown.
"""
