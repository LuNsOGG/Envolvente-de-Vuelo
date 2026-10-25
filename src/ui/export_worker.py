"""Exportación en segundo plano; solo las señales actualizan la interfaz Qt."""
from PySide6.QtCore import QThread,Signal

class ExportWorker(QThread):
    progress=Signal(int,str)
    completed=Signal(str)
    failed=Signal(str)
    cancelled=Signal(str)

    def __init__(self,project,current,parent=None):
        super().__init__(parent)
        self.project=project;self.current=current

    def run(self):
        from src.reporting.exporter import export_project,ExportCancelled
        try:
            path=export_project(self.project,self.current,all_cases=True,include_niu=False,
                progress=self.progress.emit,cancel=self.isInterruptionRequested)
            self.completed.emit(str(path))
        except ExportCancelled as exc:self.cancelled.emit(str(exc.path) if exc.path else '')
        except Exception as exc:self.failed.emit(str(exc))
