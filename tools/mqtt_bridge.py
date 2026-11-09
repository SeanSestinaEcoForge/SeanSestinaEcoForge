"""Optional MQTT → API bridge example (not required for tests or CI).

Subscribes to ecoforge/pilot/<sensor_id>/telemetry and forwards each JSON payload to the
API's POST /telemetry, so MQTT sensors use the same validated ingest as tools/fake_sensor.py.

    pip install -r requirements-mqtt.txt
    python tools/mqtt_bridge.py --broker 127.0.0.1 --api http://127.0.0.1:8000

Read-only toward devices: it never publishes commands. Use a local/private broker only.
"""
import argparse
import json
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

TOPIC = 'ecoforge/pilot/+/telemetry'


def to_reading(topic, payload_bytes):
    """Map an MQTT message to a /telemetry body. sensor_id comes from the topic."""
    parts = topic.split('/')
    if len(parts) != 4 or parts[:2] != ['ecoforge', 'pilot'] or parts[3] != 'telemetry':
        raise ValueError(f'unexpected topic {topic!r}')
    body = json.loads(payload_bytes)
    if not isinstance(body, dict):
        raise ValueError('payload must be a JSON object')
    body['sensor_id'] = parts[2]
    body.setdefault('label', 'SIM')
    body.setdefault('source', f'MQTT {topic} via tools/mqtt_bridge.py')
    return body


def forward(api, reading):
    req = Request(api.rstrip('/') + '/telemetry', data=json.dumps(reading).encode(), method='POST',
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=10) as r:
        return r.status


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--broker', default='127.0.0.1')
    p.add_argument('--port', type=int, default=1883)
    p.add_argument('--api', default='http://127.0.0.1:8000')
    a = p.parse_args(argv)
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print('paho-mqtt is not installed (optional). Run: pip install -r requirements-mqtt.txt', file=sys.stderr)
        return 2

    def on_message(_client, _userdata, msg):
        try:
            print(msg.topic, '->', forward(a.api, to_reading(msg.topic, msg.payload)))
        except (ValueError, URLError, OSError) as exc:
            print(msg.topic, 'rejected:', exc)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(a.broker, a.port)
    client.subscribe(TOPIC)
    print(f'Bridging {TOPIC} on {a.broker}:{a.port} → {a.api}/telemetry (Ctrl-C to stop)')
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
