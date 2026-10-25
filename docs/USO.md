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

## Exportar

**Exportar** trabaja en segundo plano, muestra el progreso y permite cancelar al terminar la etapa actual. Los archivos parciales de una cancelación se conservan identificados. Si faltan datos, la entrega completa se bloquea; puede guardar el proyecto para completarlo después.

**Exportar** crea una carpeta nueva `outputs/entrega_FECHA_HORA/`. Incluye el proyecto JSON, las tablas CSV, resultados JSON, las gráficas y reportes PDF/DOCX. Las fórmulas de los reportes se incorporan como imágenes; el texto y las tablas del DOCX son editables.

Para exportar sin abrir la interfaz:

```powershell
python -B main.py --project examples/ejemplo_cessna.json --all
python -B main.py --project examples/ejemplo_libro.json --all
```

Con `--all` se generan los resultados de todas las condiciones y el informe de la condición activa. El proyecto histórico `data/proyecto_inicial.json` se conserva para reproducir la tarea inicial; no equivale a los dos ejemplos actuales.

La cuerda se calcula con S/b cuando se selecciona el modo geométrico; se edita en modo introducido desde Datos de cálculo. Va seleccionada, A y Va mínimo base aparecen separadas en Resultados. El aviso de AR>7 identifica el alcance académico del Cessna. Consulte [la revisión vigente](cessna_tesis_20261024/README.md).
