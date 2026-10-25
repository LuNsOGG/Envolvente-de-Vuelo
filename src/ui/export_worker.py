"""Exportación en segundo plano; solo las señales actualizan la interfaz Qt."""
from PySide6.QtCore import QThread,Signal

class ExportWorker(QThread):
    progress=Signal(int,str)
    completed=Signal(str)
    failed=Signal(str)
    cancelled=Signal(str)

    def __init__(self,project,current,parent=None,*,show_reference=False):
        super().__init__(parent)
        self.project=project;self.current=current;self.show_reference=show_reference

    def run(self):
        from src.reporting.graphs import export_graphs,ExportCancelled
        try:
            path=export_graphs(self.project,self.current,show_reference=self.show_reference,
                progress=self.progress.emit,cancel=self.isInterruptionRequested)
            self.completed.emit(str(path))
        except ExportCancelled as exc:self.cancelled.emit(str(exc.path) if exc.path else '')
        except Exception as exc:self.failed.emit(str(exc))
