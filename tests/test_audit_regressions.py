from copy import deepcopy
import pytest
from src.calculations import calculate
from src.calculations.examples import example_project


def test_01_import_rejects_incompatible_units_without_mutating_data():
    from src.calculations.worksheet import adapt_case
    p=example_project(1)['cases'][0];p['parameters']['W']['unit']='kg';before=deepcopy(p)
    with pytest.raises(ValueError,match='incompatible'):adapt_case(p)
    assert p==before
    p['parameters']['W'].update(value=4000*4.4482216152605,unit='N')
    assert calculate(adapt_case(p))['values']['W']==pytest.approx(4000)


def test_02_invalid_optional_gust_is_not_silently_omitted():
    c=example_project(2)['cases'][0];c['parameters']['U_b']['unit']='incorrecta'
    r=calculate(c);assert r['blocked'] and not r['curves']
    assert any('U_b' in message for message in r['blocked'])
    c['parameters']['U_b']['value']=None
    assert not calculate(c)['blocked']

