"""Motor independiente de Qt, Matplotlib y archivos.

Dos criterios separados: apéndice A (fig. A4, factores A1/A2 introducidos)
y subparte C histórica (§§23.333-341). Ningún contorno representa certificación.
Las listas de curvas son la única fuente numérica de tablas, gráficos y reportes.
"""
from copy import deepcopy
from math import sqrt, isfinite
from .units import convert, KT_TO_FPS, RHO0

SPECS = {
 'span': ('Envergadura de referencia', 'length'),
 'Va_selected': ('Velocidad de maniobra seleccionada', 'speed'),
 'U_b': ('Ráfaga máxima en VB', 'gust'),
 'Cse': ('Velocidad del sonido equivalente', 'speed'),
 'W': ('Peso de la condición', 'weight'), 'S': ('Superficie alar', 'area'),
 'n_pos': ('Factor límite positivo seleccionado', 'ratio'),
 'n_neg': ('Factor límite negativo seleccionado', 'ratio'),
 'CN_pos': ('Coeficiente normal máximo positivo', 'ratio'),
 'CN_neg': ('Coeficiente normal máximo negativo', 'ratio'),
 'rho': ('Densidad local para relación de masas', 'density'),
 'rho0': ('Densidad de referencia EAS', 'density'),
 'chord': ('Cuerda geométrica media', 'length'),
 'a': ('Pendiente de fuerza normal de la aeronave', 'slope'),
 'g': ('Aceleración gravitatoria', 'accel'), 'Vc': ('Velocidad de crucero de diseño', 'speed'),
 'Vd': ('Velocidad de picada de diseño', 'speed'), 'Va': ('Velocidad de maniobra seleccionada', 'speed'),
 'U_c': ('Ráfaga derivada a Vc', 'gust'), 'U_d': ('Ráfaga derivada a Vd', 'gust'),
 'altitude': ('Altitud de la condición', 'length'), 'n3': ('Factor de Fig. A1 a Vc', 'ratio'),
 'n4': ('Factor de Fig. A2 a Vc', 'ratio'), 'W_other': ('Peso de comparación', 'weight'),
 'W_S_photo': ('Carga alar transcrita de la foto', 'loading'),
 'nu_photo': ('Factor utilidad de la foto', 'ratio'), 'nn_photo': ('Factor normal de la foto', 'ratio'),
 'Wn_photo': ('Peso con subíndice n de la foto', 'weight'), 'Wu_photo': ('Peso con subíndice u de la foto', 'weight'),
 'a_photo': ('Pendiente a de la foto', 'slope'), 'CLalpha_photo': ('Pendiente CLalpha de la foto', 'slope'),
}

def parameter_rows(case):
    return [{'símbolo': key, 'descripción': SPECS.get(key, (key,''))[0],
             'valor': p.get('value'), 'unidad': p.get('unit',''), 'fuente': p.get('source',''),
             'página':p.get('page',''), 'estado': p.get('status','pendiente'),
             'observaciones':p.get('notes',''), 'original':p.get('original',{})}
            for key,p in case['parameters'].items()]

def positive_root(A, B, C):
    """Raíces reales no negativas de A*x² + B*x + C = 0."""
    if abs(A) < 1e-15:
        return [-C/B] if abs(B)>1e-15 and -C/B>=0 else []
    disc = B*B-4*A*C
    if disc < 0:
        return []
    return sorted(set(x for x in ((-B-sqrt(disc))/(2*A),(-B+sqrt(disc))/(2*A)) if x>=0))

def _segments_intersections(stall_k, pieces):
    roots=[]
    for lo,hi,m,b in pieces:
        for v in positive_root(stall_k,-m,-b):
            if lo-1e-9<=v<=hi+1e-9:
                roots.append(v)
    return roots

def calculate(case, samples=601):
    """Devuelve resultados parciales cuando hay datos ausentes o ambiguos."""
    if case.get('worksheet'):
        from .worksheet import calculate_worksheet
        return calculate_worksheet(case, samples)
    if case.get('method') == 'niu':
        from .niu import calculate_niu
        result=calculate_niu(case, samples)
        from .context import update_context
        update_context(case,result)
        return result
    if samples<3:
        raise ValueError('Se necesitan al menos tres muestras')
    params=case.get('parameters',{})
    legacy=case.get('requires_thesis','Wn_photo' in params)
    r={'case_id':case.get('id',''), 'name':case.get('name',''), 'method':case.get('method',''),
       'aircraft':case.get('aircraft','Aeronave sin identificar'),'requires_thesis':legacy,
       'values':{}, 'checks':[], 'equations':[], 'points':[], 'curves':{}, 'intersections':[],
       'blocked':[], 'assumptions':list(case.get('assumptions',[])), 'parameters':parameter_rows(case)}
    values=r['values']; checks=r['checks']
    def check(code, state, text):
        checks.append({'código':code,'estado':state,'detalle':text})
    def get(key, required=True):
        p=params.get(key,{})
        try:
            if key not in SPECS:
                raise ValueError('Símbolo desconocido')
            value=convert(p.get('value'),p.get('unit',''),SPECS[key][1])
            values[key]=value
            return value
        except (ValueError,TypeError,OverflowError) as e:
            if required:
                r['blocked'].append(f'{key}: {e}')
            return None
    def equation(name,formula,sub,result,unit,source):
        r['equations'].append({'nombre':name,'ecuación':formula,'sustitución':sub,
                               'resultado':result,'unidad':unit,'fuente':source})
    if legacy:
        check('ALCANCE','PENDIENTE','Falta tesis cap. 1.9: variante, configuración, condiciones, edición y procedimiento originales sin confirmar. Uso académico; no certificación.')
    else:
        check('ALCANCE','INFO','Aeronave: '+case.get('aircraft','Sin identificar')+'. Categoría y criterio seleccionados por el usuario; documentar fuentes y aplicabilidad del proyecto.')
    wn=get('Wn_photo',False);wu=get('Wu_photo',False);nn=get('nn_photo',False);nu=get('nu_photo',False)
    if None not in (wn,wu,nn,nu):
        values['nW_normal_photo']=nn*wn;values['nW_utility_photo']=nu*wu
        check('A23.5 nW','OK' if abs(nn*wn-nu*wu)<.005*max(nn*wn,nu*wu) else 'ADVERTENCIA',
              f'Lecturas fotográficas: nn Wn={nn*wn:.6f}; nu Wu={nu*wu:.6f} lbf. Revisar si los subíndices representan categorías; no se confirma igualdad multicategoría.')
    for item in case.get('applicability',[]):
        check('A23.1 '+item['criterion'], item.get('state','PENDIENTE'),item['detail'])
    W=get('W'); S=get('S'); np_=get('n_pos')
    if W is None or S is None or np_ is None:
        check('ENTRADAS','BLOQUEADO','No se pueden calcular carga alar ni velocidades mínimas.')
        return r
    if min(W,S,np_)<=0:
        r['blocked'].append('W, S y n_pos deben ser positivos'); return r
    ws=W/S; values['W_S']=ws
    equation('Carga alar','W/S',f'{W:.6g} lbf / {S:.6g} ft²',ws,'lbf/ft²','W y S de esta condición; referencias conservadas en la tabla de datos')
    photo=get('W_S_photo',False)
    if photo is not None:
        check('CARGA ALAR','OK' if abs(ws-photo)/ws<0.005 else 'ADVERTENCIA',f'W/S calculado = {ws:.6f}; foto = {photo:g} lbf/ft². Diferencia {100*(ws-photo)/ws:.4f} %.')
    check('PESO A23.1','OK' if W<=6000 else 'NO APLICA',f'W={W:g} lbf; el límite de 6000 lbf es solo una de las condiciones de A23.1.')
    chord_geom=get('chord',False)
    if chord_geom is not None and chord_geom>0:
        ar=S/(chord_geom*chord_geom);values['AR_conditional']=ar
        check('AR CONDICIONAL A23.1','NO APLICA' if ar>7 else 'INFO',
              f'Si c={chord_geom:g} ft es realmente la cuerda geométrica S/b, AR=S/c²={ar:.6f}. '+
              ('Supera AR=7 de A23.1: el apéndice A sería incompatible bajo esta hipótesis. ' if ar>7 else 'Satisface solo el requisito AR<=7 bajo esa hipótesis. ')+
              'No se aplica esta inferencia a una cuerda aerodinámica media distinta de S/b; confirmar la definición de c en la fuente de la aeronave.')
    n_speed=max(np_,3.8)
    for symbol,factor in [('Vc_A_raw',17),('Vd_A_raw',24),('Va_A_raw',15),('Vf_A_raw',11)]:
        values[symbol]=factor*sqrt(n_speed*ws)
        equation(symbol,f'{factor} sqrt(max(n1,3.8) W/S)',f'{factor} [kt/sqrt(lbf/ft²)] × sqrt({n_speed:g} × {ws:.6f} lbf/ft²)',values[symbol],'kt EAS','FAR 23 2016, Ap. A, Fig. A3, p.345; valores sin aplicar excepciones')
    check('MÍNIMOS A3','INFO','Vc_A_raw, Vd_A_raw y Va_A_raw son expresiones base. Las excepciones con VH y Vc requieren esos datos; Va_A_raw no es la intersección A.')
    Vc=get('Vc',False); Vd=get('Vd',False); Va=get('Va',False)
    if Vc is not None and Vd is not None and not (0<Vc<Vd):
        r['blocked'].append('Se requiere 0 < Vc < Vd'); return r
    nneg=get('n_neg',False)
    if nneg is not None and nneg>=0:
        r['blocked'].append('n_neg debe ser negativo'); return r
    cn=get('CN_pos'); cnneg=get('CN_neg'); rho0=get('rho0')
    kp=kn=None
    if cn is not None and rho0 is not None and cn>0 and rho0>0:
        kp=0.5*rho0*KT_TO_FPS**2*cn/ws
        values['Vs']=sqrt(1/kp); values['V_A_stall']=sqrt(np_/kp)
        equation('Pérdida EAS','Vs = sqrt(2 (W/S)/(rho0 CN+)) / kt_to_fps',f'sqrt[2 × ({ws:.6f} lbf/ft²) / (({rho0:.9g} slug/ft³) × {cn:g})] / ({KT_TO_FPS:.9g} ft/s por kt)',values['Vs'],'kt EAS','Equilibrio N = q S CN; CN es fuerza normal, no CL intercambiado')
        equation('Intersección A','V_A_stall = Vs sqrt(n+)',f'({values["Vs"]:.6f} kt EAS) × sqrt({np_:g})',values['V_A_stall'],'kt EAS','Intersección de pérdida positiva y límite de maniobra')
        if Va is not None:
            check('VA','OK' if values['V_A_stall']<=Va<= (Vc or float('inf')) else 'ADVERTENCIA',f'Intersección A={values["V_A_stall"]:.3f}; Va elegida={Va:g} kt EAS. Revisar criterio de selección; no se igualan por definición.')
    elif cn is not None and rho0 is not None:
        r['blocked'].append('CN_pos y rho0 deben ser positivos')
    if cnneg is not None and rho0 is not None and cnneg<0 and rho0>0 and nneg is not None:
        kn=0.5*rho0*KT_TO_FPS**2*cnneg/ws
        values['V_G_stall']=sqrt(nneg/kn)
    elif cnneg is not None and cnneg>=0:
        r['blocked'].append('CN_neg debe ser negativo')
    method=case.get('method')
    if method not in ['apendice_a','subparte_c']:
        r['blocked'].append('Método desconocido'); return r
    if Vc is None or Vd is None:
        r['blocked'].append('Faltan Vc/Vd seleccionadas: no se generan diagramas completos')
        return r
    check('ORDEN V','OK' if (kp is not None and values['Vs']<values['V_A_stall']<=Vc<Vd) else 'ADVERTENCIA','Requisito evaluado: Vs < A <= Vc < Vd. Un incumplimiento se informa sin ajustar parámetros.')
    # Subparte C, criterios básicos sin reducciones opcionales por carga alar.
    cat=case.get('category','normal')
    if cat not in ['normal','utilidad','acrobática']:
        r['blocked'].append('Categoría no admitida por esta implementación'); return r
    if method=='subparte_c':
        required_n=min(3.8,2.1+24000/(W+10000)) if cat=='normal' else (4.4 if cat=='utilidad' else 6)
        values['n_required']=required_n
        reqneg=-(0.5 if cat=='acrobática' else 0.4)*np_
        check('23.337','OK' if np_>=required_n and nneg is not None and nneg<=reqneg else 'ADVERTENCIA',f'Para {cat}: n+ >= {required_n:.5f}; n- <= {reqneg:.5f}. Factores seleccionados explícitos.')
        vcmin=(36 if cat=='acrobática' else 33)*sqrt(ws)
        vdmin=max(1.25*Vc,{'normal':1.4,'utilidad':1.5,'acrobática':1.55}[cat]*vcmin)
        values.update(Vc_C_base=vcmin,Vd_C_base=vdmin)
        check('23.335','OK' if Vc>=vcmin and Vd>=vdmin else 'ADVERTENCIA',f'Sin reducciones opcionales: Vc >= {vcmin:.3f}, Vd >= {vdmin:.3f} kt EAS. No se usa Fig. A3 para demostrar este criterio.')
    else:
        reqn={'normal':3.8,'utilidad':4.4,'acrobática':6}[cat]
        check('TABLA A1','OK' if np_>=reqn and nneg is not None and nneg<=-.5*np_ else 'ADVERTENCIA',f'Apéndice A: n1 >= {reqn:g}, n2 <= -0.5 n1 (distinto de §23.337).')
        check('FIGURA A3','OK' if Vc>=values['Vc_A_raw'] and Vd>=values['Vd_A_raw'] else 'ADVERTENCIA','Comparación con expresiones base, sin excepciones VH. Revisar A3 original antes de usar reducciones.')
    # Ráfagas de subparte C o factores introducidos de gráficos A1/A2.
    gp=gm=None; pieces_p=[]; pieces_m=[];continuity_ok=True
    if method=='subparte_c':
        rho=get('rho'); chord=get('chord'); a=get('a'); g=get('g'); uc=get('U_c'); ud=get('U_d'); h=get('altitude')
        if None not in (rho,chord,a,g,uc,ud,h):
            if min(rho,chord,a,g)<=0 or min(uc,ud)<0 or h<0:
                r['blocked'].append('Densidad, cuerda, pendiente y gravedad positivas; ráfagas y altitud no negativas')
            else:
                mu=2*ws/(rho*chord*a*g); kg=.88*mu/(5.3+mu)
                delta_c=kg*uc*Vc*a/(498*ws); delta_d=kg*ud*Vd*a/(498*ws)
                values.update(mu=mu,Kg=kg,n_gust_c_pos=1+delta_c,n_gust_c_neg=1-delta_c,n_gust_d_pos=1+delta_d,n_gust_d_neg=1-delta_d)
                equation('Relación de masas','mu_g = 2 (W/S)/(rho c a g)',f'2 × ({ws:.6f} lbf/ft²) / [({rho:.8g} slug/ft³) × ({chord:g} ft) × ({a:.7g} 1/rad) × ({g:g} ft/s²)]',mu,'1','§23.341, 2016, p.219; a por radián, rho local; radián adimensional')
                equation('Alivio de ráfaga','Kg = 0.88 mu_g/(5.3+mu_g)',f'0.88 × {mu:.6f}/(5.3+{mu:.6f})',kg,'1','§23.341, 2016, p.219')
                for label,U,V,d in [('C',uc,Vc,delta_c),('D',ud,Vd,delta_d)]:
                    equation('Ráfaga '+label,'Δn = Kg Ude V a/[498 (W/S)]; n = 1 ± Δn',f'{kg:.6f} × ({U:g} ft/s) × ({V:g} kt EAS) × ({a:.6f} 1/rad) / [498 × ({ws:.6f} lbf/ft²)]',d,'1 (incremento Δn)','§23.341: constante 498 calibrada para estas unidades imperiales; no es una constante universal sin unidades')
                check('MASA Y ALIVIO','OK' if mu>0 and 0<kg<.88 else 'ERROR',f'mu={mu:.6f}; Kg={kg:.6f}. Peso en lbf y rho en slug/ft³; no se introduce g dos veces.')
                if h<=50000:
                    reduction=1 if h<=20000 else 1-.5*(h-20000)/30000
                    check('23.333 Ude','OK' if abs(uc-50*reduction)<1e-6 and abs(ud-25*reduction)<1e-6 else 'ADVERTENCIA',f'Valores prescritos para h={h:g} ft: Uc={50*reduction:g}, Ud={25*reduction:g} ft/s. Los datos no se sustituyen automáticamente.')
                else:
                    check('ALTITUD','ADVERTENCIA','Altitud superior al intervalo de §23.333 implementado; no se extrapola Ude.')
                m=delta_c/Vc; t=(delta_d-delta_c)/(Vd-Vc); b=delta_c-t*Vc
                pieces_p=[(0,Vc,m,1),(Vc,Vd,t,1+b)]
                pieces_m=[(0,Vc,-m,1),(Vc,Vd,-t,1-b)]
                continuity_ok=all(abs(ps[0][2]*Vc+ps[0][3]-(ps[1][2]*Vc+ps[1][3]))<1e-9 for ps in [pieces_p,pieces_m])
                # Fijar coeficientes al crear la función: los recorridos de raíces
                # usan otras pendientes y no deben alterar estas rectas.
                def gp(v,m=m,t=t,b=b): return 1+(m*v if v<=Vc else t*v+b)
                def gm(v,m=m,t=t,b=b): return 1-(m*v if v<=Vc else t*v+b)
                check('GUST LINEAL','INFO','Se unen linealmente los factores a Vc y Vd. No se interpola Ude para luego multiplicarlo por V: produciría una parábola.')
    else:
        n3=get('n3'); n4=get('n4')
        if None not in (n3,n4,nneg):
            if n3<0 or n4>0:
                r['blocked'].append('Figuras A1/A2: se requieren n3 positivo y n4 negativo')
            else:
                values.update(n3=n3,n4=n4)
                # A4: A-C-D y G-F-E, con C/F cuando las cargas de ráfaga gobiernan.
                check('FIGURAS A1 A2','INFO','n3/n4 deben proceder de lectura documentada de A1/A2. No se sustituyen por §23.341 ni se fuerzan a n1/n2 cuando una lectura falta.')
    def negative_limit(v):
        if nneg is None: return None
        if method=='apendice_a' or v<=Vc: return nneg
        end=0 if cat=='normal' else -1
        return nneg+(end-nneg)*(v-Vc)/(Vd-Vc)
    if kp is None or kn is None or nneg is None:
        r['blocked'].append('Faltan datos de pérdida o límite negativo: contornos de maniobras y combinado bloqueados')
    knots=[0,Vc,Vd]
    for key in ['Vs','V_A_stall','V_G_stall']:
        if key in values and values[key]<=Vd: knots.append(values[key])
    if gp and gm:
        for k,ps,side in [(kp,pieces_p,'positiva'),(kn,pieces_m,'negativa')]:
            if k is not None:
                for v in _segments_intersections(k,ps):
                    if v<=Vd:
                        knots.append(v);r['intersections'].append({'tipo':'pérdida-ráfaga '+side,'V':v,'n':k*v*v})
        # Intersecciones ráfaga con límites de maniobra, incluidos cambios de tramo.
        for ps,positive in [(pieces_p,True),(pieces_m,False)]:
            for lo,hi,m,b in ps:
                if positive: ml,bl=0,np_
                elif nneg is not None:
                    ml=0 if hi<=Vc or method=='apendice_a' else ((0 if cat=='normal' else -1)-nneg)/(Vd-Vc)
                    bl=nneg-ml*Vc if ml else nneg
                else: continue
                if abs(m-ml)>1e-12:
                    v=(bl-b)/(m-ml)
                    if lo<=v<=hi:
                        knots.append(v); r['intersections'].append({'tipo':'ráfaga-límite '+('positivo' if positive else 'negativo'),'V':v,'n':m*v+b})
    grid=sorted(set([Vd*i/(samples-1) for i in range(samples)]+knots))
    curves={'V':grid}
    if kp is not None: curves['stall_pos']=[kp*v*v for v in grid]
    if kn is not None: curves['stall_neg']=[kn*v*v for v in grid]
    if kp is not None and kn is not None and nneg is not None:
        curves['man_pos']=[min(kp*v*v,np_) for v in grid]
        curves['man_neg']=[max(kn*v*v,negative_limit(v)) for v in grid]
        r['points'] += [{'punto':'O','V':0,'n':0},{'punto':'S','V':values['Vs'],'n':1},
                        {'punto':'A','V':values['V_A_stall'],'n':np_},
                        {'punto':'G','V':values['V_G_stall'],'n':nneg},
                        {'punto':'D','V':Vd,'n':min(kp*Vd*Vd,np_)},
                        {'punto':'E','V':Vd,'n':max(kn*Vd*Vd,negative_limit(Vd))}]
        check('INTERSECCIONES','OK' if abs(kp*values['V_A_stall']**2-np_)<1e-9 and abs(kn*values['V_G_stall']**2-nneg)<1e-9 else 'ERROR','A y G resueltos analíticamente; ambos se incluyen exactamente en la malla de las gráficas.')
    if gp and gm:
        curves['gust_pos']=[gp(v) for v in grid]; curves['gust_neg']=[gm(v) for v in grid]
        for label,v in [('C',Vc),('D',Vd)]:
            r['points'] += [{'punto':'R+'+label,'V':v,'n':gp(v)},{'punto':'R-'+label,'V':v,'n':gm(v)}]
        check('SIGNOS RÁFAGA','OK' if all(p>=1 and m<=1 and abs(p+m-2)<1e-8 for p,m in zip(curves['gust_pos'],curves['gust_neg'])) else 'ERROR','Ráfagas simétricas alrededor de n=1; la rama inferior no es el negativo de la superior.')
        if 'man_pos' in curves:
            # Envolvente de condiciones de diseño §23.333(a): extremos de casos
            # de maniobra/ráfaga a la misma V, limitados por CN estático.
            # Las rectas de ráfaga crudas quedan visibles fuera de ese límite.
            curves['combined_pos']=[min(kp*v*v,max(mp,gp(v))) for v,mp in zip(grid,curves['man_pos'])]
            curves['combined_neg']=[max(kn*v*v,min(mn,gm(v))) for v,mn in zip(grid,curves['man_neg'])]
            check('FRONTERA','INFO','Subparte C: extremos de las condiciones de maniobra y ráfaga a cada V, limitados por CN estático, y cierre vertical en Vd. Ráfagas lineales sin recortar se conservan. Aproximación cuasiestática; no modela pérdida dinámica.')
            exceed=gp(Vc)>np_ or gm(Vc)<nneg or gp(Vd)>np_ or gm(Vd)<negative_limit(Vd)
            check('RÁFAGA DOMINANTE','ADVERTENCIA' if exceed else 'OK',f'En C: n+={gp(Vc):.5f}, n-={gm(Vc):.5f}; en D: n+={gp(Vd):.5f}, n-={gm(Vd):.5f}. Una demanda superior a maniobras no se elimina; exige investigar la condición de diseño.')
    if method=='apendice_a' and 'n3' in values and 'man_pos' in curves:
        va=values['V_A_stall']; vg=values['V_G_stall']; n3=values['n3']; n4=values['n4']
        if va>=Vc or vg>=Vc:
            r['blocked'].append('A4 requiere A y G antes de Vc para esta construcción por tramos')
        else:
            nc=max(np_,n3); nf=min(nneg,n4)
            def pos_a4(v):
                if v<=va:return kp*v*v
                if v<=Vc:return np_+(nc-np_)*(v-va)/(Vc-va)
                return nc+(np_-nc)*(v-Vc)/(Vd-Vc)
            def neg_a4(v):
                if v<=vg:return kn*v*v
                if v<=Vc:return nneg+(nf-nneg)*(v-vg)/(Vc-vg)
                return nf+(nneg-nf)*(v-Vc)/(Vd-Vc)
            curves['combined_pos']=[pos_a4(v) for v in grid]
            curves['combined_neg']=[neg_a4(v) for v in grid]
            # A4 es un contorno combinado; no representa un cálculo separado
            # de ráfagas. La vista de hoja migra al motor Niu para calcularlas.
            check('RÁFAGA A4','INFO','A4 no suministra una curva física de ráfaga independiente. Abra este caso en la hoja y especifique Uc/Ud para calcular n=1±Δn.')
            r['points'] += [{'punto':'C A4','V':Vc,'n':nc},{'punto':'F A4','V':Vc,'n':nf}]
            check('FRONTERA A4','INFO','A4: O-A-C-D-E-F-G-O; C/F solo si gobiernan n3/n4. Se conectan A-C-D y G-F-E según la figura, no mediante una unión geométrica arbitraria. La malla conserva A, G, Vc y Vd.')
    elif method=='apendice_a':
        r['blocked'].append('Combinado A4 pendiente de lectura documentada de n3/n4 en Fig. A1/A2')
    if 'combined_pos' in curves:
        if kp is not None and kn is not None:
            continuity_ok=continuity_ok and abs(kp*values['V_A_stall']**2-np_)<1e-9 and abs(kn*values['V_G_stall']**2-nneg)<1e-9
        check('CONTINUIDAD','OK' if continuity_ok else 'ERROR','Residuos de empalme en A/G y rectas de ráfaga a Vc menores que 1e-9; min/max de funciones continuas conserva continuidad. Cierre vertical en Vd.')
        check('ORDEN FRONTERA','OK' if all(p>=m-1e-9 for p,m in zip(curves['combined_pos'],curves['combined_neg'])) else 'ERROR','Comprobación en todas las abscisas: frontera superior >= inferior.')
    r['curves']=curves
    return r

def compare(cases):
    """Comparación de resultados y de entradas sin alterar ninguno de los casos."""
    results=[calculate(c) for c in cases]
    if len(results)<2:return []
    first=results[0]
    rows=[]
    for result in results[1:]:
        for key in sorted(set(first['values'])|set(result['values'])):
            a=first['values'].get(key);b=result['values'].get(key)
            rows.append({'variable':key,'caso original':first['name'],'original':a,'caso comparado':result['name'],
                         'revisado':b,'diferencia':b-a if a is not None and b is not None else None})
    return rows
