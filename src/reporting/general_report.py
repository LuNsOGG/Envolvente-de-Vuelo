"""Reporte de la aeronave activa sin textos específicos de la tarea Cessna."""
from .reports import number,chunks,equation_art
from src.calculations import calculate

def general_analysis_pages(project,case,result,plots,directory):
    meta=project['metadata'];aircraft=case.get('aircraft','Aeronave');v=result['values']
    pages=[dict(title='Envolventes de vuelo para '+aircraft,subtitle=case['name'],cover=True,footer='Calculadora de envolventes de vuelo',paragraphs=[
        'Proyecto: '+meta.get('title','Proyecto de envolventes'),
        'Nombre: '+(meta.get('student') or '[Nombre editable]'),'Materia: '+(meta.get('subject') or '[Materia editable]'),
        'Docente: '+(meta.get('teacher') or '[Docente editable]'),'Fecha: '+meta.get('date',''),
        'Criterio: '+case['method']+' · Categoría: '+case.get('category','normal'),
        'Este reporte documenta los datos, ecuaciones y resultados de la condición activa de la calculadora. Cada aeronave y cada condición conserva sus propios parámetros y referencias.'])]
    pages.append(dict(title='Aeronave y condiciones de cálculo',paragraphs=[
        'Aeronave: '+aircraft+'. Condición: '+case['name']+'. La configuración, pesos y condiciones deben documentarse en las hipótesis y fuentes de los parámetros.',
        'El cálculo utiliza los criterios históricos de FAR 23 seleccionados en la aplicación. La subparte C y el apéndice A se mantienen separados y sus verificaciones aparecen en este reporte. El resultado es un cálculo académico y no constituye certificación ni información operativa del avión.',
        'Las velocidades de las gráficas están expresadas en kt EAS. Peso como fuerza en lbf, densidad en slug/ft³ y pendiente aerodinámica por radián se obtienen mediante conversiones explícitas desde las unidades de entrada.',
        'Los datos marcados como supuestos no son mediciones ni especificaciones verificadas del avión. Un dato ausente bloquea el cálculo correspondiente.']+result['assumptions']+['Pendiente: '+s for s in result['blocked']]))
    for i,rows in enumerate(chunks(result['parameters'],7),1):
        table=[['Dato','Valor y unidad','Estado','Referencia','Observación']]
        for p in rows:table.append([p['símbolo']+'\n'+p['descripción'],number(p['valor'])+'\n'+p['unidad'],p['estado'],p['fuente']+'\n'+p['página'],p['observaciones']])
        pages.append(dict(title=f'Datos y trazabilidad {i}',table=table,widths=[1.35,1.05,.95,1.5,1.95],paragraphs=[
            'Los parámetros originales y su referencia se conservan en proyecto.json y parametros.csv. Las modificaciones se registran sin reemplazar los proyectos guardados.']))
    for i,eqs in enumerate(chunks(result['equations'],4),1):
        entries=[]
        for eq in eqs:
            index=result['equations'].index(eq)
            entries.append(dict(heading=eq['nombre'],image=equation_art(eq,directory,index),body='Sustitución: '+eq['sustitución']+' = '+number(eq['resultado'])+' '+eq['unidad']+'.',source=eq['fuente']))
        pages.append(dict(title=f'Ecuaciones y sustituciones {i}',equations=entries))
    pages.append(dict(title='Puntos característicos y construcción',paragraphs=[
        'Las curvas de pérdida usan el coeficiente normal positivo y negativo introducidos. La intersección A se obtiene con Vs por la raíz de n positivo; la Va elegida se mantiene como un parámetro separado.',
        'En subparte C, las cargas de ráfaga se calculan alrededor de n igual a uno. Entre Vc y Vd se interpolan los factores completos de forma lineal. El combinado conserva las condiciones que gobiernan con la limitación estática de CN declarada en la formulación.',
        'En apéndice A se utiliza la frontera O-A-C-D-E-F-G-O; los factores n3/n4 deben introducirse con una lectura documentada de A1/A2. Las intensidades y ecuaciones de un criterio no se sustituyen por las de otro.'],
        table=[['Punto','V kt EAS','n']]+[[p['punto'],number(p['V']),number(p['n'])] for p in result['points']],widths=[3.4,1.7,1.7],
        second_table=[['Intersección','V kt EAS','n']]+[[p['tipo'],number(p['V']),number(p['n'])] for p in result['intersections']]))
    for kind,title in [('man','Envolvente de maniobras'),('gust','Envolvente de ráfagas'),('combined','Envolvente combinada')]:
        pages.append(dict(title=title,image=plots[kind+'_png'],paragraphs=[aircraft+' · '+case['name']+'.',
            'La figura usa los mismos datos numéricos que curvas.csv y la pantalla de la calculadora. Las ráfagas que superan un límite de maniobra se muestran y se señalan; no se corrigen cambiando los datos.']))
    for i,checks in enumerate(chunks(result['checks'],8),1):
        pages.append(dict(title=f'Verificaciones de la condición {i}',paragraphs=[ck['estado']+' | '+ck['código']+'. '+ck['detalle'] for ck in checks]))
    ordered=[case]+[c for c in project['cases'] if c['id']!=case['id']]
    for i,group in enumerate(chunks(ordered,3),1):
        results=[calculate(c) for c in group];table=[['Resultado']+[c.get('aircraft','Aeronave')+'\n'+c['name'] for c in group]]
        for key in ['W_S','Vs','V_A_stall','Kg','n_gust_c_pos','n_gust_c_neg']:
            table.append([key]+[number(r['values'].get(key)) for r in results])
        pages.append(dict(title=f'Comparación de aeronaves y condiciones {i}',table=table,widths=[1.6]+[5.2/len(group)]*len(group),paragraphs=[
            'Cada columna conserva los parámetros y condiciones de su caso. La comparación numérica no implica que dos aeronaves tengan la misma base de diseño ni que una satisfaga la categoría de otra.']))
    if 'n_gust_c_pos' in v:
        discussion=f'W/S={v["W_S"]:.5f} lbf/ft²; n de ráfaga en Vc: positivo {v["n_gust_c_pos"]:.5f} y negativo {v["n_gust_c_neg"]:.5f}.'
    else:discussion='Consulte los datos pendientes indicados por el motor antes de interpretar las envolventes.'
    pages.append(dict(title='Resultados y referencias',paragraphs=[discussion,
        'Las hipótesis y las observaciones de esta condición delimitan el alcance del resultado. La aplicabilidad de la normativa se revisa para cada aeronave, y el modelo cuasiestático no resuelve pérdida dinámica, flutter ni resistencia estructural.',
        'Referencias de cálculo: 14 CFR Part 23, edición 2016, §§23.333, 23.335, 23.337 y 23.341, o apéndice A cuando está seleccionado. Las referencias específicas de la aeronave se muestran en la tabla de datos.',
        'GovInfo oficial: https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/CFR-2016-title14-vol1-sec23-341.pdf',
        'Se incluye proyecto.json para reproducir el cálculo, así como CSV, gráficas PNG y SVG. El DOCX conserva texto y tablas editables; las ecuaciones se insertan como imágenes.']))
    if case.get('method')=='niu':
        pages[1]['paragraphs'][1]='Ráfagas cuasiestáticas de Niu, cap.3, ecuaciones 3.4.3–3.4.5. Las velocidades y límites de maniobra se especifican por caso; no se impone n3=N ni n4=-0.5N.'
        for page in pages:
            if page['title']=='Puntos característicos y construcción':
                page['paragraphs']=[
                    'La pérdida usa '+case.get('coefficient_basis','CN')+'. Se resuelven sus intersecciones con n=1 y los límites de maniobra. La tabla por Mach se aplica solo cuando está seleccionada.',
                    'Las ráfagas parten de n=1 y emplean μ=2(W/S)/(ρ c a g), Kg=0.88μ/(5.3+μ) y Δn=Kg U V a/[498(W/S)]. La pendiente se convierte a radianes.',
                    'Con Ub>0, VB es la intersección de pérdida positiva y la ráfaga máxima. Los factores se unen linealmente de B a C y D; con Ub=0 se usa Uc hasta Vc. El combinado conserva extremos y la limitación de pérdida estática.',
                    'Las raíces numéricas y los puntos B/C/D se incluyen explícitamente en la malla. La demanda de ráfaga puede superar el límite de maniobra.']
        pages[-1]['paragraphs'][2]='Referencia principal: Niu, Airframe Structural Design, capítulo 3, ecuaciones 3.4.1–3.4.5 y ejemplo 2 de §3.11, pp.74–77, Chapter3.pdf del proyecto. Las aproximaciones de lectura e intensidades seleccionadas figuran en las hipótesis.'
        from src.calculations.examples import VARIABLES
        for i,rows in enumerate(chunks(VARIABLES,8),1):
            pages.append(dict(title=f'Resumen de variables {i}',table=[['Símbolo','Nombre','Significado']]+[list(row) for row in rows],widths=[1.,1.8,4.]))
    if result.get('reference_rows'):
        rows=[['Magnitud','kt EAS','Criterio']]+[[row['magnitud'],number(row['valor']),row['criterio']] for row in result['speed_rows']]
        pages.append(dict(title='Velocidades mínimas seleccionadas e intersecciones',table=rows,widths=[1.65,1.05,4.1],paragraphs=['A, Va mínimo base y Va seleccionada son magnitudes independientes. La selección de la tesis se conserva; el peso y la polar revisados modifican las intersecciones.']))
        for i,group in enumerate(chunks(result['reference_rows'],8),1):
            rows=[['Dato','Tesis','Actual','Unidad','Página']]+[[row['dato'],number(row['tesis']),number(row['recalculado']),row['unidad'],row['pagina']] for row in group]
            pages.append(dict(title=f'Contraste con la tesis IPN {i}',table=rows,widths=[2.4,1.,1.,1.1,1.3],paragraphs=['La referencia publicada conserva sus inconsistencias; el cálculo actual no adopta resultados erróneos para forzar coincidencias.']))
        for i,group in enumerate(chunks(result['source_issues'],4),1):
            pages.append(dict(title=f'Discrepancias e hipótesis de la tesis {i}',paragraphs=group))
    return pages
