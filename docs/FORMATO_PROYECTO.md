# Formato de proyectos y resultados

Los proyectos se almacenan como JSON UTF-8 con `schema_version=1`. [Ejemplo Cessna](../examples/ejemplo_cessna.json) y [Ejemplo libro](../examples/ejemplo_libro.json) son archivos completos que pueden abrirse directamente.

## Campos del proyecto

| Campo | Contenido |
|---|---|
| `schema_version` | Entero 1 |
| `kind` | Habitualmente `worksheet`; puede faltar en proyectos históricos |
| `metadata` | Objeto de textos: título, estudiante, materia, profesor y fecha |
| `active_case` | ID de una condición existente |
| `cases` | Lista no vacía de condiciones con IDs distintos |

Cada condición incluye `id`, `name`, `aircraft`, `method`, `parameters` y, cuando corresponde, `assumptions`, `changes` y `applicability`. Los IDs usan minúsculas, números, guion o guion bajo, con un máximo de 64 caracteres; no se admiten rutas relativas en ellos.

El método actual es `niu`. En condiciones de hoja aparecen `worksheet`, `speed_mode` (`excel`, `subparte_c` o `manual`), `negative_rule` (`excel`, `normal`, `transport` o `manual`), `negative_end` (`constant`, `zero` u otra selección histórica), `aero_model` (`constant` o `niu_table`) y `coefficient_basis` (`CN` o `CL`). El Ejemplo libro usa `q_convention=niu_296`.

El Cessna incluye `reference_dataset="ipn_2007"`, `chord_mode="geometric"` y las condiciones `cessna_revisado` y `cessna_capitulo_19`. `span` y `Va_selected` son parámetros con unidades y procedencia. En modo geométrico, c se deriva de S/b; en modo `manual` se conserva la cuerda introducida. Va seleccionada no sustituye la intersección A.

`export_options` admite opciones booleanas `include_niu`, `include_appendix` e `include_matlab`. Cada condición puede conservar `appendix_review` con n3, n4, source, page y speed_mode (`selected` o `minimum`). Estas lecturas están separadas de los n3/n4 calculados por Niu.

## Parámetros y procedencia

```json
{
  "value": 4631,
  "unit": "lbf",
  "source": "Fuente del dato",
  "page": "",
  "status": "documentado",
  "notes": "Condición y supuestos",
  "original": {"value": 4631, "unit": "lbf", "source": "Fuente original"}
}
```

`value` admite números finitos o `null` si está pendiente. Se rechazan booleanos, NaN e infinitos. `original` conserva la lectura previa; su estructura puede contener más campos que en este ejemplo reducido. Una unidad no admitida bloquea su conversión. `metadata` requiere valores de texto.

Los símbolos internos principales son W, S, n_pos, n_neg, CN_pos, CN_neg, Vc, Vd, rho, chord, a, g, U_b, U_c, U_d y Cse. Se conservan las claves CN_pos/CN_neg también cuando el caso declara base CL; revise `coefficient_basis` para interpretarlas. Los campos `*_photo` conservan datos de referencia de la hoja y no deben confundirse con los valores efectivos del cálculo.

## Adaptación de versiones anteriores

`adapt_case()` adapta una copia para la interfaz vigente y conserva el método previo cuando cambia a Niu. No reescribe el archivo fuente automáticamente. Algunas selecciones ilustrativas anteriores pueden quedar pendientes de introducir. El motor histórico sigue siendo accesible al reproducir el proyecto original mediante el despacho correspondiente.

## Resultado común

| Clave | Contenido |
|---|---|
| `values` | Valores normalizados y derivados, velocidades, μ, Kg y factores |
| `parameters` | Tabla de entradas y procedencia |
| `equations` | Nombre, ecuación, sustitución, resultado, unidad y fuente |
| `checks` | Código, estado y detalle de verificaciones |
| `blocked` | Motivos por los que el cálculo no puede completarse |
| `points`, `intersections` | Puntos característicos y empalmes numéricos |
| `curves` | Listas de igual longitud para V, pérdida, maniobra, ráfaga y combinado |
| `assumptions` | Hipótesis de la condición |

El contraste Cessna añade `speed_rows`, `reference_rows`, `source_issues`, `academic_notice`, `reference_curves` y `reference_curve_note`. Las curvas publicadas son referencias separadas y no reemplazan `curves`.

No interprete un resultado con `blocked` como una envolvente completa. Los CSV usan UTF-8 con BOM para facilitar su apertura en Excel. `curvas.csv` conserva cada nodo de la malla, incluidas las intersecciones.

`huellas_fuentes.json` registra los PDF/JPG presentes en la raíz al exportar. Si el clon no contiene esos originales, el registro puede quedar vacío; esto no impide calcular los ejemplos. Los reportes históricos pueden citar documentos conservados únicamente en la estación original.

## Exportación vigente 4.3

Los campos de portada y `export_options` se conservan por compatibilidad con proyectos anteriores. La interfaz actual guarda exclusivamente las tres gráficas PNG/SVG de la condición seleccionada; esos campos no activan reportes ni archivos de cálculos. El proyecto JSON se guarda mediante Guardar, de forma independiente.
