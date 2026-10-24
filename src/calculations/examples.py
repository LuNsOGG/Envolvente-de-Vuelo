"""Dos casos independientes; cargarlos nunca modifica un proyecto guardado."""
from .worksheet import worksheet_project
from .cases import parameter


def example_project(number):
    if number==1:return worksheet_project()
    if number!=2:raise ValueError('Ejemplo desconocido')
    project=worksheet_project(False,'Ejemplo 2');c=project['cases'][0]
    c.update(name='Ejemplo 2',example=2,category='transporte',speed_mode='manual',negative_rule='transport',
             negative_end='zero',aero_model='niu_table',coefficient_basis='CL',q_convention='niu_296')
    source='Niu, cap. 3, ejemplo 2 de §3.11, pp.74–77'
    data={'W':(88000,'lbf'),'S':(1200,'ft²'),'n_pos':(2.5,'1'),'CN_pos':(1.3,'1'),
          'CN_neg':(-1.3,'1'),'rho':(.00176,'slug/ft³'),'chord':(13,'ft'),
          'a':(5.22,'1/rad'),'g':(32.2,'ft/s²'),'CLalpha_photo':(4.75,'1/rad'),
          'altitude':(10000,'ft'),'Vc':(325,'kt EAS'),'Vd':(400,'kt EAS'),
          'U_b':(66,'ft/s'),'U_c':(50,'ft/s'),'U_d':(25,'ft/s'),'Cse':(548.6,'kt EAS')}
    for key,(value,unit) in data.items():c['parameters'][key]=parameter(value,unit,source,'documentado')
    c['assumptions']=[
        'Avión comercial genérico del ejemplo 2, sección 3.11 de Niu: W=88000 lbf, S=1200 ft², altitud 10000 ft, Vc=325 y Vd=400 kt EAS.',
        'Se usa CL, no CN. CLmax(0)=1.3 y CLmin(0)=-1.3, simetría supuesta explícitamente en el libro. a(0)=5.22/rad es de la aeronave; CLα=4.75/rad es del ala.',
        'Pendiente a(M) interpolada de Fig.3.11.6. En V=400 kt se usa 6.78/rad: 5.22×1.300≈6.786 y μ≈29.3; el dígito de la columna a es ambiguo.',
        'CLmax tabulado hasta 300 kt. Para 325,350,400 kt, lectura aproximada de Fig.3.11.4: 1.17,1.13,1.02. Interpolación lineal entre puntos; no extrapolación fuera de M=0…400/548.6.',
        'q=V²/296, como en el libro. W/S se calcula exactamente: 73.333333 lbf/ft²; el valor impreso 73.2 es redondeado/inconsistente.',
        'Ub/Uc/Ud=66/50/25 ft/s. VB se construye con la intersección pérdida-ráfaga de máxima intensidad de Fig.3.11.7; no es una velocidad operativa certificada.',
        'Límites de maniobra +2.5/-1; la rama negativa llega a cero en Vd. Los campos de categorías normal/utilidad no corresponden a este avión y quedan vacíos.',
        'Al editar este caso se conservan sus tablas aerodinámicas. Para otra aeronave seleccione coeficientes constantes o introduzca su propia condición.']
    return project


VARIABLES=[
 ('nᵤ','Factor de utilidad','Límite positivo de categoría utilidad; referencia, no selecciona N.'),
 ('nₙ','Factor normal','Límite positivo de categoría normal; referencia, no selecciona N.'),
 ('Wₙ','Peso normal','Peso asociado a categoría normal; no sustituye W.'),
 ('Wᵤ','Peso de utilidad','Peso asociado a categoría utilidad; no sustituye W.'),
 ('W','Peso','Peso total de la condición que se calcula.'),
 ('S','Superficie alar','Área del ala usada para calcular la carga alar.'),
 ('W/S','Carga alar','Peso por unidad de superficie del ala; calculado.'),
 ('N, n+','Límite positivo','Factor máximo de maniobra positiva seleccionado.'),
 ('n−','Límite negativo','Factor límite de maniobra negativa; regla en Datos de cálculo.'),
 ('CN máx./mín.','Coeficiente normal','Fuerza normal al eje de referencia dividida por qS; Ejemplo 1.'),
 ('CL máx./mín.','Coeficiente de sustentación','Sustentación dividida por qS; Ejemplo 2. No es intercambiable con CN.'),
 ('ρ','Densidad local','Densidad del aire de la condición; interviene en μ.'),
 ('ρ₀','Densidad de referencia','Densidad estándar que define la velocidad equivalente EAS.'),
 ('c','Cuerda media','Longitud de referencia del ala utilizada en μ; 13 ft en el libro.'),
 ('a','Pendiente de la aeronave','Cambio de coeficiente por ángulo de ataque; entra en las ráfagas.'),
 ('a₀','Pendiente a Mach cero','Base de a(M) cuando se usa la tabla del Ejemplo 2.'),
 ('CLα','Pendiente de sustentación de referencia','Dato independiente: en el libro corresponde al ala. No reemplaza a automáticamente.'),
 ('g','Gravedad','Aceleración usada para convertir peso a masa en μ.'),
 ('Vc','Crucero de diseño','Velocidad del punto de ráfaga Uc; automática o introducida.'),
 ('Vd','Picada de diseño','Velocidad máxima del diagrama, donde se aplica Ud.'),
 ('Vs','Pérdida a 1 g','Intersección de la curva de pérdida positiva con n=1.'),
 ('A / Va','Maniobra','Intersección de pérdida positiva con el límite N.'),
 ('G','Maniobra negativa','Intersección de pérdida negativa con el límite n−.'),
 ('VB','Turbulencia','Intersección de pérdida positiva con 1+Δn para Ub; calculada si Ub>0.'),
 ('Ub, Uc, Ud','Intensidad de ráfaga','Velocidad vertical del aire en VB, Vc y Vd; ft/s. Ub=0 omite VB.'),
 ('μ','Relación de masas','Relaciona la inercia del avión con la acción de la masa de aire.'),
 ('Kg','Alivio de ráfaga','Factor que reduce la respuesta respecto de la ráfaga ideal.'),
 ('Δn','Incremento de carga','Cambio producido por una ráfaga; n=1±Δn.'),
 ('n3, n4','Factores de ráfaga en Vc','Resultados 1+Δn y 1−Δn; independientes de N y n−.'),
 ('h','Altitud','Altitud de referencia. Al editarla, compruebe también ρ, Cse y las intensidades.'),
 ('Cse','Sonido equivalente','Permite calcular Mach=V_EAS/Cse para la tabla del libro.'),
 ('q','Presión dinámica','Presión asociada a la velocidad; q=ρ₀V²/2 en unidades consistentes.'),
 ('EAS','Velocidad equivalente','Velocidad referida a densidad estándar; eje horizontal en nudos.'),
]
