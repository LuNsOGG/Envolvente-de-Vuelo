"""Ramas independientes cuando faltan datos; nunca completa entradas con supuestos."""
from .units import convert, RHO0, KT_TO_FPS
from .engine import SPECS
from .niu import roots,interpolate,gust_increment,BOOK_V,BOOK_A,BOOK_CL,SOURCE

def recover_independent(case,r,samples):
    if not r['blocked'] or any('Dato pendiente' not in x for x in r['blocked']):return
    v=r['values'];p=case['parameters']
    for key in ['U_b','Cse']:
        q=p.get(key,{})
        if q.get('value') is not None:
            try:v[key]=convert(q['value'],q.get('unit',''),SPECS[key][1])
            except (ValueError,TypeError):return
    common=['W','S','n_pos','Vc','Vd']
    if any(k not in v for k in common):return
    W,S,N,vc,vd=(v[k] for k in common)
    if min(W,S,vc,vd)<=0 or N<1 or vc>=vd:return
    ws=W/S;v['W_S']=ws;book=case.get('aero_model')=='niu_table'
    if book:
        cse=v.get('Cse',0)
        if case.get('coefficient_basis')!='CL' or cse<=0 or vd/cse>400/548.6+1e-9:return
        xs=[x/548.6 for x in BOOK_V]
        def scale(x):return interpolate(x/cse,xs,BOOK_CL)/1.3
        def slope(x):return v['a']*interpolate(x/cse,xs,BOOK_A)/5.22
    else:
        def scale(x):return 1.
        def slope(x):return v['a']
    qfactor=1/296 if case.get('q_convention')=='niu_296' else .5*RHO0*KT_TO_FPS**2
    cp=v.get('CN_pos');cn=v.get('CN_neg');nn=v.get('n_neg')
    positive=cp is not None and cp>0;negative=cn is not None and cn<0 and nn is not None and nn<0
    def sp(x):return qfactor*x*x*cp*scale(x)/ws
    def sn(x):return qfactor*x*x*cn*scale(x)/ws
    def limit(x):
        if x<=vc or case.get('negative_end','constant')=='constant':return nn
        target=0 if case.get('negative_end')=='zero' else -1
        return nn+(target-nn)*(x-vc)/(vd-vc)
    if positive:
        for key,target in [('Vs',1),('V_A_stall',N)]:
            rr=roots(lambda x:sp(x)-target,vd)
            if rr:v[key]=rr[0]
        positive='V_A_stall' in v and v['V_A_stall']<=vc
    if negative:
        rr=roots(lambda x:sn(x)-nn,vd);negative=bool(rr and rr[0]<=vc)
        if negative:v['V_G_stall']=rr[0]
    gust=all(v.get(k,0)>0 for k in ['rho','chord','a','g']) and all(k in v and v[k]>=0 for k in ['U_c','U_d'])
    anchors=[];ub=v.get('U_b',0)
    if ub<0:gust=False
    if gust:
        def delta(x,u):return gust_increment(ws,v['rho'],v['chord'],slope(x),v['g'],x,u)[2]
        anchors=[(vc,delta(vc,v['U_c'])),(vd,delta(vd,v['U_d']))]
        if ub:
            rr=roots(lambda x:sp(x)-1-delta(x,ub),vc) if positive and ub>=v['U_c'] else []
            if not rr or rr[0]>=vc:gust=False
            else:v['Vb']=rr[0];anchors.insert(0,(rr[0],delta(rr[0],ub)))
    knots=[0,vc,vd]+[v[k] for k in ['Vs','V_A_stall','V_G_stall','Vb'] if k in v]
    if book:knots += [x/548.6*v['Cse'] for x in BOOK_V if x/548.6*v['Cse']<=vd]
    grid=sorted(set(knots+[vd*i/(samples-1) for i in range(samples)]));curves={};partial={}
    if positive:
        curves.update(V=grid,stall_pos=[sp(x) for x in grid],man_pos=[min(N,sp(x)) for x in grid],man_neg=[max(sn(x),limit(x)) if negative else None for x in grid])
        if negative:curves['stall_neg']=[sn(x) for x in grid]
        else:partial['man']='Solo rama positiva: falta CN_neg o límite negativo; no se cierra el contorno.'
    if gust:
        def gd(x):
            if x<=anchors[0][0]:return delta(x,ub or v['U_c'])
            for (x0,d0),(x1,d1) in zip(anchors,anchors[1:]):
                if x<=x1:return d0+(d1-d0)*(x-x0)/(x1-x0)
            return anchors[-1][1]
        curves.update(V=grid,gust_pos=[1+gd(x) for x in grid],gust_neg=[1-gd(x) for x in grid])
        for letter,x,u in [('c',vc,v['U_c']),('d',vd,v['U_d'])]+([('b',v['Vb'],ub)] if ub else []):
            mu,kg,d=gust_increment(ws,v['rho'],v['chord'],slope(x),v['g'],x,u)
            v.update({f'mu_{letter}':mu,f'Kg_{letter}':kg,f'a_{letter}':slope(x),f'delta_{letter}':d,f'n_gust_{letter}_pos':1+d,f'n_gust_{letter}_neg':1-d})
            r['points'] += [dict(punto='R+'+letter.upper(),V=x,n=1+d),dict(punto='R-'+letter.upper(),V=x,n=1-d)]
            r['equations'].append(dict(nombre='Ráfaga '+letter.upper(),ecuación='Δn = Kg U V a/[498(W/S)]',sustitución=f'{kg:.9g} × {u:g} × {x:.9g} × {slope(x):.9g} / (498 × {ws:.9g})',resultado=d,unidad='1',fuente=SOURCE))
        v.update(mu=v['mu_c'],Kg=v['Kg_c'],n3=v['n_gust_c_pos'],n4=v['n_gust_c_neg'])
    if curves:
        partial['combined']='Combinado pendiente: requiere maniobras y ráfagas completas.'
        r.update(curves=curves,partial=partial)
        r['checks'].append(dict(código='CÁLCULO PARCIAL',estado='ADVERTENCIA',detalle='Se muestran solo ramas calculables con datos disponibles. La entrega completa permanece bloqueada.'))
