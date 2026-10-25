"""Envolventes cuasiestáticas de Niu, cap. 3, ecuaciones 3.4.1–3.4.5.

Las cargas de ráfaga son independientes de los límites de maniobra. Las tablas
del ejemplo del libro se interpolan por Mach, sin extrapolar su intervalo.
"""
from math import sqrt
from .units import convert, KT_TO_FPS, RHO0
from .engine import SPECS, parameter_rows

SOURCE = 'Niu, Airframe Structural Design, cap. 3, pp. 43–45 y 74–77'
# Fig. 3.11.6: pendientes por radián. En V=400, 5.22*1.300=6.786;
# 6.78 es coherente con mu=29.3 y Kg=.745 (el dígito del escaneo es ambiguo).
BOOK_V = (0, 50, 100, 150, 200, 250, 300, 325, 350, 400)
BOOK_A = (5.22, 5.25, 5.25, 5.32, 5.37, 5.44, 5.60, 5.74, 5.95, 6.78)
# CLmax se transcribe hasta 300 kt, donde termina esa columna de la tabla.
# Por encima se usa la lectura aproximada de Fig. 3.11.4, declarada en el caso.
BOOK_CL = (1.3, 1.290, 1.288, 1.275, 1.260, 1.241, 1.202, 1.17, 1.13, 1.02)


def interpolate(x, xs, ys):
    if x < xs[0]-1e-9 or x > xs[-1]+1e-9:
        raise ValueError('Mach fuera del intervalo tabulado del Ejemplo 2; use coeficientes propios.')
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t=(x-xs[i-1])/(xs[i]-xs[i-1])
            return ys[i-1]*(1-t)+ys[i]*t
    return ys[-1]


def roots(function, upper, divisions=600):
    """Detecta cambios de signo y resuelve cada raíz por bisección."""
    found=[]; lo=0.; flo=function(lo)
    if abs(flo)<1e-12: found.append(lo)
    for i in range(1, divisions+1):
        hi=upper*i/divisions; fhi=function(hi)
        if flo*fhi<0:
            left,right=lo,hi; fl=flo
            for _ in range(55):
                mid=(left+right)/2; fm=function(mid)
                if fl*fm<=0: right=mid
                else: left=mid; fl=fm
            found.append((left+right)/2)
        elif abs(fhi)<1e-12:
            found.append(hi)
        lo,flo=hi,fhi
    return sorted(set(round(v,11) for v in found))


def gust_increment(ws, rho, chord, a, g, speed, gust):
    """W/S [lbf/ft²], rho [slug/ft³], c [ft], a [/rad], V [kt], U [ft/s]."""
    mu=2*ws/(rho*chord*a*g)
    kg=.88*mu/(5.3+mu)
    return mu, kg, kg*gust*speed*a/(498*ws)


def calculate_niu(case, samples=601):
    if samples<3: raise ValueError('Se necesitan al menos tres muestras')
    p=case['parameters']
    r=dict(case_id=case['id'],name=case['name'],aircraft=case['aircraft'],method='niu',
           requires_thesis=False,values={},checks=[],equations=[],points=[],curves={},
           intersections=[],blocked=[],assumptions=list(case.get('assumptions',[])),
           parameters=parameter_rows(case),coefficient_basis=case.get('coefficient_basis','CN'))
    values=r['values']
    def get(key, required=True):
        q=p.get(key,{})
        try:
            v=convert(q.get('value'),q.get('unit',''),SPECS[key][1]); values[key]=v; return v
        except (ValueError,TypeError,OverflowError) as exc:
            if required:r['blocked'].append(key+': '+str(exc))
            return None
    def check(code,state,detail):r['checks'].append(dict(código=code,estado=state,detalle=detail))
    def equation(name,formula,value,unit,sub=''):
        r['equations'].append(dict(nombre=name,ecuación=formula,sustitución=sub or formula,
                                  resultado=value,unidad=unit,fuente=SOURCE))
    for key in ['W','S','n_pos','n_neg','CN_pos','CN_neg','Vc','Vd','rho','chord','a','g','U_c','U_d']:
        get(key)
    get('U_b',False); get('altitude',False)
    if r['blocked']:return r
    W,S,N,nn,cp,cn,vc,vd,rho,chord,a,g,uc,ud=(values[k] for k in
        ['W','S','n_pos','n_neg','CN_pos','CN_neg','Vc','Vd','rho','chord','a','g','U_c','U_d'])
    if min(W,S,N,cp,vc,vd,rho,chord,a,g)<=0 or nn>=0 or cn>=0 or min(uc,ud)<0:
        r['blocked'].append('W, S, N, coeficiente positivo, velocidades, ρ, c, a y g deben ser positivos; límite y coeficiente negativos menores que cero; ráfagas no negativas.');return r
    if not vc<vd:
        r['blocked'].append('Se requiere Vc < Vd.');return r
    ws=W/S;values['W_S']=ws
    equation('Carga alar','W/S',ws,'lbf/ft²',f'{W:g} / {S:g}')
    book=case.get('aero_model')=='niu_table'
    cse=get('Cse') if book else None
    if book and (cse is None or cse<=0 or vd/cse>400/548.6+1e-9):
        r['blocked'].append('La tabla del Ejemplo 2 cubre 0 ≤ Mach ≤ 400/548.6. Ajuste Cse/Vd o seleccione coeficientes constantes.');return r
    if book:
        machs=[v/548.6 for v in BOOK_V]
        def slope(v):return a*interpolate(v/cse,machs,BOOK_A)/5.22
        def lift_scale(v):return interpolate(v/cse,machs,BOOK_CL)/1.3
        check('TABLA AERODINÁMICA','INFO','Interpolación por Mach de Fig. 3.11.6. CLmax después de 300 kt: lectura aproximada de Fig. 3.11.4. a(400)=6.78/rad, coherente con 5.22×1.300 y μ≈29.3. Las curvas pertenecen solo a este ejemplo.')
    else:
        def slope(v):return a
        def lift_scale(v):return 1.
    # El ejemplo del libro utiliza la constante redondeada 296. El ejercicio
    # Excel conserva la conversión EAS exacta, documentada en Resultados.
    qfactor=1/296 if case.get('q_convention')=='niu_296' else .5*RHO0*KT_TO_FPS**2
    def stall_pos(v):return qfactor*v*v*cp*lift_scale(v)/ws
    def stall_neg(v):return qfactor*v*v*cn*lift_scale(v)/ws
    end=case.get('negative_end','constant')
    def negative_limit(v):
        if v<=vc or end=='constant':return nn
        target=0 if end=='zero' else -1
        return nn+(target-nn)*(v-vc)/(vd-vc)
    def delta(v,u):return gust_increment(ws,rho,chord,slope(v),g,v,u)[2]
    va_roots=roots(lambda v:stall_pos(v)-N,vd)
    vg_roots=roots(lambda v:stall_neg(v)-nn,vd)
    vs_roots=roots(lambda v:stall_pos(v)-1,vd)
    for key,rr in [('Vs',vs_roots),('V_A_stall',va_roots),('V_G_stall',vg_roots)]:
        if rr:values[key]=rr[0]
    if not va_roots or not vg_roots or not vs_roots or va_roots[0]>vc or vg_roots[0]>vc:
        r['blocked'].append('Las intersecciones de pérdida y límites de maniobra deben quedar antes de Vc. Revise velocidades, peso y coeficientes.');return r
    values['Va']=values['V_A_stall']
    dc,dd=delta(vc,uc),delta(vd,ud)
    ub=values.get('U_b',0)
    if ub<0:
        r['blocked'].append('U_b no puede ser negativo.');return r
    anchors=[(vc,dc),(vd,dd)]
    if ub:
        if ub<uc:
            r['blocked'].append('La ráfaga máxima Ub debe ser mayor o igual a Uc.');return r
        # Construcción del punto B de Fig. 3.11.7: intersección entre la curva
        # de pérdida positiva y la condición de máxima ráfaga.
        rr=roots(lambda v:stall_pos(v)-1-delta(v,ub),vc)
        if not rr or rr[0]>=vc:
            r['blocked'].append('No existe una intersección VB < Vc para la ráfaga Ub y los datos actuales.');return r
        vb=rr[0];values['Vb']=vb;anchors.insert(0,(vb,delta(vb,ub)))
        equation('Turbulencia VB','n_pérdida(VB) = 1 + Δn(VB, Ub)',vb,'kt EAS')
    def gust_delta(v):
        if v<=anchors[0][0]:return delta(v,ub or uc)
        for (v0,d0),(v1,d1) in zip(anchors,anchors[1:]):
            if v<=v1:return d0+(d1-d0)*(v-v0)/(v1-v0)
        return anchors[-1][1]
    def gp(v):return 1+gust_delta(v)
    def gm(v):return 1-gust_delta(v)
    for name,v,u in [('c',vc,uc),('d',vd,ud)]+([('b',values['Vb'],ub)] if ub else []):
        mu,kg,d=gust_increment(ws,rho,chord,slope(v),g,v,u)
        values.update({f'mu_{name}':mu,f'Kg_{name}':kg,f'a_{name}':slope(v),f'delta_{name}':d,
                       f'n_gust_{name}_pos':1+d,f'n_gust_{name}_neg':1-d})
        equation('Ráfaga '+name.upper(),'Δn = Kg Ude V a / [498 (W/S)]; n = 1 ± Δn',d,'1',
                 f'{kg:.8g} × {u:g} × {v:.8g} × {slope(v):.8g} / (498 × {ws:.8g})')
    values['mu']=values['mu_c'];values['Kg']=values['Kg_c']
    values['n3']=1+dc;values['n4']=1-dc
    equation('Relación de masas','μ = 2 (W/S)/(ρ c a g)',values['mu'],'1',f'En Vc: 2×{ws:.8g}/({rho:g}×{chord:g}×{slope(vc):.8g}×{g:g})')
    equation('Alivio de ráfaga','Kg = 0.88 μ/(5.3+μ)',values['Kg'],'1')
    equation('Pérdida EAS (Niu)','q S C / W = 1',values['Vs'],'kt EAS',
             ('q = V²/296; C = CL(M)' if book else 'q = ρ0 (V × kt_to_fps)²/2; C = '+r['coefficient_basis']))
    knots=[0,vc,vd,*values_subset(values,['Vs','V_A_stall','V_G_stall','Vb'])]
    if book:knots.extend(v/548.6*cse for v in BOOK_V if v/548.6*cse<=vd)
    for fn,kind,nfunc in [(lambda v:stall_pos(v)-gp(v),'pérdida-ráfaga positiva',gp),
                          (lambda v:stall_neg(v)-gm(v),'pérdida-ráfaga negativa',gm),
                          (lambda v:gp(v)-N,'ráfaga-límite positivo',gp),
                          (lambda v:gm(v)-negative_limit(v),'ráfaga-límite negativo',gm)]:
        for v in roots(fn,vd):
            knots.append(v);r['intersections'].append(dict(tipo=kind,V=v,n=nfunc(v)))
    grid=sorted(set(knots+[vd*i/(samples-1) for i in range(samples)]))
    sp=[stall_pos(v) for v in grid];sn=[stall_neg(v) for v in grid]
    mp=[min(s,N) for s in sp];mn=[max(s,negative_limit(v)) for s,v in zip(sn,grid)]
    gustp=[gp(v) for v in grid];gustn=[gm(v) for v in grid]
    r['curves']=dict(V=grid,stall_pos=sp,stall_neg=sn,man_pos=mp,man_neg=mn,gust_pos=gustp,gust_neg=gustn,
                     combined_pos=[min(s,max(m,gp_)) for s,m,gp_ in zip(sp,mp,gustp)],
                     combined_neg=[max(s,min(m,gn)) for s,m,gn in zip(sn,mn,gustn)])
    for label,speed,n in [('O',0,0),('S',values['Vs'],1),('A',values['V_A_stall'],N),
                           ('G',values['V_G_stall'],nn),('D',vd,N),('E',vd,negative_limit(vd))]:
        r['points'].append(dict(punto=label,V=speed,n=n))
    for label,v in [('C',vc),('D',vd)]+([('B',values['Vb'])] if ub else []):
        r['points'] += [dict(punto='R+'+label,V=v,n=gp(v)),dict(punto='R-'+label,V=v,n=gm(v))]
    check('RÁFAGAS','OK','Cálculo independiente n=1±Δn. n3 y n4 son resultados en Vc; nunca se fijan iguales a los límites de maniobra.')
    check('COMBINADO','INFO','Extremos de maniobra y ráfaga limitados por pérdida estática, con cierre en Vd. Las demandas de ráfaga completas permanecen visibles; no se recortan al límite de maniobra.')
    check('ALCANCE','INFO','Modelo cuasiestático del capítulo 3. Las reglas de velocidad y maniobra se declaran por caso; no es análisis de ráfaga dinámica ni demostración de certificación.')
    return r


def values_subset(values,keys):return [values[k] for k in keys if k in values]
