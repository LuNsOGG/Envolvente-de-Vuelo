"""Datos efectivos para títulos e hipótesis; las lecturas originales se conservan."""
from .units import convert

def case_label(case):
    name=case.get('name','Condición')
    if case.get('reference_dataset')=='ipn_2007':
        p=case['parameters'].get('W',{})
        try:w=convert(p.get('value'),p.get('unit',''),'weight')
        except (ValueError,TypeError):return name+' · peso pendiente'
        base=4000 if case.get('id')=='cessna_revisado' else 4631
        return name if w==base else f'Condición editada · W={w:.9g} lbf (base {base} lb)'
    return name

def update_context(case,result):
    if case.get('method')!='niu':return
    v=result['values'];p=case['parameters'];original=list(case.get('assumptions',[]))
    from .examples import example_project
    from .worksheet import worksheet_project
    known=set(worksheet_project()['cases'][0]['assumptions'])
    for n in [1,2]:
        for c in example_project(n)['cases']:known.update(c.get('assumptions',[]))
    current=[]
    def value(key):
        q=p.get(key,{})
        return 'pendiente' if q.get('value') is None else f"{q['value']:.12g} {q.get('unit','')}"
    current.append('Condición efectiva: W='+value('W')+'; S='+value('S')+'; N='+value('n_pos')+'; coeficiente '+case.get('coefficient_basis','CN')+' positivo='+value('CN_pos')+' y negativo='+value('CN_neg')+'.')
    current.append('Ráfagas de la condición: a='+value('a')+'; Uc='+value('U_c')+'; Ud='+value('U_d')+'; Ub='+value('U_b')+'; densidad='+value('rho')+'.')
    current.append('Velocidades efectivas: Vc='+value('Vc')+'; Vd='+value('Vd')+'; Va seleccionada='+value('Va_selected')+'. La intersección A se calcula por separado.')
    current.append('Cuerda '+('geométrica S/b' if case.get('chord_mode')=='geometric' else 'introducida')+': '+value('chord')+'. Modelo aerodinámico: '+case.get('aero_model','constant')+'.')
    if case.get('reference_dataset')=='ipn_2007':current.append('Las lecturas de la tesis y sus hipótesis originales se conservan como referencias. Los coeficientes y la pendiente efectivos requieren justificar la condición del avión; la polar de origen es 2D a Mach 0.5 y Re=4e6.')
    current.append('Modelo cuasiestático con pérdida estática. La aplicabilidad normativa y las fuentes se revisan para esta condición.')
    current += ['Anotación del proyecto: '+x for x in original if x not in known]
    result.update(name=case_label(case),assumptions=current,reference_assumptions=original)
