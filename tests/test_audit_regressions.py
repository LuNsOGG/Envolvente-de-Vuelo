from copy import deepcopy
import pytest
from src.calculations import calculate
from src.calculations.examples import example_project


def test_01_import_rejects_incompatible_units_without_mutating_data():
    from src.calculations.worksheet import adapt_case
    p=example_project(1)['cases'][0];p['parameters']['W']['unit']='kg';before=deepcopy(p)
    with pytest.raises(ValueError,match='incompatible'):adapt_case(p)
    assert p==before
    p['parameters']['W'].update(value=4000*4.4482216152605,unit='N')
    assert calculate(adapt_case(p))['values']['W']==pytest.approx(4000)


def test_02_invalid_optional_gust_is_not_silently_omitted():
    c=example_project(2)['cases'][0];c['parameters']['U_b']['unit']='incorrecta'
    r=calculate(c);assert r['blocked'] and not r['curves']
    assert any('U_b' in message for message in r['blocked'])
    c['parameters']['U_b']['value']=None
    assert not calculate(c)['blocked']


@pytest.mark.parametrize('damage',[lambda p:p['cases'][0].pop('name'),lambda p:p['cases'][0]['parameters'].update(W=None),lambda p:p['cases'][0]['parameters']['W'].pop('unit'),lambda p:p['cases'].__setitem__(0,None),lambda p:p['cases'][0].update(assumptions=[1])])
def test_03_malformed_project_has_controlled_validation_error(damage):
    from src.project import validate_project
    p=example_project(1);damage(p)
    with pytest.raises(ValueError):validate_project(p)

@pytest.mark.parametrize('value',[[],None,4,'texto'])
def test_03_non_object_project_is_rejected(value):
    from src.project import validate_project
    with pytest.raises(ValueError):validate_project(value)


def test_04_invalid_draft_keeps_units_and_survives_condition_switch(qt_lifetime,monkeypatch):
    from uuid import uuid4
    from bootstrap import ROOT
    import src.ui.worksheet as ui
    from src.calculations.worksheet import FIELD_KEYS
    from src.project import load_project
    monkeypatch.setattr(ui,'ROOT',ROOT/'tests/artifacts'/uuid4().hex)
    w=ui.WorksheetWindow(example_project(1))
    try:
        w.set_value('W','pendiente');w.table.cellWidget(FIELD_KEYS.index('S'),2).setCurrentText('m²');w.changed=True
        saved=w.snapshot();p=load_project(saved)
        assert p['draft_units']['S']=='m²'
        w.replace_project(p)
        assert w.table.cellWidget(FIELD_KEYS.index('S'),2).currentText()=='m²'
        w.condition_selector.setCurrentIndex(1);w.condition_selector.setCurrentIndex(0)
        assert w.table.item(FIELD_KEYS.index('W'),1).text()=='pendiente'
        assert w.table.cellWidget(FIELD_KEYS.index('S'),2).currentText()=='m²'
    finally:w.timer.stop();w.changed=False;w.close()


def test_05_rejects_maneuver_limit_below_one_g():
    c=example_project(1)['cases'][0];c['parameters']['n_pos']['value']=.5
    r=calculate(c);assert r['blocked'] and not r['curves'] and '1 g' in r['blocked'][0]

def test_05_active_subpart_checks_category_and_gust_requirements():
    c=example_project(1)['cases'][0];c.update(speed_mode='subparte_c',negative_rule='normal')
    for k,v in [('n_pos',2),('U_c',0),('U_d',0),('altitude',0)]:c['parameters'][k]['value']=v
    r=calculate(c);checks={x['código']:x for x in r['checks']}
    assert not r['blocked'] and checks['23.337']['estado']=='ADVERTENCIA'
    assert checks['23.333 Ude']['estado']=='ADVERTENCIA'
    assert r['values']['n_required']==3.8


def test_06_report_context_describes_edited_values_and_keeps_reference():
    c=example_project(1)['cases'][0];before=deepcopy(c['assumptions'])
    c['parameters']['W']['value']=3600;c['parameters']['a']['value']=.08
    r=calculate(c);actual=' '.join(r['assumptions'])
    assert 'W=3600' in actual and 'a=0.08' in actual
    assert 'a=0.105' not in actual and 'W=4000' not in actual
    assert '3600' in r['name'] and r['reference_assumptions']==before and c['assumptions']==before


def test_07_open_and_accept_do_not_invent_user_changes(qt_lifetime):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication,QDialogButtonBox
    from src.ui.worksheet import WorksheetWindow
    p=example_project(1);w=WorksheetWindow(p)
    try:
        assert w.case()['parameters']['Wu_photo']==p['cases'][0]['parameters']['Wu_photo']
        before=deepcopy(w.case()['parameters']);history=deepcopy(w.case().get('changes',[]))
        def accept():QApplication.activeModalWidget().findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok).click()
        QTimer.singleShot(30,accept);w.niu_data()
        assert w.case()['parameters']['span']==before['span']
        assert w.case().get('changes',[])==history
        assert w.case()['parameters']['span']['unit']=='m'
    finally:w.timer.stop();w.changed=False;w.close()


def test_08_selected_va_is_checked_and_visible_in_both_examples():
    from src.plotting.envelopes import envelope_figure
    for n in [1,2]:
        c=example_project(n)['cases'][0];c['parameters']['Va_selected']['value']=500
        r=calculate(c)
        assert r['values']['Va_selected']==500
        assert any(x['código']=='CONGRUENCIA Va' and x['estado']=='ADVERTENCIA' for x in r['checks'])
        fig=envelope_figure(r,'man');assert any('Va sel.' in t.get_text() for t in fig.axes[0].texts)



def test_09_engine_rejects_book_table_with_cn_from_json():
    from src.project import validate_project
    p=example_project(2);p['cases'][0]['coefficient_basis']='CN';validate_project(p)
    r=calculate(p['cases'][0]);assert r['blocked'] and not r['curves']
    assert 'CL' in r['blocked'][0]


def test_10_every_current_equation_has_a_rendered_expression():
    from uuid import uuid4
    from bootstrap import ROOT
    from src.reporting.reports import equation_art
    folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True)
    for n in [1,2]:
        r=calculate(example_project(n)['cases'][0])
        assert {'Intersección A','Intersección G'} <= {e['nombre'] for e in r['equations']}
        for i,e in enumerate(r['equations']):assert equation_art(e,folder,n*100+i).is_file()
        vs=next(e for e in r['equations'] if e['nombre']=='Pérdida EAS (Niu)')
        assert 'Resolver' in vs['sustitución'] and 'Vs' in vs['ecuación']


def test_11_combined_axes_include_uncut_gust_and_published_reference():
    from src.plotting.envelopes import envelope_figure
    c=example_project(1)['cases'][0];c['parameters']['U_c']['value']=200;r=calculate(c)
    fig=envelope_figure(r,'combined',show_reference=True);ax=fig.axes[0];low,high=ax.get_ylim()
    for line in ax.lines:
        assert all(low<=y<=high for y in line.get_ydata() if y is not None)
    assert high>max(r['curves']['gust_pos'])
    assert ax.get_xlim()[1]>=max(r['reference_curves']['V'])

