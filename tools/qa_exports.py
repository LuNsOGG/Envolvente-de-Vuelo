"""Revisión reproducible de exportaciones; conserva todos los intermedios."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT,inside,fresh
import argparse
import csv
import json
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib

def main():
    import pymupdf
    from PIL import Image,ImageOps,ImageDraw
    from src.project import load_project
    from src.calculations import calculate
    parser=argparse.ArgumentParser();parser.add_argument('directory');args=parser.parse_args()
    out=inside(args.directory);qa=fresh(ROOT/'outputs/qa'/out.name);qa.mkdir()
    info={'export':str(out),'pdf':[],'docx':[],'checks':[]}
    project=load_project(out/'proyecto.json')
    for c in project['cases']:
        folder=out/c['id']
        if not folder.exists():continue
        r=calculate(c);saved=json.loads((folder/'resultados.json').read_text(encoding='utf-8'))
        assert saved==r,'El JSON exportado no coincide con el motor actual'
        rows=list(csv.DictReader((folder/'curvas.csv').open(encoding='utf-8-sig')))
        for i,row in enumerate(rows):
            for k,v in row.items():
                expected=r['curves'][k][i]
                assert (v=='' and expected is None) or float(v)==expected
        info['checks'].append(c['id']+': JSON y cada fila de CSV coinciden con el motor')
    original=json.loads((out/'huellas_fuentes.json').read_text(encoding='utf-8'))
    for name,digest in original.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    info['checks'].append('Huellas de los tres archivos originales sin cambios')
    for path in out.glob('*.pdf'):
        doc=pymupdf.open(path);dest=qa/path.stem;dest.mkdir();images=[]
        for i,page in enumerate(doc):
            name=dest/f'pagina_{i+1:02}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(name);images.append(name)
            assert len(page.get_text().strip())>50,'Página vacía o sin texto suficiente'
            # Control geométrico de texto fuera de la hoja.
            for block in page.get_text('blocks'):
                assert block[0]>=0 and block[1]>=0 and block[2]<=page.rect.width+.5 and block[3]<=page.rect.height+.5
        info['pdf'].append(dict(file=path.name,pages=len(doc),text_within_page=True))
        for batch in range(0,len(images),6):
            sheet=Image.new('RGB',(3*440,2*600),'#d6dee3');draw=ImageDraw.Draw(sheet)
            for j,name in enumerate(images[batch:batch+6]):
                im=Image.open(name);im.thumbnail((420,555));x=(j%3)*440+(440-im.width)//2;y=(j//3)*600+25
                sheet.paste(im,(x,y));draw.text(((j%3)*440+12,(j//3)*600+6),f'Página {batch+j+1}',fill='#17394b')
            sheet.save(dest/f'contacto_{batch//6+1}.png')
    for path in out.glob('*.docx'):
        with ZipFile(path) as z:
            assert z.testzip() is None
            xml=ElementTree.fromstring(z.read('word/document.xml'))
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            texts=xml.findall('.//w:t',ns);assert len(texts)>50
            info['docx'].append(dict(file=path.name,OOXML_valid=True,text_runs=len(texts),visual_render='Pendiente: no hay LibreOffice incluido en el runtime Windows'))
    (qa/'verificacion_automatica.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(qa)

if __name__=='__main__':main()
