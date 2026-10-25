"""Genera casos iniciales nuevos, conserva cualquier archivo existente."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT, fresh
import json
from copy import deepcopy
from src.calculations.engine import SPECS
from src.calculations.units import RHO0

PHOTO='308aa1a8-3551-4e50-a2fb-7b7e27fd85c9.jpg y cd1a2819-dc32-4a24-b668-615ca1cc63e5.jpg'
BASE='https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-'

def param(value,unit,source='',page='',status='documentado',notes=''):
    return dict(value=value,unit=unit,source=source,page=page,status=status,notes=notes,
                original=dict(value=value,unit=unit,source=source,page=page,status=status))

def main():
    p={k:param(None,'1','','','pendiente','Dato sin confirmar') for k in SPECS}
    for k,v,u in [('W',4631,'lbf'),('S',181,'ft²'),('n_pos',3.8,'1'),('CN_pos',1.46,'1'),
                  ('W_S_photo',25.58,'lbf/ft²'),('nu_photo',4.4,'1'),('nn_photo',3.8,'1'),
                  ('Wn_photo',4631.5,'lbf'),('Wu_photo',3454.54,'lbf'),('g',32.2,'ft/s²')]:
        p[k]=param(v,u,PHOTO,'fotografías','documentado','Lectura visual de la hoja; no prueba el dato de una variante Cessna. lb se interpreta explícitamente como peso en lbf.')
    for k,v,u,note in [('rho',.0023,'lb/ft³ sin tipo','La foto rotula lb/ft³; debe aclararse si corresponde a slug/ft³ o lbm/ft³.'),
                      ('chord',4.26,'sin confirmar','Unidad no legible.'),('a',.105,'sin confirmar','No se ve unidad por grado o por radián.'),
                      ('a_photo',.105,'sin confirmar','Pendiente a distinta de CLalpha; no se intercambian.'),
                      ('CLalpha_photo',.11,'sin confirmar','No se confirma unidad ni si es del ala o de la aeronave.')]:
        p[k]=param(v,u,PHOTO,'fotografías','pendiente',note)
    for k,u in [('CN_neg','1'),('n_neg','1'),('rho0','slug/ft³'),('Vc','kt EAS'),('Vd','kt EAS'),('Va','kt EAS'),
                 ('U_c','ft/s'),('U_d','ft/s'),('altitude','ft'),('W_other','lbf')]:p[k]['unit']=u
    requirements=[
      ('01 motor','Un motor, excluidas turbinas.'),('02 posición alar','Ala más cerca del CG que del empenaje posterior.'),
      ('03 flecha','Flecha al cuarto de cuerda <=15 grados.'),('04 mandos','Mandos de borde de salida.'),
      ('05 AR ala','Alargamiento alar <=7.'),('06 AR horizontal','Alargamiento horizontal <=4.'),
      ('07 volumen horizontal','Volumen horizontal >=0.34.'),('08 AR vertical','Alargamiento vertical <=2.'),
      ('09 área vertical','Área vertical <=0.1 S.'),('10 perfiles cola','Perfiles de cola simétricos.'),
      ('11 exclusiones','Sin canard, biplano, colas T/V/cruciforme, slats, winglets ni dispositivos excluidos por A23.1(b).')]
    app=[dict(criterion=k,state='PENDIENTE',detail=t+' Falta documentación de la variante.') for k,t in requirements]
    original=dict(id='original_fotos',name='Original de las fotos con datos pendientes',method='apendice_a',category='normal',
                  aircraft='Cessna Centurión, variante pendiente de tesis',parameters=p,applicability=app,
                  assumptions=['No se infieren velocidades seleccionadas a partir de los dígitos borrosos.',
                               'No se identifica el significado físico de Wn y Wu sin la tesis.',
                               'Se calcula W/S interpretando el peso rotulado lb como lbf.'],changes=[])
    revised=deepcopy(original);revised.update(id='revisado_ilustrativo',name='Ejemplo revisado con hipótesis explícitas',method='subparte_c')
    revised['assumptions']=[
       'Caso ilustrativo normal con flaps retraídos, nivel del mar y pesos de las fotografías. No es la envolvente validada de un Cessna.',
       'Se utiliza CN positivo de la foto; no se convierte a CL. La pendiente elegida se trata como pendiente normal de la aeronave para esta demostración.',
       'rho=0.0023 se interpreta como slug/ft³. rho0 es atmósfera estándar para usar velocidades EAS; no se confunden ambas densidades.',
       'Se usa a=0.105 por grado de la foto como hipótesis pendiente; se convierte explícitamente a por radián. CLalpha=0.11 se conserva sin sustituir a.',
       'CN negativo=-1.35 es aproximación académica explícita tomada de A23.9(b)(1)(ii), no un dato de Cessna ni una verificación de esa aerodinámica.',
       'Vc=180, Vd=250 y Va=150 kt EAS son selecciones de demostración; no son lecturas de la foto ni velocidades operativas del avión.',
       'El ejemplo usa subparte C 2016 como referencia independiente. La edición y el criterio exacto de la tesis siguen pendientes.'
    ]
    def revise(k,v,u,reason,source='Selección explícita del caso ilustrativo',page=''):
        old=deepcopy(revised['parameters'][k])
        revised['parameters'][k].update(value=v,unit=u,status='supuesto',notes=reason)
        # Se conserva siempre la referencia y lectura original al revisar.
        if not old.get('source'):revised['parameters'][k]['source']=source;revised['parameters'][k]['page']=page
        revised['changes'].append(dict(parameter=k,before=old['value'],before_unit=old['unit'],after=v,after_unit=u,reason=reason))
    for k,v,u,reason in [
       ('rho',.0023,'slug/ft³','Interpretación física explícita; la unidad de la foto permanece en original.'),
       ('rho0',RHO0,'slug/ft³','Referencia EAS de atmósfera estándar al nivel del mar, independiente de rho local.'),
       ('chord',4.26,'ft','Se supone que la cuerda de la foto está en ft.'),('a',.105,'1/deg','Se supone por grado; conversión interna a por radián.'),
       ('CN_neg',-1.35,'1','Aproximación explícita del Ap. A; validar con polar de la aeronave.'),
       ('n_neg',-1.52,'1','Selección -0.4 n+ de §23.337 para subparte C normal; no es -0.5 n1 del Ap. A.'),
       ('Vc',180,'kt EAS','Selección ilustrativa de velocidad de crucero de diseño.'),
       ('Vd',250,'kt EAS','Selección ilustrativa de picada, satisface mínimos básicos de subparte C sin reducciones.'),
       ('Va',150,'kt EAS','Selección ilustrativa; distinta de intersección A y del mínimo de Fig. A3.'),
       ('U_c',50,'ft/s','§23.333(c), intervalo 0 a 20000 ft.'),('U_d',25,'ft/s','§23.333(c), intervalo 0 a 20000 ft.'),
       ('altitude',0,'ft','Nivel del mar, supuesto para demostración.'),('W_other',3454.54,'lbf','Peso Wu de fotografía solo para sensibilidad; no prueba categoría utilidad.')]:revise(k,v,u,reason)
    sensitivity=deepcopy(revised);sensitivity.update(id='peso_menor',name='Sensibilidad al peso menor de la foto')
    sensitivity['parameters']['W']['value']=3454.54;sensitivity['parameters']['W']['status']='supuesto'
    sensitivity['parameters']['W']['notes']='Se compara el peso Wu, sin asignar categoría utilidad.'
    sensitivity['changes'].append(dict(parameter='W',before=4631,before_unit='lbf',after=3454.54,after_unit='lbf',reason='Sensibilidad manteniendo velocidades y configuración; no acredita una condición real.'))
    project=dict(schema_version=1,metadata=dict(title='Tarea 04 segundo parcial Envolvente de Vuelo Cessna Centurión',
                 student='',subject='',teacher='',date='2026-10-23'),active_case='revisado_ilustrativo',cases=[original,revised,sensitivity])
    out=fresh(ROOT/'data/proyecto_inicial.json');out.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out)

if __name__=='__main__':main()
