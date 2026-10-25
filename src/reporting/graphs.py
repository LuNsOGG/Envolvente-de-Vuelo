"""Exportación de las tres gráficas de la condición seleccionada."""
from datetime import datetime
import re
import unicodedata
from bootstrap import ROOT, fresh
from src.calculations import calculate
from src.calculations.context import case_label
from src.plotting.envelopes import envelope_figure
from .exporter import ExportCancelled


def export_graphs(project, case_id, *, show_reference=False, progress=None, cancel=None):
    out = None
    def checkpoint(value, message):
        if cancel and cancel():
            raise ExportCancelled(out)
        if progress:
            progress(value, message)
    checkpoint(0, 'Validando gráficas')
    case = next((c for c in project['cases'] if c['id'] == case_id), None)
    if case is None:
        raise ValueError('Condición desconocida: ' + case_id)
    result = calculate(case)
    if result['blocked'] or any(k + '_pos' not in result['curves'] for k in ['man', 'gust', 'combined']):
        raise ValueError('Exportación incompleta: corrija los datos pendientes. ' + '; '.join(result['blocked']))
    label = unicodedata.normalize('NFKD', case_label(case)).encode('ascii', 'ignore').decode()
    label = re.sub('[^a-zA-Z0-9]+', '_', label).strip('_').lower()[:70] or 'condicion'
    out = fresh(ROOT / 'outputs' / ('graficas_' + label + '_' + datetime.now().strftime('%Y%m%d_%H%M%S')))
    out.mkdir(parents=True)
    for index, (kind, name) in enumerate([('man', 'maniobras'), ('gust', 'rafagas'), ('combined', 'combinado')]):
        checkpoint(5 + index * 30, 'Preparando ' + name)
        figure = envelope_figure(result, kind, show_reference=show_reference)
        try:
            for j, ext in enumerate(['png', 'svg']):
                checkpoint(10 + index * 30 + j * 10, 'Guardando ' + name + '.' + ext)
                figure.savefig(out / (name + '.' + ext), dpi=260, bbox_inches='tight')
        finally:
            figure.clear()
    checkpoint(100, 'Tres gráficas guardadas en PNG y SVG')
    return out
