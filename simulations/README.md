# Simulations map

All outputs are **SIM**; parameters are **ASSUME** example values unless a file says otherwise. Run from the repository root after `pip install -r requirements.txt`. Plots go to `outputs/` (git-ignored); add `--show` where supported to open a window.

| Script | What it models | Run |
|---|---|---|
| `aquaponics_vermiponics_enhanced_ph_alk.py` | Fish, plants, N species, solids, DO, alkalinity (Q10 temperature). pH is a rough linear ASSUME toy. | `python simulations/aquaponics_vermiponics_enhanced_ph_alk.py` |
| `aquaponics_vermiponics_enhanced_ph_alk.ipynb` | Notebook twin with sliders (needs Jupyter + ipywidgets) | open in Jupyter |
| `sim_biogas_digestion.py` | Anaerobic digestion: organic matter → methane + digestate N (simplified, not mass-coupled) | `python simulations/sim_biogas_digestion.py [--plot]` |
| `aquaponics_nutrient_cycle.py` | Simpler 5-state nutrient cycle (no temperature/pH/DO) | `python simulations/aquaponics_nutrient_cycle.py` |
| `param_sweep_example.py` | Temperature sweep of the enhanced model → final nitrate | `python simulations/param_sweep_example.py` |
| `energy_basic.py` | Placeholder solar kWh/day (gross generation, no load ledger — not the +16 kWh/day net target) | `python simulations/energy_basic.py` |
| `fouling_sim.py` | Drip-line fouling with monthly cleaning (cartoon curve) | `python simulations/fouling_sim.py` |
| `perchlorate_sim.py` | Mars-analog perchlorate yield curves (IDEA stub) | `python simulations/perchlorate_sim.py` |
| `space_solar.py` | Earth vs orbital solar multiplier (IDEA stub) | `python simulations/space_solar.py` |
| `viz_utils.py` | Plot helper (import only) | — |

The tested garage-pilot model is separate: see [../api/README.md](../api/README.md).
