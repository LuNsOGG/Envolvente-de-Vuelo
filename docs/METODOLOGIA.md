# Metodología de cálculo

La implementación vigente está en `src/calculations/niu.py` y usa el modelo cuasiestático del capítulo 3 de *Airframe Structural Design*, de Michael Chun-Yung Niu. Las selecciones de velocidad y límites de maniobra se preparan en `worksheet.py`. Los motores históricos siguen disponibles para reproducir proyectos anteriores.

## Unidades y coeficientes

| Magnitud | Unidad interna |
|---|---|
| W, peso | lbf |
| S, superficie | ft² |
| W/S, carga alar | lbf/ft² |
| ρ, densidad local | slug/ft³ |
| c, cuerda | ft |
| a, pendiente de la aeronave | rad⁻¹ |
| g | ft/s² |
| V | kt EAS |
| Ude | ft/s |
| n, μ, Kg, coeficientes | adimensional |

El módulo `units.py` convierte las entradas con unidades explícitas. Una pendiente por grado se multiplica por 180/π para obtenerla por radián. La densidad local ρ interviene en μ; la referencia ρ₀ define EAS. CN (fuerza normal) y CL (sustentación) se distinguen por caso. CLα se conserva como referencia y no sustituye silenciosamente la pendiente a de la aeronave.

## Maniobras y pérdida estática

Con unidades consistentes:

$$q=\frac12\rho_0 V_{ft/s}^2,\qquad n_{pérdida}=\frac{qSC}{W}.$$

En el Ejemplo 2 se conserva la convención redondeada del libro `q = V_kt²/296`. Los coeficientes de pérdida pueden ser constantes o variar por Mach según la tabla de ese ejemplo.

La rama positiva es el mínimo entre la curva de pérdida positiva y N. La rama negativa es el máximo entre pérdida negativa y límite negativo. Este último puede ser constante o cambiar linealmente desde Vc hasta el valor declarado en Vd.

Vs es la primera intersección positiva con n=1; A/Va, con N; G, con n−. Para los casos admitidos, las intersecciones de maniobra deben quedar antes de Vc.

## Ráfagas independientes

$$\mu=\frac{2(W/S)}{\rho c a g},\qquad K_g=\frac{0.88\mu}{5.3+\mu}.$$

$$\Delta n=\frac{K_g U_{de} V a}{498(W/S)},\qquad n=1\pm\Delta n.$$

La constante 498 corresponde a las unidades indicadas. No se utiliza con una mezcla de unidades SI e inglesas. Las ramas parten de n=1 en V=0 y pueden superar los límites de maniobra. `n3` y `n4` son los factores positivo y negativo en Vc; son resultados, no límites impuestos.

Con Ub=0, se utiliza Uc hasta Vc y se conectan linealmente los factores de C a D. Con Ub>0, se busca VB resolviendo:

$$n_{pérdida,+}(V_B)=1+\Delta n(V_B,U_b).$$

Se exige Ub≥Uc y VB<Vc. Hasta B se calcula la condición Ub; entre B, C y D se interpolan los factores de carga. En el modelo tabulado, a y Kg se evalúan con la velocidad correspondiente.

## Combinado y malla numérica

El contorno superior es `min(pérdida+, max(maniobra+, ráfaga+))`. El inferior es `max(pérdida−, min(maniobra−, ráfaga−))`. La demanda de ráfaga sin recortar permanece visible en las gráficas.

La malla de cálculo utiliza 601 muestras por defecto e incorpora las velocidades características, nodos aerodinámicos e intersecciones detectadas. Las raíces se localizan mediante cambios de signo en 600 intervalos y 55 pasos de bisección; este procedimiento no garantiza detectar una raíz tangencial sin cambio de signo que no coincida con un nodo. Las velocidades de intersección se redondean a once decimales para incorporarlas a la malla.

## Condiciones de los ejemplos

| Elección | Ejemplo 1 | Ejemplo 2 |
|---|---|---|
| Base de coeficiente | CN | CL |
| Coeficientes | Constantes; CN+=1.46, CN−=−1.35 | Tabla por Mach, CL(0)=±1.3 |
| Maniobra | +3.8/−1.9 | +2.5/−1; rama negativa llega a cero en Vd |
| Vc, Vd | 17 y 24 multiplicados por √(max(N,3.8)W/S) | 325 y 400 kt EAS |
| Ub/Uc/Ud | 0/50/25 ft/s | 66/50/25 ft/s |
| Altitud | No inferida de ρ | 10000 ft como dato de referencia |

En el Ejemplo 1, CN− y Uc/Ud son aproximaciones o hipótesis autorizadas del ejercicio. Las velocidades base conservan la elección de la hoja Excel sin demostrar la aplicabilidad normativa del apéndice A.

En el Ejemplo 2, a(M) se interpola con pendientes 5.22, 5.25, 5.25, 5.32, 5.37, 5.44, 5.60, 5.74, 5.95 y 6.78/rad para V=0,50,100,150,200,250,300,325,350,400 kt de la referencia Cse=548.6 kt EAS. El dígito de 400 kt es ambiguo en el escaneo; 6.78 es la interpretación documentada. Los CLmax de 325/350/400 kt (1.17/1.13/1.02) son lecturas aproximadas de una figura. Se bloquea la extrapolación fuera del intervalo de Mach.

W/S se obtiene de W y S exactos: 88000/1200=73.333333, sin forzarlo al 73.2 impreso. Las discrepancias por redondeo se conservan visibles en [VALIDACION.md](VALIDACION.md).

## Alcance

No se resuelven respuesta dinámica de ráfaga, aeroelasticidad, flutter, cargas locales ni resistencia. El combinado incorpora la pérdida estática como criterio del modelo; esto no reemplaza un análisis dinámico. La normativa histórica citada y la aerodinámica de cada ejemplo requieren evaluación propia antes de aplicarse a otra aeronave. La tesis y la variante exacta del Cessna del ejercicio original siguen sin documentarse.
