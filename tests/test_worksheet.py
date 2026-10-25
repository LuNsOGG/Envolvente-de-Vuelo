from copy import deepcopy
import os
import pytest
from src.calculations import calculate
from src.calculations.worksheet import worksheet_project, FIELD_KEYS, adapt_case
from src.worksheet_selfcheck import completed_fixture


def test_default_contains_transcribed_values_and_authorized_approximation():
    c=worksheet_project()['cases'][0]; p=c['parameters']
    assert p['W']['value']==4631 and p['Wn_photo']['value']==4631.5
    assert p['Wu_photo']['value']==3454.54 and p['CLalpha_photo']['value']==.11
    assert p['rho']['unit']=='slug/ft³' and p['rho']['original']['unit']=='lb/ft³ sin tipo'
    assert p['CN_neg']['value']==-1.35 and p['CN_neg']['status']=='aproximación'
    assert p['U_c']['value']==50 and p['U_d']['value']==25
    for key in ['n3','n4','altitude']:assert p[key]['value'] is None


def test_formulas_and_independent_gust_branch():
    c=worksheet_project()['cases'][0]; before=deepcopy(c); r=calculate(c)
    assert c==before
    assert r['values']['W_S']==4631/181
    assert r['values']['Vc']==pytest.approx(17*(3.8*4631/181)**.5)
    assert r['values']['Vd']==pytest.approx(24*(3.8*4631/181)**.5)
    assert r['values']['n_neg']==pytest.approx(-1.9)
    assert r['values']['n3']==pytest.approx(3.910272016204428)
    assert r['values']['n4']==pytest.approx(-1.910272016204428)
    assert r['curves']['man_pos']!=r['curves']['gust_pos']
    assert r['curves']['combined_pos']!=r['curves']['man_pos']


def test_explicit_additional_data_complete_all_three_and_edit_changes_them():
    c=completed_fixture()['cases'][0]; a=calculate(c); c['parameters']['W']['value']=4000; b=calculate(c)
    assert not a['blocked'] and not b['blocked']
    for key in ['man_pos','gust_pos','combined_pos']:
        assert a['curves'][key]!=b['curves'][key]


def test_empty_input_removes_old_speeds_instead_of_reusing_them():
    c=completed_fixture()['cases'][0]; c['parameters']['Vc']['value']=180; c['parameters']['W']['value']=None
    r=calculate(c); assert r['blocked'] and not r['curves']
    assert 'Vc' not in r['values']


def test_subpart_derives_gust_only_with_explicit_altitude():
    c=completed_fixture()['cases'][0]; c['method']='subparte_c'
    c['parameters']['altitude']['value']=None
    assert 'gust_pos' not in calculate(c)['curves']
    c['parameters']['altitude'].update(value=0,unit='ft'); r=calculate(c)
    assert not r['blocked'] and r['values']['U_c']==50 and r['values']['U_d']==25
    assert r['values']['Vc']==pytest.approx(33*(4631/181)**.5)
    assert r['values']['n_neg']==pytest.approx(-.4*3.8)


def test_a_and_clalpha_are_preserved_separately():
    c=completed_fixture()['cases'][0]; c['parameters']['CLalpha_photo']['value']=.2
    r=calculate(c); assert c['parameters']['a']['value']==.105
    assert next(p for p in r['parameters'] if p['símbolo']=='CLalpha_photo')['valor']==.2


@pytest.fixture
def sheet():
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from src.ui.worksheet import WorksheetWindow
    app=QApplication.instance() or QApplication([]); w=WorksheetWindow(worksheet_project())
    yield w
    w.timer.stop(); w.changed=False; w.close(); app.processEvents()


def test_exact_excel_order_readonly_calculated_loading_and_four_tabs(sheet):
    from PySide6.QtCore import Qt
    assert [sheet.table.item(i,0).text() for i in range(14)]==['nᵤ','nₙ','Wₙ','Wᵤ','W','S','W/S','N','Cₙ máx.','ρ','c','a','g','CLα']
    assert not sheet.table.item(6,1).flags() & Qt.ItemFlag.ItemIsEditable
    assert sheet.tabs.count()==4
    assert not any(hasattr(sheet,key) for key in ['category','method','condition','aircraft','selector'])


def test_ui_edit_recalculates_loading_and_invalid_clears_curves(sheet):
    sheet.set_value('W',4000); sheet.recalculate()
    assert float(sheet.table.item(6,1).text())==pytest.approx(4000/181)
    sheet.set_value('S','xyz'); assert not sheet.recalculate() and not sheet.result['curves']


def test_previous_demonstration_additions_are_not_imported_as_aircraft_data():
    from bootstrap import ROOT
    from src.project import load_project
    original=load_project(ROOT/'data/proyecto_inicial.json')['cases'][1]
    with pytest.raises(ValueError,match='incompatible'):adapt_case(original)
    compatible=deepcopy(original);compatible['parameters']['CLalpha_photo']['value']=None
    adapted=adapt_case(compatible)
    assert adapted['parameters']['CN_neg']['value'] is None and original['parameters']['CN_neg']['value']==-1.35
    assert adapted['parameters']['altitude']['value'] is None


def test_worksheet_units_convert_without_changing_original_inputs():
    c=completed_fixture()['cases'][0]; c['parameters']['S'].update(value=181*.3048**2,unit='m²')
    assert calculate(c)['values']['W_S']==pytest.approx(4631/181)


def test_new_worksheet_does_not_copy_photo_aircraft_values():
    c=worksheet_project(False,'Otro avión')['cases'][0]
    assert all(c['parameters'][key]['value'] is None for key in FIELD_KEYS)


def test_plot_cannot_close_unknown_negative_boundary():
    from src.plotting.envelopes import envelope_figure
    c=worksheet_project()['cases'][0];c['parameters']['CN_neg']['value']=None
    r=calculate(c); fig=envelope_figure(r,'man'); ax=fig.axes[0]
    assert not ax.collections
    assert any('CN_neg' in text.get_text() for text in ax.texts)


def test_replacement_canvases_remain_visible_after_recalculation(sheet):
    from PySide6.QtWidgets import QApplication
    sheet.show(); QApplication.processEvents(); sheet.replace_project(completed_fixture()); QApplication.processEvents()
    sheet.set_value('W',4000); sheet.recalculate(); QApplication.processEvents()
    assert all(sheet.canvases['overview_'+kind].isVisible() for kind in ['man','gust','combined'])


def test_invalid_draft_is_preserved_and_restored(sheet,monkeypatch):
    from bootstrap import ROOT
    from uuid import uuid4
    from src.project import load_project
    import src.ui.worksheet as ui
    folder=ROOT/'tests/artifacts'/uuid4().hex; monkeypatch.setattr(ui,'ROOT',folder)
    sheet.set_value('S','por confirmar'); sheet.changed=True; saved=sheet.snapshot(); project=load_project(saved)
    assert project['draft_cells']['S']=='por confirmar'
    sheet.replace_project(project)
    assert sheet.table.item(FIELD_KEYS.index('S'),1).text()=='por confirmar'
    assert not sheet.result['curves']


def test_reference_category_weights_do_not_replace_active_weight():
    c=completed_fixture()['cases'][0]; c['parameters']['Wu_photo']['value']=1000
    r=calculate(c); assert r['values']['W']==4631 and r['values']['W_S']==4631/181


def test_example_menu_loads_independent_units_and_returns_to_excel(sheet):
    actions=sheet.examples_button.menu().actions()
    assert [a.text() for a in actions]==['Ejemplo Cessna','Ejemplo libro']
    actions[1].trigger()
    assert sheet.result['values']['W']==88000 and sheet.case()['parameters']['a']['unit']=='1/rad'
    assert sheet.result['values']['Vb']<325 and sheet.table.item(8,0).text()=='Cʟ máx.'
    actions[0].trigger()
    assert sheet.result['values']['W']==4000 and sheet.case()['parameters']['a']['unit']=='1/deg'
    assert sheet.result['values']['CN_neg']==-.8381569 and 'Vb' not in sheet.result['values']


def test_niu_dialog_edits_gust_and_preserves_other_data(sheet):
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication,QDialog,QLineEdit,QDialogButtonBox
    def fill_dialog():
        dialog=next(w for w in QApplication.topLevelWidgets() if isinstance(w,QDialog) and w.windowTitle()=='Datos de cálculo')
        fields=dialog.findChildren(QLineEdit)
        fields[4].setText('40')
        dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Ok).click()
    before=sheet.result['values']['n3']
    QTimer.singleShot(50,fill_dialog);sheet.complete_data()
    assert sheet.result['values']['U_c']==40 and sheet.result['values']['n3']<before
    assert sheet.result['values']['CN_neg']==-1.35 and sheet.result['values']['W']==4631
