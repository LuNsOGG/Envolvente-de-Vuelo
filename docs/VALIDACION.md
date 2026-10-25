# Validación

## Valores numéricos de referencia

Resultados del motor actual, conservados también en `rafagas_niu_20261024/valores_referencia.json` y contrastados por `tests/test_niu.py`.

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

## Evidencia previa del ejecutable instalado

La entrega anterior registró **97 pruebas aprobadas**, salida 0, y comprobación del EXE instalado en la raíz, con `frozen=true`, `status=correcto` y salida 0. Los registros se conservan localmente en `outputs/qa/niu_pruebas_20261024_final.*` y `outputs/qa/niu_exe_20261024_002359/`.

SHA256 del EXE entregado: `FD253C3A9E3DA1B49CA5494A536A127B34A1F7FE05B59F3C05D489C06E0C2863`.

La captura incluida en `docs/imagenes/ejemplo_2.png` procede de esa comprobación. La publicación del código y la documentación no recompila ni sustituye ese EXE.

## Comprobación de esta publicación

La suite se vuelve a ejecutar sobre el código preparado para GitHub. El resumen actualizado se registra en `validacion_publicacion.json`. Los registros completos permanecen en `outputs/qa/`; los flujos de Actions tendrán sus propios resultados, que no se presuponen aprobados por la validación local.

La validación de ecuaciones y software no demuestra la validez aerodinámica de una aeronave distinta ni la resistencia de su estructura. Las fuentes escaneadas y sus ambigüedades están descritas en [FUENTES.md](FUENTES.md).
