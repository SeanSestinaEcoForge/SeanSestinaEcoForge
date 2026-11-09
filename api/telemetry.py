"""In-memory sensor telemetry store with heartbeat staleness checks.

SIM/demo plumbing for the 5-minute heartbeat path (QUOTED 300 s, measurement protocol v1.2).
Readings are kept in process memory only: nothing is written to disk, nothing is
forwarded anywhere, and a server restart clears everything. Advisory only, no actuation.
"""
from collections import deque
from threading import Lock
import time

MAX_SENSORS = 50            # ASSUME local demo resource bound
MAX_READINGS_PER_SENSOR = 500  # ASSUME local demo resource bound
STALE_AFTER_INTERVALS = 2   # flag a sensor STALE once more than 2 expected beats are missing


class StoreFull(Exception):
    """Raised when a new sensor would exceed the demo sensor limit."""


class TelemetryStore:
    def __init__(self, clock=time.time):
        self._clock = clock
        self._lock = Lock()
        self._readings = {}

    def clear(self):
        with self._lock:
            self._readings.clear()

    def add(self, reading: dict) -> dict:
        sensor = reading['sensor_id']
        with self._lock:
            if sensor not in self._readings and len(self._readings) >= MAX_SENSORS:
                raise StoreFull(f'Demo store holds at most {MAX_SENSORS} sensors')
            record = {**reading, 'received_at_unix': self._clock()}
            self._readings.setdefault(sensor, deque(maxlen=MAX_READINGS_PER_SENSOR)).append(record)
            return record

    def _status(self, record, now):
        interval = record['interval_seconds']
        age = max(0.0, now - record['received_at_unix'])
        missed = int(age // interval)
        if age > STALE_AFTER_INTERVALS * interval:
            status = 'STALE'
        elif age > interval:
            status = 'LATE'
        else:
            status = 'OK'
        return {'age_seconds': round(age, 1), 'missed_intervals': missed,
                'stale': status == 'STALE', 'heartbeat_status': status}

    def latest(self) -> dict:
        now = self._clock()
        with self._lock:
            sensors = {sid: {**rows[-1], **self._status(rows[-1], now)}
                       for sid, rows in self._readings.items() if rows}
        return {'label': 'SIM' if all(s.get('label') == 'SIM' for s in sensors.values()) else 'MIXED',
                'source': 'In-memory telemetry received by this API process; labels are as submitted by each sensor',
                'stale_rule': f'STALE when more than {STALE_AFTER_INTERVALS} expected intervals pass without a reading; '
                              'LATE after one missed interval (protocol v1.2 treats one missed critical beat as FAIL)',
                'sensor_count': len(sensors), 'any_stale': any(s['stale'] for s in sensors.values()),
                'sensors': sensors}

    def history(self, sensor_id=None, limit=100) -> list:
        with self._lock:
            if sensor_id is not None:
                rows = list(self._readings.get(sensor_id, []))
            else:
                rows = sorted((r for d in self._readings.values() for r in d),
                              key=lambda r: r['received_at_unix'])
        return rows[-limit:]


STORE = TelemetryStore()
