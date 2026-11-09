"""Dashboard page: served by the API, offline (no external assets), SIM banner."""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_dashboard_served_offline_with_banner():
    r = client.get('/dashboard')
    assert r.status_code == 200 and 'SIMULATION — NOT MEASURED DATA' in r.text
    assert 'http://' not in r.text and 'https://' not in r.text  # no external assets
    assert 'executed' in r.text and '/advisor/suggest' in r.text and '/telemetry/latest' in r.text
