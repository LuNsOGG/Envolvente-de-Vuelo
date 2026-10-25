from copy import deepcopy
from datetime import date
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QLineEdit,QDialogButtonBox,QLabel

class CoverDialog(QDialog):
    def __init__(self,metadata,parent=None):
        super().__init__(parent);self.metadata=deepcopy(metadata);self.setWindowTitle('Datos de portada');self.resize(560,320)
        layout=QVBoxLayout(self);form=QFormLayout();layout.addLayout(form);self.edits={}
        for key,label in [('title','Título del proyecto'),('student','Nombre del estudiante'),('subject','Materia'),('teacher','Docente'),('date','Fecha · AAAA-MM-DD')]:
            field=QLineEdit(metadata.get(key,''));field.setObjectName(key);self.edits[key]=field;form.addRow(label,field)
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Save).setText('Guardar');buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Cancelar');buttons.accepted.connect(self.save);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def save(self):
        values={key:field.text().strip() for key,field in self.edits.items()}
        if not values['title']:self.error.setText('Introduzca el título del proyecto.');return
        try:
            if values['date']:date.fromisoformat(values['date'])
        except ValueError:self.error.setText('Use una fecha válida con formato AAAA-MM-DD.');return
        self.metadata.update(values);self.accept()
