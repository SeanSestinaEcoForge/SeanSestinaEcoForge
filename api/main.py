"""Garage Pilot v2 local-only planning API. Not a hardware controller."""
from typing import Annotated, Literal
import base64
from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from .configuration import load_config, values
from .nutrient_model import run_simulation, plot_png
from .power import power_budget
from .alarms import evaluate
from .advisor import advise, safety_limits
from .telemetry import STORE, StoreFull

C = load_config()
P = values(C['power'])
S, F = values(C['simulation']), values(C['fish'])
Nonnegative = Annotated[float, Field(ge=0)]
Percent = Annotated[float, Field(ge=0, le=100)]

class Request(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)

class InitialN(Request):
    TAN: Annotated[float, Field(ge=0,le=1000)] = values(C['initial'])['TAN']
    NO2: Annotated[float, Field(ge=0,le=1000)] = values(C['initial'])['NO2']
    NO3: Annotated[float, Field(ge=0,le=1000)] = values(C['initial'])['NO3']

class ROScenario(Request):
    """ASSUME operator-entered scenario, no membrane performance default."""
    feed_L_day: Nonnegative
    recovery_pct: Percent

class SimRequest(Request):
    days: Annotated[int, Field(ge=1,le=S['max_days'])] = S['days']
    feed_g_day: Annotated[float, Field(ge=0,le=F['feed_cap_g_day'])] = F['feed_start_g_day']
    temp_C: Annotated[float, Field(ge=18,le=24)] = C['water_temp_C']['value']
    precycled: bool = False
    initial: InitialN = Field(default_factory=InitialN)
    include_plot: bool = True
    ro_scenario: ROScenario | None = None

class PowerRequest(Request):
    circuit_amps: Literal[15,20] = P['amps']
    tent_fraction: Annotated[float, Field(ge=0,le=1)] = P['tent_cap_fraction']
    other_loads_W: Nonnegative | None = None
    space_heater_W: Nonnegative = 0
    station_charging: bool = False
    wall_charge_W: Nonnegative = values(C['solar'])['wall_charge_cap_W']
    electrical_gate_confirmed: bool = False

class AlarmRequest(Request):
    data_label: Literal['MEASURED','SIM','ASSUME'] = 'ASSUME'
    data_source: str = Field(default='Caller-supplied scenario, not independently verified', max_length=500)
    pH: Annotated[float, Field(ge=0,le=14)] | None = None
    TAN_mg_L: Nonnegative | None = None
    nitrite_mg_L: Nonnegative | None = None
    nitrate_mg_L: Nonnegative | None = None
    nutrient_basis: Literal['as_N','ion'] | None = None
    protocol_nutrient_basis: Literal['as_N','ion'] | None = None
    KH_mg_L: Nonnegative | None = None
    DO_mg_L: Nonnegative | None = None
    water_levels_pct: dict[str,Percent] | None = Field(default=None,max_length=100)
    circulation_dry_run_risk: bool = False
    vermi_moisture_pct: Percent | None = None
    vermi_temp_F: Annotated[float, Field(ge=-100,le=200)] | None = None
    SOC_pct: Percent | None = None
    power_ok: bool | None = None
    heartbeat_age_seconds: dict[str,Nonnegative] | None = Field(default=None,max_length=100)
    expected_sensor_ids: list[str] | None = Field(default=None,max_length=100)
    ro_active: bool = False
    ro_recovery_pct: Percent | None = None
    ro_TDS_ppm: Nonnegative | None = None

app = FastAPI(title='EcoForge Family Garage Pilot v2 — planning model',version='2.0.0',
              description='SIM/advisory only. No actuator control. Garage pilot default, not future node.')

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    # Avoid echoing raw private inputs or nonfinite JSON values in validation errors.
    safe_errors = [{k: e[k] for k in ('type', 'loc', 'msg') if k in e} for e in exc.errors()]
    return JSONResponse(status_code=422, content={'detail': safe_errors})

@app.get('/health')
def health():
    return {'status':'ok','profile':'pilot','control_mode':'ADVISORY ONLY'}

@app.get('/config')
def config(profile: Literal['pilot','future-node']='pilot'):
    return load_config(profile)

@app.post('/simulate')
def simulate(req: SimRequest):
    result = run_simulation(load_config(),req.days,req.feed_g_day,req.temp_C,req.precycled,req.initial.model_dump())
    result['ro'] = {'status':'backup_only_not_modeled', 'source':'garage-pilot-v2.md §8/§9',
                    'label':'IDEA', 'note':'Rain makeup primary; RO has no default recovery/purity claim'}
    if req.ro_scenario:
        feed, recovery = req.ro_scenario.feed_L_day, req.ro_scenario.recovery_pct/100
        result['ro'] = {'label':'CALC','source':'ASSUME caller scenario: feed × recovery',
                        'feed_L_day':feed,'permeate_L_day':feed*recovery,'reject_L_day':feed*(1-recovery),
                        'note':'Water balance only; no purity, energy, reuse or recovery guarantee; not auto-connected to loop'}
    if req.include_plot:
        result['plot_base64'] = base64.b64encode(plot_png(result)).decode('ascii')
    return result

@app.post('/power-budget')
def budget(req: PowerRequest):
    return power_budget(load_config(),req)

@app.post('/alarms')
def alarms(req: AlarmRequest):
    return evaluate(load_config(),req)


# --- Sensor heartbeat telemetry (SIM demo path; in-memory only) -------------------------

SensorId = Annotated[str, Field(pattern=r'^[A-Za-z0-9_.-]{1,64}$')]

class TelemetryReading(Request):
    sensor_id: SensorId
    label: Literal['SIM','MEASURED','ASSUME'] = 'SIM'
    source: str = Field(default='Unspecified sender', max_length=200)
    timestamp: str | None = Field(default=None, max_length=40, description='Sender clock, informational only')
    interval_seconds: Annotated[float, Field(ge=0.1, le=3600)] = values(C['alarms'])['heartbeat_seconds']
    pH: Annotated[float, Field(ge=0,le=14)] | None = None
    temp_C: Annotated[float, Field(ge=-10,le=50)] | None = None
    DO_mg_L: Annotated[float, Field(ge=0,le=30)] | None = None
    TAN_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    nitrite_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    nitrate_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    KH_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    flow_L_h: Annotated[float, Field(ge=0,le=100000)] | None = None
    water_levels_pct: dict[SensorId, Percent] | None = Field(default=None, max_length=20)

@app.post('/telemetry', status_code=201)
def telemetry_ingest(reading: TelemetryReading):
    try:
        record = STORE.add(reading.model_dump(exclude_none=True))
    except StoreFull as exc:
        raise HTTPException(status_code=507, detail=str(exc))
    return {'accepted': True, 'sensor_id': record['sensor_id'], 'label': record['label'],
            'received_at_unix': record['received_at_unix'],
            'note': 'Stored in process memory only; no actuation, forwarding or disk write'}

@app.get('/telemetry/latest')
def telemetry_latest():
    return STORE.latest()

@app.get('/telemetry/history')
def telemetry_history(sensor_id: SensorId | None = None, limit: Annotated[int, Query(ge=1, le=500)] = 100):
    rows = STORE.history(sensor_id, limit)
    return {'label': 'SIM' if all(r.get('label') == 'SIM' for r in rows) else 'MIXED',
            'count': len(rows), 'rows': rows}

STATE_FIELDS = ('pH','temp_C','DO_mg_L','TAN_mg_L','nitrite_mg_L','nitrate_mg_L','KH_mg_L')

def state_from_telemetry():
    """Most recent value of each field across sensors; unknown fields stay absent."""
    latest = STORE.latest()
    sensors = sorted(latest['sensors'].values(), key=lambda r: r['received_at_unix'])
    state, levels, labels = {}, {}, set()
    for r in sensors:
        labels.add(r.get('label'))
        for k in STATE_FIELDS:
            if k in r: state[k] = r[k]
        levels.update(r.get('water_levels_pct') or {})
    if levels: state['water_levels_pct'] = levels
    state['heartbeat_stale'] = latest['any_stale'] if sensors else None
    state['data_label'] = labels.pop() if len(labels) == 1 else ('MIXED' if labels else 'NONE')
    return state

# --- Grok advisor demo (suggests only; never actuates) ----------------------------------

class AdvisorState(Request):
    data_label: Literal['MEASURED','SIM','ASSUME','MIXED','NONE'] = 'ASSUME'
    pH: Annotated[float, Field(ge=0,le=14)] | None = None
    temp_C: Annotated[float, Field(ge=-10,le=50)] | None = None
    DO_mg_L: Annotated[float, Field(ge=0,le=30)] | None = None
    TAN_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    nitrite_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    nitrate_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    KH_mg_L: Annotated[float, Field(ge=0,le=1000)] | None = None
    water_levels_pct: dict[SensorId, Percent] | None = Field(default=None, max_length=20)
    feed_g_day: Annotated[float, Field(ge=0,le=100)] | None = None
    heartbeat_stale: bool | None = None

class AdvisorRequest(Request):
    mode: Literal['mock','live'] = 'mock'
    model: str | None = Field(default=None, max_length=80, pattern=r'^[A-Za-z0-9_.:-]+$')
    state: AdvisorState | None = None
    use_latest_telemetry: bool = False
    feed_g_day: Annotated[float, Field(ge=0,le=100)] | None = Field(
        default=None, description='Current feed rate; used with use_latest_telemetry (telemetry has no feed channel)')
    include_safety_demo: bool = False

@app.post('/advisor/suggest')
def advisor_suggest(req: AdvisorRequest):
    if req.use_latest_telemetry:
        state = state_from_telemetry()
        if req.state:  # explicit values override telemetry
            state.update(req.state.model_dump(exclude_none=True, exclude={'data_label'}))
    else:
        state = (req.state or AdvisorState()).model_dump(exclude_none=True)
    if req.feed_g_day is not None:
        state['feed_g_day'] = req.feed_g_day
    return advise(state, mode=req.mode, model=req.model, include_safety_demo=req.include_safety_demo)

@app.get('/advisor/limits')
def advisor_limits():
    return safety_limits()
