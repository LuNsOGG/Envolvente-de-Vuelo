"""Creación y duplicación de aeronaves sin heredar datos de otro modelo."""
from copy import deepcopy
from datetime import datetime
from uuid import uuid4
from .engine import SPECS
from .units import UNITS,RHO0

MAIN_KEYS=['W','S','n_pos','n_neg','CN_pos','CN_neg','Vc','Vd','chord','a','rho']
ADVANCED_KEYS=['rho0','g','Va','U_c','U_d','altitude','n3','n4']
PHOTO_KEYS=['W_other','W_S_photo','nu_photo','nn_photo','Wn_photo','Wu_photo','a_photo','CLalpha_photo']

def parameter(value,unit,source='',status='pendiente',notes=''):
    p=dict(value=value,unit=unit,source=source,page='',status=status,notes=notes)
    p['original']=deepcopy(p)
    return p

def new_case(aircraft='Nueva aeronave',name='Condición 1'):
    params={k:parameter(None,next(iter(UNITS[SPECS[k][1]]))) for k in MAIN_KEYS+ADVANCED_KEYS}
    params['rho0']=parameter(RHO0,'slug/ft³','Atmósfera estándar: 1.225 kg/m³','documentado','Referencia para velocidades EAS.')
    params['g']=parameter(32.1740485564,'ft/s²','Gravedad estándar','documentado','Modificable para la condición de análisis.')
    return dict(id='caso_'+uuid4().hex[:12],name=name,aircraft=aircraft,method='subparte_c',category='normal',
                requires_thesis=False,parameters=params,assumptions=[],changes=[],applicability=[])

def duplicate_case(case,name='Condición duplicada'):
    result=deepcopy(case);result['id']='caso_'+uuid4().hex[:12];result['name']=name
    result.setdefault('changes',[]).append(dict(parameter='condición',before=case['name'],after=name,reason='Copia independiente de la condición; las fuentes se conservan.'))
    return result

def demo_project():
    cases=[]
    examples=[('Aeronave A (ejemplo)',2400,174,1.5,-1.1,4.9,5.5,140,200,110),
              ('Aeronave B (ejemplo)',4200,210,1.6,-1.,5.7,5.1,160,230,140)]
    for aircraft,W,S,cp,cn,chord,a,Vc,Vd,Va in examples:
        case=new_case(aircraft,'Configuración limpia')
        for key,val in dict(W=W,S=S,n_pos=3.8,n_neg=-1.52,CN_pos=cp,CN_neg=cn,chord=chord,a=a,
                            rho=RHO0,Vc=Vc,Vd=Vd,Va=Va,U_c=50,U_d=25,altitude=0).items():
            unit=case['parameters'][key]['unit']
            case['parameters'][key]=parameter(val,unit,'Ejemplo didáctico de la calculadora','supuesto','Valor ilustrativo; sustituir por la fuente de su aeronave.')
        case['assumptions']=['Ejemplo numérico inventado de forma explícita para mostrar el uso de la herramienta; no representa un modelo comercial.',
                             'Configuración limpia y condición ilustrativa al nivel del mar. Las velocidades son EAS.',
                             'Las ráfagas 50/25 ft/s corresponden al intervalo histórico hasta 20000 ft; confirmar la base del proyecto.']
        cases.append(case)
    return dict(schema_version=1,kind='general',metadata=dict(title='Proyecto de envolventes de vuelo',student='',subject='',teacher='',date=datetime.now().strftime('%Y-%m-%d')),active_case=cases[0]['id'],cases=cases)

def blank_project(aircraft='Mi aeronave'):
    p=demo_project();c=new_case(aircraft);p['cases']=[c];p['active_case']=c['id'];return p
