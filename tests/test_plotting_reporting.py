from bootstrap import ROOT
from src.project import load_project
from src.calculations import calculate
from src.plotting.envelopes import envelope_figure
from src.plotting.niu import niu_figure,FIGURES
from src.reporting.reports import equation_art

def test_graph_arrays_match_engine():
    project=load_project(ROOT/'data/proyecto_inicial.json');r=calculate(project['cases'][1])
    for kind,prefix,label in [('man','man','Frontera de maniobra'),('gust','gust','Condiciones de ráfaga'),('combined','combined','Contorno combinado')]:
        fig=envelope_figure(r,kind);ax=fig.axes[0]
        line=next(l for l in ax.lines if l.get_label()==label)
        assert list(line.get_xdata())==r['curves']['V']
        assert list(line.get_ydata())==r['curves'][prefix+'_pos']
        assert ax.get_xlabel().endswith('[kt EAS]')

def test_niu_catalog_and_all_figures_render():
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    assert len(FIGURES)==10
    assert [f['viewer'] for f in FIGURES]==[29,40,41,41,41,49,49,52,61,63]
    for row in FIGURES:
        fig=niu_figure(row['number']);canvas=FigureCanvasAgg(fig);canvas.draw()
        assert len(fig.axes)>=1

def test_gust_equations_distinguish_increment_from_load():
    project=load_project(ROOT/'data/proyecto_inicial.json');r=calculate(project['cases'][1])
    for eq in r['equations']:
        if eq['nombre'].startswith('Ráfaga'):
            suffix='c' if eq['nombre'].endswith('C') else 'd'
            assert 'Δn' in eq['ecuación']
            assert abs((1+eq['resultado'])-r['values'][f'n_gust_{suffix}_pos'])<1e-12
            assert not eq['sustitución'].startswith('1 ±')
