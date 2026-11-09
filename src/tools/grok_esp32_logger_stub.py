"""SIM-only ESP32/MQTT payload and append-only logger stub; no network I/O.
Run: python -m src.tools.grok_esp32_logger_stub --cycles 3 --interval 0
Always terminates: default is one reading. Writes artifacts/sensor-stub.csv (git-ignored).
Heartbeat every 300 seconds (QUOTED protocol v1.2). No brokers or controls.
"""
import argparse
import csv
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from api.configuration import ROOT, load_config, values
from api.main import AlarmRequest
from api.alarms import evaluate

HEARTBEAT_SECONDS = values(load_config()['alarms'])['heartbeat_seconds']
LOG_FILE = ROOT / 'artifacts' / 'sensor-stub.csv'
SENSOR_ID = 'pilot-esp32-sim'

def read_sensors_sim():
    # ASSUME synthetic fixture, NOT an instrument sample. Unknown channels stay missing.
    return {'timestamp':datetime.now(ZoneInfo('America/New_York')).isoformat(),
            'label':'SIM','source':'ASSUME synthetic demo fixture, not hardware',
            'sensor_id':SENSOR_ID,**values(load_config()['sensor_stub_fixture']),'ro_active':False}

def heartbeat_payload(reading):
    return {'topic':f"ecoforge/pilot/{reading['sensor_id']}/heartbeat",
            'interval_seconds':HEARTBEAT_SECONDS,'label':'SIM',
            'source':'measurement-protocol-v1.md v1.2 §3; fake ESP32 fixture',
            'payload':{'sensor_id':reading['sensor_id'],'timestamp':reading['timestamp'],
                       'label':'SIM','alive':True},'network_publish_executed':False}

def heartbeat_due(last_sent_monotonic, now_monotonic):
    return last_sent_monotonic is None or now_monotonic-last_sent_monotonic >= HEARTBEAT_SECONDS

def log_reading(data, path=LOG_FILE):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Logs must remain inside the local app copy')
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open('a',newline='') as fh:
        w = csv.DictWriter(fh,fieldnames=list(data))
        if not exists:w.writeheader()
        w.writerow(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cycles',type=int,default=1,help='number of readings, then exit (default 1)')
    parser.add_argument('--interval',type=float,default=HEARTBEAT_SECONDS,
                        help='seconds between readings (default: QUOTED 300 s protocol heartbeat; use 0 for a quick demo)')
    args=parser.parse_args()
    if not 1 <= args.cycles <= 100:parser.error('cycles must be 1..100 (ASSUME local demo bound)')
    if not 0 <= args.interval <= 3600:parser.error('interval must be 0..3600 seconds')
    for i in range(args.cycles):
        reading=read_sensors_sim(); log_reading(reading)
        print(json.dumps(heartbeat_payload(reading)))
        req=AlarmRequest(data_label='SIM',data_source=reading['source'],pH=reading['pH'],DO_mg_L=reading['DO_mg_L'],
                         heartbeat_age_seconds={SENSOR_ID:0},expected_sensor_ids=[SENSOR_ID])
        print(json.dumps({'alarm_status':evaluate(load_config(),req)['status'],
                          'note':'Unmeasured channels remain INCOMPLETE, not nominal'}))
        if i+1 < args.cycles:time.sleep(args.interval)

if __name__=='__main__':main()
