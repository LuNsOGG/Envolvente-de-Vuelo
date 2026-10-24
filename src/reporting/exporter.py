from datetime import datetime
from pathlib import Path
import csv
import hashlib
import json
from bootstrap import ROOT,fresh
from src.project import save_project
from src.calculations import calculate,compare
from src.plotting.envelopes import export_plots
from src.plotting.niu import export_niu,FIGURES
from .reports import analysis_pages,niu_pages,render_pdf,render_docx

def write_csv(path,rows,fields=None):
    rows=list(rows)
    if fields is None:fields=list(rows[0]) if rows else ['sin datos']
    with path.open('x',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items() if k in fields})

def export_project(project,case_id,all_cases=False,niu_only=False,include_niu=None):
    chosen=next(c for c in project['cases'] if c['id']==case_id)
    legacy=chosen.get('requires_thesis','Wn_photo' in chosen['parameters'])
    if include_niu is None:include_niu=legacy
    out=fresh(ROOT/'outputs'/('entrega_'+datetime.now().strftime('%Y%m%d_%H%M%S')));out.mkdir(parents=True)
    save_project(project,out/'proyecto.json')
    originals={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.iterdir() if p.suffix.lower() in ['.pdf','.jpg']}
    (out/'huellas_fuentes.json').write_text(json.dumps(originals,indent=2),encoding='utf-8')
    if not niu_only:
        cases=project['cases'] if all_cases else [chosen]
        paths={};results={}
        for case in cases:
            folder=out/case['id'];folder.mkdir();result=calculate(case);results[case['id']]=result
            (folder/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
            write_csv(folder/'parametros.csv',result['parameters']);write_csv(folder/'ecuaciones.csv',result['equations'])
            write_csv(folder/'puntos.csv',result['points'],['punto','V','n'])
            write_csv(folder/'intersecciones.csv',result['intersections'],['tipo','V','n'])
            write_csv(folder/'verificaciones.csv',result['checks'])
            curves=result['curves'];keys=list(curves)
            write_csv(folder/'curvas.csv',({k:curves[k][i] for k in keys} for i in range(len(curves.get('V',[])))),keys or ['sin datos'])
            paths[case['id']]=export_plots(result,folder)
        result=results[case_id];folder=out/case_id
        equations=folder/'ecuaciones';equations.mkdir()
        pages=analysis_pages(project,chosen,result,paths[case_id],equations)
        render_pdf(pages,out/'reporte_analisis.pdf');render_docx(pages,out/'reporte_analisis.docx')
        write_csv(out/'comparacion_resultados.csv',compare(project['cases']))
        write_csv(out/'cambios.csv',chosen.get('changes',[]))
    if include_niu or niu_only:
        niudir=out/'figuras_niu';niudir.mkdir();images=export_niu(niudir)
        pages=niu_pages(project,images);render_pdf(pages,out/'reporte_figuras_niu.pdf');render_docx(pages,out/'reporte_figuras_niu.docx')
        write_csv(out/'indice_niu.csv',[dict(figura=f['number'],título=f['title'],impresa=f['page'],visor=f['viewer'],estado='Localizada y revisada visualmente') for f in FIGURES])
    note='Aeronave: '+chosen.get('aircraft','Sin identificar')+'\nCondición: '+chosen['name']+'\n'
    if legacy:note+='Caso de la tarea Cessna: falta tesis y confirmación de variante y fuentes.\n'
    (out/'LEER_PRIMERO.txt').write_text(note+'Todas las cifras proceden del motor común. Revise hipótesis y verificaciones de esta condición.\nDOCX editable en texto y tablas; fórmulas como imágenes.\nCada exportación es nueva; no se sobrescriben ni borran archivos.\n',encoding='utf-8')
    return out
