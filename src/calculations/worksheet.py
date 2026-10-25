"""Adaptador de la hoja fotografiada: entradas fieles y resultados trazables.

Las expresiones mínimas se calculan; los datos aerodinámicos o lecturas de
nomogramas ausentes permanecen vacíos. No se interpolan figuras sin datos.
"""
from copy import deepcopy
from datetime import datetime
from math import sqrt
from .cases import new_case, parameter
from .units import convert, RHO0, KT_TO_FPS, UNITS
from .engine import SPECS

EXCEL_FIELDS = [
    ('nu_photo', 'nᵤ', 'Factor límite de categoría utilidad; referencia'),
    ('nn_photo', 'nₙ', 'Factor límite de categoría normal; referencia'),
    ('Wn_photo', 'Wₙ', 'Peso asociado a categoría normal; referencia'),
    ('Wu_photo', 'Wᵤ', 'Peso asociado a categoría utilidad; referencia'),
    ('W', 'W', 'Peso de la condición'), ('S', 'S', 'Superficie alar'),
    ('W_S_photo', 'W/S', 'Resultado automático de W dividido entre S'),
    ('n_pos', 'N', 'Factor positivo seleccionado en la hoja'),
    ('CN_pos', 'Cₙ máx.', 'Coeficiente normal máximo positivo'),
    ('rho', 'ρ', 'Densidad local'), ('chord', 'c', 'Cuerda'),
    ('a', 'a', 'Pendiente usada en la ecuación de ráfaga'),
    ('g', 'g', 'Aceleración gravitatoria'),
    ('CLalpha_photo', 'CLα', 'Pendiente CLα de referencia; no sustituye a a automáticamente'),
]
FIELD_KEYS = [x[0] for x in EXCEL_FIELDS]
DEFAULT_UNITS = dict(nu_photo='1', nn_photo='1', Wn_photo='lbf', Wu_photo='lbf',
                    W='lbf', S='ft²', W_S_photo='lbf/ft²', n_pos='1', CN_pos='1',
                    rho='slug/ft³', chord='ft', a='1/deg', g='ft/s²', CLalpha_photo='1/deg')
APPENDIX = 'https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-part23-appA.pdf'
SUBPART = 'https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-335.pdf'


def worksheet_case(name='Mi aeronave'):
    case = new_case(name, 'Hoja de cálculo')
    case.update(worksheet=True, requires_thesis=False, method='niu', speed_mode='excel',
                negative_rule='excel', negative_end='constant', aero_model='constant', coefficient_basis='CN')
    for key in FIELD_KEYS:
        case['parameters'][key] = parameter(None, DEFAULT_UNITS[key])
    case['parameters']['rho0'] = parameter(RHO0, 'slug/ft³', 'Densidad estándar de referencia EAS', 'constante')
    for key,unit in [('U_b','ft/s'),('Cse','kt EAS'),('span','ft'),('Va_selected','kt EAS')]:case['parameters'][key]=parameter(None,unit)
    return case


def worksheet_project(photographs=True, name='Mi aeronave'):
    c = worksheet_case('Ejemplo 1' if photographs else name)
    if photographs:
        readings = dict(nu_photo=4.4, nn_photo=3.8, Wn_photo=4631.5, Wu_photo=3454.54,
                        W=4631, S=181, W_S_photo=25.58, n_pos=3.8, CN_pos=1.46,
                        rho=.0023, chord=4.26, a=.105, g=32.2, CLalpha_photo=.11)
        source = 'Fotografías originales de la hoja Excel, filas 2 a 15'
        for key, value in readings.items():
            p = parameter(value, DEFAULT_UNITS[key], source, 'transcrito')
            if key in ['rho', 'chord', 'a', 'CLalpha_photo', 'Wn_photo', 'Wu_photo']:
                p['status'] = 'unidad interpretada'
                p['notes'] = 'Unidad interpretada con autorización del usuario; el número procede de la foto.'
                p['original']['unit'] = {'rho':'lb/ft³ sin tipo', 'chord':'sin confirmar', 'a':'sin confirmar',
                                         'CLalpha_photo':'sin confirmar', 'Wn_photo':'sin confirmar', 'Wu_photo':'sin confirmar'}[key]
            c['parameters'][key] = p
        c.update(name='Ejemplo 1',example=1)
        for key,value,unit in [('CN_neg',-1.35,'1'),('U_c',50,'ft/s'),('U_d',25,'ft/s'),('U_b',0,'ft/s')]:
            c['parameters'][key]=parameter(value,unit,'Hipótesis del ejercicio Excel','aproximación',
                'CN negativo autorizado por el usuario.' if key=='CN_neg' else 'Intensidades de diseño seleccionadas para el ejercicio; editables en Datos de cálculo.')
        c['assumptions'] = ['Ejercicio Excel: coeficientes de fuerza normal CN; unidades interpretadas como lbf, slug/ft³, ft y pendientes por grado.',
                            'CN negativo = -1.35 como aproximación autorizada. Pendiente a = 0.105/grado; CLα = 0.11/grado se conserva como referencia independiente.',
                            'Vc y Vd: mínimos base de Fig. A3; límite negativo de maniobra -0.5N. Se conservan como elecciones del ejercicio, sin afirmar aplicabilidad del apéndice A.',
                            'Ráfagas de Niu con Uc=50 y Ud=25 ft/s, hipótesis de diseño para este ejercicio; no son datos medidos ni derivados de la foto. ρ local permanece en 0.0023 slug/ft³.',
                            'n3 y n4 se calculan como 1±Δn en Vc. No se igualan a N y -0.5N.']
    return dict(schema_version=1, kind='worksheet', metadata=dict(title=c['aircraft'], student='', subject='', teacher='',
                 date=datetime.now().strftime('%Y-%m-%d')), active_case=c['id'], cases=[c])


def adapt_case(case):
    """Importa sin alterar el archivo guardado ni sus lecturas originales."""
    c = deepcopy(case)
    already = c.get('worksheet', False)
    c.update(worksheet=True, requires_thesis=False)
    for key in FIELD_KEYS:
        c['parameters'].setdefault(key, parameter(None, DEFAULT_UNITS[key]))
        if c['parameters'][key]['unit'] not in UNITS[SPECS[key][1]]:
            if c['parameters'][key].get('value') is None:
                c['parameters'][key]['unit']=DEFAULT_UNITS[key]
            else:
                raise ValueError(f"{key}: unidad {c['parameters'][key]['unit']!r} incompatible; no se reinterpretará el valor.")
    if not already:
        # Los ejemplos anteriores incluían cifras elegidas para demostrar la UI.
        # Se preservan en original, pero no se convierten en datos de la hoja nueva.
        for key in ['CN_neg', 'n3', 'n4', 'altitude', 'U_c', 'U_d']:
            p = c['parameters'].get(key)
            if p and p.get('status') == 'supuesto':
                p['value'] = None
                p['notes'] = 'Pendiente de introducir en la hoja; selección anterior conservada en original.'
        c.setdefault('assumptions', []).append('Importación a la vista Excel: las selecciones ilustrativas adicionales no se usan como datos confirmados.')
    if c.get('method')!='niu':
        previous=c.get('method');c['previous_method']=previous;c['method']='niu'
        c.update(speed_mode='excel' if previous=='apendice_a' else 'subparte_c',
                 negative_rule='excel' if previous=='apendice_a' else 'normal',
                 negative_end='constant' if previous=='apendice_a' else 'zero',
                 aero_model='constant',coefficient_basis='CN')
        # Los factores A1/A2 se conservan en el proyecto original; no sustituyen
        # las intensidades verticales requeridas por la ecuación de ráfaga.
        c.setdefault('assumptions',[]).append('Cálculo actualizado a ráfagas de Niu; las intensidades Uc y Ud deben estar especificadas.')
    for key,unit in [('U_b','ft/s'),('Cse','kt EAS'),('span','ft'),('Va_selected','kt EAS')]:c['parameters'].setdefault(key,parameter(None,unit))
    return c


def prepare_case(case):
    c = deepcopy(case); p = c['parameters']; derived = []
    def automatic(key, value, unit, formula, source):
        before = p.get(key, parameter(None, unit))
        p[key] = dict(before, value=value, unit=unit, source=source, status='calculado', notes=formula)
        p[key].setdefault('original', deepcopy(before))
        derived.append(dict(variable=key, value=value, unit=unit, formula=formula, source=source))
    def get(key, dimension):
        q = p.get(key, {})
        try: return convert(q.get('value'), q.get('unit', ''), dimension)
        except (ValueError, TypeError): return None
    w, s, n = get('W', 'weight'), get('S', 'area'), get('n_pos', 'ratio')
    if c['method']=='niu':
        if c.get('chord_mode')=='geometric':
            span=get('span','length')
            chord=s/span if s is not None and span is not None and s>0 and span>0 else None
            automatic('chord',chord,'ft','c = S/b; pendiente si falta superficie o envergadura','Tesis IPN, tabla 1.1; cuerda geométrica calculada')
        mode=c.get('speed_mode','excel'); rule=c.get('negative_rule','excel')
        if mode!='manual':
            for key in ['Vc','Vd']:automatic(key,None,'kt EAS','Pendiente de W, S y N','')
        automatic('Va',None,'kt EAS','Intersección de pérdida positiva y N','Niu, cap. 3')
        if rule!='manual':automatic('n_neg',None,'1','Pendiente de N','')
        derived.clear()
        if None not in (w,s,n) and min(w,s,n)>0:
            ws=w/s
            derived.append(dict(variable='W/S',value=ws,unit='lbf/ft²',formula='W/S',source='W y S'))
            if mode=='excel':
                for key,k in [('Vc',17),('Vd',24)]:
                    automatic(key,k*sqrt(max(n,3.8)*ws),'kt EAS',f'{k} sqrt(max(N,3.8) W/S)',APPENDIX+' Fig. A3; elección del ejercicio')
            elif mode=='subparte_c':
                cat=c.get('category','normal')
                if cat not in ['normal','utilidad','acrobática']:cat='normal'
                vc=(36 if cat=='acrobática' else 33)*sqrt(ws)
                automatic('Vc',vc,'kt EAS','Mínimo base de diseño',SUBPART)
                automatic('Vd',max(1.25*vc,{'normal':1.4,'utilidad':1.5,'acrobática':1.55}[cat]*vc),'kt EAS','Mínimo base de diseño',SUBPART)
            if rule=='excel':automatic('n_neg',-.5*n,'1','-0.5 N','Límite de maniobra del ejercicio Excel')
            elif rule=='normal':automatic('n_neg',-.4*n,'1','-0.4 N','FAR 23 histórico, categoría normal')
            elif rule=='transport':automatic('n_neg',-1.,'1','-1','Niu, ejemplo de transporte, p.77')
        for key in ['n3','n4']:automatic(key,None,'1','Resultado de ráfaga en Vc; pendiente del cálculo','Niu, ec. 3.4.3')
        return c,derived
    # Borrar valores derivados de la copia en memoria evita curvas antiguas
    # cuando una entrada queda vacía; no se modifica ningún archivo.
    for key in ['Vc', 'Vd', 'Va', 'n_neg', 'U_c', 'U_d']:
        automatic(key, None, 'kt EAS' if key in ['Vc','Vd','Va'] else ('1' if key=='n_neg' else 'ft/s'), 'Pendiente de entradas', '')
    derived.clear()
    automatic('rho0', RHO0, 'slug/ft³', 'Referencia estándar para EAS; ρ local se conserva por separado', 'Atmósfera estándar, 1.225 kg/m³')
    if w is not None and s is not None and n is not None and min(w, s, n) > 0:
        ws = w / s
        derived.append(dict(variable='W/S', value=ws, unit='lbf/ft²', formula='W/S', source='W y S de la hoja'))
        if c['method'] == 'apendice_a':
            for key, factor in [('Vc',17),('Vd',24),('Va',15)]:
                automatic(key, factor*sqrt(max(n,3.8)*ws), 'kt EAS', f'{factor} sqrt(max(N,3.8) W/S): mínimo base', APPENDIX+' (Fig. A3)')
            automatic('n_neg', -.5*n, '1', 'n2 = -0.5 N', APPENDIX+' (Tabla 1)')
        else:
            cat = c.get('category', 'normal'); vc = (36 if cat=='acrobática' else 33)*sqrt(ws)
            automatic('Vc', vc, 'kt EAS', 'Vc mínimo base = '+('36' if cat=='acrobática' else '33')+' sqrt(W/S)', SUBPART)
            automatic('Vd', max(1.25*vc, {'normal':1.4,'utilidad':1.5,'acrobática':1.55}[cat]*vc), 'kt EAS', 'Vd mínimo base, sin reducciones opcionales', SUBPART)
            cn = get('CN_pos', 'ratio')
            if cn and cn > 0:
                automatic('Va', sqrt(2*ws/(RHO0*cn))/KT_TO_FPS*sqrt(n), 'kt EAS', 'Va mínima = Vs EAS sqrt(N)', SUBPART)
            automatic('n_neg', -(.5 if cat=='acrobática' else .4)*n, '1', 'Límite negativo del criterio seleccionado', 'FAR 23 2016 §23.337')
            h = get('altitude', 'length')
            if h is not None and 0 <= h <= 50000:
                factor = 1 if h<=20000 else 1-.5*(h-20000)/30000
                automatic('U_c', 50*factor, 'ft/s', 'Ráfaga prescrita según altitud introducida', 'FAR 23 2016 §23.333(c)')
                automatic('U_d', 25*factor, 'ft/s', 'Ráfaga prescrita según altitud introducida', 'FAR 23 2016 §23.333(c)')
    return c, derived


def calculate_worksheet(case, samples=601):
    from .engine import calculate
    prepared, derived = prepare_case(case)
    prepared.pop('worksheet', None)
    r = calculate(prepared, samples)
    r['derived'] = derived; r['worksheet'] = True; r['partial'] = {}
    if case['method']=='niu':
        from .thesis import augment_review
        augment_review(prepared,r)
        for row in r['parameters']:
            if row['símbolo'] in ['n3','n4']:
                row.update(valor=r['values'].get(row['símbolo']),estado='calculado',fuente='Niu, ecuación de ráfaga en Vc',
                           descripción='Factor de ráfaga en Vc',observaciones='1±Δn; independiente del límite de maniobra.')
            if case.get('coefficient_basis')=='CL' and row['símbolo'] in ['CN_pos','CN_neg']:
                row['descripción']='Coeficiente de sustentación CL '+('máximo' if row['símbolo']=='CN_pos' else 'mínimo')
        for key,unit,formula in [('Vs','kt EAS','n_pérdida(Vs)=1'),('V_A_stall','kt EAS','n_pérdida(A)=N'),
                ('Vb','kt EAS','n_pérdida(VB)=1+Δn(VB,Ub)'),
                ('Vc_min_base','kt EAS','Mínimo base A3, no velocidad seleccionada'),
                ('Vd_min_base','kt EAS','Mínimo base A3, no velocidad seleccionada'),
                ('Va_min_base','kt EAS','15 sqrt(max(N,3.8) W/S); distinto de A'),
                ('Va_selected','kt EAS','Velocidad seleccionada; independiente de A'),('mu','1','2(W/S)/(ρ c a g), en Vc'),
                ('Kg','1','0.88 μ/(5.3+μ), en Vc'),('n3','1','1+Δn en Vc'),('n4','1','1-Δn en Vc'),
                ('n_gust_d_pos','1','1+Δn en Vd'),('n_gust_d_neg','1','1-Δn en Vd')]:
            if key in r['values']:derived.append(dict(variable=key,value=r['values'][key],unit=unit,formula=formula,source='Niu, cap. 3'))
    else:
        r['checks'].insert(0, dict(código='AUTOMÁTICO', estado='INFO', detalle='Velocidades mínimas base calculadas; no son datos operativos. Las entradas ausentes permanecen pendientes.'))
    curves = r['curves']; v = curves.get('V', []); values = r['values']
    # Una rama conocida puede consultarse, pero nunca se cierra/finge la rama
    # negativa ausente. El resto de paneles indica sus entradas pendientes.
    if v and 'stall_pos' in curves and 'man_pos' not in curves:
        curves['man_pos'] = [min(x, values['n_pos']) for x in curves['stall_pos']]
        curves['man_neg'] = [None]*len(v)
        r['partial']['man'] = 'Solo rama positiva: falta CN mínimo negativo'
        if 'gust_pos' in curves:
            curves['combined_pos'] = [min(st, max(ma, gu)) for st, ma, gu in zip(curves['stall_pos'],curves['man_pos'],curves['gust_pos'])]
            curves['combined_neg'] = [None]*len(v)
            r['partial']['combined'] = 'Solo rama positiva: falta CN mínimo negativo'
    return r
