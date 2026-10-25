import os
from copy import deepcopy
from uuid import uuid4
import pytest
from bootstrap import ROOT
from src.calculations.cases import new_case,demo_project,duplicate_case,blank_project
from src.calculations import calculate
from src.project import validate_project,save_project,load_project

def test_new_aircraft_has_no_other_aircraft_values():
    c=new_case('Mi avión');assert c['parameters']['W']['value'] is None
    assert c['parameters']['CN_neg']['value'] is None
    assert not c['requires_thesis'] and c['aircraft']=='Mi avión'

def test_demonstrations_are_explicit_and_both_calculate():
    p=demo_project();validate_project(p)
    for c in p['cases']:
        r=calculate(c);assert not r['blocked'];assert not r['requires_thesis']
        assert not any('Falta tesis' in x['detalle'] for x in r['checks'])
        assert c['parameters']['W']['status']=='supuesto'
        assert 'Ejemplo' in c['parameters']['W']['source']

def test_duplicate_preserves_provenance_and_is_independent():
    c=demo_project()['cases'][0];d=duplicate_case(c);d['parameters']['W']['value']=1500
    assert d['id']!=c['id'] and c['parameters']['W']['value']==2400
    assert d['parameters']['W']['original']==c['parameters']['W']['original']

@pytest.fixture
def calculator():
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from src.ui.calculator import CalculatorWindow
    app=QApplication.instance() or QApplication([])
    window=CalculatorWindow(demo_project());window.automatic.setChecked(False)
    yield window
    window.changed=False;window.close();app.processEvents()

def test_dashboard_contains_all_three_envelopes(calculator):
    w=calculator;assert w.tabs.currentIndex()==0
    assert all(k in w.canvases for k in ['overview_man','overview_gust','overview_combined'])
    assert w.tabs.count()==6

def test_edit_updates_all_graphs(calculator):
    w=calculator;before=w.result['values']['Vs'];w.set_value('W',3000);w.recalculate(silent=True)
    assert w.result['values']['W']==3000 and w.result['values']['Vs']>before
    for kind,label,key in [('man','Frontera de maniobra','man_pos'),('gust','Condiciones de ráfaga','gust_pos'),('combined','Contorno combinado','combined_pos')]:
        for prefix in ['overview_','']:
            line=next(l for l in w.canvases[prefix+kind].figure.axes[0].lines if l.get_label()==label)
            assert list(line.get_ydata())==w.result['curves'][key]

def test_new_aircraft_and_duplicate_are_independent(calculator):
    w=calculator;original=w.current;copy=w.duplicate_current('Peso menor');w.set_value('W',1800);w.recalculate(silent=True)
    assert next(c for c in w.project['cases'] if c['id']==original)['parameters']['W']['value']==2400
    assert copy['parameters']['W']['value']==1800
    fresh=w.add_aircraft('Avión nuevo');assert fresh['parameters']['S']['value'] is None
    assert len(w.project['cases'])==4

def test_invalid_edit_does_not_leave_stale_envelope(calculator):
    w=calculator;w.set_value('S','incorrecto');assert not w.recalculate(silent=True)
    assert w.result['blocked'] and not w.result['curves']
    assert not any(l.get_label()=='Contorno combinado' for l in w.canvases['overview_combined'].figure.axes[0].lines)
    w.set_value('S',174);assert w.recalculate(silent=True) and not w.result['blocked']

def test_category_edit_is_explicit(calculator):
    w=calculator;w.category.setCurrentIndex(w.category.findData('utilidad'));w.recalculate(silent=True)
    assert w.result['values']['n_pos']==3.8  # no se cambia el dato silenciosamente
    w.category_factors();assert w.result['values']['n_pos']==4.4
    assert w.result['values']['n_neg']==pytest.approx(-1.76)

def test_source_edits_keep_original(calculator):
    w=calculator;key=w.keys.index('W');original=deepcopy(w.case()['parameters']['W']['original'])
    w.trace.item(key,4).setText('Manual del avión página 12');w.set_value('W',2800);w.recalculate(silent=True)
    assert w.case()['parameters']['W']['original']==original
    assert w.case()['parameters']['W']['source']=='Manual del avión página 12'

def test_units_from_ui_are_converted(calculator):
    w=calculator;w.set_value('S',16.16512896,'m²');w.recalculate(silent=True)
    assert w.result['values']['S']==pytest.approx(174)

def test_reusable_project_roundtrip(calculator):
    w=calculator;w.add_aircraft('Otro modelo');folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True)
    path=save_project(w.project,folder/'aviones.json');p=load_project(path)
    assert len(p['cases'])==3 and p['cases'][-1]['aircraft']=='Otro modelo'

def test_general_report_names_active_aircraft(calculator):
    from src.reporting.reports import analysis_pages
    w=calculator;w.aircraft.setText('Modelo del usuario');w.recalculate(silent=True)
    folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True)
    from src.plotting.envelopes import export_plots
    plots=export_plots(w.result,folder);pages=analysis_pages(w.project,w.case(),w.result,plots,folder)
    assert pages[0]['title']=='Envolventes de vuelo para Modelo del usuario'
    assert 'Cessna' not in str(pages) and 'Falta tesis' not in str(pages)
