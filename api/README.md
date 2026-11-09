# Family garage pilot — planning simulator API

A small, **tested** FastAPI app for the family garage pilot (fish → solids → worms → plants, goldfish first).
It is a planning and teaching tool: **SIM and advisory only, no hardware control.**

## Run it (from the repository root)

```bash
pip install -r requirements-dev.txt
python -m pytest -q                                   # 77 tests
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

## Sensor logger stub

```bash
python -m src.tools.grok_esp32_logger_stub --cycles 3 --interval 0
```

Emits **SIM** readings and an MQTT-format heartbeat payload (QUOTED 300 s interval) to stdout and `artifacts/sensor-stub.csv`.
It always terminates, never opens a network connection and never talks to hardware.
