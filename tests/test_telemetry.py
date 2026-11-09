"""Heartbeat ingest, validation, stale detection, fake sensor and MQTT mapping (no network)."""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.telemetry import STORE, TelemetryStore
from tools.fake_sensor import FakeSensor, run
from tools.mqtt_bridge import to_reading

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean():
    STORE.clear()

def test_ingest_and_latest():
    r = client.post('/telemetry', json={'sensor_id': 'water-1', 'pH': 7.1, 'DO_mg_L': 6.2, 'interval_seconds': 300})
    assert r.status_code == 201 and r.json()['label'] == 'SIM'
    latest = client.get('/telemetry/latest').json()
    s = latest['sensors']['water-1']
    assert s['pH'] == 7.1 and s['heartbeat_status'] == 'OK' and s['stale'] is False and latest['label'] == 'SIM'

@pytest.mark.parametrize('bad', [{'pH': 7}, {'sensor_id': 'a b'}, {'sensor_id': 'x', 'pH': 15},
                                 {'sensor_id': 'x', 'DO_mg_L': -1}, {'sensor_id': 'x', 'interval_seconds': 0},
                                 {'sensor_id': 'x', 'label': 'GUESS'}, {'sensor_id': 'x', 'valve': 'open'},
                                 {'sensor_id': 'x', 'water_levels_pct': {'sump': 120}}])
def test_ingest_validation(bad):
    assert client.post('/telemetry', json=bad).status_code == 422

@pytest.mark.parametrize('age,status,stale', [(0, 'OK', False), (300, 'OK', False), (301, 'LATE', False),
                                              (600, 'LATE', False), (601, 'STALE', True)])
def test_stale_after_more_than_two_missed_intervals(age, status, stale):
    now = [1000.0]
    store = TelemetryStore(clock=lambda: now[0])
    store.add({'sensor_id': 's', 'label': 'SIM', 'interval_seconds': 300})
    now[0] += age
    s = store.latest()['sensors']['s']
    assert (s['heartbeat_status'], s['stale']) == (status, stale)
    assert store.latest()['any_stale'] is stale

def test_history_filter_and_limit():
    for i in range(5):
        client.post('/telemetry', json={'sensor_id': 'a' if i % 2 else 'b', 'pH': 7 + i / 10})
    assert client.get('/telemetry/history?sensor_id=a').json()['count'] == 2
    assert client.get('/telemetry/history?limit=3').json()['count'] == 3
    assert client.get('/telemetry/history?limit=0').status_code == 422

def test_fake_sensor_posts_sim_readings_deterministically():
    posted = []
    def post(payload):
        resp = client.post('/telemetry', json=payload)
        posted.append(payload)
        return resp.status_code, resp.json()
    sent = run(FakeSensor(seed=1, interval=2), post, count=3, interval=2, sleep=lambda s: None, out=lambda m: None)
    assert sent == 3 and all(p['label'] == 'SIM' and 'NOT hardware' in p['source'] for p in posted)
    again = [FakeSensor(seed=1).read()['pH'] for _ in range(1)]
    assert again[0] == posted[0]['pH']
    assert client.get('/telemetry/latest').json()['sensors']['pilot-fake-01']['interval_seconds'] == 2

def test_fake_sensor_do_drop_scenario_declines():
    s = FakeSensor(seed=3, scenario='do-drop')
    first = s.read()['DO_mg_L']
    for _ in range(20):
        last = s.read()['DO_mg_L']
    assert last < first - 1

def test_fake_sensor_default_interval_is_protocol_heartbeat():
    assert FakeSensor().interval == 300

def test_fake_sensor_stops_on_rejected_reading_and_counts_attempts():
    from urllib.error import HTTPError
    def rejected(payload):
        raise HTTPError('http://x/telemetry', 422, 'Unprocessable', {}, None)
    with pytest.raises(SystemExit):
        run(FakeSensor(), rejected, count=0, interval=0, sleep=lambda s: None, out=lambda m: None)
    def down(payload):
        raise OSError('connection refused')
    msgs = []
    assert run(FakeSensor(), down, count=3, interval=0, sleep=lambda s: None, out=msgs.append) == 0
    assert len(msgs) == 3  # terminates after --count attempts even when the API is down

def test_mqtt_topic_mapping():
    r = to_reading('ecoforge/pilot/tank-a/telemetry', b'{"pH": 7.0}')
    assert r['sensor_id'] == 'tank-a' and r['label'] == 'SIM'
    assert client.post('/telemetry', json=r).status_code == 201
    with pytest.raises(ValueError):
        to_reading('other/topic', b'{}')
