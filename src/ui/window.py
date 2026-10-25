from copy import deepcopy
from datetime import datetime
import math
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette,QColor
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QPushButton,QComboBox,QTabWidget,QTableWidget,QTableWidgetItem,QHeaderView,QTextBrowser,
    QFileDialog,QMessageBox,QLineEdit,QFormLayout,QSplitter,QScrollArea)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from bootstrap import ROOT, inside
from src.project import load_project,save_project
from src.calculations import calculate,compare,parameter_rows
from src.calculations.engine import SPECS
from src.calculations.units import UNITS
from src.plotting.envelopes import envelope_figure

class MainWindow(QMainWindow):
    def __init__(self,project):
        super().__init__();self.project=deepcopy(project);self.loading=False
        self.current=self.project['active_case'];self.result=None
        self.setWindowTitle('Envolvente de Vuelo | Tarea 04');self.resize(1440,900)
        central=QWidget();layout=QVBoxLayout(central);self.setCentralWidget(central)
        header=QLabel('Envolvente de vuelo');header.setStyleSheet('font-size:25px;font-weight:600;color:#18364b;padding:8px')
        layout.addWidget(header)
        self.banner=QLabel('Falta la tesis · Variante Cessna pendiente · Ejemplo con hipótesis explícitas · Uso académico')
        self.banner.setWordWrap(True);self.banner.setStyleSheet('background:#fff2d7;color:#624414;padding:9px;border-radius:5px')
        layout.addWidget(self.banner)
        row=QHBoxLayout();self.selector=QComboBox();self.selector.setMinimumWidth(380)
        row.addWidget(QLabel('Condición:'));row.addWidget(self.selector,1)
        for label,fn in [('Abrir JSON',self.open_project),('Guardar versión',self.save),('Calcular',self.recalculate),('Exportar',self.export)]:
            b=QPushButton(label);b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row);self.tabs=QTabWidget();layout.addWidget(self.tabs,1)
        data=QWidget();dl=QVBoxLayout(data)
        dl.addWidget(QLabel('Edite valor, unidad y observaciones. Un campo vacío significa pendiente. La fuente original se conserva al cambiar un dato.'))
        self.method=QComboBox();self.method.addItem('Apéndice A histórico (A1/A2 y A4)','apendice_a');self.method.addItem('Subparte C histórica (§§23.333–341)','subparte_c')
        dl.addWidget(self.method)
        self.table=QTableWidget();self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['Símbolo','Descripción','Valor','Unidad','Fuente','Página','Estado','Observaciones'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0,95);self.table.setColumnWidth(1,265);self.table.setColumnWidth(2,115)
        self.table.setColumnWidth(3,125);self.table.setColumnWidth(4,200);self.table.setColumnWidth(5,95)
        self.table.setColumnWidth(6,105);self.table.setColumnWidth(7,320)
        self.table.setAlternatingRowColors(True);dl.addWidget(self.table)
        self.tabs.addTab(data,'Datos')
        self.plot_tabs={}
        for kind,name in [('man','Maniobras'),('gust','Ráfagas'),('combined','Combinado')]:
            tab=QWidget();tab.setLayout(QVBoxLayout());self.plot_tabs[kind]=tab;self.tabs.addTab(tab,name)
        checks=QWidget();cl=QVBoxLayout(checks);self.check_text=QTextBrowser();cl.addWidget(self.check_text)
        self.results_table=QTableWidget();self.results_table.setColumnCount(2);self.results_table.setHorizontalHeaderLabels(['Resultado','Valor interno y unidades del reporte'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);cl.addWidget(self.results_table)
        self.tabs.addTab(checks,'Verificaciones')
        reports=QWidget();rl=QVBoxLayout(reports);form=QFormLayout();self.meta={}
        for key,label in [('student','Nombre'),('subject','Materia'),('teacher','Docente'),('date','Fecha')]:
            w=QLineEdit();self.meta[key]=w;form.addRow(label,w)
        rl.addLayout(form);self.sources=QTextBrowser();rl.addWidget(self.sources)
        self.tabs.addTab(reports,'Reportes y fuentes')
        self.selector.currentIndexChanged.connect(self.switch_case)
        self.fill_selector();self.display_case();self.render()
        self.setStyleSheet('QMainWindow{background:#f0f4f7} QTabWidget::pane{background:white} QPushButton{padding:7px 13px} QTabBar::tab{padding:10px 18px} QTableWidget{gridline-color:#dce4eb} QTextBrowser{padding:8px}')

    def case(self):return next(c for c in self.project['cases'] if c['id']==self.current)

    def fill_selector(self):
        self.selector.blockSignals(True);self.selector.clear()
        for c in self.project['cases']:self.selector.addItem(c['name'],c['id'])
        self.selector.setCurrentIndex(self.selector.findData(self.current));self.selector.blockSignals(False)

    def display_case(self):
        c=self.case();self.loading=True
        self.method.setCurrentIndex(self.method.findData(c['method']))
        rows=parameter_rows(c);self.table.setRowCount(len(rows))
        for i,p in enumerate(rows):
            vals=[p['símbolo'],p['descripción'],'' if p['valor'] is None else str(p['valor']),p['unidad'],p['fuente'],p['página'],p['estado'],p['observaciones']]
            for j,val in enumerate(vals):
                item=QTableWidgetItem(str(val))
                if j not in [2,3,7]:item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if j==3:
                    item.setToolTip('Unidades válidas: '+', '.join(UNITS.get(SPECS.get(p['símbolo'],('',''))[1],{})))
                if j==4:item.setToolTip(str(c['parameters'][p['símbolo']].get('original',{})))
                self.table.setItem(i,j,item)
        for k,w in self.meta.items():w.setText(self.project.get('metadata',{}).get(k,''))
        self.loading=False

    def commit(self):
        c=self.case();new=deepcopy(c['parameters']);changes=[]
        for i in range(self.table.rowCount()):
            key=self.table.item(i,0).text();s=self.table.item(i,2).text().strip();unit=self.table.item(i,3).text().strip();note=self.table.item(i,7).text()
            try:
                value=float(s.replace(',','.')) if s else None
                if value is not None and not math.isfinite(value):raise ValueError()
            except ValueError:raise ValueError(f'{key}: escriba un número finito o deje vacío')
            p=new[key]
            if (p.get('value'),p.get('unit'),p.get('notes'))!=(value,unit,note):
                changes.append(dict(parameter=key,before=p.get('value'),before_unit=p.get('unit'),after=value,after_unit=unit,
                                    reason=note or 'Edición del usuario; requiere verificación documental',time=datetime.now().isoformat()))
                p.setdefault('original',deepcopy(c['parameters'][key]))
                p.update(value=value,unit=unit,notes=note,status='supuesto' if value is not None else 'pendiente')
        if c['method']!=self.method.currentData():
            changes.append(dict(parameter='criterio',before=c['method'],after=self.method.currentData(),reason='Selección del usuario; revisar aplicabilidad'))
        c['method']=self.method.currentData();c['parameters']=new;c.setdefault('changes',[]).extend(changes)
        for k,w in self.meta.items():self.project.setdefault('metadata',{})[k]=w.text()
        self.project['active_case']=self.current

    def guarded(self,fn):
        try:return fn()
        except Exception as e:QMessageBox.warning(self,'Revisar datos',str(e));return None

    def switch_case(self,index):
        target=self.selector.itemData(index)
        if not target or self.loading:return
        try:self.commit()
        except Exception as e:
            self.selector.blockSignals(True);self.selector.setCurrentIndex(self.selector.findData(self.current));self.selector.blockSignals(False)
            QMessageBox.warning(self,'Revisar datos',str(e));return
        self.current=target;self.project['active_case']=target;self.display_case();self.render()

    def recalculate(self):
        def go():self.commit();self.display_case();self.render()
        return self.guarded(go)

    def render(self):
        import html
        r=calculate(self.case());self.result=r
        for kind,tab in self.plot_tabs.items():
            # Solo libera widgets de memoria; no elimina ningún archivo.
            lay=tab.layout()
            while lay.count():
                w=lay.takeAt(0).widget()
                if w:w.deleteLater()
            canvas=FigureCanvasQTAgg(envelope_figure(r,kind));lay.addWidget(NavigationToolbar2QT(canvas,self));lay.addWidget(canvas)
        h='<h2>Comprobaciones de la condición</h2>'
        if r['blocked']:h+='<p><b>Pendientes de cálculo</b><br>'+'<br>'.join(html.escape(s) for s in r['blocked'])+'</p>'
        for ck in r['checks']:
            color={'OK':'#19705c','ERROR':'#af2525','BLOQUEADO':'#af2525'}.get(ck['estado'],'#8a5d12')
            h+=f'<p><b style="color:{color}">{html.escape(ck["estado"])} · {html.escape(ck["código"])}</b><br>{html.escape(ck["detalle"])}</p>'
        self.check_text.setHtml(h)
        self.results_table.setRowCount(len(r['values']))
        for i,(key,value) in enumerate(r['values'].items()):
            for j,txt in enumerate([key,f'{value:.9g}']):
                item=QTableWidgetItem(txt);item.setFlags(item.flags()&~Qt.ItemFlag.ItemIsEditable);self.results_table.setItem(i,j,item)
        self.sources.setHtml('<h2>Fuentes y alcance</h2><p>Libro adjunto: <i>Airframe Structural Design</i>, capítulo 3. Inicio: visor 28, impresa 21. El título Aircraft Structural Design de la solicitud no coincide con el documento recibido.</p><p><b>Tesis pendiente:</b> Diseño de la caja de torsión de una aeronave cuatriplaza, capítulo 1.9 y páginas de características de la aeronave. Falta identificar variante, plazas, pesos y edición normativa.</p><p>Referencia oficial guardada en sources/: FAR 23, edición 2016, Apéndice A y §§23.333, 335, 337, 341. La edición utilizada por la tesis aún no está confirmada.</p><h3>Hipótesis de esta condición</h3>'+''.join('<p>'+html.escape(a)+'</p>' for a in r['assumptions'])+'<h3>Exportación</h3><p>CSV, PNG, SVG, PDF de análisis, DOCX editable y reporte independiente de Niu. Cada ejecución crea una carpeta nueva en outputs; nunca reemplaza documentos previos.</p>')
        self.statusBar().showMessage(f'{r["name"]} · {len(r["blocked"])} pendientes de cálculo · {len(r["checks"])} verificaciones')

    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,'Abrir proyecto dentro de esta carpeta',str(ROOT/'data'),'Proyecto JSON (*.json)')
        if not path:return
        def go():
            project=load_project(path);self.project=project;self.current=project['active_case'];self.fill_selector();self.display_case();self.render()
        self.guarded(go)

    def save(self):
        path,_=QFileDialog.getSaveFileName(self,'Guardar como nueva versión dentro de esta carpeta',str(ROOT/'data/proyecto_usuario.json'),'Proyecto JSON (*.json)')
        if not path:return
        def go():
            self.commit();saved=save_project(self.project,path);self.statusBar().showMessage('Guardado sin sobrescribir: '+str(saved))
        self.guarded(go)

    def export(self):
        def go():
            self.commit();self.render()
            from src.reporting.exporter import export_project
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:out=export_project(self.project,self.current)
            finally:QApplication.restoreOverrideCursor()
            QMessageBox.information(self,'Exportación terminada',str(out)+'\nCada cifra proviene del motor. Consulte las hipótesis y los pendientes en el reporte.')
        self.guarded(go)

def launch(project,screenshot=None):
    app=QApplication.instance() or QApplication([]);app.setStyle('Fusion')
    palette=QPalette()
    for role,color in [(QPalette.ColorRole.Window,'#f0f4f7'),(QPalette.ColorRole.WindowText,'#233e50'),
                       (QPalette.ColorRole.Base,'#ffffff'),(QPalette.ColorRole.AlternateBase,'#edf3f7'),
                       (QPalette.ColorRole.Text,'#233e50'),(QPalette.ColorRole.Button,'#e4edf3'),
                       (QPalette.ColorRole.ButtonText,'#233e50'),(QPalette.ColorRole.Highlight,'#176f82'),
                       (QPalette.ColorRole.HighlightedText,'#ffffff')]:palette.setColor(role,QColor(color))
    app.setPalette(palette)
    window=MainWindow(project);window.show()
    if screenshot:
        def capture():
            path=inside(screenshot)
            if path.exists():raise FileExistsError('La captura ya existe')
            window.grab().save(str(path));app.quit()
        QTimer.singleShot(2000,capture)
    return app.exec()
