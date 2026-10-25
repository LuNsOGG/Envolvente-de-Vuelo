"""Procedimiento A3/A4 independiente del recálculo Niu; lecturas explícitas."""
from copy import deepcopy
from math import sqrt,isfinite
from .engine import calculate,SPECS
from .worksheet import prepare_case,APPENDIX
from .cases import parameter
from .units import convert,RHO0
from .context import case_label

def appendix_defaults(case):
    thesis=case.get('reference_dataset')=='ipn_2007'
    defaults=dict(n3=3.8 if thesis else None,n4=-1.9 if thesis else None,
        source='Tesis IPN 2007, §1.9: lectura adoptada; no digitalización propia del nomograma' if thesis else '',page='34' if thesis else '',speed_mode='selected')
    defaults.update(case.get('appendix_review',{}));return defaults

def appendix_case(case):
    config=appendix_defaults(case)
    if config.get('speed_mode') not in ['selected','minimum']:raise ValueError('Selección de velocidades del apéndice desconocida')
    if case.get('coefficient_basis','CN')!='CN':raise ValueError('El procedimiento del Apéndice A requiere CN; no se sustituye CL por CN.')
    if case.get('category','normal') not in ['normal','utilidad','acrobática']:raise ValueError('Categoría fuera del procedimiento del Apéndice A.')
    for key in ['source','page']:
        if not isinstance(config.get(key),str):raise ValueError('La referencia de n3/n4 debe ser texto')
    for key in ['n3','n4']:
        x=config.get(key)
        if x is not None and (isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) or (x<=0 if key=='n3' else x>=0)):raise ValueError('n3 debe ser positivo y n4 negativo, con valores finitos')
    if any(config.get(k) is not None for k in ['n3','n4']) and not config['source'].strip():raise ValueError('Documente la fuente de las lecturas n3/n4')
    prepared,_=prepare_case(case);c=deepcopy(prepared);p=c['parameters']
    c.pop('worksheet',None);c.update(method='apendice_a',requires_thesis=False,name='Apéndice A · '+case_label(case),coefficient_basis='CN')
    def read(k):
        q=p.get(k,{})
        try:return convert(q.get('value'),q.get('unit',''),SPECS[k][1])
        except (ValueError,TypeError):return None
    W,S,N=read('W'),read('S'),read('n_pos')
    if None not in [W,S,N] and min(W,S,N)>0:
        ws=W/S
        if config['speed_mode']=='minimum':
            for k,m in [('Vc',17),('Vd',24)]:p[k]=parameter(m*sqrt(max(N,3.8)*ws),'kt EAS',APPENDIX+' Fig. A3','calculado')
        p['n_neg']=parameter(-.5*N,'1',APPENDIX+' Tabla 1','calculado')
    p['rho0']=parameter(RHO0,'slug/ft³','Referencia estándar EAS','constante')
    p['Va']=deepcopy(p.get('Va_selected',parameter(None,'kt EAS')))
    for key in ['n3','n4']:
        p[key]=parameter(config[key],'1',config['source'],'lectura documentada' if config[key] is not None else 'pendiente');p[key]['page']=config['page']
    c['assumptions']=['Procedimiento académico de A3/A4. Las lecturas n3/n4 son independientes de la ecuación de ráfaga de Niu.',
        'n3/n4: '+(config['source'] or 'Fuente pendiente')+'; página '+(config['page'] or 'pendiente')+'.',
        'Se conservan por separado los mínimos A3 y las velocidades efectivas; C/F solo gobiernan cuando exceden los límites de maniobra.',
        'El diagrama A4 es un contorno de condiciones de diseño; no se presenta como una curva física de ráfaga independiente.']
    return c

def calculate_appendix(case):
    c=appendix_case(case);r=calculate(c);r['worksheet']=True
    span=c['parameters'].get('span',{})
    try:b=convert(span.get('value'),span.get('unit',''),'length');r['values']['AR']=b*b/r['values']['S']
    except (ValueError,TypeError,KeyError,ZeroDivisionError):pass
    r['academic_notice']='Procedimiento académico · Apéndice A: AR>7; no se demuestra aplicabilidad.' if r['values'].get('AR',0)>7 else 'Procedimiento académico · aplicabilidad pendiente de comprobación completa.'
    r['procedure']=[dict(paso='1 · Entradas',detalle='W, S, N y coeficientes CN de la condición; rho0 estándar para EAS.'),
        dict(paso='2 · A3',detalle='Mínimos base Vc=17√(max(N,3.8)W/S), Vd=24√(...), Va=15√(...), Vf=11√(...).'),
        dict(paso='3 · Maniobras',detalle='n1=N; n2=-0.5N; A/G son intersecciones de pérdida y límites.'),
        dict(paso='4 · Lecturas',detalle='n3/n4 se conservan con fuente y página; no se igualan a 1±Δn.'),
        dict(paso='5 · A4',detalle='Construcción O-A-C-D-E-F-G-O; las condiciones C/F se investigan si sus factores gobiernan.'),
        dict(paso='6 · Contraste',detalle='Comparar este resultado con el recálculo Niu y con los valores publicados; revisar los avisos de aplicabilidad.')]
    return r
