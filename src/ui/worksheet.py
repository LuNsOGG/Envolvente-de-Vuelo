"""Interfaz simple: las catorce filas de Excel y cuatro vistas monocromas."""
from copy import deepcopy
from datetime import datetime
from html import escape
import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QFontDatabase, QFont
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,
    QLabel,QPushButton,QCheckBox,QComboBox,QTableWidget,QTableWidgetItem,QHeaderView,QSplitter,QTabWidget,
    QFileDialog,QMessageBox,QInputDialog,QDialog,QDialogButtonBox,QFormLayout,QLineEdit,QTextBrowser,QMenu)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from bootstrap import ROOT, fresh, inside
from src.project import load_project, save_project
from src.calculations import calculate
from src.calculations.engine import SPECS
from src.calculations.units import UNITS, convert
from src.calculations.worksheet import EXCEL_FIELDS, FIELD_KEYS, adapt_case, prepare_case, worksheet_project
from src.plotting.envelopes import envelope_figure
from src.calculations.examples import example_project, VARIABLES
from src.calculations.cases import parameter


def cell(value, editable=False):
    result=QTableWidgetItem(str(value))
    if not editable:result.setFlags(result.flags() & ~Qt.ItemFlag.ItemIsEditable)
    return result


class WorksheetWindow(QMainWindow):
    def __init__(self, project):
        super().__init__(); configure_font(QApplication.instance()); self.project=deepcopy(project); self.current=project['active_case']
        self.project['cases']=[adapt_case(c) for c in self.project['cases']]
        self.changed=False; self.loading=True; self.canvases={}; self.toolbars={}; self.result=None
        self.timer=QTimer(self); self.timer.setSingleShot(True); self.timer.setInterval(550); self.timer.timeout.connect(self.recalculate)
        self.setWindowTitle('Envolventes de Vuelo | Hoja de cálculo'); self.resize(1500,940); self.setMinimumSize(1080,740)
        root=QWidget(); self.setCentralWidget(root); layout=QVBoxLayout(root)
        top=QHBoxLayout(); title=QLabel('Calculadora de envolventes de vuelo'); title.setStyleSheet('font-size:21px;font-weight:600;padding:7px 0')
        top.addWidget(title,1)
        self.examples_button=QPushButton('Ejemplos'); menu=QMenu(self.examples_button)
        for number,label in [(1,'Ejemplo Cessna'),(2,'Ejemplo libro')]:
            action=menu.addAction(label); action.triggered.connect(lambda checked=False,n=number:self.load_example(n))
        self.examples_button.setMenu(menu); top.addWidget(self.examples_button)
        for label,fn in [('Nuevo',self.new_project),('Abrir',self.open_project),('Guardar',self.save),('Exportar',self.export)]:
            b=QPushButton(label); b.clicked.connect(fn); top.addWidget(b)
        layout.addLayout(top)
        self.conditions_row=QWidget(); conditions=QHBoxLayout(self.conditions_row);conditions.setContentsMargins(0,0,0,0)
        conditions.addWidget(QLabel('Condición'))
        self.condition_selector=QComboBox();conditions.addWidget(self.condition_selector,1)
        self.reference_toggle=QCheckBox('Comparar con tesis publicada');conditions.addWidget(self.reference_toggle)
        self.reference_button=QPushButton('Tesis y revisión');conditions.addWidget(self.reference_button)
        self.condition_selector.currentIndexChanged.connect(self.select_condition)
        self.reference_toggle.toggled.connect(self.recalculate)
        self.reference_button.clicked.connect(self.show_reference)
        layout.addWidget(self.conditions_row)
        split=QSplitter(Qt.Orientation.Horizontal); layout.addWidget(split,1)
        inputs=QWidget(); left=QVBoxLayout(inputs); left.setContentsMargins(0,0,10,0)
        self.table=QTableWidget(len(EXCEL_FIELDS),3); self.table.setHorizontalHeaderLabels(['Nombre','Valor','Unidad']); self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch); self.table.setColumnWidth(1,125); self.table.setColumnWidth(2,105)
        self.table.setAlternatingRowColors(True); self.table.verticalHeader().setDefaultSectionSize(34); left.addWidget(self.table,1)
        actions=QHBoxLayout(); self.complete_button=QPushButton('Completar cálculo…'); self.complete_button.clicked.connect(self.complete_data); actions.addWidget(self.complete_button)
        b=QPushButton('Resultados'); b.clicked.connect(self.show_results); actions.addWidget(b); left.addLayout(actions)
        self.variables_button=QPushButton('Resumen de variables'); self.variables_button.clicked.connect(self.show_variables); left.addWidget(self.variables_button)
        self.message=QLabel(); self.message.setWordWrap(True); left.addWidget(self.message)
        inputs.setMinimumWidth(340); split.addWidget(inputs)
        right=QWidget(); rl=QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); self.summary=QLabel(); self.summary.setWordWrap(True); self.summary.setStyleSheet('padding:8px;background:#eeeeee'); rl.addWidget(self.summary)
        self.tabs=QTabWidget(); rl.addWidget(self.tabs,1)
        together=QWidget(); grid=QGridLayout(together); grid.setContentsMargins(2,2,2,2); self.tabs.addTab(together,'Las tres envolventes')
        self.result=calculate(self.case())
        for kind,row,column,span in [('man',0,0,1),('gust',0,1,1),('combined',1,0,2)]:
            canvas=FigureCanvasQTAgg(envelope_figure(self.result,kind,compact=True)); self.canvases['overview_'+kind]=canvas; grid.addWidget(canvas,row,column,1,span)
        grid.setRowStretch(0,1); grid.setRowStretch(1,1);grid.setColumnStretch(0,1);grid.setColumnStretch(1,1)
        for kind,label in [('man','Maniobras'),('gust','Ráfagas'),('combined','Combinado')]:
            page=QWidget(); pl=QVBoxLayout(page); canvas=FigureCanvasQTAgg(envelope_figure(self.result,kind)); self.canvases[kind]=canvas
            toolbar=NavigationToolbar2QT(canvas,self); self.toolbars[kind]=toolbar; pl.addWidget(toolbar); pl.addWidget(canvas,1); self.tabs.addTab(page,label)
        split.addWidget(right); split.setSizes([370,1120]); self.table.itemChanged.connect(self.schedule)
        self.setStyleSheet('QMainWindow,QWidget{color:#111111} QMainWindow{background:white} QTabWidget::pane{background:white;border:1px solid #aaaaaa} QTabBar::tab{padding:8px 12px;background:#eeeeee;border:1px solid #aaaaaa} QTabBar::tab:selected{background:white;font-weight:600} QPushButton{padding:7px 12px;background:#f5f5f5;border:1px solid #999999;border-radius:3px} QPushButton:hover{background:#dddddd} QTableWidget{background:white;alternate-background-color:#f2f2f2;gridline-color:#cccccc} QHeaderView::section{background:#eeeeee;padding:6px;border:1px solid #cccccc}')
        self.fill(); self.loading=False; self.recalculate(); self.changed=False

    def case(self):return next(c for c in self.project['cases'] if c['id']==self.current)

    def fill(self):
        self.loading=True
        self.condition_selector.blockSignals(True);self.condition_selector.clear()
        for candidate in self.project['cases']:self.condition_selector.addItem(candidate['name'],candidate['id'])
        self.condition_selector.setCurrentIndex(self.condition_selector.findData(self.current));self.condition_selector.blockSignals(False)
        thesis=self.case().get('reference_dataset')=='ipn_2007'
        self.conditions_row.setVisible(thesis or len(self.project['cases'])>1)
        self.reference_toggle.setVisible(thesis);self.reference_button.setVisible(thesis)
        for i,(key,label,description) in enumerate(EXCEL_FIELDS):
            old=self.table.cellWidget(i,2)
            if old:old.hide()
            p=self.case()['parameters'][key]; self.table.setItem(i,0,cell(label)); self.table.item(i,0).setToolTip(description)
            if key=='CN_pos' and self.case().get('coefficient_basis')=='CL':self.table.item(i,0).setText('Cʟ máx.')
            if key=='a' and self.case().get('aero_model')=='niu_table':self.table.item(i,0).setText('a₀')
            value=cell('' if p.get('value') is None else f'{p["value"]:.10g}',key!='W_S_photo' and not(key=='chord' and self.case().get('chord_mode')=='geometric')); self.table.setItem(i,1,value)
            value.setToolTip(p.get('notes','')+'\nFuente: '+p.get('source',''))
            if key=='W_S_photo':
                self.table.setItem(i,2,cell('lbf/ft²')); value.setBackground(QColor('#dddddd')); continue
            combo=QComboBox(); combo.addItems(list(UNITS[SPECS[key][1]])); combo.setCurrentText(p['unit']); combo.setEnabled(not(key=='chord' and self.case().get('chord_mode')=='geometric')); combo.currentTextChanged.connect(self.schedule); self.table.setCellWidget(i,2,combo)
        state=self.project.get('case_drafts',{}).get(self.current,{})
        draft=state.get('cells',self.project.get('draft_cells',{}) if self.project.get('draft_case_id',self.current)==self.current else {})
        draft_units=state.get('units',self.project.get('draft_units',{}) if self.project.get('draft_case_id',self.current)==self.current else {})
        for key,unit in draft_units.items():
            if key in FIELD_KEYS and key!='W_S_photo' and unit in UNITS[SPECS[key][1]]:self.table.cellWidget(FIELD_KEYS.index(key),2).setCurrentText(unit)
        for key,raw in draft.items():
            if key in FIELD_KEYS and key!='W_S_photo':self.table.item(FIELD_KEYS.index(key),1).setText(raw)
        self.loading=False

    def schedule(self,*args):
        if self.loading:return
        self.changed=True; self.timer.start()

    def commit(self):
        c=self.case(); p=deepcopy(c['parameters']); changes=[]
        for i,key in enumerate(FIELD_KEYS):
            if key=='W_S_photo' or (key=='chord' and c.get('chord_mode')=='geometric'):continue
            raw=self.table.item(i,1).text().strip(); unit=self.table.cellWidget(i,2).currentText()
            try:
                value=float(raw.replace(',','.')) if raw else None
                if value is not None and not math.isfinite(value):raise ValueError()
            except ValueError:raise ValueError(EXCEL_FIELDS[i][1]+': escriba un número o deje el campo vacío.')
            q=p[key]
            if (value,unit)!=(q.get('value'),q['unit']):
                changes.append(dict(parameter=key,before=q.get('value'),before_unit=q['unit'],after=value,after_unit=unit,reason='Edición en la hoja Excel',time=datetime.now().isoformat()))
                q.update(value=value,unit=unit,status='usuario' if value is not None else 'pendiente',source='Introducido por el usuario')
        c['parameters']=p; c.setdefault('changes',[]).extend(changes)
        prepared,_=prepare_case(c); c['parameters']=prepared['parameters']; self.project['active_case']=self.current
        self.project.get('case_drafts',{}).pop(self.current,None)
        if self.project.get('draft_case_id',self.current)==self.current:
            for key in ['draft_cells','draft_units','draft_case_id']:self.project.pop(key,None)

    def set_value(self,key,value,unit=None):
        i=FIELD_KEYS.index(key); self.table.item(i,1).setText('' if value is None else str(value))
        if unit is not None:self.table.cellWidget(i,2).setCurrentText(unit)

    def recalculate(self,*args):
        try:self.commit(); r=calculate(self.case())
        except (ValueError,TypeError,KeyError) as exc:
            r=dict(name=self.case()['name'],aircraft=self.case()['aircraft'],requires_thesis=False,worksheet=True,values={},curves={},points=[],blocked=[str(exc)],checks=[],equations=[],parameters=[],derived=[],partial={})
        self.render(r); return not r['blocked']

    def render(self,r):
        self.result=r; self.loading=True
        ws=r['values'].get('W_S'); self.table.item(6,1).setText('' if ws is None else f'{ws:.6f}')
        if self.case().get('chord_mode')=='geometric':
            q=self.case()['parameters']['chord'];self.table.item(FIELD_KEYS.index('chord'),1).setText('' if q.get('value') is None else f'{q["value"]:.10g}')
        self.loading=False
        for key,old in list(self.canvases.items()):
            compact=key.startswith('overview_'); kind=key.removeprefix('overview_'); new=FigureCanvasQTAgg(envelope_figure(r,kind,compact,show_reference=self.reference_toggle.isChecked())); page_layout=old.parentWidget().layout()
            page_layout.replaceWidget(old,new); old.hide(); old.deleteLater(); self.canvases[key]=new; new.show()
            if not compact:
                previous=self.toolbars[kind]; toolbar=NavigationToolbar2QT(new,self); page_layout.replaceWidget(previous,toolbar); previous.hide(); previous.deleteLater(); self.toolbars[kind]=toolbar; toolbar.show()
            new.draw_idle()
        def v(key):return f'{r["values"][key]:.3f}' if key in r['values'] else '—'
        self.summary.setText(f'{self.case()["aircraft"]}     W/S  {v("W_S")} lbf/ft²     Vs  {v("Vs")} kt EAS     Vc  {v("Vc")}     Vd  {v("Vd")}     Kg  {v("Kg")}')
        missing=[]; p=self.case()['parameters']
        if p.get('CN_neg',{}).get('value') is None:missing.append('CN mínimo negativo')
        for k in ['U_c','U_d']:
            if p.get(k,{}).get('value') is None:missing.append(k)
        self.complete_button.setText('Completar cálculo…' if missing else 'Datos de cálculo…')
        self.message.setText(('Faltan: '+', '.join(missing)+'.') if missing else ('Revise los datos en Resultados.' if r['blocked'] else ''))
        if r.get('academic_notice') and not r['blocked']:self.message.setText(r['academic_notice'])
        if not r['values'] and r['blocked']:self.message.setText(r['blocked'][0])
        self.message.setVisible(bool(self.message.text()))
        self.statusBar().clearMessage(); self.statusBar().hide()

    def complete_data(self):
        if self.case()['method']=='niu':return self.niu_data()
        if not self.try_commit():return
        dialog=QDialog(self); dialog.setWindowTitle('Completar cálculo'); dialog.resize(520,340); box=QVBoxLayout(dialog)
        form=QFormLayout(); box.addLayout(form)
        model=QComboBox(); model.addItem('Fórmulas de la hoja · apéndice A','apendice_a'); model.addItem('FAR 23 histórico · subparte C','subparte_c'); model.setCurrentIndex(model.findData(self.case()['method'])); form.addRow('Modelo de cálculo',model)
        category=QComboBox()
        for key in ['normal','utilidad','acrobática']:category.addItem(key.capitalize(),key)
        category.setCurrentIndex(category.findData(self.case().get('category','normal'))); form.addRow('Categoría',category)
        edits={}; labels={}
        for key,label in [('CN_neg','CN mínimo negativo'),('n3','n3 · lectura de figura A1'),('n4','n4 · lectura de figura A2'),('altitude','Altitud [ft]')]:
            edit=QLineEdit(); parameter=self.case()['parameters'].get(key,{}); current=parameter.get('value')
            if key=='altitude' and current is not None:current=convert(current,parameter['unit'],'length')
            edit.setText('' if current is None else str(current)); edits[key]=edit; labels[key]=QLabel(label); form.addRow(labels[key],edit)
        def filter_fields():
            for key in ['n3','n4','altitude']:
                visible=(model.currentData()=='apendice_a') if key!='altitude' else (model.currentData()=='subparte_c'); edits[key].setVisible(visible); labels[key].setVisible(visible)
        model.currentIndexChanged.connect(filter_fields); filter_fields()
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel); box.addWidget(buttons); buttons.rejected.connect(dialog.reject)
        def accept():
            try:
                updates={}
                for key,edit in edits.items():
                    raw=edit.text().strip(); value=float(raw.replace(',','.')) if raw else None
                    if value is not None and not math.isfinite(value):raise ValueError('Escriba valores finitos.')
                    if value is not None and ((key in ['CN_neg','n4'] and value>=0) or (key=='n3' and value<=0) or (key=='altitude' and not 0<=value<=50000)):raise ValueError('Revise los signos: CN mínimo y n4 negativos; n3 positivo; altitud entre 0 y 50000 ft.')
                    updates[key]=value
                c=self.case(); c['method']=model.currentData(); c['category']=category.currentData()
                for key,value in updates.items():
                    p=c['parameters'].setdefault(key,dict(value=None,unit='ft' if key=='altitude' else '1',source='',page='',status='pendiente',notes=''))
                    if p.get('value')!=value or (key=='altitude' and p.get('unit')!='ft'):
                        c.setdefault('changes',[]).append(dict(parameter=key,before=p.get('value'),after=value,reason='Dato adicional introducido por el usuario'))
                        p.update(value=value,unit='ft' if key=='altitude' else '1',status='usuario' if value is not None else 'pendiente',source='Introducido por el usuario en Completar cálculo')
                self.changed=True; dialog.accept(); self.recalculate()
            except ValueError as exc:QMessageBox.warning(dialog,'Revisar dato',str(exc))
        buttons.accepted.connect(accept); dialog.exec()

    def niu_data(self):
        if not self.try_commit():return
        c=self.case(); dialog=QDialog(self); dialog.setWindowTitle('Datos de cálculo'); dialog.resize(610,620)
        box=QVBoxLayout(dialog); form=QFormLayout(); box.addLayout(form)
        def choice(label,items,current):
            combo=QComboBox()
            for text,value in items:combo.addItem(text,value)
            combo.setCurrentIndex(max(0,combo.findData(current)));form.addRow(label,combo);return combo
        speed=choice('Vc y Vd',[('Automáticas · fórmulas del Excel','excel'),('Automáticas · normal FAR 23 histórico','subparte_c'),('Introducidas','manual')],c.get('speed_mode'))
        negative=choice('Límite de maniobra negativo',[('−0.5 N · ejercicio Excel','excel'),('−0.4 N · normal','normal'),('−1 · ejemplo de transporte','transport'),('Introducido','manual')],c.get('negative_rule'))
        end=choice('Límite negativo entre Vc y Vd',[('Constante','constant'),('Llega a cero en Vd','zero')],c.get('negative_end'))
        aero=choice('Coeficientes aerodinámicos',[('Constantes','constant'),('Tabla por Mach · Ejemplo libro','niu_table')],c.get('aero_model'))
        basis=choice('Tipo de coeficiente',[('CN · fuerza normal','CN'),('CL · sustentación','CL')],c.get('coefficient_basis'))
        chord_choice=choice('Cuerda para ráfagas',[('Introducida','manual'),('Geométrica · S/b','geometric')],c.get('chord_mode','manual'))
        edits={};labels={}
        rows=[('CN_neg','Coeficiente mínimo negativo','1'),('n_neg','Factor negativo n−','1'),
              ('Vc','Vc [kt EAS]','kt EAS'),('Vd','Vd [kt EAS]','kt EAS'),
              ('U_c','Uc [ft/s]','ft/s'),('U_d','Ud [ft/s]','ft/s'),('U_b','Ub [ft/s] · 0 omite VB','ft/s'),
              ('altitude','Altitud [ft] · referencia','ft'),('Cse','Sonido equivalente Cse [kt EAS]','kt EAS'),
              ('Va_selected','Va seleccionada [kt EAS] · distinta de A','kt EAS'),('span','Envergadura [ft] · para S/b','ft')]
        for key,label,unit in rows:
            q=c['parameters'].get(key,{}); value=q.get('value'); edit=QLineEdit()
            if value is not None:value=convert(value,q['unit'],SPECS[key][1])
            edit.setText('' if value is None else f'{value:.12g}');edits[key]=edit;labels[key]=QLabel(label);form.addRow(labels[key],edit)
        def visibility():
            for key,visible in [('Vc',speed.currentData()=='manual'),('Vd',speed.currentData()=='manual'),('n_neg',negative.currentData()=='manual'),('Cse',aero.currentData()=='niu_table')]:
                labels[key].setVisible(visible);edits[key].setVisible(visible)
        speed.currentIndexChanged.connect(visibility);negative.currentIndexChanged.connect(visibility);aero.currentIndexChanged.connect(visibility);visibility()
        note=QLabel('n3 y n4 se calculan en Vc. La tabla por Mach pertenece al Ejemplo 2.');note.setWordWrap(True);box.addWidget(note)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);box.addWidget(buttons);buttons.rejected.connect(dialog.reject)
        def accept():
            try:
                trial=deepcopy(c)
                trial.update(speed_mode=speed.currentData(),negative_rule=negative.currentData(),negative_end=end.currentData(),
                             aero_model=aero.currentData(),coefficient_basis=basis.currentData(),chord_mode=chord_choice.currentData())
                for key,_,unit in rows:
                    if edits[key].isHidden():continue
                    raw=edits[key].text().strip();value=float(raw.replace(',','.')) if raw else None
                    if value is not None and (not math.isfinite(value) or (key in ['CN_neg','n_neg'] and value>=0) or (key not in ['CN_neg','n_neg'] and value<0)):
                        raise ValueError('Revise signos y valores finitos; los coeficientes y límites negativos deben ser menores que cero.')
                    before=trial['parameters'].get(key,{})
                    if (value,unit)!=(before.get('value'),before.get('unit')):
                        trial.setdefault('changes',[]).append(dict(parameter=key,before=before.get('value'),after=value,reason='Edición en Datos de cálculo'))
                        trial['parameters'][key]=dict(before or parameter(None,unit),value=value,unit=unit,status='usuario',source='Introducido por el usuario')
                if trial['aero_model']=='niu_table' and trial['coefficient_basis']!='CL':raise ValueError('La tabla del libro utiliza CL. Seleccione CL o coeficientes constantes.')
                c.update(trial);self.changed=True;dialog.accept();self.fill();self.recalculate()
            except ValueError as exc:QMessageBox.warning(dialog,'Revisar dato',str(exc))
        buttons.accepted.connect(accept);dialog.exec()

    def select_condition(self,index):
        if self.loading or index<0:return
        selected=self.condition_selector.itemData(index)
        if selected==self.current:return
        self.timer.stop();self.snapshot();self.current=selected;self.project['active_case']=selected
        self.fill();self.recalculate();self.changed=True

    def reference_html(self,r):
        if not r.get('reference_rows'):return ''
        def val(x):return 'Pendiente' if x is None else f'{x:.8g}'
        text='<h3>Velocidades: mínimo, selección e intersección</h3><table border="1" cellspacing="0" cellpadding="5"><tr><th>Magnitud</th><th>kt EAS</th><th>Criterio</th></tr>'
        for row in r['speed_rows']:text+='<tr><td>'+escape(row['magnitud'])+'</td><td>'+val(row['valor'])+'</td><td>'+escape(row['criterio'])+'</td></tr>'
        text+='</table><h3>Tesis publicada y condición actual</h3><p>Los valores publicados son referencias: no se utilizan para forzar las curvas revisadas.</p><table border="1" cellspacing="0" cellpadding="5"><tr><th>Dato</th><th>Tesis</th><th>Actual</th><th>Unidad</th><th>Página</th></tr>'
        for row in r['reference_rows']:text+='<tr><td>'+escape(row['dato'])+'</td><td>'+val(row['tesis'])+'</td><td>'+val(row['recalculado'])+'</td><td>'+escape(row['unidad'])+'</td><td>'+escape(row['pagina'])+'</td></tr>'
        text+='</table><h3>Discrepancias e hipótesis</h3>'
        for issue in r['source_issues']:text+='<p>'+escape(issue)+'</p>'
        return text+'<p>'+escape(r['reference_curve_note'])+'</p>'

    def show_reference(self):
        self.recalculate();dialog=QDialog(self);dialog.setWindowTitle('Tesis y revisión');dialog.resize(1050,760)
        box=QVBoxLayout(dialog);view=QTextBrowser();view.setHtml(self.reference_html(self.result));box.addWidget(view)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);buttons.rejected.connect(dialog.reject);box.addWidget(buttons);dialog.exec()

    def load_example(self,number):
        self.replace_project(example_project(number))

    def variables_html(self):
        text='<h3>Resumen de variables</h3><p>Ejemplo Cessna: tesis IPN, ficha revisada y comparación con el capítulo 1.9. Ejemplo libro: avión comercial de Niu.</p>'
        text+='<table border="1" cellspacing="0" cellpadding="6"><tr><th>Símbolo</th><th>Nombre</th><th>Significado</th></tr>'
        for symbol,name,meaning in VARIABLES:text+='<tr><td>'+escape(symbol)+'</td><td>'+escape(name)+'</td><td>'+escape(meaning)+'</td></tr>'
        return text+'</table>'

    def show_variables(self):
        dialog=QDialog(self);dialog.setWindowTitle('Resumen de variables');dialog.resize(830,680);box=QVBoxLayout(dialog)
        view=QTextBrowser();view.setHtml(self.variables_html());box.addWidget(view)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close);buttons.rejected.connect(dialog.reject);box.addWidget(buttons);dialog.exec()

    def show_results(self):
        self.recalculate(); dialog=QDialog(self); dialog.setWindowTitle('Resultados'); dialog.resize(850,650); layout=QVBoxLayout(dialog); view=QTextBrowser(); layout.addWidget(view)
        r=self.result; text='<h2>Resultados</h2><p>Modelo: '+escape(self.case()['method'])+' · '+escape(self.case().get('category','normal'))+'</p>'
        text+='<p>Velocidades en kt EAS. Modelo cuasiestático: maniobra y ráfagas se calculan por separado.</p>'
        for assumption in self.case().get('assumptions',[]):text+='<p>'+escape(assumption)+'</p>'
        text+='<table border="1" cellspacing="0" cellpadding="6"><tr><th>Resultado</th><th>Valor</th><th>Fórmula / fuente</th></tr>'
        for d in r.get('derived',[]):text+='<tr><td>'+escape(d['variable'])+'</td><td>'+('Pendiente' if d['value'] is None else f'{d["value"]:.7g}')+' '+escape(d['unit'])+'</td><td>'+escape(d['formula'])+'<br>'+escape(d['source'])+'</td></tr>'
        text+='</table>'+self.reference_html(r)+'<h3>Datos y unidades</h3>'
        for key,label,_ in EXCEL_FIELDS:
            p=self.case()['parameters'][key]; text+='<p><b>'+escape(label)+':</b> '+escape(str(p.get('value')))+' '+escape(p['unit'])+' · '+escape(p.get('status',''))+'<br>'+escape(p.get('notes',''))+'</p>'
        text+='<h3>Resultados de ráfaga</h3>'
        for key in ['U_b','U_c','U_d','Vc','Vd','Vb','a_c','a_d','mu_c','mu_d','Kg_c','Kg_d','n_gust_b_pos','n_gust_b_neg','n3','n4','n_gust_d_pos','n_gust_d_neg']:
            if key in r['values']:text+='<p><b>'+key+':</b> '+f'{r["values"][key]:.8g}'+'</p>'
        text+='<p>Ráfagas: se usa a. CLα se conserva como referencia independiente.</p><h3>Verificaciones</h3>'
        for item in r.get('checks',[]):text+='<p><b>'+escape(item['estado']+' · '+item['código'])+'</b><br>'+escape(item['detalle'])+'</p>'
        for pending in r['blocked']:text+='<p>Pendiente: '+escape(pending)+'</p>'
        view.setHtml(text); buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Close); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons); dialog.exec()

    def try_commit(self):
        try:self.commit(); return True
        except ValueError as exc:QMessageBox.warning(self,'Revisar dato',str(exc)); return False

    def snapshot(self):
        if not self.changed:return
        try:self.commit()
        except ValueError:
            self.project['draft_cells']={key:self.table.item(i,1).text() for i,key in enumerate(FIELD_KEYS)}
            self.project['draft_case_id']=self.current
            self.project['draft_units']={key:self.table.cellWidget(i,2).currentText() for i,key in enumerate(FIELD_KEYS) if key!='W_S_photo'}
            self.project.setdefault('case_drafts',{})[self.current]=dict(cells=deepcopy(self.project['draft_cells']),units=deepcopy(self.project['draft_units']))
        folder=ROOT/'data/recuperaciones'; folder.mkdir(parents=True,exist_ok=True)
        saved=save_project(self.project,folder/('hoja_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')); self.changed=False; return saved

    def replace_project(self,project):
        self.timer.stop(); self.snapshot(); self.project=deepcopy(project); self.project['cases']=[adapt_case(c) for c in self.project['cases']]; self.current=project['active_case']; self.changed=False; self.fill(); self.recalculate()

    def new_project(self):
        name,ok=QInputDialog.getText(self,'Nuevo proyecto','Nombre de su aeronave:',text='Mi aeronave')
        if ok and name.strip():self.replace_project(worksheet_project(False,name.strip()))

    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,'Abrir proyecto',str(ROOT/'data'),'Proyecto JSON (*.json)')
        if not path:return
        try:
            p=load_project(path)
            if len(p['cases'])>1:
                labels=[c.get('aircraft','Aeronave')+' · '+c['name'] for c in p['cases']]; label,ok=QInputDialog.getItem(self,'Abrir hoja','Seleccione la condición:',labels,0,False)
                if not ok:return
                p['active_case']=p['cases'][labels.index(label)]['id']
            self.replace_project(p)
        except (ValueError,OSError) as exc:QMessageBox.warning(self,'Abrir',str(exc))

    def save(self):
        if not self.try_commit():return
        path,_=QFileDialog.getSaveFileName(self,'Guardar proyecto',str(ROOT/'data/hoja_usuario.json'),'Proyecto JSON (*.json)')
        if path:
            try:saved=save_project(self.project,path); self.changed=False; self.statusBar().showMessage('Guardado: '+str(saved)); self.statusBar().show()
            except (ValueError,OSError) as exc:QMessageBox.warning(self,'Guardar',str(exc))

    def export(self):
        if not self.try_commit():return
        self.recalculate()
        try:
            from src.reporting.exporter import export_project
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            try:self.last_export=export_project(self.project,self.current,all_cases=True,include_niu=False)
            finally:QApplication.restoreOverrideCursor()
            QMessageBox.information(self,'Exportación terminada','Archivos guardados en:\n'+str(self.last_export))
        except (ValueError,OSError,RuntimeError) as exc:QMessageBox.warning(self,'Exportar',str(exc))

    def closeEvent(self,event):
        self.timer.stop()
        try:self.snapshot(); event.accept()
        except (ValueError,OSError) as exc:self.message.setText('No se pudo conservar la recuperación: '+str(exc)); event.ignore()


def configure_font(app):
    # Qt offscreen en Windows puede no descubrir fuentes del sistema.
    # La fuente ya acompaña a Matplotlib y se carga solo en este proceso.
    from pathlib import Path
    from matplotlib import get_data_path
    if 'DejaVu Sans' not in QFontDatabase.families():
        font_id=QFontDatabase.addApplicationFont(str(Path(get_data_path())/'fonts/ttf/DejaVuSans.ttf'))
        if font_id<0:raise RuntimeError('No se pudo cargar la fuente incluida con la aplicación.')
    app.setFont(QFont('DejaVu Sans',9))


def launch(project,screenshot=None):
    app=QApplication.instance() or QApplication([]); app.setStyle('Fusion'); palette=QPalette()
    for role,color in [(QPalette.ColorRole.Window,'#ffffff'),(QPalette.ColorRole.WindowText,'#111111'),(QPalette.ColorRole.Base,'#ffffff'),
                       (QPalette.ColorRole.AlternateBase,'#f2f2f2'),(QPalette.ColorRole.Text,'#111111'),(QPalette.ColorRole.Button,'#f5f5f5'),
                       (QPalette.ColorRole.ButtonText,'#111111'),(QPalette.ColorRole.Highlight,'#333333'),(QPalette.ColorRole.HighlightedText,'#ffffff'),
                       (QPalette.ColorRole.Link,'#111111'),(QPalette.ColorRole.LinkVisited,'#555555')]:palette.setColor(role,QColor(color))
    app.setPalette(palette); window=WorksheetWindow(project); window.show()
    if screenshot:
        QTimer.singleShot(1800,lambda:(window.grab().save(str(fresh(inside(screenshot)))),app.quit()))
    return app.exec()
