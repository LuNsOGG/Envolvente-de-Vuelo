"""Casos IPN y contraste trazable: los valores publicados no gobiernan el motor."""
from copy import deepcopy
from math import sqrt
from .cases import parameter
from .units import convert

THESIS = 'Tesis IPN, Diseño de la caja de torsión del ala de una aeronave cuatriplaza (2007)'
# dato, valor publicado, unidad, página, clave del resultado revisado
PUBLISHED = [
 ('Peso máximo de la ficha',4000,'lbf','12','W'),
 ('Peso usado en §1.9',4631,'lbf','32','W'),
 ('Peso sustituido en ráfagas',4016,'lbf','37','W'),
 ('Superficie alar',181,'ft²','12, 32','S'),
 ('CN máximo positivo',1.45816142,'1','29, 34','CN_pos'),
 ('CN mínimo: simetría de la tabulación',-1.45816142,'1','35','CN_neg'),
 ('CN mínimo de la polar 2D',-.8381569,'1','28','CN_neg'),
 ('Cuerda sustituida en ráfagas',4.26,'ft','37','chord'),
 ('Densidad de ráfagas',.0023769,'slug/ft³','37','rho'),
 ('Vc mínimo base',167.62,'kt EAS','33','Vc_min_base'),
 ('Vc seleccionado',170,'kt EAS','33','Vc'),
 ('Vd mínimo base',236.62,'kt EAS','33','Vd_min_base'),
 ('Vd seleccionado',240,'kt EAS','33','Vd'),
 ('Va mínimo base',147.88,'kt EAS','33','Va_min_base'),
 ('Va seleccionado',150,'kt EAS','33','Va_selected'),
 ('Pérdida Vs',71.92,'kt EAS','34','Vs'),
 ('Intersección A',140.19789,'kt EAS','35','V_A_stall'),
 ('Intersección G',99.1348786,'kt EAS','35','V_G_stall'),
 ('Relación de masas',1296.22,'1','37','mu'),
 ('Alivio de ráfaga',.876,'1','37','Kg'),
 ('n3 del apéndice: lectura adoptada',3.8,'1','34','n3'),
 ('n4 del apéndice: lectura adoptada',-1.9,'1','34','n4'),
 ('Ráfaga C positiva: tabla publicada',1.634,'1','37','n_gust_c_pos'),
 ('Ráfaga C negativa: tabla publicada',.366,'1','37','n_gust_c_neg'),
 ('Ráfaga D positiva: tabla publicada',1.47,'1','37','n_gust_d_pos'),
 ('Ráfaga D negativa: tabla publicada',.53,'1','37','n_gust_d_neg'),
]
ISSUES = [
 'Tabla de ráfagas (pp.37–38): los rótulos nc/nd y positivo/negativo son inconsistentes. Para contrastar se interpretan las parejas 1.634/0.366 y 1.47/0.53 como C y D, apoyándose en la figura 1.15; no se consideran resultados físicos validados.',
 'Pesos (pp.12,31,32,37): la ficha declara 4000 lb; §1.9 usa 4631 lb y la sustitución de ráfagas usa 4016 lb. Se conservan como lecturas distintas.',
 'Categorías (p.31): 4631.57×3.8≈17600, mientras 3454.54×4.4≈15200. No constituyen una pareja que satisfaga Wn nn = Wu nu. Los pesos de referencia revisados sí satisfacen esa igualdad; no acreditan certificación en utilidad.',
 'Velocidades (pp.33,35): mínimos base, velocidades seleccionadas y la intersección A son magnitudes diferentes. Se conservan por separado, sin sustituir A por Va seleccionada.',
 'Ráfagas (p.37): la expresión impresa omite a en el incremento de carga. El motor usa Δn=Kg U V a/[498(W/S)] y la pendiente por radián; no copia μ=1296.22 ni Kg=0.876.',
 'Pendiente (p.37): 0.105 no tiene unidad declarada. Interpretarla por grado es una hipótesis editable; equivale a 6.01605685/rad. No se ha validado como pendiente del avión completo.',
 'Polar (pp.25–29): NACA 2412 2D, Mach 0.5 y Re=4e6. Se emplean CN+=1.45816142 y CN−=-0.8381569 como idealización académica constante; no son una polar 3D validada ni una tabla universal por Mach.',
 'Cuerda (pp.12,37): 4.26 ft no coincide con S/b de la ficha. La condición revisada usa c=S/b; el modo manual permite introducir otra cuerda con su fuente.',
 'Normativa: la geometría publicada produce AR≈8.73, superior al máximo de 7 de A23.1 (edición histórica consultada de 2016). El uso de velocidades y límites del apéndice es académico y no demuestra su aplicabilidad.',
 'Ráfagas 50/25 ft/s: son hipótesis de diseño del recálculo, no datos medidos de la tesis. La lectura adoptada n3=3.8/n4=-1.9 de A1/A2 se conserva solo como referencia independiente.',
 'La tesis se basa en un Cessna 210; no es un AFM/POH aprobado ni identifica suficientemente una variante certificada. La pérdida estática no sustituye un análisis de ráfaga dinámica.',
]

def cessna_project():
    from .worksheet import worksheet_project
    project=worksheet_project(False,'Ejemplo Cessna')
    base=project['cases'][0]
    base.update(id='cessna_revisado',name='Revisado · ficha 4000 lb',aircraft='Ejemplo Cessna',example=1,
                reference_dataset='ipn_2007',category='normal',speed_mode='manual',negative_rule='excel',
                negative_end='constant',aero_model='constant',coefficient_basis='CN',chord_mode='geometric')
    data={
      'W':(4000,'lbf','12','documentado','Peso máximo de la ficha; distinto de los pesos usados posteriormente.'),
      'S':(181,'ft²','12,32','documentado','Superficie de la ficha y del capítulo 1.9.'),
      'span':(12.12,'m','12','documentado','Envergadura; AR y cuerda geométrica se calculan con esta magnitud.'),
      'n_pos':(3.8,'1','31–32','elección académica','Factor normal conservado del ejercicio histórico.'),
      'nu_photo':(4.4,'1','31','referencia','Factor de utilidad, no asigna categoría a la aeronave.'),
      'nn_photo':(3.8,'1','31','referencia','Factor normal de referencia.'),
      'Wn_photo':(4000,'lbf','12,31','recalculado','Referencia normal coherente con la ficha.'),
      'Wu_photo':(4000*3.8/4.4,'lbf','31','recalculado','Wn nn/nu; corrige la pareja incompatible sin acreditar categoría utilidad.'),
      'CN_pos':(1.45816142,'1','29,34','idealización 2D','Máximo de la tabla del perfil; no coeficiente 3D validado.'),
      'CN_neg':(-.8381569,'1','28','idealización 2D','Mínimo tabulado; sustituye la simetría de la gráfica y la anterior aproximación -1.35.'),
      'rho':(.0023769,'slug/ft³','37','unidad interpretada','Densidad usada en la sustitución de ráfagas, sin inferir altitud.'),
      'chord':(181/(12.12/.3048),'ft','12','calculado','Cuerda geométrica S/b. La sustitución publicada usa 4.26 ft.'),
      'a':(.105,'1/deg','37','hipótesis','La tesis no declara unidad. Interpretación por grado, editable; se convierte a /rad.'),
      'g':(32.2,'ft/s²','37','documentado','Valor usado en la sustitución.'),
      'Vc':(170,'kt EAS','33','selección publicada','Velocidad seleccionada, distinta del mínimo base.'),
      'Vd':(240,'kt EAS','33','selección publicada','Velocidad seleccionada, distinta del mínimo base.'),
      'Va_selected':(150,'kt EAS','33','selección publicada','Conservada por separado de la intersección A y el mínimo base.'),
      'U_c':(50,'ft/s','','hipótesis','Intensidad de diseño elegida para el recálculo cuasiestático; no medida.'),
      'U_d':(25,'ft/s','','hipótesis','Intensidad de diseño elegida para el recálculo cuasiestático; no medida.'),
      'U_b':(0,'ft/s','','elección académica','Omite VB en este ejercicio.'),
    }
    for key,(value,unit,page,status,note) in data.items():
        base['parameters'][key]=parameter(value,unit,THESIS if page else 'Hipótesis del recálculo',status,note)
        base['parameters'][key]['page']=page
    base['assumptions']=[
      'Condición revisada basada en la ficha de la tesis IPN: W=4000 lbf. El capítulo 1.9 usa 4631 lbf; se conserva como otra condición seleccionable.',
      'Velocidades seleccionadas de la tesis: Vc=170, Vd=240 y Va sel.=150 kt EAS. Los mínimos base de A3 se muestran como referencia académica independiente.',
      'CN positivo y negativo de la polar 2D NACA 2412 a Mach 0.5 y Re=4e6; se idealizan constantes para el ejercicio. No validan el comportamiento del avión completo.',
      'a=0.105 por grado es una interpretación explícita y editable. Uc/Ud=50/25 ft/s son hipótesis; no se deduce una altitud a partir de la densidad.',
      'Se usa c=S/b de la ficha; la cuerda 4.26 ft de la sustitución de ráfagas queda registrada en el contraste. CLα no se rellena con el antiguo valor del Excel por carecer de confirmación en la tesis.',
      'N=3.8 y n−=-1.9 conservan la elección académica del apéndice. AR>7 impide afirmar la aplicabilidad directa de A23.1. Ráfagas de Niu y lectura A1/A2 publicada se mantienen diferenciadas.',
      'El contorno combinado usa pérdida estática; no es una envolvente operativa aprobada ni un análisis dinámico.']
    comparison=deepcopy(base)
    comparison.update(id='cessna_capitulo_19',name='Comparación · cap. 1.9, 4631 lb')
    comparison['parameters']['W']=parameter(4631,'lbf',THESIS,'transcrito','Peso del capítulo 1.9; supera las 4000 lb de la ficha y no se adopta como MTOW aprobado.')
    comparison['parameters']['W']['page']='32'
    comparison['parameters']['Wn_photo']['value']=4631
    comparison['parameters']['Wu_photo']['value']=4631*3.8/4.4
    comparison['parameters']['Wn_photo']['notes']='Referencia reconstruida para W=4631; no es la pareja incompatible publicada.'
    comparison['parameters']['Wu_photo']['notes']='4631×3.8/4.4; pareja coherente para esta comparación.'
    for key in ['Wn_photo','Wu_photo']:
        comparison['parameters'][key]['original']=deepcopy(comparison['parameters'][key])
    comparison['assumptions'][0]='Comparación con W=4631 lbf de §1.9. Se mantienen las correcciones de unidades, polar, cuerda y velocidades seleccionadas; no reproduce errores aritméticos ni acredita un peso máximo real.'
    project.update(cases=[base,comparison],active_case=base['id'])
    project['metadata']['title']='Ejemplo Cessna · tesis IPN y recálculo'
    return project

def augment_review(case,result):
    """Añade referencia y diagnósticos; nunca altera las curvas ni el caso."""
    if case.get('reference_dataset')!='ipn_2007':return
    v=result['values'];p=case['parameters']
    def read(key,dimension):
        q=p.get(key,{})
        try:return convert(q.get('value'),q.get('unit',''),dimension)
        except (ValueError,TypeError):return None
    ws=v.get('W_S');N=v.get('n_pos');span=read('span','length')
    if span and span>0 and v.get('S',0)>0:
        v['span']=span;v['AR']=span**2/v['S'];v['chord_geometric']=v['S']/span
        for name,formula,key,unit in [('Cuerda geométrica','c = S/b','chord_geometric','ft'),('Alargamiento alar','AR = b²/S','AR','1')]:
            result['equations'].append(dict(nombre=name,ecuación=formula,sustitución=f'S={v["S"]:.9g} ft²; b={span:.9g} ft',resultado=v[key],unidad=unit,fuente='Tesis IPN, tabla 1.1; cálculo geométrico'))
    va=read('Va_selected','speed')
    if va is not None:v['Va_selected']=va
    if ws and N and min(ws,N)>0:
        for key,k in [('Vc_min_base',17),('Vd_min_base',24),('Va_min_base',15),('Vf_min_base',11)]:
            v[key]=k*sqrt(max(N,3.8)*ws)
            result['equations'].append(dict(nombre=key,ecuación=f'{k} sqrt(max(N,3.8) W/S)',
              sustitución=f'{k} × sqrt(max({N:g},3.8) × {ws:.9g})',resultado=v[key],unidad='kt EAS',fuente='Apéndice A histórico, Fig. A3; referencia académica, AR>7'))
    result['speed_rows']=[dict(magnitud=label,valor=v.get(key),unidad='kt EAS',criterio=note) for key,label,note in [
      ('Vs','Vs','Pérdida positiva a 1 g'),('V_A_stall','A','Intersección de pérdida positiva con N'),
      ('Va_min_base','Va mínimo base','15 sqrt(max(N,3.8) W/S); referencia A3'),
      ('Va_selected','Va seleccionada','Dato independiente de A y del mínimo base'),
      ('Vc_min_base','Vc mínimo base','Referencia A3'),('Vc','Vc seleccionada','Velocidad efectiva para Uc'),
      ('Vd_min_base','Vd mínimo base','Referencia A3'),('Vd','Vd seleccionada','Velocidad efectiva para Ud')]]
    result['reference_rows']=[dict(dato=label,tesis=value,recalculado=v.get(key),unidad=unit,pagina=page,
       diferencia=None if v.get(key) is None else v[key]-value) for label,value,unit,page,key in PUBLISHED]
    result['source_issues']=list(ISSUES)
    result['academic_notice']=('Uso académico · AR>7: no se demuestra aplicabilidad del Apéndice A.' if v.get('AR',0)>7 else 'Uso académico · Apéndice A: aplicabilidad pendiente de comprobación completa.')
    def check(code,state,detail):result['checks'].append(dict(código=code,estado=state,detalle=detail))
    if 'AR' in v:check('A23.1 AR','NO APLICA' if v['AR']>7 else 'PENDIENTE',f'AR=b²/S={v["AR"]:.6f}; límite histórico 7. El resto de condiciones de aplicabilidad tampoco se acredita automáticamente.')
    for selected,minimum in [('Vc','Vc_min_base'),('Vd','Vd_min_base'),('Va_selected','Va_min_base')]:
        if selected in v and minimum in v:check('VELOCIDADES '+selected,'OK' if v[selected]>=v[minimum] else 'ADVERTENCIA',f'Seleccionada {v[selected]:.6f}; mínimo base académico {v[minimum]:.6f} kt EAS. A permanece separado.')
    weights=[read(k,d) for k,d in [('Wn_photo','weight'),('Wu_photo','weight'),('nn_photo','ratio'),('nu_photo','ratio')]]
    if all(x is not None for x in weights):
        wn,wu,nn,nu=weights;check('PAREJA nW','OK' if abs(wn*nn-wu*nu)<1e-6*max(abs(wn*nn),1) else 'ADVERTENCIA',f'Referencias actuales: Wn nn={wn*nn:.6f}; Wu nu={wu*nu:.6f} lbf. No sustituyen el peso activo W.')
    if v.get('W',0)>4000:check('PESO DE FICHA','ADVERTENCIA','La condición supera 4000 lb de la tabla 1.1. Es una comparación con §1.9, no un MTOW aprobado.')
    check('POLAR 2D','HIPÓTESIS','Referencias 2D de la tesis: CN+=1.45816142 y CN−=-0.8381569. Los coeficientes efectivos figuran en los parámetros actuales y requieren justificar la condición del avión.')
    check('PENDIENTE Y RÁFAGA','HIPÓTESIS','La pendiente y las intensidades son hipótesis editables del recálculo, no datos aeronáuticos confirmados; ver los parámetros efectivos y sus unidades.')
    # Curvas PUBLICADAS: reconstrucción de la tabla, no resultado del motor.
    xs=sorted(set([236.62*i/400 for i in range(401)]+[71.92,99.1348786,140.19789,147.88,150,167.62,170,236.62]))
    def dn(x):
        if x<=167.62:return .634*x/167.62
        return .634+(.47-.634)*(x-167.62)/(236.62-167.62)
    source_p=[min((x/71.92)**2,3.8) for x in xs]
    source_n=[max(-(x/71.92)**2,-1.9) for x in xs]
    result['reference_curves']=dict(V=xs,man_pos=source_p,man_neg=source_n,
       gust_pos=[1+dn(x) for x in xs],gust_neg=[1-dn(x) for x in xs],combined_pos=source_p,combined_neg=source_n)
    result['reference_curve_note']='Tesis publicada: reconstrucción de tablas pp.35–38, con Vc mínimo 167.62 y Vd mínimo 236.62. Ráfagas 1.634/0.366 y 1.47/0.53 tomadas como referencias tabuladas; no se consideran un cálculo físico validado.'
