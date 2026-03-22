# EcoForge – Open-Source Closed-Loop AI Homesteads

![EcoForge Earth-Mars Hero](images/ecoforge-earth-mars-hero.png)  
**Grok-optimized regenerative systems for Earth abundance & Mars readiness.**  
Vermiponics + biogas spine + RO + Grok reasoning/voice agents (**Ara** default) + Optimus hooks. Family-scale nodes scaling to multi-node networks.

## Visual Overview

![EcoForge Container Cutaway](images/ecoforge-container-cutaway.png)  
*Insulated shipping container prototype with vermiponics beds, biogas integration, RO unit, and energy storage layout*

![EcoForge Process Flow](images/ecoforge-process-flow.png)  
*Closed-loop nutrient & energy flow: Vermiponics → Biogas → RO → Powerwall hybrid (pH, NH₃, recovery, energy all monitored)*

![EcoForge Isometric Diagram](images/ecoforge-isometric-diagram.png)  
*Isometric overview of the full homestead node system*

![EcoForge BOM Exploded View](images/ecoforge-bom-exploded.png)  
*Exploded BOM: Vermi crates, RO membranes, biogas digester, sensors, solar/Powerwall*

![EcoForge Scaling Roadmap](images/ecoforge-scaling-roadmap.png)  
*Roadmap for multi-node expansion and community rollout*

**Current Status (March 2026)**  
- Blueprint v3 "Supernova" locked: 95–96.5% resource recovery, NH₃ <6 ppm, RO 0.55 kWh/m³, 18.8 LMH flux.  
- API: FastAPI /simulate endpoint (vermiponic + RO ODEs) – live but throttled.  
- Grok Integration: In progress – API key ready, testing reasoning for sim tuning + realtime voice agents (**Ara** voice locked for warm, conversational agents). Awaiting credits top-up for heavy usage.
- [Grok-Ara-Integration-Plan.md](/docs/Grok-Ara-Integration-Plan.md)
- Physical Build: Container 1 prototype queued (Cambridge I-70/I-77 node) – awaiting site confirmation from Dad/Danny.  
- Team: Core push with Danny (build experience), Bridget (reviewing repo/sims), Sean leading. Open for aligned contributors!  
- Treasury: Activation pending (X Money/multisig) – $0 current.  

**Vision**  
True closed-loop abundance: Waste-to-food-to-energy cycles powering homesteads. Grok agents (**Ara** voice) guide ops, explain sims, optimize in realtime. Dual-use Earth/Mars (Starship scalable).  
Full details: [Complete v1.1 Master Protocol List](complete-v1.1-master-protocol-list.md)

**Key Metrics (v3 Supernova – Targets Achieved in Sims)**  
- Vermiponics: 95–96.5% recovery, NH₃ <6 ppm  
- RO: 4.5–5.8 ppm permeate, 0.55 kWh/m³  
- Pilot Scale: 10-person node → 400+ lbs/month surplus food, 30–90 min daily ops  
Live dashboard/sensor feeds: In dev (ESP32 → Grok → Ara alerts with full pH/energy closed-loop monitoring)
[ForgeHub-UI-Concept.md](/docs/ForgeHub-UI-Concept.md)

**Quick Start**  
1. Clone: `git clone https://github.com/SeanSestinaEcoForge/SeanSestinaEcoForge`  
2. Install: `pip install -r requirements.txt`  
3. Run sim: `python simulations/sim-aquaponics-nutrient-cycle.py`  
4. API: `uvicorn api.main:app --reload` (throttled)  
5. Grok/Voice: Key at console.x.ai. Test **Ara** TTS in playground (x.ai/api/voice):  
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
Current priorities: Sensor integration examples (pH + full energy management), Grok tool calling stubs, BOM sourcing updates, Container 1 build sequencing  

License: MIT  
Let's forge abundance together! 🌱⚡️🚀
