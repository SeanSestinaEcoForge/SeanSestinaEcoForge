# Contributing to EcoForge

Thanks for helping. EcoForge is a family-built, open-source vermi-aquaponics project: a garage pilot first, then a 40-ft node. The most useful contributions make the work **more honest, safer, or easier to reproduce**.

## ⚠️ IMPORTANT SAFETY & LIABILITY DISCLAIMER

**EcoForge designs, simulations, blueprints, code, BOMs, and all materials are provided "AS IS" and "WITH ALL FAULTS" for experimental, educational, and open-source research purposes only.**

Building or operating any EcoForge system (vermiponics, biogas digester, RO unit, solar/Powerwall integration, shipping container mods, sensors, etc.) involves **serious risks** including but not limited to:
- Fire or explosion (biogas/methane)
- Electrical shock or arc flash
- Chemical exposure or burns
- Biological hazards (pathogens, ammonia)
- Structural failure
- Flooding or system leaks
- Injury or property damage

**You assume 100% of the risk.**  
We make **no warranties** whatsoever (express or implied) about safety, performance, accuracy of simulations, or fitness for any purpose. Real-world results may differ from sims.

Always:
- Consult licensed engineers, electricians, plumbers, and local authorities
- Comply with all building, environmental, electrical, and safety codes
- Get proper permits and inspections
- Start small and test safely

**Neither Sean Sestina, EcoForge, contributors, nor any affiliates shall be liable** for any damages, injuries, losses, claims, or liabilities arising from the use of this material.

Prototype and build **at your own risk only**. Not for commercial replication without independent professional review and certification.

Read the full [LICENSE](LICENSE) (MIT) and [DISCLAIMER.md](DISCLAIMER.md) for additional terms.

---

## Set up (about 5 minutes)

Python 3.12 or newer (CI uses 3.12).

```bash
git clone https://github.com/SeanSestinaEcoForge/SeanSestinaEcoForge.git
cd SeanSestinaEcoForge
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt                    # sims + API + pytest
```

Optional extras, never needed for tests or CI:

- `pip install -r requirements-grok.txt` for the Grok helper scripts in `src/` (your own `XAI_API_KEY`)
- `pip install -r requirements-mqtt.txt` for `tools/mqtt_bridge.py`

## Run the checks before opening a PR

```bash
python -m pytest -q                       # all tests (API, advisor safety layer, telemetry)
python tools/smoke_local.py               # starts a loopback server, calls every endpoint, stops it
python simulations/aquaponics_vermiponics_enhanced_ph_alk.py
python simulations/sim_biogas_digestion.py
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs the same steps plus a syntax/undefined-name lint, and fails if anything fails.
Tests must not need an API key, a broker, hardware or network access beyond `pip install`.

Try the dashboard locally: `python -m uvicorn api.main:app --port 8000`, then `python tools/fake_sensor.py --interval 2 --count 60`, then open `http://127.0.0.1:8000/dashboard`.

## The labeling rule (required)

Every number you add (in code, configs, docs or PR text) carries one of these labels and a source:

| Label | Meaning | Example |
|---|---|---|
| **MEASURED** | Read from a real instrument or test, with method and date | Breaker rating read from the panel |
| **QUOTED** | From a datasheet, paper or protocol, cited | DO critical 4 mg/L (protocol v1.2) |
| **SIM** | Output of a model in this repo | 30-day nitrate curve from `/simulate` |
| **ASSUME** | A stated assumption or scenario input | Feed starts at 5 g/day |
| **IDEA** | A plan or target, not yet built or decided | Solar, 40-ft node, tilapia candidate |
| **CALC** | Arithmetic on labeled inputs | 991.3 L total working water |

Also:

- **MOCK** marks canned or rule-based advisor output that is not from Grok.
- A model result is never MEASURED. Software tests passing is a MEASURED *software* result only, not physical validation.
- Unknown is not healthy: missing readings stay missing and must not default to a "good" value.
- Configs in `configs/` enforce this: every parameter has `value`, `unit`, `label` and `source`, and a test checks it.

## Safety first

- **Software suggests; people decide.** Nothing in this repo may switch, dose, feed, stop or start hardware, send messages or buy anything. PRs that add actuation will not be merged.
- Hard rules stay hard: aeration never stops, software never stops core circulation, no chemical dose amounts, feed stays under the cap. Changes to `api/advisor/safety.py` need tests that show the limit still holds.
- Keep the API on loopback. It has no authentication; never expose it to the internet.
- Electrical, gas, biogas and structural work: follow codes, get permits, use licensed professionals.

## No personal data

- No family names, home or land locations, addresses, phone numbers, personal emails, finances or photos that identify private places.
- No secrets: never commit API keys, `.env` files, tokens, broker passwords or logs that contain them. Use environment variables.
- Use roles ("site / heavy work", "plants & media") instead of names. Commit with your GitHub noreply email if you prefer privacy.

## Pull requests

1. Fork and branch (`feature/short-description`).
2. Keep changes focused; one topic per PR.
3. Run the checks above; add or update tests for code changes.
4. Label any new numbers; update the relevant README if behavior changes.
5. Describe what changed, why, and how you tested it.

Good places to start: issues labeled `good first issue`, sensor examples, sim units and documentation fixes.

Questions or ideas? Open an issue, or DM [@SeanSestina](https://x.com/SeanSestina) on X.

Family first, share improvements openly, build for abundance and resilience — carefully, and with receipts. 🌱
