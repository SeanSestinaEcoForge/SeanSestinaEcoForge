# EcoForge for Humanity

**Open-source closed-loop family nodes**  
Waste → Food → Energy → Knowledge  

Family-forged regenerative systems for Earth abundance — and a practical analog for long-duration life support beyond Earth.

![Closed-loop flow](images/ecoforge-closed-loop-flow.png)

---

## What this is (10-second read)

EcoForge is a family-built, open-source **vermi-aquaponics** node: worms turn waste into fertility, fish feed the plants, plants clean the water, solar and storage keep the critical loops alive, and labeled measurements keep hope from being mistaken for results.

**Right now (November 2026):** a measured garage pilot is the active physical build (starting with goldfish sentinels).  
**Next:** the first **40-ft high-cube** node on purpose-fit family land, once the pilot produces real data and the site is ready.

**Latest snapshot:** [progress/2026-11-update.md](progress/2026-11-update.md)

---

## Unique belief

A regular family, without degrees or investors, can build a system that covers its own food, water, and energy — and give the blueprint away. Independence does not require credentials or equity; it requires honest labels, caution-first engineering, and the patience to start small. The same container that feeds a family in Ohio is a rough draft of regenerative life support people will one day need farther from home.

---

## Current obsession

Shipping the first physical system and collecting **MEASURED** data. Everything else — grants, open-source polish, the 40-ft node — serves that proof.

---

## Hero targets (not achievements)

No physical EcoForge node has produced measured surplus yet. Numbers below are **design targets** until a labeled MEASURED result replaces them. Older “sim validated” wording is retired.

| Target | Value | Label | Notes |
|---|---|---|---|
| RO recovery | ≥ 96.5% | TARGET (SIM / ASSUME) | Make-up water path; prove after water test |
| RO effluent TDS | < 6 ppm | TARGET (SIM / ASSUME) | Protocol alarm divert/stop |
| Net energy | +16 kWh/day | TARGET (ASSUME / IDEA) | Design north star; sized from a load ledger, not claimed as proven |
| Surplus produce + protein | ~400 lb/mo | TARGET (ASSUME / IDEA) | Full-node goal; retired as a *promise* until MEASURED |
| Biochar in media | ~35% | TARGET (ASSUME / IDEA) | Design mix; not MEASURED in a live node |
| Sensor heartbeat | every 5 min | TARGET (IDEA) | MQTT mesh; missing beat = fail |
| First fish (pilot) | 10 comet goldfish | IDEA / plan | Sentinels; species for the full node compared later |
| Full-node fish | tilapia hybrid candidate | IDEA | Thesis preference; **not locked** — garage pilot decides |

Sources for the labeling rule and protocol bounds live locally today; public protocol stubs: [docs/Phase1_Checklist.md](docs/Phase1_Checklist.md), [docs/Phase2_Checklist.md](docs/Phase2_Checklist.md), [docs/Simulation-Roadmap.md](docs/Simulation-Roadmap.md).

---

## Best thing pulled off so far

I have no degree in engineering, biology, or agriculture. I work by finding a hard problem and engineering backward from it.

What exists today:

1. **An honest design system** — every number labeled MEASURED, QUOTED, SIM, ASSUME, IDEA, or CALC so nobody confuses a hope with a result.
2. **Public simulations** you can run — nutrient/vermiponics models and a biogas digestion ODE:
   - [simulations/aquaponics-vermiponics-enhanced-ph-alk.py](simulations/aquaponics-vermiponics-enhanced-ph-alk.py)
   - [simulations/sim-biogas-digestion.py](simulations/sim-biogas-digestion.py)
   - [simulations/energy_basic.py](simulations/energy_basic.py)
   - [docs/Simulation-Roadmap.md](docs/Simulation-Roadmap.md)
3. **Blueprints, BOMs, and ops docs** — [Master-BOM-All-Tiers.md](Master-BOM-All-Tiers.md), [docs/](docs/), [designs/](designs/)
4. **System visuals** — container cutaway, isometric, BOM exploded, Earth/Mars framing:
   - [images/ecoforge-container-cutaway.png](images/ecoforge-container-cutaway.png)
   - [images/ecoforge-isometric-diagram.png](images/ecoforge-isometric-diagram.png)
   - [images/ecoforge-bom-exploded.png](images/ecoforge-bom-exploded.png)
5. **A measured garage pilot ready to build** — floor, power path, rain tank, and layout taped; electrical safety gate before water; goldfish first. (Pilot package is local until the next public release.)
6. **Earlier family proof of agency** — wiring a whole house with family crew, end to end.

People say this is too good to be true. That is why the garage pilot exists: prove it with data, not promises.

![Container cutaway](images/ecoforge-container-cutaway.png)

---

## Status — November 2026

| Track | Status | Honest note |
|---|---|---|
| Design / docs / sims | Active | Public repo + deeper local packages in progress |
| Garage pilot (small fish–plant–worm bench) | **Active physical path** | Measured space; nothing wet until the electrical gate passes |
| First 40-ft high-cube node | **Planned next** | Purpose-fit family land; stream/pond preferred; one family parcel on hold pending a power upgrade |
| Open-source public release | Staged | Full drop when the pilot story and living docs are ready together |
| Funding | Grants first | No equity. Loans deferred. Crowdfund after MEASURED proof |

### Family crew (roles)

| Role | Focus |
|---|---|
| Coordination / wiring / software | Measurement protocol, MQTT skeleton, Grok optimization path, build sequencing |
| Site / heavy work & plumbing | Pad, tank path, plumbing, biochar retort, physical install |
| Logistics & safety | Delivery, gas/electrical safety review, sequencing |
| Plants & media | Propagation, winter greens, outreach |
| Gray water | Branched-drain path and local rules |


---

## Planned first node (design intent)

One **40-ft high-cube** for fish + water treatment, with plant beds in a greenhouse extension (layout decision locked locally Oct 2026; public diagrams above). Intended stack:

- Vermi-aquaponics + biochar media
- RO make-up after a real water test (rain-first preferred)
- Solar + storage hybrid; critical aeration/circulation protected
- GAHT earth tubes **designed**; install timing still open
- MQTT 5-minute heartbeat on critical sensors
- Grok-assisted optimization once MEASURED streams exist ([docs/Grok-Ara-Integration-Plan.md](docs/Grok-Ara-Integration-Plan.md))
- Dual-use framing: Earth homestead + Mars-analog life-support research ([docs/06_Mars_Analog_R&D_Roadmap.md](docs/06_Mars_Analog_R%26D_Roadmap.md))

**Living BOM:** estimates only; nothing ordered. Public March 2026 tier table: [Master-BOM-All-Tiers.md](Master-BOM-All-Tiers.md). A tighter DIY living BOM is maintained locally and will replace the public table in a future release.

---

## What’s next

1. Clear the garage pilot electrical safety gate (GFCI / fuse-wire check).
2. Build the garage pilot dry, then wet; fishless cycle; goldfish sentinels; log MEASURED water, nutrients, and power.
3. Feed real data back into the models (retire SIM assumptions that fail).
4. Sequence Container 1: site ready → pad/container → plumbing → sensors → greenhouse.
5. Sensor integration examples + MQTT topic tree in-repo.
6. One coherent public open-source release when the pilot proof and living docs are ready.

---

## Quick start

```bash
git clone https://github.com/SeanSestinaEcoForge/SeanSestinaEcoForge.git
cd SeanSestinaEcoForge
pip install -r requirements.txt
python simulations/aquaponics-vermiponics-enhanced-ph-alk.py
python simulations/sim-biogas-digestion.py
```

Optional API stub: [api/main.py](api/main.py) (development only; not a production control system).

### Repository map

- `docs/` — philosophy, checklists, roadmaps, integration notes
- `simulations/` — Python models and notebooks
- `designs/` — layout / homestead sketches
- `progress/` — dated status updates
- `images/` — diagrams and reference photos
- `api/` — FastAPI stub
- `chaos-examples/` — example simulation outputs

---

## Safety

EcoForge materials are provided **AS IS** for experimental, educational, and open-source research only. Building or operating these systems involves serious risks (fire/explosion, electrical, chemical, biological, structural). You assume 100% of the risk. Consult licensed professionals, follow codes, get permits, and start small. See [DISCLAIMER.md](DISCLAIMER.md).

---

## Get involved

- Fork and prototype your own small node
- Open issues / PRs (code, docs, sims, corrections)
- Prefer MEASURED corrections over louder claims

**Current priorities:** garage pilot MEASURED data, sensor/MQTT examples, honest BOM refresh, Container 1 sequencing.

License: [MIT](LICENSE)

Let’s forge abundance together — carefully, and with receipts. 🌱
