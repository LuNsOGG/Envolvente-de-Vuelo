# Variables

La aplicación incluye este catálogo en **Resumen de variables**. Las unidades efectivas se muestran junto a las entradas y en Datos de cálculo.

| Símbolo | Nombre | Significado |
|---|---|---|
| nᵤ | Factor de utilidad | Límite positivo de categoría utilidad; referencia, no selecciona N. |
| nₙ | Factor normal | Límite positivo de categoría normal; referencia, no selecciona N. |
| Wₙ | Peso normal | Peso asociado a categoría normal; no sustituye W. |
| Wᵤ | Peso de utilidad | Peso asociado a categoría utilidad; no sustituye W. |
| W | Peso | Peso total de la condición que se calcula. |
| S | Superficie alar | Área del ala usada para calcular la carga alar. |
| W/S | Carga alar | Peso por unidad de superficie del ala; calculado. |
| N, n+ | Límite positivo | Factor máximo de maniobra positiva seleccionado. |
| n− | Límite negativo | Factor límite de maniobra negativa; regla en Datos de cálculo. |
| CN máx./mín. | Coeficiente normal | Fuerza normal al eje de referencia dividida por qS; Ejemplo 1. |
| CL máx./mín. | Coeficiente de sustentación | Sustentación dividida por qS; Ejemplo 2. No es intercambiable con CN. |
| ρ | Densidad local | Densidad del aire de la condición; interviene en μ. |
| ρ₀ | Densidad de referencia | Densidad estándar que define la velocidad equivalente EAS. |
| c | Cuerda media | Longitud de referencia del ala utilizada en μ; 13 ft en el libro. |
| a | Pendiente de la aeronave | Cambio de coeficiente por ángulo de ataque; entra en las ráfagas. |
| a₀ | Pendiente a Mach cero | Base de a(M) cuando se usa la tabla del Ejemplo 2. |
| CLα | Pendiente de sustentación de referencia | Dato independiente: en el libro corresponde al ala. No reemplaza a automáticamente. |
| g | Gravedad | Aceleración usada para convertir peso a masa en μ. |
| Vc | Crucero de diseño | Velocidad del punto de ráfaga Uc; automática o introducida. |
| Vd | Picada de diseño | Velocidad máxima del diagrama, donde se aplica Ud. |
| Vs | Pérdida a 1 g | Intersección de la curva de pérdida positiva con n=1. |
| A / Va | Maniobra | Intersección de pérdida positiva con el límite N. |
| G | Maniobra negativa | Intersección de pérdida negativa con el límite n−. |
| VB | Turbulencia | Intersección de pérdida positiva con 1+Δn para Ub; calculada si Ub>0. |
| Ub, Uc, Ud | Intensidad de ráfaga | Velocidad vertical del aire en VB, Vc y Vd; ft/s. Ub=0 omite VB. |
| μ | Relación de masas | Relaciona la inercia del avión con la acción de la masa de aire. |
| Kg | Alivio de ráfaga | Factor que reduce la respuesta respecto de la ráfaga ideal. |
| Δn | Incremento de carga | Cambio producido por una ráfaga; n=1±Δn. |
| n3, n4 | Factores de ráfaga en Vc | Resultados 1+Δn y 1−Δn; independientes de N y n−. |
| h | Altitud | Altitud de referencia. Al editarla, compruebe también ρ, Cse y las intensidades. |
| Cse | Sonido equivalente | Permite calcular Mach=V_EAS/Cse para la tabla del libro. |
| q | Presión dinámica | Presión asociada a la velocidad; q=ρ₀V²/2 en unidades consistentes. |
| EAS | Velocidad equivalente | Velocidad referida a densidad estándar; eje horizontal en nudos. |
