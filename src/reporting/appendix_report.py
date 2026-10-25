from .reports import number,chunks,render_pdf,render_docx
from src.calculations.appendix import appendix_case,calculate_appendix
from src.plotting.envelopes import envelope_figure
import json

def export_appendix(project,cases,out,checkpoint,write_csv,allow_partial=False):
    pages=[dict(title='Procedimiento académico del Apéndice A',cover=True,author=project['metadata'].get('student',''),footer='Apéndice A · comparación académica',paragraphs=[
        'Nombre: '+(project['metadata'].get('student') or '[Nombre editable]'),
        'Proyecto: '+project['metadata'].get('title',''),
        'Materia: '+project['metadata'].get('subject',''),
        'Docente: '+project['metadata'].get('teacher',''),
        'Fecha: '+project['metadata'].get('date',''),
        'Método independiente de las ráfagas Niu. Incluye entradas, mínimos A3, lecturas documentadas y construcción A4. Las limitaciones de aplicabilidad se conservan.'])]
    root=out/'apendice_a';root.mkdir()
    for case in cases:
        checkpoint(90,'Procedimiento Apéndice A: '+case['name']);r=calculate_appendix(case)
        if r['blocked'] and not allow_partial:raise ValueError('Apéndice A incompleto: '+'; '.join(r['blocked']))
        folder=root/case['id'];folder.mkdir()
        (folder/'resultados.json').write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
        write_csv(folder/'parametros.csv',r['parameters']);write_csv(folder/'puntos.csv',r['points']);write_csv(folder/'verificaciones.csv',r['checks']);write_csv(folder/'procedimiento.csv',r['procedure'])
        curves=r['curves'];keys=list(curves);write_csv(folder/'curvas.csv',({k:curves[k][i] for k in keys} for i in range(len(curves.get('V',[])))),keys or ['sin datos'])
        pages.append(dict(title=r['name']+' · A3/A4',paragraphs=[r['academic_notice']]+r['assumptions']+['Pendiente: '+x for x in r['blocked']]+[x['paso']+': '+x['detalle'] for x in r['procedure']]))
        values=r['values'];rows=[['Magnitud','Valor','Unidad']]
        for k in ['W_S','Vc_A_raw','Vd_A_raw','Va_A_raw','Vf_A_raw','Vc','Vd','Vs','V_A_stall','V_G_stall','n_pos','n_neg','n3','n4']:
            rows.append([k,number(values.get(k)),'lbf/ft²' if k=='W_S' else ('1' if k.startswith('n') else 'kt EAS')])
        pages.append(dict(title='Tablas de velocidades y factores',table=rows,widths=[2.5,2.3,2],paragraphs=['A y G se calculan con CN positivo y negativo. Los mínimos A3 no reemplazan automáticamente las velocidades elegidas.']))
        for kind,title in [('man','Maniobras del procedimiento'),('combined','Contorno A4')]:
            fig=envelope_figure(r,kind)
            for ext in ['png','svg']:fig.savefig(folder/f'{kind}.{ext}',dpi=200,bbox_inches='tight')
            pages.append(dict(title=title,image=folder/f'{kind}.png',paragraphs=[r['academic_notice'],'A4 no se presenta como un cálculo físico independiente de ráfagas.']))
        for checks in chunks(r['checks'],7):pages.append(dict(title='Verificaciones del procedimiento',paragraphs=[x['estado']+' · '+x['código']+': '+x['detalle'] for x in checks]))
    render_pdf(pages,out/'reporte_apendice_a.pdf');render_docx(pages,out/'reporte_apendice_a.docx')
