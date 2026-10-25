from copy import deepcopy
from uuid import uuid4
import pytest
from bootstrap import ROOT
from src.calculations.examples import example_project
import src.reporting.graphs as exporter


def destination(monkeypatch):
    root=ROOT/'tests/artifacts'/uuid4().hex;root.mkdir(parents=True)
    monkeypatch.setattr(exporter,'ROOT',root)
    return root


@pytest.mark.parametrize('number',[1,2])
def test_export_saves_only_three_png_and_svg_for_selected_case(monkeypatch,number):
    from PIL import Image
    destination(monkeypatch);project=example_project(number);before=deepcopy(project)
    current=project['cases'][-1]['id'];seen=[];real=exporter.envelope_figure
    def capture(result,kind,**kwargs):
        seen.append((result['values']['W'],kwargs['show_reference']))
        return real(result,kind,**kwargs)
    monkeypatch.setattr(exporter,'envelope_figure',capture)
    path=exporter.export_graphs(project,current,show_reference=number==1)
    assert {p.name for p in path.iterdir()}=={n+'.'+e for n in ['maniobras','rafagas','combinado'] for e in ['png','svg']}
    for p in path.glob('*.png'):
        with Image.open(p) as image:assert image.width>1000 and image.height>1000
    assert seen==[(4631 if number==1 else 88000,number==1)]*3
    assert project==before


def test_invalid_data_creates_no_export_directory(monkeypatch):
    root=destination(monkeypatch);project=example_project(1)
    project['cases'][0]['parameters']['CN_neg']['value']=None
    with pytest.raises(ValueError,match='incompleta'):exporter.export_graphs(project,project['active_case'])
    assert not (root/'outputs').exists()


def test_cancel_keeps_existing_graphs_without_reports_or_overwriting(monkeypatch):
    root=destination(monkeypatch);project=example_project(1);stopped=[False]
    original=exporter.export_graphs(project,project['active_case'])
    hashes={p.name:p.read_bytes() for p in original.iterdir()}
    def progress(value,message):
        if value>=20:stopped[0]=True
    with pytest.raises(exporter.ExportCancelled) as exc:
        exporter.export_graphs(project,project['active_case'],progress=progress,cancel=lambda:stopped[0])
    partial=exc.value.path
    assert partial!=original and partial.exists() and all(p.suffix in ['.png','.svg'] for p in partial.iterdir())
    assert hashes=={p.name:p.read_bytes() for p in original.iterdir()}
