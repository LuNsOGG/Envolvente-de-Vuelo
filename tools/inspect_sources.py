"""Renderizado y OCR reproducible; no modifica los documentos originales."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import ROOT, fresh
import argparse
import json
import hashlib
import urllib.request

def main():
    import fitz
    p = argparse.ArgumentParser()
    p.add_argument('--ocr', action='store_true')
    p.add_argument('--pages', default='1-8,28-96')
    p.add_argument('--official', action='store_true')
    args = p.parse_args()
    if args.official:
        for suffix in ['part23-appA', 'sec23-333', 'sec23-335', 'sec23-337', 'sec23-341']:
            name = f'CFR-2016-title14-vol1-{suffix}.pdf'
            dest = ROOT/'sources'/name
            if not dest.exists():
                try:
                    urllib.request.urlretrieve('https://www.govinfo.gov/content/pkg/CFR-2016-title14-vol1/pdf/'+name, dest)
                    print('Descargado', name, flush=True)
                except Exception as e:
                    print(name, str(e), flush=True)
        return
    source = next(ROOT.glob('Airframe*.pdf'))
    doc = fitz.open(source)
    indices = []
    for part in args.pages.split(','):
        bounds = [int(x) for x in part.split('-')]
        indices.extend(range(bounds[0], bounds[-1]+1))
    ocr = None
    if args.ocr:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
    records = []
    for number in indices:
        image = ROOT/'sources/niu_pages'/f'visor_{number:03}.png'
        if not image.exists():
            doc[number-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(image)
        txt = image.with_suffix('.txt')
        if ocr and not txt.exists():
            lines, _ = ocr(str(image))
            txt.write_text('\n'.join(line[1] for line in (lines or [])), encoding='utf-8')
        records.append({'visor':number,'image':str(image.relative_to(ROOT)), 'text':txt.read_text(encoding='utf-8') if txt.exists() else ''})
        print('Página',number,'lista', flush=True)
    fresh(ROOT/'sources/indice_ocr.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.iterdir() if p.suffix.lower() in ['.pdf','.jpg']}
    fresh(ROOT/'sources/huellas_originales.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

if __name__ == '__main__':
    main()
