"""Compilación portable en destino nuevo, sin borrar versiones ni usar --clean."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT,fresh
import os
from datetime import datetime
import subprocess
import json

def main():
    tag=datetime.now().strftime('%Y%m%d_%H%M%S');work=fresh(ROOT/'.runtime/builds'/tag);work.mkdir(parents=True)
    dist=fresh(ROOT/'aplicacion'/('version_'+tag));dist.mkdir(parents=True)
    specs=work/'spec';specs.mkdir();cache=work/'cache';cache.mkdir()
    from PIL import Image,ImageDraw
    im=Image.new('RGBA',(256,256),'#111111');draw=ImageDraw.Draw(im)
    draw.line([(35,205),(35,44)],fill='white',width=5);draw.line([(35,161),(225,161)],fill='white',width=5)
    draw.line([(35,161),(62,145),(90,102),(115,75),(208,75),(208,182),(115,194),(78,179),(35,161)],fill='#dddddd',width=9)
    icon=work/'envolventes.ico';im.save(icon,format='ICO',sizes=[(32,32),(48,48),(64,64),(128,128),(256,256)])
    env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(ROOT/'.runtime/build_packages'),str(ROOT/'.runtime/packages'),str(ROOT)])
    env['PYINSTALLER_CONFIG_DIR']=str(cache);env['PYTHONDONTWRITEBYTECODE']='1';env['TEMP']=env['TMP']=str(ROOT/'.runtime/tmp')
    cmd=[sys.executable,'-B','-m','PyInstaller','--onedir','--windowed','--name','Envolventes_de_Vuelo',
         '--distpath',str(dist),'--workpath',str(work/'obj'),'--specpath',str(specs),
         '--paths',str(ROOT),'--paths',str(ROOT/'.runtime/packages'),'--icon',str(icon),
         '--hidden-import','matplotlib.backends.backend_qtagg','--hidden-import','docx',
         '--collect-data','docx','--collect-data','reportlab','--collect-data','matplotlib',
         '--exclude-module','PyQt5','--exclude-module','PyQt6','--exclude-module','PySide2',
         '--exclude-module','pymupdf','--exclude-module','fitz','--exclude-module','rapidocr_onnxruntime',
         '--exclude-module','onnxruntime','--exclude-module','cv2','--exclude-module','pytest',str(ROOT/'main.py')]
    for module in ['pandas','scipy','openpyxl','IPython','notebook','jupyter','sympy','torch','tensorflow','tkinter']:
        cmd[-1:-1]=['--exclude-module',module]
    # Especificación propia: no empaquetar el ICU de Poppler que aparece en
    # PATH. Qt 6 usa las funciones sin sufijo del ICU suministrado por Windows.
    # Se filtra el inventario antes de copiar archivos; no se borra nada.
    excludes=['PyQt5','PyQt6','PySide2','pymupdf','fitz','rapidocr_onnxruntime','onnxruntime','cv2','pytest',
              'pandas','scipy','openpyxl','IPython','notebook','jupyter','sympy','torch','tensorflow','tkinter']
    spec=specs/'Envolventes_de_Vuelo.spec'
    spec.write_text(f'''# Especificación de compilación en carpeta nueva
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('docx') + collect_data_files('reportlab') + collect_data_files('matplotlib') + [({str(ROOT/'src/reporting/matlab_template.m')!r}, 'src/reporting')]
a = Analysis([{str(ROOT/'main.py')!r}], pathex={[str(ROOT),str(ROOT/'.runtime/packages')]!r},
    binaries=[], datas=datas, hiddenimports=['matplotlib.backends.backend_qtagg','matplotlib.backends.backend_agg','matplotlib.backends.backend_svg','matplotlib.backends.backend_pdf','matplotlib.backends.backend_ps','docx'],
    hookspath=[], hooksconfig={{}}, runtime_hooks=[], excludes={excludes!r}, noarchive=False, optimize=0)
a.binaries = [entry for entry in a.binaries if Path(entry[0]).name.lower() not in {{'icuuc.dll','icuin.dll','icudt78.dll'}}]
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,[],exclude_binaries=True,name='Envolventes_de_Vuelo',debug=False,
    bootloader_ignore_signals=False,strip=False,upx=False,console=False,disable_windowed_traceback=False,
    argv_emulation=False,target_arch=None,codesign_identity=None,entitlements_file=None,icon=[{str(icon)!r}])
coll = COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,upx_exclude=[],name='Envolventes_de_Vuelo')
''',encoding='utf-8')
    cmd=[sys.executable,'-B','-m','PyInstaller','--distpath',str(dist),'--workpath',str(work/'obj'),str(spec)]
    (work/'comando.json').write_text(json.dumps(cmd,ensure_ascii=False,indent=2),encoding='utf-8')
    with (work/'compilacion.log').open('x',encoding='utf-8') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:
        print('Falló compilación. Consulte '+str(work/'compilacion.log'));return result.returncode
    exe=dist/'Envolventes_de_Vuelo/Envolventes_de_Vuelo.exe'
    (work/'resultado.json').write_text(json.dumps(dict(exe=str(exe),build=str(work)),indent=2),encoding='utf-8')
    print(exe);print('Registro: '+str(work/'compilacion.log'));return 0

if __name__=='__main__':raise SystemExit(main())
