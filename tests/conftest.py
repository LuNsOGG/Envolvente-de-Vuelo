import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bootstrap
import os
import pytest


@pytest.fixture(scope='session',autouse=True)
def qt_lifetime():
    """Una aplicación Qt por proceso; liberar ventanas antes de su finalización."""
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication,QEvent
    import shiboken6
    app=QApplication.instance() or QApplication([])
    yield app
    for widget in app.topLevelWidgets():
        if hasattr(widget,'changed'):widget.changed=False
        if hasattr(widget,'timer'):widget.timer.stop()
        widget.close();widget.deleteLater()
    QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    app.processEvents()
    import gc
    gc.collect()
    app.quit()
    shiboken6.delete(app)
