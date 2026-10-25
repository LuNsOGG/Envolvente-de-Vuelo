# Correcciones 1–17 de la revisión de software

La versión 4.1 corrige los primeros diecisiete hallazgos. Cada corrección tiene un commit independiente, en orden. Los puntos 18–24 quedan pendientes; esta entrega no incorpora el reporte de figuras al botón Exportar, edición de portada, Excel/MATLAB ni un nuevo modelo de certificación o aerodinámica.

| Punto | Corrección | Comprobación de regresión |
|---|---|---|
| [1](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/2a19cc1daaf0854e9deb03c02d3ca0561e7cef6d) | Rechazo de unidades incompatibles, sin reinterpretar números | Unidad kg rechazada; conversión N/lbf conservada |
| [2](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/272053061fe06f43a163a15ed1f1392dd2967071) | Ub inválido produce error; ausencia explícita sigue siendo opcional | Una unidad inválida no elimina VB silenciosamente |
| [3](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/c8e0f9815c272ae73642cda75dc81798b10fdd2b) | Validación de estructura JSON | Nombres, unidades, objetos y listas incorrectos producen ValueError |
| [4](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/f3af3b47c1ac24b6544cd99cbb32475e0c91b1de) | Borradores con valores y unidades por condición | Guardar, abrir y cambiar condición conserva ediciones inválidas |
| [5](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/e0dd727dc74cd20060afe5003f3c9b43bdf51050) | N≥1 y comprobaciones del criterio histórico seleccionado | N<1 bloqueado; factores e intensidades insuficientes advertidos |
| [6](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/957d37a5027c851513a82025009884149ef2bc52) | Hipótesis y títulos con datos efectivos | Ediciones de peso y pendiente se reflejan; originales conservados |
| [7](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/a961cad9f392e8aba2a327a4258c828fcae7dbc1) | Precisión y procedencia conservadas sin edición | Abrir y aceptar el diálogo no inventa cambios del usuario |
| [8](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/e1ac3a0745e3621556a4da639beb8f3e5ece4272) | Va seleccionada calculada y comprobada en ambos ejemplos | Se advierte si queda fuera de A…Vc y se muestra en gráficos |
| [9](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/5ae4da6cb6cc217b20fad6b77daee1cc659cbf61) | Compatibilidad CL/tabla validada en el motor | JSON con tabla y CN rechazado |
| [10](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/b1ecb742dee2a0f8ae0c2e39ce25ff6c43f83742) | Expresiones completas y pasos de Vs, A y G | Todas las ecuaciones de ambos ejemplos se renderizan |
| [11](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/64fbc57b77fe94bd3cf0f76b7716028ea5a43d3a) | Ejes incluyen demanda de ráfaga y referencias | Ninguna ordenada visible queda fuera del eje |
| [12](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/3753ddc61a4a3ff52b2e792a03acdfd51f1335d5) | VB coherente en el esquema 3.4.16 | Coincide con pérdida y ráfaga antes de VC |
| [13](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/6d1bd4c42e746dd17dbe0462d620a4e3efb29b62) | Entregas completas y parciales diferenciadas | Entrada pendiente bloquea entrega; parcial explícito identificado |
| [14](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/ec0115e8f239c994e0d1d08a8cbe56385b62fc6d) | Ramas independientes disponibles | Falta de CN negativo conserva ráfagas; falta de Uc conserva maniobra |
| [15](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/34bb0499aef6d9046e567a8d660f4877b21c8d0f) | Canvas y barras reutilizados; zoom conservado | Identidad de widgets y límites de vista preservados |
| [16](https://github.com/LuNsOGG/Envolvente-de-Vuelo/commit/480726f8ec0f02793d63b0c6c6687395ae3e8072) | Estado visible; exportación con progreso y cancelación | Qt sigue atendiendo eventos; cancelación conserva archivos identificados |
| 17 | Nombres y fuentes actualizados | Mínimos A3 citan Apéndice A; Va cita su propia fuente |

Pruebas específicas: `python -B -m pytest tests/test_audit_regressions.py -q -p no:cacheprovider`. Suite completa: `python -B tools/run_tests.py`. Comprobación del ejecutable: `Envolventes_de_Vuelo.exe --comprobar-gui`.

Las referencias publicadas, archivos de proyectos previos y distribuciones anteriores se conservan. Las advertencias normativas no se convierten en aprobaciones por corregir el software.

Validación final: **136 pruebas aprobadas** y comprobación separada por punto en copias aisladas. El EXE instalado completó la comprobación gráfica y exportó ambos ejemplos mediante el botón Exportar en segundo plano, con salida 0. Se verificaron las 1255 dependencias instaladas. [Registro resumido](correcciones_1_17_validacion.json).
