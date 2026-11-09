import base64
import math
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.configuration import ROOT, load_config
from src.tools.grok_esp32_logger_stub import heartbeat_due, heartbeat_payload, read_sensors_sim, log_reading

client = TestClient(app)

@pytest.fixture
def healthy():
    return dict(pH=7,TAN_mg_L=.1,nitrite_mg_L=.1,nitrate_mg_L=30,
                nutrient_basis='as_N',protocol_nutrient_basis='as_N',KH_mg_L=80,DO_mg_L=6,
                water_levels_pct={'fish_tank':90,'sump':90},vermi_moisture_pct=70,
                vermi_temp_F=70,SOC_pct=80,power_ok=True,
                heartbeat_age_seconds={'water':1},expected_sensor_ids=['water'])

def alarm(**kwargs):
    resp=client.post('/alarms',json=kwargs); assert resp.status_code == 200
    return resp.json()

def codes(response):return {event['code'] for event in response['events']}

def test_default_configuration_and_future_isolation():
    c=client.get('/config').json()
    assert c['fish']['species']['value']=='comet goldfish'
    assert c['fish']['count']['value']==10
    assert c['fish']['feed_cap_g_day']['value']==15
    assert c['biofilter']['media_L']['value']==70
    assert c['hydraulics']['pumps']['value']==1
    assert sum(x['value'] for x in c['volumes_L'].values()) == pytest.approx(991.3)
    future=client.get('/config?profile=future-node').json()
    assert future['runnable'] is False
    assert all(p['label']=='IDEA' for p in future['parameters'].values())
    assert client.get('/config?profile=bogus').status_code==422

def test_all_config_parameter_records_have_provenance():
    def walk(obj):
        if isinstance(obj,dict):
            if 'value' in obj:
                assert obj['label'] in ['MEASURED','QUOTED','SIM','ASSUME','IDEA','CALC']
                assert obj['source'] and obj['unit']
            for value in obj.values():walk(value)
        elif isinstance(obj,list):
            for value in obj:walk(value)
    walk(load_config());walk(load_config('future-node'))

def test_default_sim_and_plot():
    r=client.post('/simulate',json={})
    assert r.status_code == 200
    d=r.json(); assert d['label']=='SIM' and len(d['rows'])==31
    assert d['inputs']['feed_g_day']==5
    assert d['derived']['total_water_L']==pytest.approx(991.3)
    assert d['derived']['media_area_m2']==pytest.approx(35)
    assert d['derived']['feed_TAN_g_day']==pytest.approx(.1472)
    assert abs(d['mass_balance']['residual_g'])<1e-7
    assert base64.b64decode(d['plot_base64']).startswith(b'\x89PNG')
    assert d['ro']['status']=='backup_only_not_modeled'
    assert all(math.isfinite(v) and v>=-1e-8 for row in d['rows'] for v in row.values())

@pytest.mark.parametrize('temp',[18,21,24])
@pytest.mark.parametrize('feed',[0,5,15])
def test_sim_sensitivity_conserves_N(temp,feed):
    r=client.post('/simulate',json={'days':10,'feed_g_day':feed,'temp_C':temp,'include_plot':False}).json()
    assert abs(r['mass_balance']['residual_g'])<1e-7
    assert r['mass_balance']['feed_TAN_g']==pytest.approx(feed*.32*.092*10)

def test_zero_input_zero_N_stays_zero():
    r=client.post('/simulate',json={'days':2,'feed_g_day':0,'initial':{'TAN':0,'NO2':0,'NO3':0},'include_plot':False}).json()
    assert all(row['TAN_N_mg_L']==row['nitrite_N_mg_L']==row['nitrate_N_mg_L']==0 for row in r['rows'])

@pytest.mark.parametrize('data',[{'days':0},{'days':181},{'feed_g_day':15.001},{'feed_g_day':-1},{'temp_C':17.99},{'temp_C':24.01},{'alk_meq':80},{'solids_kg':10},{'initial':{'TAN':-1}},{'ro_scenario':{'feed_L_day':10,'recovery_pct':101}}])
def test_invalid_or_legacy_unsafe_requests_rejected(data):
    assert client.post('/simulate',json=data).status_code==422

def test_nonfinite_rejected():
    assert client.post('/simulate',content='{"feed_g_day":1e999}',headers={'Content-Type':'application/json'}).status_code==422

def test_ro_balance_not_guarantee():
    r=client.post('/simulate',json={'days':1,'include_plot':False,'ro_scenario':{'feed_L_day':20,'recovery_pct':50}}).json()
    assert r['ro']['permeate_L_day']==10 and r['ro']['reject_L_day']==10

def test_power_default_not_safety_pass():
    d=client.post('/power-budget',json={}).json()
    assert d['pilot_peak_W']==1245
    assert d['known_grid_peak_W']==1285
    assert d['continuous_limit_W']==1920
    assert d['status']=='INCOMPLETE'
    assert d['provisional_headroom_W']==635

@pytest.mark.parametrize('data,fail',[
    ({'other_loads_W':0,'electrical_gate_confirmed':True},False),
    ({'other_loads_W':636},True),({'space_heater_W':1500},True),
    ({'tent_fraction':1},True),
    ({'station_charging':True,'wall_charge_W':300,'circuit_amps':15},True),
    ({'station_charging':True,'wall_charge_W':150,'circuit_amps':15,'other_loads_W':0,'electrical_gate_confirmed':True},False)])
def test_power_overloads_and_caps(data,fail):
    d=client.post('/power-budget',json=data).json()
    assert (d['status']=='FAIL')==fail

def test_power_station_branch_no_double_count():
    d=client.post('/power-budget',json={'station_charging':True}).json()
    assert d['known_grid_peak_W']==1506

def test_complete_healthy_readings(healthy):
    d=alarm(**healthy)
    assert d['status']=='NO_THRESHOLD_BREACH' and not d['events']
    assert not d['missing_or_unconfirmed']

def test_missing_data_not_fabricated_healthy():
    assert alarm()['status']=='INCOMPLETE'

def test_protocol_basis_not_guessed(healthy):
    healthy.pop('protocol_nutrient_basis')
    healthy['nitrite_mg_L']=99
    d=alarm(**healthy)
    assert d['status']=='INCOMPLETE' and 'nitrite' not in codes(d)
    assert 'nitrite_mg_L_reporting_basis' in d['missing_or_unconfirmed']

def test_ion_conversion_explicit(healthy):
    healthy.update(nutrient_basis='ion',protocol_nutrient_basis='as_N',nitrite_mg_L=1,nitrate_mg_L=200)
    assert 'nitrite' not in codes(alarm(**healthy))
    assert 'nitrate' not in codes(alarm(**healthy))
    healthy['nitrite_mg_L']=2
    assert 'nitrite' in codes(alarm(**healthy))

@pytest.mark.parametrize('key,value,code,expected',[
    ('pH',6.5,'pH',False),('pH',6.49,'pH',True),('pH',7.5,'pH',False),('pH',7.51,'pH',True),
    ('TAN_mg_L',.999,'TAN',False),('TAN_mg_L',1,'TAN',True),
    ('nitrite_mg_L',.499,'nitrite',False),('nitrite_mg_L',.5,'nitrite',True),
    ('nitrate_mg_L',150,'nitrate',False),('nitrate_mg_L',150.01,'nitrate',True),
    ('KH_mg_L',50,'KH',False),('KH_mg_L',49.9,'KH',True),
    ('DO_mg_L',5.01,'DO',False),('DO_mg_L',5,'DO',True),('DO_mg_L',4,'DO',True),
    ('vermi_temp_F',50,'vermi_temperature',False),('vermi_temp_F',49.9,'vermi_temperature',True),
    ('vermi_temp_F',80,'vermi_temperature',False),('vermi_temp_F',80.1,'vermi_temperature',True),
    ('vermi_moisture_pct',60,'vermi_moisture',False),('vermi_moisture_pct',80,'vermi_moisture',False),
    ('vermi_moisture_pct',59.9,'vermi_moisture',True),('vermi_moisture_pct',80.1,'vermi_moisture',True),
    ('SOC_pct',30,'SOC',True),('SOC_pct',30.1,'SOC',False),('power_ok',False,'power',True)])
def test_exact_alarm_edges(healthy,key,value,code,expected):
    healthy[key]=value
    assert (code in codes(alarm(**healthy)))==expected

@pytest.mark.parametrize('level,severity',[(80,'ALARM'),(70,'CRITICAL'),(69,'CRITICAL')])
def test_level_preserves_core_aeration_and_circulation(healthy,level,severity):
    healthy['water_levels_pct']['sump']=level
    d=alarm(**healthy); e=next(e for e in d['events'] if e['code']=='level:sump')
    assert e['severity']==severity
    assert 'non-critical pumps only' in str(e['actions'])
    assert 'circulation' in str(e['actions']) and 'aeration' in str(e['actions'])
    assert d['control_mode'].startswith('ADVISORY ONLY')

def test_dry_run_requires_manual_confirmation(healthy):
    healthy['circulation_dry_run_risk']=True
    d=alarm(**healthy)
    assert d['status']=='CRITICAL' and 'manual confirmation' in str(d['events'])

@pytest.mark.parametrize('age,missed',[(299,False),(300,True),(301,True)])
def test_heartbeat_exact_deadline(healthy,age,missed):
    healthy['heartbeat_age_seconds']['water']=age
    assert ('heartbeat:water' in codes(alarm(**healthy)))==missed

def test_missing_expected_sensor_is_fail(healthy):
    healthy['expected_sensor_ids'].append('air')
    assert alarm(**healthy)['status']=='FAIL'

@pytest.mark.parametrize('recovery,tds,expect',[(96.5,5.99,set()),(96.49,5.99,{'RO_recovery'}),(96.5,6,{'RO_TDS'})])
def test_ro_protocol_conditional(healthy,recovery,tds,expect):
    healthy.update(ro_active=True,ro_recovery_pct=recovery,ro_TDS_ppm=tds)
    assert codes(alarm(**healthy))==expect
    healthy['ro_active']=False
    assert not codes(alarm(**healthy))

def test_alarm_extra_units_and_invalid_percent_rejected():
    for req in [{'KH_dKH':3},{'SOC_pct':101},{'water_levels_pct':{'sump':-1}},{'heartbeat_age_seconds':{'sensor':-1}}]:
        assert client.post('/alarms',json=req).status_code==422

def test_heartbeat_stub_and_append_only_log():
    assert heartbeat_due(None,0)
    assert not heartbeat_due(0,299)
    assert heartbeat_due(0,300)
    r=read_sensors_sim(); assert r['label']=='SIM'
    payload=heartbeat_payload(r)
    assert payload['interval_seconds']==300 and not payload['network_publish_executed']
    path=ROOT/'artifacts'/'test-sensor-log.csv'
    before=path.read_text().splitlines() if path.exists() else []
    log_reading(r,path);log_reading(r,path)
    lines=path.read_text().splitlines()
    assert len(lines)==len(before)+2+(not bool(before))
    assert lines[:len(before)]==before
    with pytest.raises(ValueError):log_reading(r,ROOT.parent/'not-allowed.csv')

def test_alias_launch_same_api():
    from src.server.app import app as alias
    assert alias is app
