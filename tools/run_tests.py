import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bootstrap
import pytest

if __name__=='__main__':
    raise SystemExit(pytest.main(['tests','-q','-p','no:cacheprovider']))
