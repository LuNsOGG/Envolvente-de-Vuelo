"""Persistencia restringida a la carpeta de trabajo; versiones sin sobrescribir."""
import json
import math
import re
from bootstrap import inside, fresh

def validate_project(project):
    if project.get('schema_version')!=1 or not isinstance(project.get('cases'),list) or not project['cases']:
        raise ValueError('JSON de proyecto incompatible: se requiere schema_version=1 y casos')
    ids=[]
    for case in project['cases']:
        if not isinstance(case.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}',case['id']):
            raise ValueError('ID de caso inválido: use letras minúsculas, números, guion o guion bajo')
        ids.append(case['id'])
        if not isinstance(case.get('parameters'),dict):raise ValueError('Caso sin parámetros')
        for symbol,p in case['parameters'].items():
            v=p.get('value')
            if v is not None and (isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v)):
                raise ValueError('Parámetro no finito o no numérico: '+symbol)
    if len(ids)!=len(set(ids)):raise ValueError('Identificadores de caso duplicados')
    if project.get('active_case') not in ids:raise ValueError('Caso activo desconocido')
    if not isinstance(project.get('metadata'),dict) or any(not isinstance(v,str) for v in project['metadata'].values()):
        raise ValueError('La portada requiere campos de texto')
    return project

def load_project(path):
    return validate_project(json.loads(inside(path).read_text(encoding='utf-8')))

def save_project(project,path):
    validate_project(project)
    path=fresh(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(project,f,ensure_ascii=False,indent=2,allow_nan=False)
    return path
