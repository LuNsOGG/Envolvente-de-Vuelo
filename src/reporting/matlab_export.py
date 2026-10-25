"""Exporta entradas y un motor MATLAB legible y autónomo, sin depender de Python."""
from pathlib import Path
from math import isfinite
from src.calculations.worksheet import prepare_case
from src.calculations.engine import SPECS
from src.calculations.units import convert,RHO0,KT_TO_FPS
from src.calculations.niu import BOOK_V,BOOK_A,BOOK_CL
from src.calculations.appendix import appendix_defaults,calculate_appendix
from src.calculations import calculate
from src.project import validate_project
from src.calculations.context import case_label

def literal(value):
    if isinstance(value,str):return "'"+' '.join(value.splitlines()).replace("'","''")+"'"
    if isinstance(value,bool):return 'true' if value else 'false'
    if value is None:return 'NaN'
    if not isfinite(value):raise ValueError('MATLAB: dato no finito')
    return format(value,'.17g')

def export_matlab(project,cases,path,include_appendix=False):
    validate_project(dict(project,cases=cases,active_case=cases[0]['id'] if cases else ''))
    lines=['%% Envolventes de vuelo - entradas, formulas y graficas editables',
        '% Editar los bloques cfg de cada condicion y ejecutar este archivo.',
        '% W [lbf], S [ft^2], rho [slug/ft^3], c y b [ft], a [/rad], g [ft/s^2].',
        '% V [kt EAS], U [ft/s]. Se conservan hipotesis, polar 2D y alcance estatico.',
        '% Cada ejecucion guarda resultados en una carpeta nueva.', 'casos = struct([]);']
    for key,value in project['metadata'].items():lines.append('% '+key+': '+' '.join(value.splitlines()))
    for index,case in enumerate(cases,1):
        if case.get('method')!='niu':raise ValueError('La exportación MATLAB actual requiere el motor Niu; el procedimiento A4 se incluye como comparación separada.')
        c,_=prepare_case(case);p=c['parameters']
        def read(key):
            q=p.get(key,{})
            if q.get('value') is None:return None
            return convert(q['value'],q.get('unit',''),SPECS[key][1])
        cfg=dict(id=c['id'],name=case_label(c),basis=c.get('coefficient_basis','CN'),category=c.get('category','normal'),
            speed_mode=c.get('speed_mode','manual'),negative_rule=c.get('negative_rule','manual'),negative_end=c.get('negative_end','constant'),
            aero_model=c.get('aero_model','constant'),chord_mode=c.get('chord_mode','manual'),q_convention=c.get('q_convention','exact_eas'))
        for key,symbol in [('W','W'),('S','S'),('N','n_pos'),('nn','n_neg'),('cp','CN_pos'),('cn','CN_neg'),('Vc','Vc'),('Vd','Vd'),('rho','rho'),('chord','chord'),('span','span'),('a','a'),('g','g'),('Ub','U_b'),('Uc','U_c'),('Ud','U_d'),('Cse','Cse'),('Va_selected','Va_selected')]:cfg[key]=read(symbol)
        if cfg['Ub'] is None:cfg['Ub']=0
        cfg.update(rho0=RHO0,kt_to_fps=KT_TO_FPS)
        ap=appendix_defaults(case);cfg.update(appendix_enabled=include_appendix,ap_n3=ap['n3'],ap_n4=ap['n4'],ap_source=ap['source'],appendix_speed=ap['speed_mode'])
        lines+=['',f'%% Condicion {index}: '+' '.join(c['name'].splitlines()),'cfg = struct();']
        for key,value in cfg.items():
            q=p.get(dict(N='n_pos',nn='n_neg',cp='CN_pos',cn='CN_neg',Ub='U_b',Uc='U_c',Ud='U_d').get(key,key),{})
            if q.get('source'):lines.append('% '+key+' - '+' '.join(q['source'].splitlines())+'; pagina '+q.get('page',''))
            lines.append('cfg.'+key+' = '+literal(value)+';')
        for key,values in [('book_v',BOOK_V),('book_a',BOOK_A),('book_cl',BOOK_CL)]:lines.append('cfg.'+key+' = ['+' '.join(literal(x) for x in values)+'];')
        reference=calculate(case)
        if reference['blocked']:raise ValueError('MATLAB requiere una condición completa: '+'; '.join(reference['blocked']))
        refkeys=['W_S','Vs','V_A_stall','V_G_stall','mu','Kg','n3','n4','n_gust_c_pos','n_gust_c_neg','n_gust_d_pos','n_gust_d_neg']
        numeric=['W','S','N','nn','cp','cn','Vc','Vd','rho','chord','span','a','g','Ub','Uc','Ud','Cse','Va_selected','rho0','kt_to_fps','ap_n3','ap_n4']
        modes=['basis','category','speed_mode','negative_rule','negative_end','aero_model','chord_mode','q_convention','appendix_speed']
        signature=[cfg[k] for k in numeric]+[int(cfg['appendix_enabled'])]+list(BOOK_V)+list(BOOK_A)+list(BOOK_CL)
        lines.append('% Referencias del motor para comprobar las entradas originales al ejecutar. Si se editan, se omite esta comparación.')
        lines.append('cfg.reference_signature = ['+' '.join(literal(x) for x in signature)+'];')
        lines.append('cfg.reference_modes = {'+' '.join(literal(cfg[x]) for x in modes)+'};')
        lines.append('cfg.reference_keys = {'+' '.join(literal(k) for k in refkeys)+'};')
        lines.append('cfg.reference_values = ['+' '.join(literal(reference['values'][k]) for k in refkeys)+'];')
        lines.append(f'casos({index}) = cfg;')
    template=Path(__file__).with_name('matlab_template.m').read_text(encoding='utf-8-sig')
    with path.open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n\n'+template)
    return path
