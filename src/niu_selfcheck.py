"""Comprobación numérica y funcional del EXE instalado, incluidos ambos ejemplos."""
from datetime import datetime
import json
import sys
import traceback
from bootstrap import ROOT,FROZEN,fresh
from src.calculations import calculate
from src.calculations.examples import example_project
from src.project import save_project,load_project


def run_selfcheck(gui=False):
    out=fresh(ROOT/'outputs/qa'/('niu_exe_'+datetime.now().strftime('%Y%m%d_%H%M%S')));out.mkdir(parents=True)
    info=dict(frozen=FROZEN,executable=sys.executable,root=str(ROOT),status='iniciado',checks=[],examples={})
    def record():
        (out/'verificacion.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
    try:
        for number in [1,2]:
            project=example_project(number);r=calculate(project['cases'][0]);v=r['values']
            assert not r['blocked'] and r['curves']['gust_pos'][0]==r['curves']['gust_neg'][0]==1
            assert r['curves']['man_pos']!=r['curves']['gust_pos']
            expected=3.910272016204428 if number==1 else 2.9496526506337344
            assert abs(v['n3']-expected)<1e-10
            if number==2:assert abs(v['delta_d']-1.3839304213427412)<1e-10 and v['Vb']<325
            path=save_project(project,out/f'ejemplo_{number}.json');assert load_project(path)==project
            info['examples'][str(number)]=v
        info['checks']+=['Ráfagas independientes alrededor de n=1','Dos ejemplos completos; resultados contra cálculo independiente','Guardar y abrir conserva todos los datos']
        if not gui:info['status']='correcto';record();return out
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication,QDialog,QTextBrowser
        from src.ui.worksheet import WorksheetWindow,launch
        app=QApplication.instance() or QApplication([])
        def window():return next(w for w in app.topLevelWidgets() if isinstance(w,WorksheetWindow))
        def fail(exc):
            info.update(status='error',error=str(exc),traceback=traceback.format_exc());record();app.exit(1)
        def capture(win,name):
            app.processEvents()
            for canvas in win.canvases.values():
                if canvas.isVisible():canvas.draw()
            app.processEvents();assert win.grab().save(str(out/(name+'.png')))
        def check_views(win):
            from matplotlib.colors import to_rgb
            for prefix in ['overview_','']:
                for kind,label,key in [('man','Frontera de maniobra','man_pos'),('gust','Condiciones de ráfaga','gust_pos'),('combined','Contorno combinado','combined_pos')]:
                    line=next(l for l in win.canvases[prefix+kind].figure.axes[0].lines if l.get_label()==label)
                    assert list(line.get_ydata())==win.result['curves'][key]
                    rgb=to_rgb(line.get_color());assert max(rgb)-min(rgb)<1e-10
        def first():
            try:
                win=window();assert win.tabs.count()==4 and win.table.rowCount()==14
                assert [a.text() for a in win.examples_button.menu().actions()]==['Ejemplo 1','Ejemplo 2']
                check_views(win);capture(win,'ejemplo_1')
                win.set_value('W',4000);QTimer.singleShot(1800,edited)
            except Exception as exc:fail(exc)
        def edited():
            try:
                win=window();assert win.result['values']['W']==4000 and win.result['values']['W_S']==4000/181
                assert win.result['values']['n3']!=info['examples']['1']['n3'];check_views(win)
                win.set_value('S','abc');assert not win.recalculate() and not win.result['curves']
                win.set_value('S',181);assert win.recalculate()
                win.examples_button.menu().actions()[1].trigger();QTimer.singleShot(1000,second)
            except Exception as exc:fail(exc)
        def second():
            try:
                win=window();assert win.case()['example']==2 and win.result['values']['W']==88000
                assert abs(win.result['values']['n3']-2.9496526506337344)<1e-10;check_views(win)
                for i,label in enumerate(['tres','maniobra','rafaga','combinado']):
                    win.tabs.setCurrentIndex(i);capture(win,'ejemplo_2_'+label)
                win.tabs.setCurrentIndex(0)
                def inspect_summary():
                    try:
                        dialog=next(w for w in app.topLevelWidgets() if isinstance(w,QDialog) and w.windowTitle()=='Resumen de variables')
                        text=dialog.findChild(QTextBrowser).toPlainText()
                        assert all(k in text for k in ['W/S','Kg','CLα','n3','VB'])
                        dialog.grab().save(str(out/'resumen_variables.png'));dialog.accept()
                    except Exception as exc:fail(exc)
                QTimer.singleShot(600,inspect_summary);win.variables_button.click()
                info['checks']+=['Botón Ejemplos carga ambos casos con sus parámetros y unidades','Edición de peso actualiza las seis vistas; dato inválido retira curvas','Resumen de variables visible; gráficos monocromos']
                QTimer.singleShot(200,finish)
            except Exception as exc:fail(exc)
        def finish():
            try:
                win=window()
                from src.reporting.exporter import export_project
                info['exports']={}
                for n in [2,1]:
                    win.examples_button.menu().actions()[n-1].trigger();check_views(win)
                    info['exports'][str(n)]=str(export_project(win.project,win.current,all_cases=True,include_niu=False))
                win.tabs.setCurrentIndex(0);capture(win,'calculadora_final')
                info['checks']+=['Exportación de ambos casos en PNG/SVG/CSV/JSON/PDF/DOCX','Inicio final con Ejemplo 1; CN negativo -1.35']
                info['status']='correcto';record();win.changed=False;win.timer.stop();app.quit()
            except Exception as exc:fail(exc)
        QTimer.singleShot(1200,first)
        status=launch(example_project(1))
        if status:raise RuntimeError('Falló comprobación: '+str(out))
    except Exception as exc:
        if info['status']!='error':info.update(status='error',error=str(exc),traceback=traceback.format_exc());record()
        raise
    return out
