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

