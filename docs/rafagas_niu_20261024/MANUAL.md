# Calculadora de envolventes · 24 de octubre de 2026

Abra `Envolventes_de_Vuelo.exe` en la raíz. El archivo y su carpeta `_internal` deben permanecer juntos.

## Uso

1. Pulse **Ejemplos** y elija **Ejemplo 1** o **Ejemplo 2**.
2. Edite los valores y unidades de la tabla. Las vistas **Maniobras**, **Ráfagas** y **Combinado** se recalculan juntas.
3. En **Datos de cálculo** cambie el coeficiente negativo, el límite negativo, Vc/Vd y las intensidades Ub/Uc/Ud. Ub=0 omite el punto VB.
4. **Resumen de variables** muestra símbolo, nombre y significado. Las unidades están junto a cada entrada; las de los datos adicionales aparecen en sus etiquetas.
5. **Resultados** conserva fórmulas, resultados e hipótesis. **Guardar** conserva un proyecto reutilizable. **Exportar** crea gráficas, tablas, JSON y reportes PDF/DOCX, incluido el resumen de variables.

Al cargar otro ejemplo o proyecto, una edición pendiente se conserva como recuperación. Los archivos guardados no se reemplazan: guardar con un nombre existente crea otra versión.

## Ejemplo 1

Datos de la hoja Excel: W=4631 lbf, S=181 ft², N=3.8, CN positivo=1.46 y CN negativo=-1.35 como aproximación autorizada. Se usan ρ=0.0023 slug/ft³, c=4.26 ft, a=0.105/grado y g=32.2 ft/s². CLα=0.11/grado se mantiene como referencia independiente.

Las velocidades se calculan con las expresiones base de Fig. A3 de FAR 23 histórico: Vc=17√[max(N,3.8)W/S] y Vd=24√[max(N,3.8)W/S]. El límite de maniobra negativo es -0.5N. Son elecciones del ejercicio, no una demostración de aplicabilidad del apéndice A.

Para poder calcular ráfagas físicas se seleccionan **Uc=50 y Ud=25 ft/s** como hipótesis del ejercicio. Son editables y no se presentan como datos de la fotografía. No se infiere una altitud a partir de ρ.

| Resultado | Valor |
|---|---:|
| W/S | 25.585635 lbf/ft² |
| Vc / Vd | 167.625012 / 236.647076 kt EAS |
| Vs / intersección A | 71.946288 / 140.249135 kt EAS |
| μ / Kg | 26.960067 / 0.735425 |
| n3 / n4, ráfagas en Vc | 3.910272 / -1.910272 |
| Ráfagas en Vd | 3.054310 / -1.054310 |

Los factores de maniobra siguen siendo +3.8/-1.9. El contorno combinado conserva la demanda de ráfaga cuando gobierna.

## Ejemplo 2

Avión comercial genérico de Niu, capítulo 3, ejemplo 2 de §3.11, páginas impresas 74–77: W=88000 lbf, S=1200 ft², h=10000 ft, ρ=0.00176 slug/ft³, c=13 ft, Vc=325 y Vd=400 kt EAS. Límites de maniobra +2.5/-1, con el límite negativo llegando a cero en Vd.

Aquí se usa **CL de sustentación**, no CN normal. CLmax(0)=1.3 y CLmin(0)=-1.3 por la simetría supuesta en el libro. a(0)=5.22/rad es la pendiente del avión; CLα=4.75/rad corresponde al ala. Los cuatro campos de utilidad/normal no aplican al ejemplo de transporte y quedan vacíos.

Se interpola la tabla de la Fig. 3.11.6 por Mach, con Cse=548.6 kt EAS. a(Vc)=5.74/rad; a(Vd)=6.78/rad. En la fila de 400 kt el dígito impreso es ambiguo: 6.78 es coherente con 5.22×1.300≈6.786 y μ≈29.3. Se documenta esa interpretación, sin copiar una cifra incompatible con las demás columnas.

La columna CLmax termina en 300 kt. Para continuar la curva estática se usa una lectura aproximada de Fig.3.11.4: CLmax=1.17,1.13,1.02 a 325,350,400 kt respectivamente. Se interpola linealmente entre puntos. Es una reproducción numérica aproximada de las figuras, no una tabla aerodinámica de precisión. El programa bloquea la extrapolación por encima del último Mach disponible.

q=V²/296 como en el libro. W/S se calcula exactamente como 88000/1200=73.333333; no se fuerza al 73.2 impreso. La respuesta usa Ub/Uc/Ud=66/50/25 ft/s. VB se obtiene en la intersección de pérdida positiva y la condición Ub de Fig.3.11.7.

| Resultado | Calculadora | Libro |
|---|---:|---:|
| Δn en Vc | 1.949653 | 1.95 |
| Δn en Vd | 1.383930 | 1.382 |
| VB | 211.305325 kt EAS | Construcción gráfica |
| Vs | 130.216861 kt EAS | Construcción gráfica |
| Intersección A | 207.773905 kt EAS | Construcción gráfica |

Las diferencias se deben a redondeos e interpolaciones de la fuente. Las filas del libro no tienen todas la misma precisión. Para otra aeronave, **Nuevo** inicia datos vacíos o **Datos de cálculo → Coeficientes constantes** permite trabajar con coeficientes propios. Cambiar h no modifica automáticamente ρ, Cse ni U: esos datos se introducen explícitamente.

## Ecuaciones y gráficas

- μ = 2(W/S)/(ρ c a g).
- Kg = 0.88 μ/(5.3+μ).
- Δn = Kg Ude V a/[498(W/S)]. V en kt EAS, U en ft/s y a por radián.
- Ráfagas: n=1±Δn. n3 y n4 son sus valores en Vc.
- Con Ub>0, se calcula VB y se conectan linealmente los factores en B, C y D. Con Ub=0, se utiliza Uc hasta Vc y se conecta C con D.
- Maniobra: límites positivo/negativo y curvas de pérdida estática.
- Combinado: extremos de maniobra y ráfaga, limitados por la curva de pérdida estática. Las demandas de ráfaga sin recortar permanecen dibujadas.

La pendiente introducida por grado se multiplica por 180/π. En el Ejemplo 2, a(M) y Kg(M) varían; no se reutiliza a(Vc) para Vd. Las raíces numéricas y los puntos de empalme se incluyen en la malla de las gráficas y los CSV.

El modelo es cuasiestático; no resuelve ráfaga dinámica, respuesta aeroelástica ni certificación. La fuente revisada está en `Chapter3.pdf`; el análisis previo se conserva en `outputs/revision_capitulo3_20261023_233141/INFORME_REVISION.md`.

## Conservación y pruebas

El código anterior se copió completo a `archivo_desarrollo/antes_rafagas_niu_20261024_000943`. El EXE y las dependencias anteriores se conservan juntos en una carpeta nueva antes de instalar la compilación actual. No se usan operaciones de borrado ni limpieza de compilaciones.

Pruebas: `outputs/qa/niu_pruebas_20261024_final.txt` y su XML. La comprobación del EXE instalado crea otra carpeta `outputs/qa/niu_exe_*`, con su ruta exacta, resultados, capturas y exportaciones.
