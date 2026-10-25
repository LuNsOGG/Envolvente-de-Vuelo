from copy import deepcopy
import math
import pytest
from src.project import load_project
from bootstrap import ROOT
from src.calculations.engine import calculate,positive_root,compare
from src.calculations.units import convert,KT_TO_FPS,eas_to_tas,RHO0

def case():return deepcopy(load_project(ROOT/'data/proyecto_inicial.json')['cases'][1])

@pytest.mark.parametrize('value,unit,dim,expected',[(1,'N','weight',1/4.4482216152605),(1,'m²','area',10.7639104167),
    (1,'m','length',3.280839895),(1,'kg/m³','density',1/515.3788183931961),
    (32.1740485564,'lbm/ft³','density',1),(.105,'1/deg','slope',6.01605684887),(1,'ft/s EAS','speed',1/KT_TO_FPS)])
def test_conversions(value,unit,dim,expected):assert convert(value,unit,dim)==pytest.approx(expected,rel=1e-9)

@pytest.mark.parametrize('value,unit,dim',[(1,'lb','weight'),(1,'lb/ft³','density'),(.1,'sin confirmar','slope'),(100,'kt TAS','speed'),(float('nan'),'lbf','weight'),(float('inf'),'1','ratio'),(True,'1','ratio')])
def test_ambiguous_units_rejected(value,unit,dim):
    with pytest.raises(ValueError):convert(value,unit,dim)

def test_eas_tas():assert eas_to_tas(100,RHO0/4)==200
def test_eas_bad_density():
    with pytest.raises(ValueError):eas_to_tas(100,0)

def test_reference_independent_hand_calculation():
    r=calculate(case());v=r['values']
    assert v['W_S']==pytest.approx(4631/181)
    assert v['Vc_A_raw']==pytest.approx(167.62501230837)
    assert v['Vs']==pytest.approx(71.94628810490288)
    assert v['mu']==pytest.approx(26.96006677272241)
    assert v['Kg']==pytest.approx(.735424973765285)
    assert v['n_gust_c_pos']==pytest.approx(4.125124083231102)

def test_original_remains_blocked():
    c=load_project(ROOT/'data/proyecto_inicial.json')['cases'][0];r=calculate(c)
    assert r['values']['W_S']==pytest.approx(25.585635359116022)
    assert r['blocked'] and not r['curves']
    assert 'CN_neg' not in r['values']

def test_no_mutation():
    c=case();saved=deepcopy(c);calculate(c);assert c==saved

def test_exact_stall_intersections_in_grid():
    r=calculate(case());v=r['values'];c=r['curves']
    for key,sign,limit in [('V_A_stall','stall_pos',v['n_pos']),('V_G_stall','stall_neg',v['n_neg'])]:
        index=c['V'].index(v[key]);assert c[sign][index]==pytest.approx(limit,abs=1e-10)

def test_gust_passes_c_and_d_and_center_one():
    r=calculate(case());c=r['curves'];v=r['values']
    for speed,pkey,mkey in [('Vc','n_gust_c_pos','n_gust_c_neg'),('Vd','n_gust_d_pos','n_gust_d_neg')]:
        i=c['V'].index(v[speed]);assert c['gust_pos'][i]==pytest.approx(v[pkey]);assert c['gust_neg'][i]==pytest.approx(v[mkey])
    assert all(p+m==pytest.approx(2) for p,m in zip(c['gust_pos'],c['gust_neg']))

def test_linear_gust_between_c_d():
    r=calculate(case());c=r['curves'];v=r['values']
    for speed,p in zip(c['V'],c['gust_pos']):
        if speed>=v['Vc']:
            t=(speed-v['Vc'])/(v['Vd']-v['Vc']);assert p==pytest.approx(v['n_gust_c_pos']*(1-t)+v['n_gust_d_pos']*t)

def test_exceedance_retained():
    r=calculate(case());c=r['curves'];i=c['V'].index(r['values']['Vc'])
    assert c['combined_pos'][i]>r['values']['n_pos']
    assert c['combined_neg'][i]<r['values']['n_neg']
    assert any(x['código']=='RÁFAGA DOMINANTE' and x['estado']=='ADVERTENCIA' for x in r['checks'])

def test_static_bounds_and_origin_and_closure():
    r=calculate(case());c=r['curves']
    assert c['combined_pos'][0]==c['combined_neg'][0]==0
    for i in range(len(c['V'])):
        assert c['stall_neg'][i]-1e-10<=c['combined_neg'][i]<=c['combined_pos'][i]<=c['stall_pos'][i]+1e-10
    assert c['V'][-1]==r['values']['Vd'];assert c['man_neg'][-1]==pytest.approx(0)

def test_intersections_satisfy_both_curves():
    r=calculate(case());c=r['curves']
    for point in r['intersections']:
        i=c['V'].index(point['V']);side='pos' if 'positiv' in point['tipo'] else 'neg'
        assert c['gust_'+side][i]==pytest.approx(point['n'])
        if point['tipo'].startswith('pérdida'):assert c['stall_'+side][i]==pytest.approx(point['n'])

def test_weight_sensitivity():
    c=case();r1=calculate(c);c['parameters']['W']['value']/=2;r2=calculate(c)
    assert r2['values']['Vs']==pytest.approx(r1['values']['Vs']/math.sqrt(2))
    assert r2['values']['n_gust_c_pos']>r1['values']['n_gust_c_pos']

def test_conditional_geometry_does_not_claim_appendix_applicable():
    r=calculate(case())
    assert r['values']['AR_conditional']==pytest.approx(181/4.26**2)
    check=next(x for x in r['checks'] if x['código']=='AR CONDICIONAL A23.1')
    assert check['estado']=='NO APLICA' and 'Si c=' in check['detalle']

@pytest.mark.parametrize('key,value',[('S',0),('W',-1),('n_pos',0),('Vd',150),('n_neg',1),('CN_neg',1),('rho',-1),('a',0)])
def test_invalid_input_blocks(key,value):
    c=case();c['parameters'][key]['value']=value;assert calculate(c)['blocked']

def test_missing_negative_not_mirrored():
    c=case();c['parameters']['CN_neg']['value']=None;r=calculate(c)
    assert 'combined_pos' not in r['curves'] and 'man_pos' not in r['curves']
    assert 'gust_pos' in r['curves']

def test_appendix_a4_manual_factors():
    c=case();c['method']='apendice_a'
    for k,v in [('n_neg',-1.9),('n3',4.3),('n4',-2.3)]:c['parameters'][k]['value']=v
    r=calculate(c);curves=r['curves'];v=r['values'];i=curves['V'].index(v['Vc'])
    assert curves['combined_pos'][i]==pytest.approx(4.3);assert curves['combined_neg'][i]==pytest.approx(-2.3)
    assert curves['combined_pos'][-1]==pytest.approx(3.8);assert curves['combined_neg'][-1]==pytest.approx(-1.9)
    assert 'Kg' not in v  # no se mezcla la subparte C con A1/A2
    assert 'gust_pos' not in curves  # A4 no puede hacerse pasar por ráfagas físicas

def test_appendix_a_missing_chart_blocked():
    c=case();c['method']='apendice_a';r=calculate(c)
    assert 'combined_pos' not in r['curves'];assert any('A1/A2' in b for b in r['blocked'])

def test_quadratic_roots():assert positive_root(1,-2,-3)==[3]
def test_comparison_uses_same_motor():
    p=load_project(ROOT/'data/proyecto_inicial.json');rows=compare(p['cases'])
    row=next(r for r in rows if r['variable']=='W_S' and r['caso comparado']==p['cases'][1]['name'])
    assert row['diferencia']==0

def test_sampling_independent_points():
    c=case();a=calculate(c,31);b=calculate(c,2001)
    assert a['values']==b['values'];assert a['points']==b['points'];assert a['intersections']==b['intersections']
