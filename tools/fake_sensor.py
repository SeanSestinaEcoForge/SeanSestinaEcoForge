"""Fake heartbeat sensor: posts SIM readings to the pilot API's POST /telemetry.

Every reading is labeled SIM. Values are a seeded random walk around the ASSUME synthetic
fixture in configs/pilot-v2.json (sensor_stub_fixture) — NOT hardware, NOT measured.
Default interval is the QUOTED 300 s protocol heartbeat; use --interval/--count for fast demos.

    python tools/fake_sensor.py                                  # one reading every 300 s until Ctrl-C
    python tools/fake_sensor.py --interval 1 --count 20          # quick demo
    python tools/fake_sensor.py --interval 1 --scenario do-drop  # DO drifts down so the advisor reacts

Talks only to the --url you give it (default: loopback). Never touches hardware.
"""
import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.configuration import load_config, values  # noqa: E402

FIXTURE = values(load_config()['sensor_stub_fixture'])
HEARTBEAT_S = values(load_config()['alarms'])['heartbeat_seconds']
SOURCE = 'tools/fake_sensor.py seeded random walk around ASSUME fixture; NOT hardware'


class FakeSensor:
    def __init__(self, sensor_id='pilot-fake-01', seed=7, scenario='steady', interval=HEARTBEAT_S):
        self.sensor_id, self.scenario, self.interval = sensor_id, scenario, interval
        self.rng = random.Random(seed)
        self.pH, self.DO, self.temp = FIXTURE['pH'], FIXTURE['DO_mg_L'], FIXTURE['temp_C']
        self.flow = FIXTURE['flow_L_h']
        self.n = 0

    def read(self):
        r = self.rng
        self.pH = min(8.0, max(6.0, self.pH + r.uniform(-0.04, 0.04)))
        drift = -0.12 if self.scenario == 'do-drop' else 0.0
        self.DO = min(9.0, max(3.0, self.DO + drift + r.uniform(-0.08, 0.08)))
        self.temp = min(26.0, max(16.0, self.temp + r.uniform(-0.1, 0.1)))
        self.flow = max(0.0, self.flow + r.uniform(-5, 5))
        self.n += 1
        return {'sensor_id': self.sensor_id, 'label': 'SIM', 'source': SOURCE,
                'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'interval_seconds': self.interval, 'pH': round(self.pH, 2), 'DO_mg_L': round(self.DO, 2),
                'temp_C': round(self.temp, 2), 'flow_L_h': round(self.flow, 1),
                'water_levels_pct': {'fish_tank': round(95 + r.uniform(-1, 1), 1), 'sump': round(90 + r.uniform(-1, 1), 1)}}


def http_post(url):
    def post(payload):
        req = Request(url.rstrip('/') + '/telemetry', data=json.dumps(payload).encode(), method='POST',
                      headers={'Content-Type': 'application/json'})
        with urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    return post


def run(sensor, post, count=0, interval=HEARTBEAT_S, sleep=time.sleep, out=print):
    """Send readings; count=0 means until interrupted. Returns the number accepted (HTTP 201).

    A rejected reading (HTTP 4xx) stops the run: bad data will not fix itself by retrying.
    Connection errors are reported and the next interval is tried, like a real heartbeat.
    """
    sent = attempts = 0
    while count == 0 or attempts < count:
        reading = sensor.read()
        attempts += 1
        try:
            status, _ = post(reading)
        except HTTPError as exc:
            if 400 <= exc.code < 500:
                raise SystemExit(f'API rejected the reading (HTTP {exc.code}): {exc.read()[:300]!r}')
            out(f'post failed (HTTP {exc.code}); will retry next interval')
            status = None
        except (URLError, OSError) as exc:
            out(f'post failed ({exc}); will retry next interval')
            status = None
        if status == 201:
            sent += 1
            out(json.dumps({'posted': sent, 'label': 'SIM', 'pH': reading['pH'], 'DO_mg_L': reading['DO_mg_L'],
                            'temp_C': reading['temp_C']}))
        if count and attempts >= count:
            break
        sleep(interval)
    return sent


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--url', default='http://127.0.0.1:8000', help='API base URL (default loopback)')
    p.add_argument('--interval', type=float, default=HEARTBEAT_S, help=f'seconds between readings (default {HEARTBEAT_S:g}, QUOTED protocol heartbeat)')
    p.add_argument('--count', type=int, default=0, help='readings to send, then exit (default 0 = until Ctrl-C)')
    p.add_argument('--sensor-id', default='pilot-fake-01')
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--scenario', choices=['steady', 'do-drop'], default='steady')
    a = p.parse_args(argv)
    if not 0.1 <= a.interval <= 3600:
        p.error('interval must be 0.1..3600 seconds')
    if a.count < 0:
        p.error('count must be >= 0')
    sensor = FakeSensor(a.sensor_id, a.seed, a.scenario, a.interval)
    print(f'Fake SIM sensor {a.sensor_id} → {a.url}/telemetry every {a.interval:g} s '
          f'({"until Ctrl-C" if a.count == 0 else f"{a.count} readings"}); not hardware', flush=True)
    try:
        sent = run(sensor, http_post(a.url), a.count, a.interval)
    except KeyboardInterrupt:
        print('stopped')
        return 0
    if a.count and sent < a.count:
        print(f'{a.count - sent} of {a.count} readings were not accepted', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
