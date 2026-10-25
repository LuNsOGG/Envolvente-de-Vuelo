# Manual de uso

## Abrir y seleccionar un ejemplo

En la instalación local, ejecute `Envolventes_de_Vuelo.exe` junto a `_internal/`. Desde el código, use `python -B main.py` con las dependencias instaladas. Se abre el Ejemplo Cessna.

El menú **Ejemplos** ofrece únicamente **Ejemplo Cessna** y **Ejemplo libro**. Cada uno carga un proyecto independiente. También pueden abrirse `examples/ejemplo_cessna.json` y `examples/ejemplo_libro.json` con **Abrir**.

El Cessna ofrece dos condiciones en el selector: ficha revisada de 4000 lb y comparación con las 4631 lb del capítulo 1.9. **Tesis y revisión** muestra fuentes, discrepancias y velocidades. **Comparar con tesis publicada** añade una referencia gráfica que no altera el recálculo.

## Editar una condición

La tabla contiene, en este orden, nᵤ, nₙ, Wₙ, Wᵤ, W, S, W/S, N, coeficiente positivo, ρ, c, a, g y CLα. El significado de cada símbolo se consulta con **Resumen de variables** o en [VARIABLES.md](VARIABLES.md).

Edite el valor y seleccione su unidad. W/S es un resultado automático. N es el límite positivo seleccionado; los campos de categorías nᵤ/nₙ y pesos Wₙ/Wᵤ son referencias y no sustituyen W ni N.

En **Datos de cálculo** se definen el coeficiente negativo, el límite negativo, el modo de velocidades y Ub/Uc/Ud. Seleccione coeficientes constantes al introducir datos de otra aeronave: la tabla del Ejemplo libro pertenece exclusivamente al caso del libro. Ub=0 omite VB.

Los cálculos se actualizan automáticamente: confirme la edición con **Enter** o saliendo de la celda. Después de 550 ms desde el último cambio confirmado se recalculan resultados y gráficas. Cambiar unidades también inicia ese recálculo; cambiar de condición recalcula de inmediato. La interfaz actual no tiene botón **Calcular**. Esto actualiza los resultados en pantalla; para conservar el proyecto utilice **Guardar**.

El estado visible indica cambios pendientes, cálculo en curso, actualización terminada o cálculo parcial. El zoom se conserva al recalcular una condición. Las ramas que disponen de todos sus datos pueden consultarse aunque falten entradas de otra envolvente; el combinado completo sigue pendiente.

La edición actualiza las gráficas. Si un dato requerido falta o es inválido, se retiran las curvas anteriores para evitar mostrar resultados de otra condición. Revise **Resultados** para ver ecuaciones, comprobaciones e hipótesis.

## Interpretar las vistas

| Vista | Qué muestra |
|---|---|
| Las tres envolventes | Maniobras, ráfagas y combinado en una sola pantalla |
| Maniobras | Curvas de pérdida y límites de carga de la condición |
| Ráfagas | Factores `1 ± Δn`, sin limitarlos a N o n− |
| Combinado | Extremos de maniobra y ráfaga con limitación de pérdida estática; demanda de ráfaga completa como referencia |

El eje horizontal utiliza nudos EAS. Un límite del diagrama es una condición de diseño del modelo, no una velocidad operativa aprobada.

## Guardar y recuperar

**Nuevo** prepara una aeronave con datos por introducir. **Guardar** escribe un proyecto JSON; si existe el nombre, se reserva otro para conservar la versión anterior. **Abrir** carga un proyecto ubicado dentro de la carpeta del proyecto.

Al cambiar de ejemplo o proyecto, las ediciones pendientes se conservan en `data/recuperaciones/`. Para recuperarlas, use **Abrir** y seleccione el JSON correspondiente. Estas recuperaciones son locales y no se publican en GitHub.

Cambiar h no recalcula automáticamente ρ, Cse ni las intensidades de ráfaga. Compruebe estos datos explícitamente. Guardar un ejemplo modificado no valida los datos de una nueva aeronave.

## Procedimiento del Apéndice A

**Procedimiento del Apéndice A…** abre una vista independiente de Niu con lecturas n3/n4, fuente, página y elección entre velocidades seleccionadas o mínimos A3. Actualizar muestra tablas, maniobras y contorno A4; Guardar conserva la configuración. Las lecturas predeterminadas del Cessna son las adoptadas por la tesis, no una nueva digitalización de nomogramas.

## Exportar solo las gráficas

Seleccione la condición de peso que desea y pulse **Exportar**. Se crea una carpeta nueva `outputs/graficas_CONDICION_FECHA_HORA/` con exactamente seis archivos:

- `maniobras.png` y `maniobras.svg`.
- `rafagas.png` y `rafagas.svg`.
- `combinado.png` y `combinado.svg`.

PNG sirve para pegar imágenes y SVG conserva trazos vectoriales. Si está activado **Comparar con tesis publicada**, las gráficas exportadas incluyen la misma referencia. Solo se exporta la condición activa; cambie a la otra para guardar sus gráficas.

La operación trabaja en segundo plano, muestra progreso y permite cancelar. Los archivos ya escritos se conservan; una cancelación puede dejar menos de seis archivos. No se generan reportes, tablas, MATLAB ni portadas. **Guardar** conserva por separado el proyecto JSON. Las entregas anteriores permanecen intactas.

Sin interfaz:

```powershell
python -B main.py --project examples/ejemplo_cessna.json --export
python -B main.py --project examples/ejemplo_cessna.json --case cessna_capitulo_19 --export
python -B main.py --project examples/ejemplo_libro.json --all
```

`--all` guarda las gráficas de cada condición en una carpeta independiente. El Live Script y el código de Overleaf se entregan aparte, no se añaden automáticamente a las exportaciones.
