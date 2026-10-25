"""Pruebas del producto instalado, incluido el EXE real y sus dependencias."""
from datetime import datetime
from pathlib import Path
from copy import deepcopy
import json
import sys
import traceback
from bootstrap import ROOT,FROZEN,fresh
from src.calculations.cases import demo_project
from src.calculations import calculate
from src.project import save_project,load_project

def run_selfcheck(gui=False):
    out=fresh(ROOT/'outputs/qa'/(('exe_gui_' if gui else 'exe_calculo_')+datetime.now().strftime('%Y%m%d_%H%M%S')))
    out.mkdir(parents=True)
    info=dict(frozen=FROZEN,executable=sys.executable,root=str(ROOT),checks=[],status='iniciado')
    def record():
        path=fresh(out/'verificacion.json');path.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    try:
        project=demo_project();c=project['cases'][0];result=calculate(c)
        assert not result['blocked']
        for key in ['man_pos','gust_pos','combined_pos']:assert len(result['curves'][key])>500
        saved=save_project(project,out/'proyecto.json');assert load_project(saved)==project
        info['checks']+=['Cálculo completo de ejemplo','Tres curvas consistentes','Guardado y carga JSON']
        if gui:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            from src.ui.calculator import CalculatorWindow,launch
            app=QApplication.instance() or QApplication([])
            def verify_edit():
                try:
                    win=next(w for w in app.topLevelWidgets() if isinstance(w,CalculatorWindow))
                    assert win.result['values']['W']==3000
                    assert win.result['values']['Vs']>result['values']['Vs']
                    for prefix in ['overview_','']:
                        for kind,label in [('man','Frontera de maniobra'),('gust','Condiciones de ráfaga'),('combined','Contorno combinado')]:
                            ax=win.canvases[prefix+kind].figure.axes[0];line=next(l for l in ax.lines if l.get_label()==label)
                            assert list(line.get_ydata())==win.result['curves'][{'man':'man_pos','gust':'gust_pos','combined':'combined_pos'}[kind]]
                    info['checks']+=['Edición W de 2400 a 3000 lbf','Actualización automática de las seis vistas de gráficas']
                    dup=win.duplicate_current('Otra condición');win.set_value('W',1800);win.recalculate(silent=True)
                    assert dup['parameters']['W']['value']==1800 and win.project['cases'][0]['parameters']['W']['value']==3000
                    info['checks'].append('Duplicado independiente de condición')
                    aircraft=win.add_aircraft('Avión del usuario');assert aircraft['parameters']['W']['value'] is None
                    win.loading=True
                    for key,p in c['parameters'].items():win.set_value(key,p['value'],p['unit'])
                    win.loading=False;win.recalculate(silent=True);assert not win.result['blocked']
                    win.set_value('S','abc');assert not win.recalculate(silent=True) and not win.result['curves']
                    win.set_value('S',174);assert win.recalculate(silent=True) and not win.result['blocked']
                    info['checks']+=['Nueva aeronave sin datos heredados','Dato inválido limpia las gráficas y puede corregirse']
                    for i,name in enumerate(['tres_envolventes','maniobras','rafagas','combinado','resultados','fuentes']):
                        win.tabs.setCurrentIndex(i);app.processEvents();win.grab().save(str(out/(name+'.png')))
                    win.tabs.setCurrentIndex(0);app.processEvents();win.grab().save(str(out/'calculadora_final.png'))
                    from src.reporting.exporter import export_project
                    exported=export_project(win.project,win.current,all_cases=True,include_niu=False)
                    info['export']=str(exported);info['checks']+=['CSV, PNG, SVG, PDF y DOCX desde '+('el EXE' if FROZEN else 'Python'),'Captura de las tres gráficas visibles en la calculadora']
                    info['status']='correcto';record();win.changed=False;app.quit()
                except Exception as exc:
                    info.update(status='error',error=str(exc),traceback=traceback.format_exc());record();app.exit(1)
            def edit():
                win=next(w for w in app.topLevelWidgets() if isinstance(w,CalculatorWindow));win.set_value('W',3000)
                QTimer.singleShot(1900,verify_edit)
            QTimer.singleShot(1000,edit)
            status=launch(project)
            if status:raise RuntimeError('Falló comprobación de interfaz; consulte '+str(out))
        else:
            import matplotlib;matplotlib.use('Agg')
            from src.reporting.exporter import export_project
            exported=export_project(project,project['active_case'],all_cases=True,include_niu=False)
            info['export']=str(exported);info['checks'].append('Exportación completa de dos aeronaves');info['status']='correcto';record()
    except Exception as exc:
        info.update(status='error',error=str(exc),traceback=traceback.format_exc());record();raise
    return out
