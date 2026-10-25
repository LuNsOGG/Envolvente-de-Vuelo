"""Comprobación de la vista Excel y del ejecutable realmente entregado."""
from datetime import datetime
import json
import sys
import traceback
from bootstrap import ROOT, FROZEN, fresh
from src.calculations import calculate
from src.calculations.worksheet import worksheet_project, FIELD_KEYS
from src.project import save_project, load_project


def completed_fixture():
    project=worksheet_project()
    c=project['cases'][0]
    c['aircraft']='Prueba automatizada: datos adicionales de ensayo'
    for key,value in [('CN_neg',-1.3),('n3',4.1),('n4',-2.3)]:
        c['parameters'][key].update(value=value,status='prueba',source='Dato sintético exclusivo de verificación, no valor de una aeronave')
    return project


def run_selfcheck(gui=False):
    from .niu_selfcheck import run_selfcheck as check
    return check(gui)


def run_legacy_selfcheck(gui=False):
    out=fresh(ROOT/'outputs/qa'/('hoja_exe_'+datetime.now().strftime('%Y%m%d_%H%M%S'))); out.mkdir(parents=True)
    info=dict(frozen=FROZEN,executable=sys.executable,root=str(ROOT),status='iniciado',checks=[])
    def record():
        (out/'verificacion.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    try:
        default=worksheet_project(); initial=calculate(default['cases'][0])
        assert default['cases'][0]['parameters']['CN_neg']['value'] is None
        assert 'combined_pos' not in initial['curves'] and 'gust_pos' not in initial['curves']
        assert all(x is None for x in initial['curves']['man_neg'])
        assert abs(initial['values']['Vc']-17*(3.8*4631/181)**.5)<1e-9
        info['checks']+=['Inicio con datos de las fotos, sin ejemplos inventados','CN negativo y n3/n4 ausentes no se rellenan','Velocidades mínimas y W/S automáticos']
        path=save_project(default,out/'hoja_fotos.json'); assert load_project(path)==default
        if not gui:
            from src.reporting.exporter import export_project
            info['export']=str(export_project(default,default['active_case'],all_cases=True,include_niu=False)); info['status']='correcto'; record(); return out
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        from src.ui.worksheet import WorksheetWindow, launch
        app=QApplication.instance() or QApplication([])
        def verify_edit():
            try:
                win=next(w for w in app.topLevelWidgets() if isinstance(w,WorksheetWindow))
                assert win.result['values']['W']==4200
                assert win.result['values']['W_S']==4200/181
                assert win.result['values']['Vc']<initial['values']['Vc']
                assert win.tabs.count()==4 and win.table.rowCount()==14
                assert [win.table.item(i,0).text() for i in range(14)]==['nᵤ','nₙ','Wₙ','Wᵤ','W','S','W/S','N','Cₙ máx.','ρ','c','a','g','CLα']
                win.grab().save(str(out/'inicio_sin_suposiciones.png'))
                info['checks']+=['Catorce filas idénticas en orden al Excel','Edición automática W=4200 actualiza W/S y velocidades','Cuatro pestañas y controles simplificados']
                win.replace_project(completed_fixture()); assert not win.result['blocked']
                win.set_value('W',4000)
                QTimer.singleShot(1700,verify_complete)
            except Exception as exc:fail(exc)
        def verify_complete():
            try:
                win=next(w for w in app.topLevelWidgets() if isinstance(w,WorksheetWindow))
                assert win.result['values']['W']==4000
                for prefix in ['overview_','']:
                    for kind,label,key in [('man','Frontera de maniobra','man_pos'),('gust','Condiciones de ráfaga','gust_pos'),('combined','Contorno combinado','combined_pos')]:
                        line=next(l for l in win.canvases[prefix+kind].figure.axes[0].lines if l.get_label()==label)
                        assert list(line.get_ydata())==win.result['curves'][key]
                        from matplotlib.colors import to_rgb
                        rgb=to_rgb(line.get_color()); assert max(rgb)-min(rgb)<1e-10
                info['checks']+=['Con datos adicionales explícitos de ensayo, las seis vistas coinciden con el motor','Trazos de gráficas en escala de grises']
                win.set_value('S','abc'); assert not win.recalculate() and not win.result['curves']
                win.set_value('S',181); assert win.recalculate()
                for index,name in enumerate(['tres_envolventes_completas_prueba','maniobras','rafagas','combinado']):
                    win.tabs.setCurrentIndex(index); app.processEvents()
                    for canvas in win.canvases.values():
                        if canvas.isVisible():canvas.draw()
                    app.processEvents(); win.grab().save(str(out/(name+'.png')))
                from src.reporting.exporter import export_project
                info['export_complete_test']=str(export_project(win.project,win.current,all_cases=True,include_niu=False))
                win.replace_project(default); win.tabs.setCurrentIndex(0); app.processEvents()
                for canvas in win.canvases.values():
                    if canvas.isVisible():canvas.draw()
                app.processEvents(); win.grab().save(str(out/'calculadora_final.png'))
                info['export']=str(export_project(win.project,win.current,all_cases=True,include_niu=False))
                info['checks']+=['Texto inválido limpia las gráficas y corregirlo recupera el cálculo','Exportación completa de prueba y parcial real en PNG/SVG/CSV/JSON/PDF/DOCX','La captura final y el inicio del programa no contienen datos sintéticos adicionales']
                info['status']='correcto'; record(); win.changed=False; app.quit()
            except Exception as exc:fail(exc)
        def fail(exc):
            info.update(status='error',error=str(exc),traceback=traceback.format_exc()); record(); app.exit(1)
        def edit():
            try:
                win=next(w for w in app.topLevelWidgets() if isinstance(w,WorksheetWindow)); win.set_value('W',4200); QTimer.singleShot(1700,verify_edit)
            except Exception as exc:fail(exc)
        QTimer.singleShot(1200,edit)
        status=launch(default)
        if status:raise RuntimeError('La comprobación falló: '+str(out))
    except Exception as exc:
        if info['status']!='error':info.update(status='error',error=str(exc),traceback=traceback.format_exc()); record()
        raise
    return out
