"""Advisor demo: safety-layer clamping/blocking, deterministic MOCK mode, LIVE fallback (no network)."""
import json
import logging
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.advisor import advise
from api.advisor.safety import check, limits
from api.telemetry import STORE

client = TestClient(app)
LIM = limits()
CAP = LIM['feed_cap_g_day']['value']
STEP = LIM['feed_ramp_g_week']['value']
LO, HI = LIM['temp_range_C']['value']

@pytest.fixture
def ok_state():
    return dict(pH=7.0, temp_C=21.0, DO_mg_L=6.5, TAN_mg_L=0.1, nitrite_mg_L=0.05, KH_mg_L=80,
                water_levels_pct={'fish_tank': 95, 'sump': 90}, feed_g_day=5.0, heartbeat_stale=False)

@pytest.fixture(autouse=True)
def no_key(monkeypatch):
    monkeypatch.delenv('XAI_API_KEY', raising=False)
    STORE.clear()

def test_limits_come_from_pilot_config_with_labels():
    assert CAP == 15 and STEP == 2 and (LO, HI) == (18, 24)
    for k in ('feed_cap_g_day', 'DO_critical_mg_L', 'temp_range_C'):
        assert LIM[k]['label'] in {'QUOTED', 'ASSUME'} and LIM[k]['source']
    assert client.get('/advisor/limits').json()['feed_cap_g_day']['value'] == CAP

def test_feed_above_cap_and_ramp_is_clamped(ok_state):
    r = check({'action': 'feed_rate', 'value': 40}, ok_state, LIM)
    assert r['safety_status'] == 'CLAMPED' and r['final_value'] == ok_state['feed_g_day'] + STEP
    assert r['executed'] is False and r['requires_human_confirmation'] is True
    ok_state['feed_g_day'] = 14.5
    assert check({'action': 'feed_rate', 'value': 40}, ok_state, LIM)['final_value'] == CAP

@pytest.mark.parametrize('change', [dict(DO_mg_L=5.0), dict(DO_mg_L=None), dict(TAN_mg_L=1.0),
                                    dict(nitrite_mg_L=0.5), dict(heartbeat_stale=True), dict(heartbeat_stale=None)])
def test_feed_increase_blocked_when_unsafe_or_unknown(ok_state, change):
    ok_state.update(change)
    r = check({'action': 'feed_rate', 'value': 6}, ok_state, LIM)
    assert r['safety_status'] == 'BLOCKED' and r['final_value'] == ok_state['feed_g_day']

def test_feed_decrease_and_pause_always_allowed(ok_state):
    ok_state.update(DO_mg_L=3, TAN_mg_L=4)
    assert check({'action': 'feed_rate', 'value': 0}, ok_state, LIM)['safety_status'] == 'ALLOWED'
    assert check({'action': 'feed_rate', 'value': -3}, ok_state, LIM)['final_value'] == 0
    assert check({'action': 'feed_rate', 'value': 0}, {}, LIM)['safety_status'] == 'ALLOWED'
    assert check({'action': 'feed_rate', 'value': 4}, {}, LIM)['safety_status'] == 'BLOCKED'  # current unknown

@pytest.mark.parametrize('suggestion,final', [
    ({'action': 'aeration', 'value': 'off'}, 'keep_on'),
    ({'action': 'circulation', 'value': 'stop'}, 'keep_on'),
    ({'action': 'dose', 'value': 'sodium bicarbonate 50 g'}, None),
    ({'action': 'open_valve', 'value': 1}, None),
    ({'action': 'feed_rate', 'value': float('nan')}, 5.0),
    ({'action': 'feed_rate', 'value': '10'}, 5.0),
    ({'action': 'water_temp_setpoint', 'value': 'hot'}, None),
    ({'action': 'manual_test', 'value': {'x': 1}}, None),
])
def test_unsafe_or_malformed_suggestions_blocked(ok_state, suggestion, final, caplog):
    with caplog.at_level(logging.WARNING, logger='ecoforge.advisor.safety'):
        r = check(suggestion, ok_state, LIM)
    assert r['safety_status'] == 'BLOCKED' and r['final_value'] == final and r['safety_reasons']
    assert 'BLOCKED' in caplog.text  # every block is logged with its reason

def test_temperature_clamped_to_pilot_range(ok_state):
    assert check({'action': 'water_temp_setpoint', 'value': 30}, ok_state, LIM)['final_value'] == HI
    assert check({'action': 'water_temp_setpoint', 'value': 10}, ok_state, LIM)['final_value'] == LO
    assert check({'action': 'water_temp_setpoint', 'value': 21}, ok_state, LIM)['safety_status'] == 'ALLOWED'

def test_long_manual_text_truncated(ok_state):
    r = check({'action': 'manual_review', 'value': 'x' * 1000}, ok_state, LIM)
    assert r['safety_status'] == 'CLAMPED' and len(r['final_value']) == 300

def test_mock_is_default_deterministic_and_labeled(ok_state):
    a = client.post('/advisor/suggest', json={'state': ok_state}).json()
    b = client.post('/advisor/suggest', json={'state': ok_state}).json()
    assert a == b and a['label'] == 'MOCK' and a['mode_used'] == 'mock' and a['executed'] is False
    assert all(s['executed'] is False for s in a['suggestions'])
    feed = [s for s in a['suggestions'] if s['action'] == 'feed_rate']
    assert feed and feed[0]['final_value'] == 5.0  # no auto-ramp: hold

def test_mock_low_do_triggers_aeration_and_feed_pause(ok_state):
    ok_state['DO_mg_L'] = 3.8
    r = advise(ok_state)
    acts = {(s['action'], s['final_value'], s['safety_status']) for s in r['suggestions']}
    assert ('aeration', 'backup_on', 'ALLOWED') in acts and ('feed_rate', 0, 'ALLOWED') in acts

def test_mock_unknown_values_are_not_healthy():
    r = advise({})
    tests = [s['final_value'] for s in r['suggestions'] if s['action'] == 'manual_test']
    assert any('dissolved oxygen' in t for t in tests) and any('TAN' in t for t in tests)

def test_mock_suggestions_never_need_clamping_in_mock_rules(ok_state):
    for change in [{}, dict(DO_mg_L=3), dict(pH=6.0, KH_mg_L=30), dict(temp_C=27), dict(water_levels_pct={'sump': 65})]:
        st = dict(ok_state, **change)
        assert all(s['safety_status'] == 'ALLOWED' for s in advise(st)['suggestions'])

def test_safety_demo_shows_blocked_and_clamped(ok_state):
    r = client.post('/advisor/suggest', json={'state': ok_state, 'include_safety_demo': True}).json()
    assert r['safety_counts']['BLOCKED'] >= 3 and r['safety_counts']['CLAMPED'] >= 2

def test_live_without_key_falls_back_to_mock(ok_state):
    r = client.post('/advisor/suggest', json={'mode': 'live', 'state': ok_state}).json()
    assert r['mode_used'] == 'mock' and r['label'] == 'MOCK' and 'XAI_API_KEY' in r['notice']

def test_live_output_goes_through_safety_layer(ok_state, monkeypatch):
    monkeypatch.setenv('XAI_API_KEY', 'test-placeholder')
    sent = {}
    def fake_post(url, body, key):
        sent.update(url=url, model=body['model'])
        reply = {'suggestions': [{'action': 'feed_rate', 'value': 50, 'reason': 'grow faster'},
                                 {'action': 'aeration', 'value': 'off', 'reason': 'save power'}]}
        return {'output': [{'type': 'reasoning'}, {'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(reply)}]}]}
    r = advise(ok_state, mode='live', model='grok-test', post=fake_post)
    assert sent == {'url': 'https://api.x.ai/v1/responses', 'model': 'grok-test'}
    assert r['label'] == 'LIVE' and r['model'] == 'grok-test'
    by = {s['action']: s for s in r['suggestions']}
    assert by['feed_rate']['safety_status'] == 'CLAMPED' and by['feed_rate']['final_value'] == 5.0 + STEP
    assert by['aeration']['safety_status'] == 'BLOCKED'
    assert 'test-placeholder' not in json.dumps(r)

def test_live_bad_reply_or_error_falls_back(ok_state, monkeypatch):
    monkeypatch.setenv('XAI_API_KEY', 'test-placeholder')
    r = advise(ok_state, mode='live', post=lambda *a: {'output_text': 'no json here'})
    assert r['mode_used'] == 'mock' and 'expected JSON' in r['notice']
    def boom(*a):
        raise OSError('network down')
    r = advise(ok_state, mode='live', post=boom)
    assert r['mode_used'] == 'mock' and 'OSError' in r['notice'] and 'test-placeholder' not in json.dumps(r)

def test_advisor_uses_latest_telemetry():
    client.post('/telemetry', json={'sensor_id': 'water', 'pH': 7.0, 'DO_mg_L': 3.9, 'temp_C': 21})
    r = client.post('/advisor/suggest', json={'use_latest_telemetry': True, 'feed_g_day': 5}).json()
    assert r['state_used']['DO_mg_L'] == 3.9 and r['state_used']['data_label'] == 'SIM'
    assert any(s['action'] == 'aeration' for s in r['suggestions'])

def test_advisor_request_validation():
    assert client.post('/advisor/suggest', json={'mode': 'actuate'}).status_code == 422
    assert client.post('/advisor/suggest', json={'state': {'pH': 20}}).status_code == 422
    assert client.post('/advisor/suggest', json={'model': 'bad model; rm'}).status_code == 422
