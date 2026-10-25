"""Persistencia restringida a la carpeta de trabajo; versiones sin sobrescribir."""
import json
import math
import re
from bootstrap import inside, fresh

def validate_project(project):
    if not isinstance(project,dict):raise ValueError('El proyecto debe ser un objeto JSON')
    if project.get('schema_version')!=1 or not isinstance(project.get('cases'),list) or not project['cases']:
        raise ValueError('JSON de proyecto incompatible: se requiere schema_version=1 y casos')
    ids=[]
    for case in project['cases']:
        if not isinstance(case,dict):raise ValueError('Cada condición debe ser un objeto')
        for field in ['name','aircraft','method']:
            if not isinstance(case.get(field),str) or not case[field].strip():raise ValueError('Condición sin campo de texto: '+field)
        for field in ['assumptions','changes','applicability']:
            if field in case and not isinstance(case[field],list):raise ValueError(field+': se requiere una lista')
        if any(not isinstance(x,str) for x in case.get('assumptions',[])):raise ValueError('Las hipótesis deben ser textos')
        if any(not isinstance(x,dict) for x in case.get('changes',[])+case.get('applicability',[])):raise ValueError('Historial y aplicabilidad deben contener objetos')
        if not isinstance(case.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',case['id']):
            raise ValueError('ID de caso inválido: use letras minúsculas, números, guion o guion bajo')
        ids.append(case['id'])
        if not isinstance(case.get('parameters'),dict):raise ValueError('Caso sin parámetros')
        for symbol,p in case['parameters'].items():
            if not isinstance(p,dict):raise ValueError('Parámetro sin estructura: '+symbol)
            if not isinstance(p.get('unit'),str) or not p['unit']:raise ValueError('Parámetro sin unidad: '+symbol)
            for field in ['source','page','status','notes']:
                if field in p and not isinstance(p[field],str):raise ValueError(symbol+': '+field+' debe ser texto')
            v=p.get('value')
            if v is not None and (isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v)):
                raise ValueError('Parámetro no finito o no numérico: '+symbol)
    if len(ids)!=len(set(ids)):raise ValueError('Identificadores de caso duplicados')
    if project.get('active_case') not in ids:raise ValueError('Caso activo desconocido')
    if not isinstance(project.get('metadata'),dict) or any(not isinstance(v,str) for v in project['metadata'].values()):
        raise ValueError('La portada requiere campos de texto')
    return project

def load_project(path):
    return validate_project(json.loads(inside(path).read_text(encoding='utf-8-sig')))

def save_project(project,path):
    validate_project(project)
    path=fresh(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(project,f,ensure_ascii=False,indent=2,allow_nan=False)
    return path
