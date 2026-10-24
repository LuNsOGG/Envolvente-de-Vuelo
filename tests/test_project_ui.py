from copy import deepcopy
from uuid import uuid4
import os
import pytest
from bootstrap import ROOT,inside
from src.project import load_project,save_project,validate_project

def test_path_scope():
    with pytest.raises(ValueError):inside(ROOT.parent/'fuera.json')

def test_non_destructive_roundtrip():
    p=load_project(ROOT/'data/proyecto_inicial.json');folder=ROOT/'tests/artifacts'/uuid4().hex;folder.mkdir(parents=True)
    a=save_project(p,folder/'proyecto.json');first=a.read_bytes();b=save_project(p,a)
    assert b!=a and a.read_bytes()==first
    assert load_project(a)==load_project(b)==p

def test_nan_and_duplicate_ids_rejected():
    p=load_project(ROOT/'data/proyecto_inicial.json');p['cases'][0]['parameters']['W']['value']=float('nan')
    with pytest.raises(ValueError):validate_project(p)

def test_case_cannot_escape_export_directory():
    p=load_project(ROOT/'data/proyecto_inicial.json');p['cases'][0]['id']='../../fuera'
    with pytest.raises(ValueError):validate_project(p)

def test_duplicate_ids_rejected():
    p=load_project(ROOT/'data/proyecto_inicial.json');p['cases'][1]['id']=p['cases'][0]['id']
    with pytest.raises(ValueError):validate_project(p)

def test_ui_edit_retains_source_and_original():
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from src.ui.window import MainWindow
    app=QApplication.instance() or QApplication([])
    p=load_project(ROOT/'data/proyecto_inicial.json');win=MainWindow(p)
    before=deepcopy(win.case()['parameters']['W']);win.table.item(0,2).setText('4000');win.commit()
    after=win.case()['parameters']['W']
    assert after['value']==4000 and after['status']=='supuesto'
    assert after['source']==before['source'] and after['original']==before['original']
    index=win.selector.findData('peso_menor');win.selector.setCurrentIndex(index)
    assert win.current=='peso_menor';assert win.project['cases'][1]['parameters']['W']['value']==4000
    assert win.tabs.count()==6
    win.close();app.processEvents()
