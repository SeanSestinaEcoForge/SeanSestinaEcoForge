# Family garage pilot — planning simulator API

A small, **tested** FastAPI app for the family garage pilot (fish → solids → worms → plants, goldfish first).
It is a planning and teaching tool: **SIM and advisory only, no hardware control.**

## Run it (from the repository root)

```bash
pip install -r requirements-dev.txt
python -m pytest -q                                   # 127 tests
python tools/smoke_local.py                           # starts a loopback server, calls every endpoint, stops it
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the interactive API. Stop with Ctrl-C.
Never bind this unauthenticated prototype to the public internet.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/config` | Pilot parameters, each with value, unit, label and source |
| GET | `/config?profile=future-node` | Historical future-node targets, all **IDEA**, not runnable |
| POST | `/simulate` | Dissolved-nitrogen ODE (TAN → nitrite → nitrate → plant uptake), optional PNG |
| POST | `/power-budget` | Circuit arithmetic, caps and missing-load warnings |
| POST | `/alarms` | Measurement-protocol v1.2 threshold rules, advisory only |
| GET | `/health` | Software health — **not** fish-system health |
| POST | `/telemetry` | Ingest one sensor reading (validated; in-memory only) |
| GET | `/telemetry/latest` | Latest reading per sensor, age and heartbeat status (OK / LATE / STALE) |
| GET | `/telemetry/history` | Recent readings (`sensor_id`, `limit` ≤ 500) |
| POST | `/advisor/suggest` | Grok advisor demo: suggestions + safety-layer verdicts; never actuates |
| GET | `/advisor/limits` | Safety-layer limits with labels and sources |
| GET | `/dashboard` | Static demo dashboard (no build step, no external assets) |

```bash
curl -s http://127.0.0.1:8000/simulate -H 'Content-Type: application/json' \
  -d '{"days":30,"feed_g_day":5,"temp_C":21,"include_plot":false}'
curl -s http://127.0.0.1:8000/power-budget -H 'Content-Type: application/json' -d '{}'
curl -s http://127.0.0.1:8000/alarms -H 'Content-Type: application/json' \
  -d '{"DO_mg_L":4,"water_levels_pct":{"sump":70}}'
```

## What the pilot defaults say (labels from `configs/pilot-v2.json`)

- **IDEA:** one pump: sump → fish tank; gravity → settler → fines bag → K1 MBBR → raised DWC → sump. Sludge goes to separate worm bins.
- **CALC:** six working-water stages sum to **991.3 L**; verify by metered fill.
- **IDEA/CALC:** **10 comet goldfish** first; about **70 L** of K1 carrier.
- **ASSUME:** feed starts at **5 g/day**, hard ceiling **15 g/day**, no automatic ramp.
- **CALC on QUOTED/ASSUME ratings:** known peak **1,285 W**; continuous budget **1,920 W** on a 20 A / assumed 120 V circuit.
  The default power result is deliberately `INCOMPLETE` until the wiring/GFCI check and other loads are known.
- **IDEA:** solar is optional and off by default. RO is backup only, with no recovery guarantee.

Every parameter carries a label (MEASURED, QUOTED, SIM, ASSUME, IDEA, CALC), a unit and a source.
Sources name sections of the family's private planning package (`garage-pilot-v2.md`, `measurement-protocol-v1.md`,
`model/…`), which will be published with a later release; they are not files in this repository.

## What this does NOT prove

No predicted safe dissolved oxygen, pH, KH, fish or plant yield, worm throughput, RO purity, solar uptime or electrical safety.
No automatic dosing, stocking, feed ramp, pump stop, message or purchase. Missing sensor readings stay unknown; they are never treated as healthy.
Software tests passing is a **MEASURED software** result only — not physical validation.

The older models in `simulations/` are separate teaching sims; this API does not use their linear pH-from-alkalinity shortcut.
Experimental educational software, not an engineered or certified control system. See [../DISCLAIMER.md](../DISCLAIMER.md).

## Grok advisor demo (suggests, never actuates)

`POST /advisor/suggest` takes the current state (pH, TAN, nitrite, nitrate, KH, DO, temperature, tank levels,
current feed rate, heartbeat staleness), either in the request body or from the latest telemetry
(`"use_latest_telemetry": true`), and returns suggested adjustments with reasons.

- **`mock` (default):** deterministic rules over the pilot thresholds ([advisor/mock.py](advisor/mock.py)). No key, no network. Labeled **MOCK**.
- **`live`:** asks Grok through the xAI API over plain HTTPS ([advisor/live.py](advisor/live.py)). Needs `XAI_API_KEY` in the server's environment;
  uses the xAI Responses API (`POST https://api.x.ai/v1/responses`); model from the request, `XAI_MODEL`, or the default `grok-4.7`. If the key is missing or the call or reply fails, it falls back to MOCK and says why in `notice`.
  The key is never logged or returned.
  **Not tested against the real xAI API** in CI or on the maintainer box (no API key there); only the MOCK path and a faked transport are exercised. Change the model with `XAI_MODEL` or the request field.
- **Safety layer ([advisor/safety.py](advisor/safety.py)), same for both modes:** every suggestion comes back `ALLOWED`, `CLAMPED` or `BLOCKED` with reasons, and blocked or clamped ones are logged
  (`ecoforge.advisor.safety`). Limits come from `configs/pilot-v2.json` (see `GET /advisor/limits`):
  feed never above the 15 g/day cap (ASSUME); increases only one ramp step (+2 g/day, ASSUME) and only with known, non-alarming DO/TAN/nitrite and fresh heartbeats;
  temperature setpoints clamped to 18–24 °C (ASSUME); aeration never stops; software never stops core circulation; no dose amounts; unknown actions blocked.
  Every suggestion carries `executed: false` and `requires_human_confirmation: true`.
- `"include_safety_demo": true` appends canned unsafe suggestions (labeled as such) so you can watch the safety layer block them.

```bash
curl -s http://127.0.0.1:8000/advisor/suggest -H 'Content-Type: application/json' \
  -d '{"state":{"DO_mg_L":3.8,"TAN_mg_L":0.2,"nitrite_mg_L":0.1,"pH":7.0,"temp_C":21,"feed_g_day":5,"heartbeat_stale":false},"include_safety_demo":true}'
```

## Sensor heartbeat telemetry

```bash
python tools/fake_sensor.py                                   # one SIM reading every 300 s (QUOTED heartbeat) until Ctrl-C
python tools/fake_sensor.py --interval 1 --count 20           # quick demo
python tools/fake_sensor.py --interval 1 --scenario do-drop   # DO drifts down so the advisor reacts
```

The fake sensor is a seeded random walk around the ASSUME fixture in `configs/pilot-v2.json`; every reading is labeled **SIM**.
`POST /telemetry` validates each reading (sensor id pattern, physical ranges, no unknown fields) and keeps it in process memory only
(at most 50 sensors × 500 readings; a restart clears it). `GET /telemetry/latest` flags a sensor **LATE** after one missed interval and
**STALE** after more than two; the measurement protocol itself treats one missed critical beat as FAIL, which `/alarms` still enforces.

Optional MQTT bridge: `pip install -r requirements-mqtt.txt`, then `python tools/mqtt_bridge.py --broker 127.0.0.1` forwards
`ecoforge/pilot/<sensor_id>/telemetry` JSON payloads to the same `POST /telemetry`. Not needed for tests or CI.
**Not tested against a real MQTT broker**; topic→body mapping is unit-tested, and CI only checks the bridge exits cleanly when `paho-mqtt` is missing.

## Dashboard

`GET /dashboard` serves one static HTML page ([static/dashboard.html](static/dashboard.html)): telemetry charts with protocol threshold lines,
latest heartbeats with OK/LATE/STALE, advisor suggestions with their safety verdicts, and the 30-day planning-model nitrogen curve.
It refreshes every 5 s (`/dashboard?refresh=1` for faster), loads nothing from the internet, and carries a **SIMULATION — not measured data** banner.

## Sensor logger stub

```bash
python -m src.tools.grok_esp32_logger_stub --cycles 3 --interval 0
```

Emits **SIM** readings and an MQTT-format heartbeat payload (QUOTED 300 s interval) to stdout and `artifacts/sensor-stub.csv`.
It always terminates, never opens a network connection and never talks to hardware.
