from copy import deepcopy
import pytest
from src.calculations import calculate
from src.calculations.examples import example_project


def test_18_figures_option_defaults_on_and_is_preserved(qt_lifetime):
    from src.ui.worksheet import WorksheetWindow
    w=WorksheetWindow(example_project(1))
    try:
        assert w.include_niu.isChecked()
        w.include_niu.setChecked(False);p=deepcopy(w.project);w.replace_project(p)
        assert not w.include_niu.isChecked() and not w.project['export_options']['include_niu']
    finally:w.changed=False;w.timer.stop();w.close()

def test_18_export_contains_both_figure_reports_and_all_ten_drawings(monkeypatch):
    import src.reporting.exporter as exporter
    from bootstrap import ROOT
    from uuid import uuid4
    folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True);monkeypatch.setattr(exporter,'ROOT',folder)
    p=example_project(1);out=exporter.export_project(p,p['active_case'],niu_only=True)
    assert (out/'reporte_figuras_niu.pdf').exists() and (out/'reporte_figuras_niu.docx').exists()
    assert len(list((out/'figuras_niu').glob('*.png')))==10
    assert len((out/'indice_niu.csv').read_text(encoding='utf-8-sig').splitlines())==11


def test_19_appendix_is_independent_and_preserves_inputs():
    from src.calculations.appendix import calculate_appendix
    c=example_project(1)['cases'][0];before=deepcopy(c);niu=calculate(c);a=calculate_appendix(c)
    assert c==before and not a['blocked']
    assert a['values']['n3']==3.8 and niu['values']['n3']>4
    assert a['values']['Vc_A_raw']<a['values']['Vc']==170
    assert 'combined_pos' in a['curves'] and 'gust_pos' not in a['curves']
    c['appendix_review']=dict(n3=5,n4=-3,source='Lectura de prueba',page='A1/A2',speed_mode='minimum')
    b=calculate_appendix(c);assert b['values']['Vc']==pytest.approx(b['values']['Vc_A_raw'])
    assert max(b['curves']['combined_pos'])==5

def test_19_missing_or_undocumented_readings_are_not_invented():
    from src.calculations.appendix import calculate_appendix
    c=example_project(1)['cases'][0];c['appendix_review']=dict(n3=None,n4=None,source='',page='')
    r=calculate_appendix(c);assert r['blocked'] and 'combined_pos' not in r['curves']
    c['appendix_review']['n3']=4
    with pytest.raises(ValueError,match='fuente'):calculate_appendix(c)

def test_19_preview_cancel_preserves_main_method(qt_lifetime):
    from src.ui.appendix_dialog import AppendixDialog
    c=example_project(1)['cases'][0];before=deepcopy(c);d=AppendixDialog(c)
    d.edits['n3'].setText('5');assert d.preview();d.reject();assert c==before
    d=AppendixDialog(c);d.edits['n3'].setText('5');d.save()
    assert c['method']=='niu' and c['appendix_review']['n3']==5


def test_19_appendix_configuration_roundtrip_and_export(monkeypatch):
    import json,zipfile
    from uuid import uuid4
    from bootstrap import ROOT
    from src.project import save_project,load_project
    import src.reporting.exporter as exporter
    folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True);monkeypatch.setattr(exporter,'ROOT',folder)
    p=example_project(1);p['cases']=p['cases'][:1];c=p['cases'][0]
    c['appendix_review']=dict(n3=5,n4=-3,source='Lectura QA A1/A2',page='345',speed_mode='selected')
    saved=load_project(save_project(p,folder/'fuente.json'));assert saved['cases'][0]['appendix_review']==c['appendix_review']
    out=exporter.export_project(p,p['active_case'],include_niu=False,include_appendix=True)
    result=json.loads((out/'apendice_a'/c['id']/'resultados.json').read_text(encoding='utf-8'))
    assert result['values']['n3']==5 and result['values']['n4']==-3
    assert (out/'reporte_apendice_a.pdf').read_bytes().startswith(b'%PDF')
    with zipfile.ZipFile(out/'reporte_apendice_a.docx') as doc:
        assert 'Lectura QA A1/A2' in doc.read('word/document.xml').decode('utf-8')

