# Manual de uso

## Abrir y seleccionar un ejemplo

En la instalación local, ejecute `Envolventes_de_Vuelo.exe` junto a `_internal/`. Desde el código, use `python -B main.py` con las dependencias instaladas. Se abre el Ejemplo 1.

El menú **Ejemplos** ofrece únicamente **Ejemplo 1** y **Ejemplo 2**. Cada uno carga un proyecto independiente. También pueden abrirse `examples/ejemplo_1.json` y `examples/ejemplo_2.json` con **Abrir**.

## Editar una condición

La tabla contiene, en este orden, nᵤ, nₙ, Wₙ, Wᵤ, W, S, W/S, N, coeficiente positivo, ρ, c, a, g y CLα. El significado de cada símbolo se consulta con **Resumen de variables** o en [VARIABLES.md](VARIABLES.md).

Edite el valor y seleccione su unidad. W/S es un resultado automático. N es el límite positivo seleccionado; los campos de categorías nᵤ/nₙ y pesos Wₙ/Wᵤ son referencias y no sustituyen W ni N.

En **Datos de cálculo** se definen el coeficiente negativo, el límite negativo, el modo de velocidades y Ub/Uc/Ud. Seleccione coeficientes constantes al introducir datos de otra aeronave: la tabla del Ejemplo 2 pertenece exclusivamente al caso del libro. Ub=0 omite VB.

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

**Exportar** crea una carpeta nueva `outputs/entrega_FECHA_HORA/`. Incluye el proyecto JSON, las tablas CSV, resultados JSON, las gráficas y reportes PDF/DOCX. Las fórmulas de los reportes se incorporan como imágenes; el texto y las tablas del DOCX son editables.

Para exportar sin abrir la interfaz:

```powershell
python -B main.py --project examples/ejemplo_1.json --export
python -B main.py --project examples/ejemplo_2.json --all
```

Con `--all` se generan los resultados de todas las condiciones y el informe de la condición activa. El proyecto histórico `data/proyecto_inicial.json` se conserva para reproducir la tarea inicial; no equivale a los dos ejemplos actuales.
