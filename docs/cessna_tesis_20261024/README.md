# Ejemplos Cessna y libro · revisión de la tesis IPN

La aplicación abre **Ejemplo Cessna**. El menú ofrece exclusivamente **Ejemplo Cessna** y **Ejemplo libro**. Los archivos anteriores del Excel y del libro siguen conservados; abrirlos no los reescribe.

## Condiciones del Cessna

El selector de condición ofrece **Revisado · ficha 4000 lb** (predeterminada) y **Comparación · cap. 1.9, 4631 lb**. Se conserva la edición de cada condición al pasar a la otra. El peso activo no se sustituye por los pesos de referencia de categorías.

| Magnitud | Elección actual | Procedencia y alcance |
|---|---:|---|
| W | 4000 lbf; alternativa 4631 | Ficha p.12 / cálculo p.32 de la tesis |
| S | 181 ft² | Ficha y §1.9 |
| Envergadura | 12.12 m | Ficha p.12 |
| c | S/b = 4.551881188 ft | Cuerda geométrica requerida en relación de masas; la sustitución publicada usa 4.26 ft |
| CN positivo | 1.45816142 | Máximo de la polar 2D NACA 2412 |
| CN negativo | −0.8381569 | Mínimo tabulado; reemplaza la simetría de la gráfica y la anterior aproximación −1.35 |
| ρ | 0.0023769 slug/ft³ | Sustitución de ráfagas p.37; sin inferir altitud |
| a | 0.105/grado | Interpretación editable: la tesis no indica la unidad |
| Vc / Vd / Va seleccionada | 170 / 240 / 150 kt EAS | Selecciones de p.33 |
| N / n− | 3.8 / −1.9 | Elección académica de la tesis; no afirmación de aplicabilidad normativa |
| Uc / Ud | 50 / 25 ft/s | Hipótesis de diseño explícitas del recálculo |

CN positivo y negativo son valores del perfil bidimensional, calculado en la tesis a Mach 0.5 y Re=4e6. Se idealizan constantes para estudiar la envolvente; no son datos aerodinámicos 3D validados del avión. La pendiente sigue siendo una hipótesis. El valor 0.11/grado del Excel ya no se introduce como si estuviera confirmado en la tesis.

La geometría con las unidades elegidas produce AR=8.735680455 (≈8.73 con los datos SI redondeados de la ficha). Supera el máximo 7 de A23.1 histórico. El aviso se muestra en pantalla, gráficas y reportes. No se presenta la condición académica como envolvente certificada.

## Tesis y revisión

El botón **Tesis y revisión** contiene los valores publicados, sus páginas, el recálculo de la condición activa y los problemas encontrados: pesos 4000/4631/4016, pareja nW incompatible, ausencia de a en la fórmula final de ráfaga, unidad de pendiente no declarada, cuerda, polar y aplicabilidad normativa.

Se distinguen **A (intersección)**, **Va mínimo base** y **Va seleccionada**. Vc/Vd seleccionadas gobiernan el recálculo; sus mínimos base se muestran aparte. Las fórmulas base A3 no se convierten en una demostración normativa.

**Comparar con tesis publicada** superpone una referencia trazada desde las tablas y la figura de pp.35–38. La simetría de pérdida y las parejas 1.634/0.366 y 1.47/0.53 se identifican como referencias publicadas; los rótulos de su tabla son inconsistentes. Esta capa no altera los cálculos actuales ni valida las fórmulas de la tesis. La lectura A1/A2 que adopta n3=3.8 y n4=−1.9 se conserva separada del cálculo de Niu.

## Guardado y exportación

Los dos pesos pertenecen al mismo proyecto JSON; guardar y abrir conserva ambos. El botón Exportar de la interfaz crea una carpeta nueva e incluye resultados de las dos condiciones. En la línea de comandos, use `--all` para exportar ambas; `--export` genera los archivos de la condición activa. Ambos conservan todas las condiciones en el proyecto JSON y comparan sus valores en `comparacion_resultados.csv`. Para cada una se añaden `velocidades.csv`, `contraste_tesis.csv`, `discrepancias_tesis.csv`, `curvas_tesis_publicadas.csv` y gráficas de comparación PNG/SVG. El reporte de la condición activa incluye tablas de velocidades, contraste y explicaciones; compara los resultados de ambos pesos. Los informes PDF/DOCX mantienen el alcance académico y la aproximación de pérdida estática.

`examples/ejemplo_cessna.json` y `examples/ejemplo_libro.json` son los proyectos nuevos. `ejemplo_1.json`, `ejemplo_2.json`, la documentación histórica y las recuperaciones anteriores se conservan para reproducción histórica.

El ejemplo del libro mantiene sus ecuaciones, tabla por Mach y valores de referencia; únicamente cambia su nombre visible.
