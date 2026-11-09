"""Reproducible loopback HTTP smoke test; starts and stops its own local server.
Writes only under artifacts/ (git-ignored). Does not use GitHub, a broker or any external API.
"""
import base64
import csv
from datetime import datetime
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts'

def main():
    OUT.mkdir(exist_ok=True)
    # Select an unused loopback port (ASSUME local smoke-test routing only).
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    url=f'http://127.0.0.1:{port}'
    report={'timestamp_ET':datetime.now(ZoneInfo('America/New_York')).isoformat(),
            'label':'MEASURED','source':'Loopback HTTP test on this computer; not physical system validation','checks':[]}
    def hit(method,path,payload=None):
        data=json.dumps(payload).encode() if payload is not None else None
        req=Request(url+path,data=data,method=method,headers={'Content-Type':'application/json'})
        with urlopen(req,timeout=30) as r:
            result=json.loads(r.read())
            report['checks'].append({'method':method,'path':path,'HTTP_status':r.status})
            return result
    with (OUT/'uvicorn-smoke.log').open('w') as log:
        proc=subprocess.Popen([sys.executable,'-m','uvicorn','api.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,stdout=log,stderr=log)
        try:
            for _ in range(100):
                if proc.poll() is not None:raise RuntimeError('Local server exited; inspect uvicorn-smoke.log')
                try:
                    with urlopen(url+'/health',timeout=.5) as r:
                        if r.status==200:break
                except (URLError,TimeoutError):time.sleep(.1)
            else:raise RuntimeError('Local server not ready in smoke-test timeout')
            assert hit('GET','/health')['status']=='ok'
            c=hit('GET','/config'); assert c['fish']['count']['value']==10
            assert hit('GET','/config?profile=future-node')['runnable'] is False
            result=hit('POST','/simulate',{})
            png=base64.b64decode(result.pop('plot_base64'))
            assert png.startswith(b'\x89PNG')
            (OUT/'pilot-v2-sample.png').write_bytes(png)
            (OUT/'pilot-v2-sample.json').write_text(json.dumps(result,indent=2)+'\n')
            with (OUT/'pilot-v2-sample.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
            power=hit('POST','/power-budget',{})
            assert power['known_grid_peak_W']==1285 and power['status']=='INCOMPLETE'
            (OUT/'power-budget-sample.json').write_text(json.dumps(power,indent=2)+'\n')
            alarm=hit('POST','/alarms',{'DO_mg_L':4,'water_levels_pct':{'sump':70},'heartbeat_age_seconds':{'water':300},'expected_sensor_ids':['water','air']})
            assert alarm['status']=='CRITICAL'
            assert any(e['code']=='heartbeat:air' for e in alarm['events'])
            assert 'core circulation' in str(alarm)
            (OUT/'alarms-sample.json').write_text(json.dumps(alarm,indent=2)+'\n')
            # Heartbeat path: run the fake SIM sensor briefly against this server.
            subprocess.run([sys.executable,'tools/fake_sensor.py','--url',url,'--interval','0.2','--count','3'],
                           cwd=ROOT,check=True,timeout=60,stdout=subprocess.DEVNULL)
            latest=hit('GET','/telemetry/latest')
            assert latest['sensors']['pilot-fake-01']['heartbeat_status']=='OK' and latest['label']=='SIM'
            assert hit('GET','/telemetry/history?limit=10')['count']==3
            advice=hit('POST','/advisor/suggest',{'use_latest_telemetry':True,'feed_g_day':5,'include_safety_demo':True})
            assert advice['label']=='MOCK' and advice['executed'] is False and advice['safety_counts']['BLOCKED']>=3
            (OUT/'advisor-sample.json').write_text(json.dumps(advice,indent=2)+'\n')
            assert hit('GET','/advisor/limits')['feed_cap_g_day']['value']==15
            with urlopen(url+'/dashboard',timeout=30) as r:
                assert r.status==200 and b'SIMULATION' in r.read()
                report['checks'].append({'method':'GET','path':'/dashboard','HTTP_status':r.status})
            spec=hit('GET','/openapi.json');assert '/power-budget' in spec['paths'] and '/advisor/suggest' in spec['paths']
            report['sample']={'label':'SIM','days':result['inputs']['days'], 'mass_balance_residual_g_N':result['mass_balance']['residual_g'],
                              'final':result['rows'][-1]}
            report['outcome']='ALL HTTP CHECKS PASSED; server stopped after verification'
        finally:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
            report['server_returncode']=proc.returncode
            (OUT/'http-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
