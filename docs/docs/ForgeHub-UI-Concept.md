# ForgeHub – EcoForge Closed-Loop Sensor Dashboard & API

**Version:** 1.0 (March 2026)  
**Status:** Design Phase – Ready for React/FastAPI build once API credits + Container 1 site confirmed  
**Core Principle:** True closed-loop integration. Every subsystem talks to every other. pH + all water chemistry parameters monitored across vermiponics, RO, biogas, and energy systems. Grok reasons holistically; Ara speaks the unified story.

## Monitored Parameters (All Systems – Real-Time)
| Subsystem              | Key Parameters (pH + etc.)                          | Alert Thresholds          | Icon |
|------------------------|-----------------------------------------------------|---------------------------|------|
| Vermiponics            | pH, NH₃, TDS, DO, temp, humidity, nitrate, recovery % | pH 6.5–7.5, NH₃ <6 ppm   | 🪱🌱 |
| RO Unit                | Permeate TDS, flux (LMH), pressure, recovery %, energy use | TDS <6 ppm, flux >18 LMH | 💧🔄 |
| Biogas Spine           | CH₄ %, pressure, temp, kWh produced, H₂S           | Pressure 0.8–1.2 bar     | 🔥⚡ |
| Energy Storage & Management | Solar input (kW), Powerwall SOC %, consumption (kWh), biogas contribution, net draw | SOC <20% or >95%         | ☀️🔋 |
| Overall Closed Loop    | Holistic Health Score (0–100), 96.5% recovery target, surplus food projection | Health <85 → Ara alert   | 🌍🔄 |

## Interactive Dashboard Layout
- **Hero Overview** (default screen)  
  Circular “Closed-Loop Health” gauge (96.5% target) + live subsystem tiles + one-click **Ara Voice Status** button.

- **Subsystem Deep-Dives** (tap to jump)  
  Vermi tray view with pH/NH3 heatmaps, RO flux curve, Biogas pulsing flame, **Energy Management** Sankey diagram.

- **Holistic Insights Panel** (Grok-powered)  
  “pH drop in vermi → 15% higher aeration → Powerwall draw up 9% → Biogas ramp recommended”

- **Alert Center**  
  Auto-escalation with Ara voice call-outs.

## Sample Ara Voice Flows
- Daily: “Morning fam. Closed-loop health at 97.2%. pH perfect, energy balanced.”  
- Critical: “Alert — Powerwall SOC 15% and vermi pH dipping. Rerouting biogas now.”

## Tech Ties Everything Together
- Backend: FastAPI `/sensors/all`, `/energy/balance`, `/grok/holistic-reason`  
- Voice: **Ara** default  
- Energy: Live Sankey + “Abundance Saved Today” counter

## Next Steps
1. Credits top-up  
2. Dad/Danny site confirmation  
3. Build MVP dashboard  
4. Bridget review  

**This is the brain that ties EcoForge together.** One dashboard. One voice. One closed loop.

— Your backbone (Grok) + Sean Sestina  
Last Updated: March 22, 2026
