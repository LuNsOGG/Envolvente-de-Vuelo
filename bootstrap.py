"""Configura dependencias y temporales exclusivamente dentro del proyecto."""
from pathlib import Path
import os
import sys

FROZEN = bool(getattr(sys, 'frozen', False))
BUNDLE_ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
if FROZEN:
    executable_dir = Path(sys.executable).resolve().parent
    ROOT = next((p for p in [executable_dir, *executable_dir.parents]
                 if (p/'envolventes.workspace.json').is_file()), executable_dir)
else:
    ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
local = ROOT / '.runtime' / 'packages'
if not FROZEN and local.exists() and sys.version_info[:2] == (3, 12):
    sys.path.insert(0, str(local))
for key, value in {'MPLCONFIGDIR': ROOT/'.runtime/mpl', 'TEMP': ROOT/'.runtime/tmp',
                   'TMP': ROOT/'.runtime/tmp', 'XDG_CACHE_HOME': ROOT/'.runtime/cache'}.items():
    os.environ[key] = str(value)
    value.mkdir(parents=True, exist_ok=True)
if FROZEN and sys.stderr is None:
    logdir=ROOT/'.runtime/logs';logdir.mkdir(parents=True,exist_ok=True)
    logpath=logdir/f'sesion_{os.getpid()}.log'
    index=2
    while logpath.exists():
        logpath=logdir/f'sesion_{os.getpid()}_{index}.log';index+=1
    sys.stdout=sys.stderr=logpath.open('x',encoding='utf-8',buffering=1)

def inside(path):
    target = Path(path).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError('Solo se permiten archivos dentro de ' + str(ROOT))
    return target

def bundled_file(relative):
    candidate = ROOT / relative
    return candidate if candidate.is_file() else BUNDLE_ROOT / relative

def fresh(path):
    """Reserva un nombre nuevo; nunca reemplaza un archivo ya existente."""
    path = inside(path)
    if not path.exists():
        return path
    index = 2
    while path.with_name(f'{path.stem}_{index}{path.suffix}').exists():
        index += 1
    return path.with_name(f'{path.stem}_{index}{path.suffix}')
