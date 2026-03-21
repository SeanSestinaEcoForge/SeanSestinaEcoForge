# EcoForge – Open-Source Closed-Loop AI Homesteads

**Grok-optimized regenerative systems for Earth abundance & Mars readiness.**  
Vermiponics + biogas spine + RO + Grok reasoning/voice agents (Ara default) + Optimus hooks. Family-scale nodes scaling to multi-node networks.

## Visual Overview

![Vermiponics Core Setup](https://raw.githubusercontent.com/SeanSestinaEcoForge/SeanSestinaEcoForge/main/images/vermiponics-vermi-beds.jpg)  
**EcoForge Vermiponics Core** – Worm beds + gravel filter + nutrient flow to plants (96.5% recovery target)

![Closed-Loop System Diagram](https://raw.githubusercontent.com/SeanSestinaEcoForge/SeanSestinaEcoForge/main/images/closed-loop-vermiponics-diagram.png)  
**Full Closed-Loop Flow** – Vermiponics → Biogas → RO → Energy Balance (pH, NH3, energy all monitored)

![Shipping Container Homestead](https://raw.githubusercontent.com/SeanSestinaEcoForge/SeanSestinaEcoForge/main/images/container-greenhouse-setup.jpg)  
**Container 1 Vision** – Modular, insulated shipping container node for Cambridge site

![RO Unit Integration](https://raw.githubusercontent.com/SeanSestinaEcoForge/SeanSestinaEcoForge/main/images/ro-filtration-aquaponics.jpg)  
**Reverse Osmosis in Action** – Low-energy water purification for permeate quality

![Biogas + Vermi Integration](https://raw.githubusercontent.com/SeanSestinaEcoForge/SeanSestinaEcoForge/main/images/biogas-vermicomposting-setup.jpg)  
**Biogas Spine** – Waste digestion powering the loop (solar/Powerwall hybrid)

**Current Status (March 2026)**  
- Blueprint v3 "Supernova" locked: 95–96.5% resource recovery, NH₃ <6 ppm, RO 0.55 kWh/m³, 18.8 LMH flux.  
- API: FastAPI /simulate endpoint (vermiponic + RO ODEs) – live but throttled.  
- Grok Integration: In progress – API key ready, testing reasoning for sim tuning + realtime voice agents (Ara voice locked for warm, conversational agents). Awaiting credits top-up for heavy usage.  
- Physical Build: Container 1 prototype queued (Cambridge I-70/I-77 node) – awaiting site confirmation from Dad/Danny.  
- Team: Core push with Danny (build experience), Bridget (reviewing repo/sims), Sean leading. Open for aligned contributors!  
- Treasury: Activation pending (X Money/multisig) – $0 current.  

**Vision**  
True closed-loop abundance: Waste-to-food-to-energy cycles powering homesteads. Grok agents (Ara voice) guide ops, explain sims, optimize in realtime. Dual-use Earth/Mars (Starship scalable).  
Full details: [docs/EcoForge-Complete-Vision-Consistency-v3.md]

**Key Metrics (v3 Supernova – Targets Achieved in Sims)**  
- Vermiponics: 95–96.5% recovery, NH₃ <6 ppm  
- RO: 4.5–5.8 ppm permeate, 0.55 kWh/m³  
- Pilot Scale: 10-person node → 400+ lbs/month surplus food, 30–90 min daily ops  
Live dashboard/sensor feeds: In dev (ESP32 → Grok → Ara alerts)

**Quick Start**  
1. Clone: `git clone https://github.com/SeanSestinaEcoForge/SeanSestinaEcoForge`  
2. Install: `pip install -r requirements.txt`  
3. Run sim: `python simulations/sim-aquaponics-nutrient-cycle.py`  
4. API: `uvicorn api.main:app --reload` (throttled)  
5. Grok/Voice: Key at console.x.ai. Test Ara TTS in playground (x.ai/api/voice):  
   Sample prompt: "Fam, let's optimize this vermiponic cycle step by step."  

**Roadmap & Phases**  
- **Phase 1**: Blueprint lock + sim validation → **Complete**  
- **Phase 2**: Container 1 physical build + first cycle → **Next** (queued for site/Danny/Dad greenlight)  
- **Phase 3**: Grok agents live (reasoning + Ara realtime voice), multi-node scaling → Queued  
- **Phase 4**: Treasury activation, community nodes, Optimus integration  

Checklists: [docs/Phase2_Checklist.md] | [docs/Master-BOM-All-Tiers.md]

**Get Involved**  
- Fork & prototype your node  
- PR code/docs/sims/feedback  
- Issues or reach out @SeanSestina  
Current priorities: Sensor integration examples, Grok tool calling stubs, BOM sourcing updates, Container 1 build sequencing  

License: MIT  
Let's forge abundance together! 🌱⚡️🚀
