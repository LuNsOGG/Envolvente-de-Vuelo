# Validación

**Versión 4.1, correcciones 1–17:** 136 pruebas aprobadas y exportación real de ambos pesos desde la interfaz con progreso. Se revisó visualmente el PDF de ecuaciones. Véase [el registro de correcciones](REVISION_1_17.md). Las comprobaciones de versiones anteriores se conservan a continuación como evidencia histórica.

## Referencias vigentes Cessna y libro

La revisión Cessna está cubierta por 105 pruebas, incluidas ocho pruebas de tesis, geometría, contraste, persistencia e interfaz. Los valores se conservan en [ejemplo_cessna_valores.json](cessna_tesis_20261024/ejemplo_cessna_valores.json) y [ejemplo_libro_valores.json](cessna_tesis_20261024/ejemplo_libro_valores.json).

| Resultado | Cessna 4000 lb | Cessna 4631 lb | Libro |
|---|---:|---:|---:|
| W/S [lbf/ft²] | 22.099448 | 25.585635 | 73.333333 |
| Vc / Vd [kt EAS] | 170 / 240 | 170 / 240 | 325 / 400 |
| Vs [kt EAS] | 66.907472 | 71.991632 | 130.216861 |
| A [kt EAS] | 130.426675 | 140.337526 | 207.773905 |
| Va seleccionada [kt EAS] | 150 | 150 | No fijada aparte |
| n3 en Vc | 4.267631 | 3.901810 | 2.949653 |
| n4 en Vc | -2.267631 | -1.901810 | -0.949653 |

El cálculo independiente usa una sola condición de peso, c=S/b, pendiente convertida a radianes y la ecuación de ráfaga completa. Los valores publicados de la tesis se contrastan por separado, sin forzar el resultado revisado. A, Va mínimo base y Va seleccionada se comprueban como magnitudes distintas.

## Ejecutable local vigente

La comprobación del EXE instalado registró `frozen=true`, estado correcto y salida 0; también se verificaron 1255 archivos de dependencias. SHA256: `F7D1D5F2B7971029D388BBD2E19FA5AD52BE6ECC81B2CA68DBF1A54787EFE565`. Los registros resumidos están en [validacion.json](cessna_tesis_20261024/validacion.json) y [validacion_exportaciones.json](cessna_tesis_20261024/validacion_exportaciones.json).

Se revisaron capturas de ambos ejemplos, contraste, edición, guardado y exportaciones. Los PDF se comprobaron en texto y límites de página; los DOCX se comprobaron por integridad OOXML, sin renderizado visual completo. Los ejecutables previos y documentos originales se conservan localmente.

## Publicación de la revisión Cessna

La nueva ejecución local de pruebas se registra en [validacion_publicacion.json](validacion_publicacion.json). La ejecución remota [Pruebas Windows](https://github.com/LuNsOGG/Envolvente-de-Vuelo/actions/runs/40151700126), asociada al commit `fdf2388c5f738a463f758cff314f04035afe5f05`, aprobó las 105 pruebas en 53.19 s y la comprobación de ejemplos. El commit posterior registra esta evidencia y solo modifica documentación. Esta publicación actualiza código y documentación, sin recompilar ni alterar el EXE local.

## Qué verifican las pruebas

- Fórmula de ráfaga frente a un cálculo independiente y conversiones de pendiente.
- Origen de ráfagas en n=1, simetría alrededor de esa referencia y distinción de los límites de maniobra.
- Inclusión de velocidades, VB e intersecciones en las curvas; continuidad entre anclas.
- Límites de pérdida del combinado y demandas de ráfaga completas.
- Tabla del libro, variación con Mach y bloqueo de extrapolación.
- Datos faltantes, inválidos o incompatibles; retirada de resultados anteriores.
- Guardado sin sobrescritura, procedencia, apertura y restricciones de ruta.
- Actualización de gráficas, menú de ejemplos y resumen de variables.
- Representación de gráficas, reportes e interfaces históricas.

## Referencias históricas Excel/libro

Resultados del motor histórico Excel/libro, conservados también en `rafagas_niu_20261024/valores_referencia.json` y contrastados por `tests/test_niu.py`.

| Resultado | Ejemplo 1 | Ejemplo 2 |
|---|---:|---:|
| W/S [lbf/ft²] | 25.585635359116 | 73.333333333333 |
| Vc [kt EAS] | 167.625012308370 | 325 |
| Vd [kt EAS] | 236.647076200052 | 400 |
| Vs [kt EAS] | 71.9462881049 | 130.21686073247 |
| A/Va [kt EAS] | 140.24913480617 | 207.77390500188 |
| VB [kt EAS] | No utilizado | 211.30532496749 |
| Δn en Vc | 2.910272016204 | 1.949652650634 |
| Δn en Vd | 2.054309658497 | 1.383930421343 |
| n3 en Vc | 3.910272016204 | 2.949652650634 |
| n4 en Vc | −1.910272016204 | −0.949652650634 |

El libro da 1.95 y 1.382 para Δn en Vc/Vd del Ejemplo 2. Las diferencias proceden del redondeo, la carga alar exacta y la interpretación de la tabla. No se alteran las entradas para forzar coincidencia.


## Evidencia previa del ejecutable instalado

La entrega anterior registró **97 pruebas aprobadas**, salida 0, y comprobación del EXE instalado en la raíz, con `frozen=true`, `status=correcto` y salida 0. Los registros se conservan localmente en `outputs/qa/niu_pruebas_20261024_final.*` y `outputs/qa/niu_exe_20261024_002359/`.

SHA256 del EXE entregado: `FD253C3A9E3DA1B49CA5494A536A127B34A1F7FE05B59F3C05D489C06E0C2863`.

La captura incluida en `docs/imagenes/ejemplo_2.png` procede de esa comprobación. La publicación del código y la documentación no recompila ni sustituye ese EXE.

## Publicación anterior en GitHub

La suite sobre el código preparado para GitHub aprobó las 97 pruebas en 53.28 s. Una copia separada, sin los documentos originales, aprobó también las 97 pruebas en 54.92 s. El resumen se registra en `validacion_publicacion.json`; los registros completos permanecen en `outputs/qa/`.

La ejecución remota de [Pruebas Windows](https://github.com/LuNsOGG/Envolvente-de-Vuelo/actions/runs/40109034103), correspondiente al commit `32e6a69d15921560a19274150305e1cacd10df14`, terminó correctamente: instalación de dependencias, suite de pruebas y comprobación de ejemplos. La compilación manual de Windows está disponible, pero no se ejecutó como parte de la publicación anterior documental.

La validación de ecuaciones y software no demuestra la validez aerodinámica de una aeronave distinta ni la resistencia de su estructura. Las fuentes escaneadas y sus ambigüedades están descritas en [FUENTES.md](FUENTES.md).
