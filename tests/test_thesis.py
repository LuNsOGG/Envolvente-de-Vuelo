from copy import deepcopy
import math
from uuid import uuid4
import pytest
from bootstrap import ROOT
from src.calculations import calculate
from src.calculations.examples import example_project
from src.project import save_project,load_project
from src.calculations.worksheet import FIELD_KEYS


def test_cessna_matches_independent_calculation_and_uses_one_weight():
    project=example_project(1);before=deepcopy(project)
    for case,weight in zip(project['cases'],[4000,4631]):
        r=calculate(case);v=r['values'];assert not r['blocked']
        ws=weight/181;span=12.12/.3048;chord=181/span;a=.105*180/math.pi
        mu=2*ws/(.0023769*chord*a*32.2);kg=.88*mu/(5.3+mu)
        assert v['chord']==pytest.approx(chord)
        assert v['mu']==pytest.approx(mu) and v['Kg']==pytest.approx(kg)
        assert v['n3']==pytest.approx(1+kg*50*170*a/(498*ws))
        assert v['n4']==pytest.approx(1-kg*50*170*a/(498*ws))
        assert v['n_gust_d_pos']==pytest.approx(1+kg*25*240*a/(498*ws))
        assert v['AR']==pytest.approx(span**2/181)
        assert v['Va_selected']==150 and v['Vc']==170 and v['Vd']==240
        assert v['V_A_stall']<v['Va_min_base']<v['Va_selected']
        assert v['Va_min_base']==pytest.approx(15*math.sqrt(3.8*ws))
        params=case['parameters'];assert params['Wn_photo']['value']*3.8==pytest.approx(params['Wu_photo']['value']*4.4)
    assert project==before


def test_polar_and_source_inconsistencies_are_explicit():
    r=calculate(example_project(1)['cases'][0]);v=r['values']
    assert v['CN_pos']==1.45816142 and v['CN_neg']==-.8381569
    assert any(c['código']=='A23.1 AR' and c['estado']=='NO APLICA' for c in r['checks'])
    issues=' '.join(r['source_issues'])
    for marker in ['4016','4631','4000','2D','50/25','1296.22','por grado','4.26']:assert marker in issues
    assert not r['blocked'] and r['reference_rows']
    assert any(row['dato']=='Peso sustituido en ráfagas' and row['tesis']==4016 for row in r['reference_rows'])
    assert v['mu']!=1296.22 and v['n3']!=3.8


def test_geometric_chord_updates_but_manual_chord_is_preserved():
    c=example_project(1)['cases'][0]
    c['parameters']['S']['value']=190;r=calculate(c)
    assert r['values']['chord']==pytest.approx(190/(12.12/.3048))
    c['chord_mode']='manual';c['parameters']['chord']['value']=4.26
    assert calculate(c)['values']['chord']==4.26
    c['chord_mode']='geometric';c['parameters']['span']['value']=None
    bad=calculate(c);assert bad['blocked'] and 'man_pos' in bad['curves'] and 'gust_pos' not in bad['curves']


def test_published_curves_never_replace_revised_curves():
    from src.plotting.envelopes import envelope_figure
    c=example_project(1)['cases'][0];r=calculate(c);original=deepcopy(r)
    for kind in ['man','gust','combined']:
        a=envelope_figure(r,kind);b=envelope_figure(r,kind,show_reference=True)
        assert len(b.axes[0].lines)==len(a.axes[0].lines)+2
        reference=next(line for line in b.axes[0].lines if line.get_label()=='Tesis publicada · referencia')
        assert list(reference.get_ydata())==r['reference_curves'][kind+'_pos']
    assert r==original
    assert r['reference_curves']['gust_pos'][0]==1
    assert max(r['curves']['gust_pos'])>max(r['reference_curves']['gust_pos'])


def test_roundtrip_preserves_both_conditions_and_published_ledger():
    p=example_project(1);folder=ROOT/'tests/artifacts'/uuid4().hex
    path=save_project(p,folder/'cessna.json');loaded=load_project(path)
    assert loaded==p and len(loaded['cases'])==2
    assert calculate(loaded['cases'][1])['reference_rows']==calculate(p['cases'][1])['reference_rows']


def test_named_presets_and_condition_switch_keep_edits():
    from PySide6.QtWidgets import QApplication
    from src.ui.worksheet import WorksheetWindow
    app=QApplication.instance() or QApplication([]);w=WorksheetWindow(example_project(1))
    try:
        assert [a.text() for a in w.examples_button.menu().actions()]==['Ejemplo Cessna','Ejemplo libro']
        assert w.condition_selector.count()==2 and w.result['values']['W']==4000
        assert not w.table.cellWidget(FIELD_KEYS.index('chord'),2).isEnabled()
        w.set_value('W',3900);w.recalculate();w.changed=True
        w.condition_selector.setCurrentIndex(1);assert w.result['values']['W']==4631
        w.condition_selector.setCurrentIndex(0);assert w.result['values']['W']==3900
        w.reference_toggle.setChecked(True)
        assert any(l.get_label()=='Tesis publicada · referencia' for l in w.canvases['combined'].figure.axes[0].lines)
        text=w.reference_html(w.result)
        for marker in ['Va mínimo base','Va seleccionada','4016','AR']:assert marker in text
        w.examples_button.menu().actions()[1].trigger()
        assert w.result['values']['delta_c']==pytest.approx(1.9496526506337344)
        assert not w.result.get('reference_rows') and w.case()['aircraft']=='Ejemplo libro'
    finally:w.timer.stop();w.changed=False;w.close();app.processEvents()


def test_bundled_font_supports_offscreen_and_spanish_text():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFontDatabase,QFontMetrics
    from src.ui.worksheet import configure_font
    app=QApplication.instance() or QApplication([]);configure_font(app)
    assert 'DejaVu Sans' in QFontDatabase.families()
    metrics=QFontMetrics(app.font())
    assert all(metrics.inFontUcs4(ord(ch)) for ch in 'áéíóúñρμΔ')


def test_geometry_notice_reflects_current_geometry_without_claiming_compliance():
    c=example_project(1)['cases'][0];c['parameters']['span'].update(value=8,unit='m')
    r=calculate(c);assert not r['blocked'] and r['values']['AR']<7
    assert 'AR>7' not in r['academic_notice'] and 'pendiente' in r['academic_notice']
    assert any(x['código']=='A23.1 AR' and x['estado']=='PENDIENTE' for x in r['checks'])
