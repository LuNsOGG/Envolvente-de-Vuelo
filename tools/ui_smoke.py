"""Abre el producto real y captura sus seis pestañas sin tocar fuentes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT,fresh
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from src.project import load_project
from src.ui.window import launch,MainWindow

app=QApplication([]);out=fresh(ROOT/'outputs/qa/interfaz_final');out.mkdir()

def capture():
    window=next(w for w in app.topLevelWidgets() if isinstance(w,MainWindow))
    for i,name in enumerate(['datos','maniobras','rafagas','combinado','verificaciones','reportes']):
        window.tabs.setCurrentIndex(i);app.processEvents();window.grab().save(str(out/(name+'.png')))
    window.selector.setCurrentIndex(window.selector.findData('original_fotos'));app.processEvents()
    assert window.result['blocked'];window.tabs.setCurrentIndex(3);app.processEvents()
    window.grab().save(str(out/'original_pendiente.png'))
    print(out);app.quit()

QTimer.singleShot(1800,capture)
raise SystemExit(launch(load_project(ROOT/'data/proyecto_inicial.json')))
