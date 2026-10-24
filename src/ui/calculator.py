"""Calculadora reutilizable: datos y las tres gráficas en una sola ventana."""
from copy import deepcopy
from datetime import datetime
from html import escape
import math
from PySide6.QtCore import Qt,QTimer
from PySide6.QtGui import QPalette,QColor
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QPushButton,QComboBox,QTabWidget,QTableWidget,QTableWidgetItem,QHeaderView,QTextBrowser,
    QFileDialog,QMessageBox,QLineEdit,QFormLayout,QSplitter,QCheckBox,QInputDialog,QPlainTextEdit)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg,NavigationToolbar2QT
from bootstrap import ROOT,inside,fresh
from src.project import load_project,save_project
from src.calculations import calculate,parameter_rows
from src.calculations.engine import SPECS
from src.calculations.units import UNITS,RHO0
from src.calculations.cases import new_case,duplicate_case,blank_project,demo_project,MAIN_KEYS,ADVANCED_KEYS
from src.plotting.envelopes import envelope_figure

LABELS={'W':'Peso W','S':'Superficie alar S','n_pos':'Carga límite n+','n_neg':'Carga límite n−',
        'CN_pos':'Coeficiente CN+ máx.','CN_neg':'Coeficiente CN− mín.','Vc':'Crucero de diseño Vc',
        'Vd':'Picada de diseño Vd','chord':'Cuerda geométrica c','a':'Pendiente normal a','rho':'Densidad local ρ',
        'rho0':'Densidad EAS ρ₀','g':'Gravedad g','Va':'Maniobra elegida Va','U_c':'Ráfaga Ude en Vc',
        'U_d':'Ráfaga Ude en Vd','altitude':'Altitud','n3':'Carga n3 de A1','n4':'Carga n4 de A2'}

def item(text,editable=False):
    cell=QTableWidgetItem(str(text))
    if not editable:cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return cell

class CalculatorWindow(QMainWindow):
    def __init__(self,project):
        super().__init__();self.project=deepcopy(project);self.current=project['active_case']
        self.loading=True;self.result=None;self.keys=[];self.canvases={};self.toolbars={};self.changed=False;self.last_export=None
        self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.setInterval(650);self.timer.timeout.connect(self.auto_recalculate)
        self.setWindowTitle('Envolventes de Vuelo | Calculadora de aeronaves');self.resize(1540,960);self.setMinimumSize(1120,740)
        root=QWidget();layout=QVBoxLayout(root);self.setCentralWidget(root)
        title=QLabel('Calculadora de envolventes de vuelo');title.setStyleSheet('font-size:23px;font-weight:600;color:#173e52;padding:5px')
        layout.addWidget(title)
        actions=QHBoxLayout()
        self.selector=QComboBox();self.selector.setMinimumWidth(280);actions.addWidget(self.selector,1)
        for label,fn in [('Nuevo proyecto',self.prompt_project),('Nueva aeronave',self.prompt_aircraft),('Duplicar condición',self.prompt_duplicate),
                         ('Abrir',self.open_project),('Guardar',self.save),('Exportar…',self.export)]:
            button=QPushButton(label);button.clicked.connect(fn);actions.addWidget(button)
        layout.addLayout(actions)
        split=QSplitter(Qt.Orientation.Horizontal);layout.addWidget(split,1)
        inputs=QWidget();left=QVBoxLayout(inputs);left.setContentsMargins(3,3,7,3)
        form=QFormLayout();self.aircraft=QLineEdit();self.condition=QLineEdit();form.addRow('Aeronave',self.aircraft);form.addRow('Condición',self.condition)
        self.category=QComboBox()
        for category in ['normal','utilidad','acrobática']:self.category.addItem(category.capitalize(),category)
        form.addRow('Categoría',self.category)
        self.method=QComboBox();self.method.addItem('FAR 23 histórico · subparte C','subparte_c');self.method.addItem('FAR 23 histórico · apéndice A','apendice_a')
        form.addRow('Criterio',self.method);left.addLayout(form)
        hint=QLabel('Cambie los valores como en una hoja de cálculo.\nLas tres envolventes se actualizan juntas.');hint.setWordWrap(True);left.addWidget(hint)
        self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['Dato','Valor','Unidad']);self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1,90);self.table.setColumnWidth(2,100);self.table.verticalHeader().hide();left.addWidget(self.table,1)
        self.advanced=QCheckBox('Opciones de atmósfera, ráfagas y más datos');left.addWidget(self.advanced)
        helpers=QHBoxLayout();b=QPushButton('Base al nivel del mar');b.setToolTip('Introduce rho, rho0, g, altitud=0 y Ude=50/25 ft/s de la referencia histórica.');b.clicked.connect(self.standard_conditions);helpers.addWidget(b)
        b=QPushButton('Factores por categoría');b.clicked.connect(self.category_factors);helpers.addWidget(b);left.addLayout(helpers)
        update=QHBoxLayout();self.automatic=QCheckBox('Actualizar automáticamente');self.automatic.setChecked(True);update.addWidget(self.automatic)
        b=QPushButton('Calcular');b.clicked.connect(self.recalculate);update.addWidget(b);left.addLayout(update)
        self.message=QLabel();self.message.setWordWrap(True);self.message.setMinimumHeight(45);left.addWidget(self.message)
        split.addWidget(inputs)
        right=QWidget();rl=QVBoxLayout(right);rl.setContentsMargins(4,2,0,2)
        self.kpis=QLabel();self.kpis.setWordWrap(True);self.kpis.setStyleSheet('background:#e4f1f4;color:#164557;padding:9px;font-size:12px');rl.addWidget(self.kpis)
        self.tabs=QTabWidget();rl.addWidget(self.tabs,1)
        dashboard=QWidget();grid=QGridLayout(dashboard);grid.setContentsMargins(2,2,2,2)
        for kind,r,c,span in [('man',0,0,1),('gust',0,1,1),('combined',1,0,2)]:
            canvas=FigureCanvasQTAgg(envelope_figure(calculate(self.case()),kind,compact=True));self.canvases['overview_'+kind]=canvas
            grid.addWidget(canvas,r,c,1,span)
        grid.setRowStretch(0,1);grid.setRowStretch(1,1);self.tabs.addTab(dashboard,'Las tres envolventes')
        for kind,label in [('man','Maniobras'),('gust','Ráfagas'),('combined','Combinado')]:
            tab=QWidget();tl=QVBoxLayout(tab);canvas=FigureCanvasQTAgg(envelope_figure(calculate(self.case()),kind));self.canvases[kind]=canvas
            toolbar=NavigationToolbar2QT(canvas,self);self.toolbars[kind]=toolbar
            tl.addWidget(toolbar);tl.addWidget(canvas,1);self.tabs.addTab(tab,label)
        results=QWidget();res=QVBoxLayout(results);self.results_table=QTableWidget(0,3);self.results_table.setHorizontalHeaderLabels(['Resultado','Valor','Unidad'])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);res.addWidget(self.results_table,1)
        self.checks=QTextBrowser();res.addWidget(self.checks,1);self.tabs.addTab(results,'Resultados y verificaciones')
        sources=QWidget();sl=QVBoxLayout(sources);meta=QFormLayout();self.meta={}
        for key,label in [('title','Nombre del proyecto'),('student','Nombre'),('subject','Materia'),('teacher','Docente'),('date','Fecha')]:
            edit=QLineEdit();self.meta[key]=edit;meta.addRow(label,edit);edit.textEdited.connect(self.schedule)
        sl.addLayout(meta)
        sl.addWidget(QLabel('Hipótesis y condiciones de esta aeronave (una por renglón)'))
        self.assumptions=QPlainTextEdit();self.assumptions.setMaximumHeight(95);sl.addWidget(self.assumptions)
        sl.addWidget(QLabel('Fuentes y observaciones editables. La referencia original permanece en el historial.'))
        self.trace=QTableWidget(0,8);self.trace.setHorizontalHeaderLabels(['Símbolo','Descripción','Valor','Unidad','Fuente','Página','Estado','Observaciones'])
        self.trace.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        for i,width in enumerate([90,190,90,100,210,80,100,240]):self.trace.setColumnWidth(i,width)
        sl.addWidget(self.trace,1);self.sources=QTextBrowser();self.sources.setMaximumHeight(130);sl.addWidget(self.sources)
        self.include_niu=QCheckBox('Incluir también el reporte independiente de figuras de Niu al exportar');sl.addWidget(self.include_niu)
        self.tabs.addTab(sources,'Proyecto y fuentes');split.addWidget(right);split.setSizes([390,1140]);inputs.setMinimumWidth(340)
        self.selector.currentIndexChanged.connect(self.switch_case);self.table.itemChanged.connect(self.schedule)
        self.trace.itemChanged.connect(self.schedule);self.advanced.toggled.connect(self.filter_rows)
        for edit in [self.aircraft,self.condition]:edit.textEdited.connect(self.schedule)
        self.category.currentIndexChanged.connect(self.schedule);self.method.currentIndexChanged.connect(self.method_changed)
        self.assumptions.textChanged.connect(self.schedule);self.automatic.toggled.connect(self.schedule)
        self.setStyleSheet('QMainWindow{background:#eff4f7} QTabWidget::pane{background:white} QTabBar::tab{padding:8px 10px} QPushButton{padding:6px 9px} QTableWidget{gridline-color:#d7e3ea} QTextBrowser{padding:5px}')
        self.loading=False;self.fill_selector();self.display_case();self.render()

    def case(self):return next(c for c in self.project['cases'] if c['id']==self.current)

    def fill_selector(self):
        self.selector.blockSignals(True);self.selector.clear()
        for c in self.project['cases']:self.selector.addItem(c.get('aircraft','Aeronave')+' · '+c['name'],c['id'])
        self.selector.setCurrentIndex(self.selector.findData(self.current));self.selector.blockSignals(False)

    def display_case(self):
        self.loading=True;c=self.case();self.keys=list(c['parameters']);self.aircraft.setText(c.get('aircraft',''));self.condition.setText(c['name'])
        self.category.setCurrentIndex(self.category.findData(c.get('category','normal')));self.method.setCurrentIndex(self.method.findData(c['method']))
        # Qt difiere la liberación de los editores. Ocultarlos de inmediato
        # evita controles anteriores superpuestos al cambiar de aeronave.
        for i in range(self.table.rowCount()):
            old_editor=self.table.cellWidget(i,2)
            if old_editor:old_editor.hide()
        self.table.setRowCount(len(self.keys));self.trace.setRowCount(len(self.keys))
        for i,key in enumerate(self.keys):
            p=c['parameters'][key];desc=SPECS[key][0];cell=item(LABELS.get(key,key));cell.setToolTip(desc);self.table.setItem(i,0,cell)
            value_item=item('' if p['value'] is None else p['value'],True);value_item.setToolTip('Pendiente' if p['value'] is None else str(p['value']))
            self.table.setItem(i,1,value_item)
            unit=QComboBox();options=list(UNITS[SPECS[key][1]])
            if p['unit'] not in options:options.insert(0,p['unit'])
            unit.addItems(options);unit.setCurrentText(p['unit']);unit.currentTextChanged.connect(self.schedule);self.table.setCellWidget(i,2,unit)
            values=[key,desc,'' if p['value'] is None else p['value'],p['unit'],p.get('source',''),p.get('page',''),p.get('status','pendiente'),p.get('notes','')]
            for j,v in enumerate(values):self.trace.setItem(i,j,item(v,j in [4,5,7]))
            self.trace.item(i,4).setToolTip(str(p.get('original',{})))
        for key,edit in self.meta.items():edit.setText(self.project.get('metadata',{}).get(key,''))
        self.assumptions.setPlainText('\n'.join(c.get('assumptions',[])));self.include_niu.setChecked(bool(c.get('requires_thesis','Wn_photo' in c['parameters'])))
        self.filter_rows();self.loading=False

    def filter_rows(self):
        method=self.method.currentData()
        for i,key in enumerate(self.keys):
            show=key in MAIN_KEYS or self.advanced.isChecked() or (method=='apendice_a' and key in ['n3','n4'])
            self.table.setRowHidden(i,not show)

    def method_changed(self,*args):self.filter_rows();self.schedule()

    def schedule(self,*args):
        if self.loading:return
        self.changed=True
        if self.automatic.isChecked():self.timer.start()
        else:self.message.setText('Datos cambiados. Pulse Calcular para actualizar las gráficas.')

    def commit(self):
        c=self.case();new=deepcopy(c['parameters']);changes=[]
        for i,key in enumerate(self.keys):
            raw=self.table.item(i,1).text().strip();unit=self.table.cellWidget(i,2).currentText()
            try:
                value=float(raw.replace(',','.')) if raw else None
                if value is not None and not math.isfinite(value):raise ValueError()
            except ValueError:raise ValueError(f'{LABELS.get(key,key)}: escriba un número finito o deje vacío')
            source=self.trace.item(i,4).text();page=self.trace.item(i,5).text();notes=self.trace.item(i,7).text();p=new[key]
            if (p.get('value'),p.get('unit'),p.get('source',''),p.get('page',''),p.get('notes',''))!=(value,unit,source,page,notes):
                changes.append(dict(parameter=key,before=p.get('value'),before_unit=p['unit'],after=value,after_unit=unit,
                                    reason=notes or 'Edición del usuario en la calculadora',time=datetime.now().isoformat()))
                p.setdefault('original',deepcopy(c['parameters'][key]));p.update(value=value,unit=unit,source=source,page=page,notes=notes,status='supuesto' if value is not None else 'pendiente')
        for key,value in [('method',self.method.currentData()),('category',self.category.currentData()),('aircraft',self.aircraft.text().strip() or 'Aeronave'),('name',self.condition.text().strip() or 'Condición')]:
            if c.get(key)!=value:changes.append(dict(parameter=key,before=c.get(key),after=value,reason='Selección del usuario'))
            c[key]=value
        c['parameters']=new;c.setdefault('changes',[]).extend(changes);c['assumptions']=[s.strip() for s in self.assumptions.toPlainText().splitlines() if s.strip()]
        for key,edit in self.meta.items():self.project['metadata'][key]=edit.text()
        self.project['active_case']=self.current
        self.trace.blockSignals(True)
        for i,key in enumerate(self.keys):
            p=new[key]
            for j,value in [(2,'' if p['value'] is None else p['value']),(3,p['unit']),(6,p['status'])]:self.trace.item(i,j).setText(str(value))
        self.trace.blockSignals(False)
        self.fill_selector()

    def auto_recalculate(self):self.recalculate(silent=True)

    def recalculate(self,checked=False,silent=False):
        self.timer.stop()
        try:self.commit();self.render();return True
        except Exception as exc:
            self.render(dict(name=self.condition.text(),aircraft=self.aircraft.text(),values={},curves={},blocked=[str(exc)],checks=[],parameters=[],assumptions=[],requires_thesis=False))
            if not silent:QMessageBox.warning(self,'Revisar dato',str(exc))
            return False

    def render(self,result=None):
        r=result or calculate(self.case());self.result=r
        for key,canvas in list(self.canvases.items()):
            compact=key.startswith('overview_');kind=key.removeprefix('overview_');fig=envelope_figure(r,kind,compact)
            new_canvas=FigureCanvasQTAgg(fig);layout=canvas.parentWidget().layout();layout.replaceWidget(canvas,new_canvas)
            # Se liberan widgets de memoria; no se borra ningún archivo.
            canvas.hide();canvas.deleteLater();self.canvases[key]=new_canvas
            if not compact:
                old_toolbar=self.toolbars[kind];toolbar=NavigationToolbar2QT(new_canvas,self)
                layout.replaceWidget(old_toolbar,toolbar);old_toolbar.hide();old_toolbar.deleteLater();self.toolbars[kind]=toolbar
            new_canvas.draw_idle()
        v=r['values'];format_value=lambda key,unit: f'{v[key]:.3f} {unit}' if key in v else 'pendiente'
        self.kpis.setText('W/S: '+format_value('W_S','lbf/ft²')+'     Vs: '+format_value('Vs','kt EAS')+'     A: '+format_value('V_A_stall','kt EAS')+'     Kg: '+format_value('Kg',''))
        self.results_table.setRowCount(len(v))
        for i,(key,value) in enumerate(v.items()):
            unit='kt EAS' if key.startswith('V') else ('lbf/ft²' if key=='W_S' else ('lbf' if key.startswith('W') else '1'))
            if key in SPECS:unit=next(iter(UNITS[SPECS[key][1]]))
            for j,txt in enumerate([key,f'{value:.9g}',unit]):self.results_table.setItem(i,j,item(txt))
        checks='<h3>Verificaciones de esta condición</h3>'
        for ck in r['checks']:checks+='<p><b>'+escape(ck['estado']+' · '+ck['código'])+'</b><br>'+escape(ck['detalle'])+'</p>'
        self.checks.setHtml(checks)
        legacy=r.get('requires_thesis',False)
        text='<b>Fuentes de esta aeronave.</b> Edite las referencias y las hipótesis en esta pestaña. Los valores y las referencias originales permanecen en el JSON. '
        text+='La calculadora aplica el criterio histórico seleccionado para aeronaves de categoría normal, utilidad o acrobática; la aplicabilidad debe revisarse por proyecto.'
        if legacy:text+='<p>Este caso conserva la tarea original de Cessna. Sigue pendiente la tesis, capítulo 1.9, para confirmar la variante y el procedimiento.</p>'
        self.sources.setHtml(text)
        errors=r['blocked'];warnings=sum(ck['estado'] in ['ADVERTENCIA','NO APLICA','ERROR'] for ck in r['checks'])
        self.message.setStyleSheet('color:#aa4527' if errors else 'color:#16665b')
        self.message.setText(('Complete: '+'; '.join(errors[:3])) if errors else f'Actualizado · {len(v)} resultados · {warnings} observaciones en Verificaciones')
        self.statusBar().showMessage('Cambie los datos y vea las tres envolventes. Los campos vacíos quedan pendientes. Exportar es opcional.')

    def set_value(self,key,value,unit=None):
        i=self.keys.index(key);self.table.item(i,1).setText('' if value is None else str(value))
        if unit is not None:self.table.cellWidget(i,2).setCurrentText(unit)

    def standard_conditions(self):
        self.loading=True
        for key,value in dict(rho=RHO0,rho0=RHO0,g=32.1740485564,U_c=50,U_d=25,altitude=0).items():
            self.set_value(key,value,next(iter(UNITS[SPECS[key][1]])))
            i=self.keys.index(key);self.trace.item(i,4).setText('Base estándar explícita: nivel del mar; FAR 23 histórico para Ude=50/25 ft/s')
        self.loading=False;self.recalculate(silent=True)

    def category_factors(self):
        c=self.category.currentData();method=self.method.currentData()
        n={'normal':3.8,'utilidad':4.4,'acrobática':6}[c]
        self.loading=True;self.set_value('n_pos',n,'1');self.set_value('n_neg',-n*(.5 if method=='apendice_a' or c=='acrobática' else .4),'1');self.loading=False
        self.recalculate(silent=True)

    def snapshot(self):
        if not self.changed:return None
        try:self.commit()
        except ValueError:
            self.project['draft_cells']={key:self.table.item(i,1).text() for i,key in enumerate(self.keys)}
        folder=ROOT/'data/recuperaciones';folder.mkdir(parents=True,exist_ok=True)
        path=save_project(self.project,folder/('recuperacion_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json'));self.changed=False;return path

    def select_case(self,case_id):
        self.timer.stop();self.current=case_id;self.project['active_case']=case_id;self.fill_selector();self.display_case();self.render()

    def switch_case(self,index):
        if self.loading:return
        target=self.selector.itemData(index)
        if not target or target==self.current:return
        if not self.recalculate(silent=True):
            self.fill_selector();return
        self.select_case(target)

    def add_aircraft(self,name):
        self.commit();c=new_case(name);self.project['cases'].append(c);self.changed=True;self.select_case(c['id']);return c

    def duplicate_current(self,name):
        self.commit();c=duplicate_case(self.case(),name);self.project['cases'].append(c);self.changed=True;self.select_case(c['id']);return c

    def replace_project(self,project):
        self.snapshot();self.project=deepcopy(project);self.current=project['active_case'];self.changed=False;self.select_case(self.current)

    def prompt_project(self):
        name,ok=QInputDialog.getText(self,'Nuevo proyecto','Nombre de la primera aeronave:',text='Mi aeronave')
        if ok and name.strip():self.replace_project(blank_project(name.strip()))

    def prompt_aircraft(self):
        name,ok=QInputDialog.getText(self,'Nueva aeronave','Nombre o modelo:',text='Nueva aeronave')
        if ok and name.strip():self.guarded(lambda:self.add_aircraft(name.strip()))

    def prompt_duplicate(self):
        name,ok=QInputDialog.getText(self,'Duplicar condición','Nombre de la nueva condición:',text=self.case()['name']+' copia')
        if ok and name.strip():self.guarded(lambda:self.duplicate_current(name.strip()))

    def guarded(self,fn):
        try:return fn()
        except Exception as exc:QMessageBox.warning(self,'Revisar datos',str(exc));return None

    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,'Abrir proyecto',str(ROOT/'data'),'Proyecto JSON (*.json)')
        if path:self.guarded(lambda:self.replace_project(load_project(path)))

    def save(self):
        path,_=QFileDialog.getSaveFileName(self,'Guardar una versión del proyecto',str(ROOT/'data/proyecto_usuario.json'),'Proyecto JSON (*.json)')
        if not path:return
        def go():
            self.commit();saved=save_project(self.project,path);self.changed=False;self.message.setText('Guardado: '+str(saved))
        self.guarded(go)

    def export(self):
        def go():
            if not self.recalculate(silent=True):return
            from src.reporting.exporter import export_project
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:self.last_export=export_project(self.project,self.current,all_cases=True,include_niu=self.include_niu.isChecked())
            finally:QApplication.restoreOverrideCursor()
            QMessageBox.information(self,'Exportación terminada','Gráficas, CSV, proyecto y reporte de esta aeronave:\n'+str(self.last_export))
        self.guarded(go)

    def closeEvent(self,event):
        self.timer.stop()
        try:self.snapshot()
        except Exception as exc:
            self.message.setText('No se pudo guardar la recuperación: '+str(exc));event.ignore();return
        event.accept()

def launch(project,screenshot=None):
    app=QApplication.instance() or QApplication([]);app.setStyle('Fusion');palette=QPalette()
    for role,color in [(QPalette.ColorRole.Window,'#eff4f7'),(QPalette.ColorRole.WindowText,'#233e50'),(QPalette.ColorRole.Base,'#ffffff'),
                       (QPalette.ColorRole.AlternateBase,'#edf3f7'),(QPalette.ColorRole.Text,'#233e50'),(QPalette.ColorRole.Button,'#e4edf3'),
                       (QPalette.ColorRole.ButtonText,'#233e50'),(QPalette.ColorRole.Highlight,'#176f82'),(QPalette.ColorRole.HighlightedText,'#ffffff')]:palette.setColor(role,QColor(color))
    app.setPalette(palette);window=CalculatorWindow(project);window.show()
    if screenshot:
        def capture():window.grab().save(str(fresh(inside(screenshot))));app.quit()
        QTimer.singleShot(2200,capture)
    return app.exec()
