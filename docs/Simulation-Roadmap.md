# EcoForge Simulation Roadmap (March 2026)

**Goal:** Single source of truth for all simulations. Track what is built, validated, and prioritized for Phase 2 container builds and Mars analogs.

## 1. Simulations Already Built & Run

| Simulation | File(s) | Key Outputs | Status |
|------------|---------|-------------|--------|
| Vermiponics / Aquaponics Nutrient Cycle (ODE) | `sim-aquaponics-nutrient-cycle.py` + Jupyter versions | 95–96.5% recovery, NH₃ <6 ppm | Fully built & FastAPI-integrated |
| Reverse Osmosis (RO) Model | Integrated in `/simulate` | 0.55 kWh/m³, 18.8 LMH flux, TDS <6 ppm | Live |
| Combined Closed-Loop (Vermiponics + RO) | FastAPI `/simulate` | Full water + nutrient recovery | Active |
| Basic Energy Balance / Surplus | `energy_basic.py` | +15–27 kWh/day surplus | Functional |
| Fouling Simulation | `fouling_sim.py` | Fouling over time | Built |
| Parameter Sweep Utility | `param_sweep_example.py` | Rapid testing | Built |
| **Biogas / Anaerobic Digestion** | `sim-biogas-digestion.py` | 16.19 m³ methane (30 days), **97.1 kWh** energy, 1.75 kg N digestate | **New – Just Run** |
| Visualization Utilities | `viz_utils.py` | Plotting | Built |

## 2. Simulations Still Needed (Prioritized)

**High Priority (Next – Direct Impact on Phase 2)**
- Upgrade Full Energy Balance (add biogas + seasonal heating)
- Grok Real-Time Optimization Loop (sensor → Grok tool-calling → adjustments)
- Integrate Biogas into combined closed-loop `/simulate` endpoint

**Medium Priority (Mars Layer)**
- Mars-adapted vermiponics / regolith nutrient cycle
- Low-G nutrient distribution & fluid dynamics
- Mars-specific RO under low pressure
- Integrated Mars closed-loop sim
- Chaos / failure-mode simulation

## 3. Latest Biogas Results (30-day run)
- Total methane: **16.19 m³**
- Energy generated: **97.1 kWh** (~3.2 kWh/day average)
- Digestate nitrogen returned: **1.75 kg N**

**Next Action:** Integrate biogas outputs into Master BOM and Phase 2 checklist. Then build Grok optimization loop.

---
Last updated: March 26, 2026
