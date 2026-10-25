from copy import deepcopy
from html import escape
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QComboBox,QLineEdit,QLabel,QTabWidget,QWidget,QTextBrowser,QDialogButtonBox,QPushButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from src.calculations.appendix import appendix_defaults,calculate_appendix
from src.plotting.envelopes import envelope_figure

class AppendixDialog(QDialog):
    def __init__(self,case,parent=None):
        super().__init__(parent);self.case=case;self.calculation=None;self.setWindowTitle('Procedimiento del Apéndice A');self.resize(1100,850)
        layout=QVBoxLayout(self);note=QLabel('Vista independiente del cálculo Niu. Las lecturas n3/n4 requieren fuente; el resultado conserva su alcance académico.');note.setWordWrap(True);layout.addWidget(note)
        form=QFormLayout();layout.addLayout(form);cfg=appendix_defaults(case);self.edits={}
        for key,label in [('n3','n3 · lectura positiva'),('n4','n4 · lectura negativa'),('source','Fuente de n3/n4'),('page','Página / figura')]:
            edit=QLineEdit('' if cfg[key] is None else str(cfg[key]));edit.setObjectName(key);self.edits[key]=edit;form.addRow(label,edit)
        self.speed=QComboBox();self.speed.addItem('Velocidades seleccionadas de la condición','selected');self.speed.addItem('Mínimos base A3','minimum');self.speed.setCurrentIndex(max(0,self.speed.findData(cfg['speed_mode'])));form.addRow('Velocidades efectivas',self.speed)
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        self.tabs=QTabWidget();layout.addWidget(self.tabs,1);self.text=QTextBrowser();self.tabs.addTab(self.text,'Procedimiento y tablas');self.views={}
        for kind,label in [('man','Maniobras'),('combined','Contorno A4')]:
            page=QWidget();box=QVBoxLayout(page);self.tabs.addTab(page,label);self.views[kind]=box
        refresh=QPushButton('Actualizar procedimiento');refresh.clicked.connect(self.preview);layout.addWidget(refresh)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel);buttons.button(QDialogButtonBox.StandardButton.Save).setText('Guardar');buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('Cancelar');buttons.accepted.connect(self.save);buttons.rejected.connect(self.reject);layout.addWidget(buttons);self.preview()

    def config(self):
        cfg={key:edit.text().strip() for key,edit in self.edits.items()}
        for k in ['n3','n4']:cfg[k]=float(cfg[k].replace(',','.')) if cfg[k] else None
        cfg['speed_mode']=self.speed.currentData();return cfg

    def preview(self):
        try:
            trial=deepcopy(self.case);trial['appendix_review']=self.config();r=calculate_appendix(trial);self.calculation=r
            self.error.setText(r['academic_notice']+' '+('Pendiente: '+'; '.join(r['blocked']) if r['blocked'] else 'Contorno A4 calculado.'))
            text='<h3>Procedimiento A3 / A4</h3>'
            for step in r['procedure']:text+='<p><b>'+escape(step['paso'])+'</b> '+escape(step['detalle'])+'</p>'
            text+='<h3>Velocidades y factores</h3>'
            for key in ['W_S','Vc_A_raw','Vd_A_raw','Va_A_raw','Vf_A_raw','Vc','Vd','Vs','V_A_stall','V_G_stall','n_pos','n_neg','n3','n4']:
                if key in r['values']:text+='<p>'+key+': '+f'{r["values"][key]:.9g}'+'</p>'
            for check in r['checks']:text+='<p>'+escape(check['estado']+' · '+check['código']+': '+check['detalle'])+'</p>'
            self.text.setHtml(text)
            for kind,box in self.views.items():
                while box.count():
                    w=box.takeAt(0).widget()
                    if w:w.deleteLater()
                canvas=FigureCanvasQTAgg(envelope_figure(r,kind));box.addWidget(NavigationToolbar2QT(canvas,self));box.addWidget(canvas)
            return True
        except (ValueError,TypeError,KeyError) as exc:self.error.setText(str(exc));return False

    def save(self):
        if self.preview():self.case['appendix_review']=self.config();self.accept()
