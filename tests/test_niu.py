from copy import deepcopy
import math
import pytest
from src.calculations import calculate
from src.calculations.examples import example_project,VARIABLES
from src.calculations.units import KT_TO_FPS
from src.calculations.worksheet import prepare_case,worksheet_project


def case(number=1):return (worksheet_project() if number==1 else example_project(number))['cases'][0]


def test_excel_matches_independent_hand_calculation():
    c=case();before=deepcopy(c);r=calculate(c);v=r['values']
    assert not r['blocked'] and c==before
    ws=4631/181;a=.105*180/math.pi
    mu=2*ws/(.0023*4.26*a*32.2);kg=.88*mu/(5.3+mu)
    vc=17*math.sqrt(3.8*ws);vd=24*math.sqrt(3.8*ws)
    assert v['mu']==pytest.approx(mu) and v['Kg']==pytest.approx(kg)
    for key,speed,u in [('c',vc,50),('d',vd,25)]:
        dn=kg*u*speed*a/(498*ws)
        assert v['n_gust_'+key+'_pos']==pytest.approx(1+dn)
        assert v['n_gust_'+key+'_neg']==pytest.approx(1-dn)
    assert v['n3']!=v['n_pos'] and v['n4']!=v['n_neg']


@pytest.mark.parametrize('number',[1,2])
def test_curves_origin_symmetry_exact_nodes_bounds_and_continuity(number):
    r=calculate(case(number));v=r['values'];curves=r['curves']
    assert curves['gust_pos'][0]==curves['gust_neg'][0]==1
    assert curves['combined_pos'][0]==curves['combined_neg'][0]==0
    for speed,letter in [('Vc','c'),('Vd','d')]+([('Vb','b')] if number==2 else []):
        i=curves['V'].index(v[speed])
        assert curves['gust_pos'][i]==pytest.approx(v['n_gust_'+letter+'_pos'])
        assert curves['gust_neg'][i]==pytest.approx(v['n_gust_'+letter+'_neg'])
    for i,x in enumerate(curves['V']):
        assert curves['gust_pos'][i]+curves['gust_neg'][i]==pytest.approx(2)
        assert curves['stall_neg'][i]-1e-9<=curves['combined_neg'][i]<=curves['combined_pos'][i]<=curves['stall_pos'][i]+1e-9
        assert curves['combined_pos'][i]>=curves['man_pos'][i]-1e-9
        assert curves['combined_neg'][i]<=curves['man_neg'][i]+1e-9
        if x>=v['Vc']:
            t=(x-v['Vc'])/(v['Vd']-v['Vc'])
            assert curves['gust_pos'][i]==pytest.approx(v['n_gust_c_pos']*(1-t)+v['n_gust_d_pos']*t)
        if i and x-curves['V'][i-1]<1e-7:
            assert abs(curves['gust_pos'][i]-curves['gust_pos'][i-1])<1e-6
    for pt in r['intersections']:
        i=curves['V'].index(pt['V']);side='pos' if 'positiv' in pt['tipo'] else 'neg'
        assert curves['gust_'+side][i]==pytest.approx(pt['n'])
        if pt['tipo'].startswith('pérdida'):assert curves['stall_'+side][i]==pytest.approx(pt['n'],abs=1e-8)


def test_book_reproduces_critical_table_results_and_mach_variation():
    c=case(2);r=calculate(c);v=r['values'];curves=r['curves']
    assert not r['blocked']
    assert v['a_c']==pytest.approx(5.74) and v['a_d']==pytest.approx(6.78)
    assert v['delta_c']==pytest.approx(1.9496526506337344)
    assert v['delta_d']==pytest.approx(1.3839304213427412)
    assert v['delta_c']==pytest.approx(1.95,rel=.0002)
    assert v['delta_d']==pytest.approx(1.382,rel=.0015)
    assert v['W_S']==88000/1200
    assert v['Vs']<v['V_A_stall']<v['Vb']<v['Vc']<v['Vd']
    i=curves['V'].index(v['Vb']);assert curves['stall_pos'][i]==pytest.approx(curves['gust_pos'][i],abs=1e-9)
    assert curves['man_neg'][-1]==0
    c['aero_model']='constant';constant=calculate(c)
    assert constant['values']['delta_d']<v['delta_d']*.9


def test_book_row_at_200_matches_unrounded_formula_and_cl_table():
    r=calculate(case(2));v=r['values'];curves=r['curves'];i=curves['V'].index(200.)
    assert curves['stall_pos'][i]==pytest.approx(200**2/296*1.26/(88000/1200))
    mu=2*(88000/1200)/(.00176*13*5.37*32.2);kg=.88*mu/(5.3+mu)
    assert curves['gust_pos'][i]==pytest.approx(1+kg*66*200*5.37/(498*(88000/1200)))


@pytest.mark.parametrize('field,value',[('W',0),('S',-1),('CN_neg',0),('rho',-1),('a',0),('U_c',-1),('chord',None),('CN_pos',None)])
def test_bad_or_missing_inputs_leave_no_stale_graph(field,value):
    c=case();calculate(c);c['parameters'][field]['value']=value;r=calculate(c)
    assert r['blocked'] and not r['curves']


def test_missing_weight_clears_derived_speeds_in_memory():
    c=case();c['parameters']=prepare_case(c)[0]['parameters'];c['parameters']['W']['value']=None
    r=calculate(c);assert r['blocked'] and 'Vc' not in r['values']


def test_missing_gust_never_substitutes_old_n3_n4():
    c=case();c['parameters']['n3']['value']=100;c['parameters']['n4']['value']=-100
    c['parameters']['U_c']['value']=None;r=calculate(c)
    assert r['blocked'] and not r['curves']


def test_book_outside_table_blocks_extrapolation():
    c=case(2);c['parameters']['Vd']['value']=450;r=calculate(c)
    assert r['blocked'] and not r['curves']


def test_units_and_user_edits_change_gust_without_renaming_reference_slope():
    c=case();first=calculate(c)
    c['parameters']['a'].update(value=.105*180/math.pi,unit='1/rad')
    assert calculate(c)['values']['n3']==pytest.approx(first['values']['n3'])
    c['parameters']['CLalpha_photo']['value']=100
    assert calculate(c)['values']['n3']==pytest.approx(first['values']['n3'])
    c['parameters']['a']['value']*=1.1
    assert calculate(c)['values']['n3']>first['values']['n3']


def test_variable_summary_explains_independence_and_units():
    text=str(VARIABLES)
    for word in ['Kg','μ','EAS','n3','n4','CN','CL','Ub','Cse']:assert word in text
