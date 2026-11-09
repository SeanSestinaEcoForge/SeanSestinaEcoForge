# Phase 2: Physical Container Node Forge (Family-Land Pilot)

> **Archived / superseded (pre-Nov 2026).** This document predates the November 2026 honesty pass. Revenue, ROI, yield, recovery, energy and "validated / locked / complete" statements in it are historical plans and assumptions (ASSUME / IDEA), **not MEASURED results** — no EcoForge node has operated yet. Current status: [README](../README.md) · [November 2026 update](../progress/2026-11-update.md).

## Goal
Deploy the first quick-deploy 20ft shipping container homestead node with active vermiponics (vermi reactor), RO greywater recycling, basic biogas stub, solar baseline, and live Grok/ESP32 monitoring.  
**Target Outcomes**: Prove 450 L/day closed-loop water cycle, consistent vermicast output, measurable food/energy surplus, and real-time data transparency. Surplus ready for local CSA drops or P2P credits (<10 min to Columbus). This becomes the replicable “Earth proof-of-concept” for Appalachia pilots and **Mars analogs**.

**Dependencies**  
- Phase 1 complete (blueprints v3 locked, simulations validated, Master-BOM sourced).  
- Site access secured (family-land agreement or equivalent).  
- 20ft used shipping container acquired and basic treasury/funding green (bootstrap fallback: personal/family/tools).  
- All materials cross-referenced from Master-BOM-All-Tiers.md.

**⚠️ Critical Reminder**  
All physical work carries real risks (see full [DISCLAIMER.md](../DISCLAIMER.md)). Consult licensed professionals for electrical, plumbing, structural, and biogas work. Obtain all required permits. Start small, test safely, and document everything.

## Detailed Week-by-Week Checklist

### Week 1: Site & Container Prep (Days 1–7)
- [ ] Day 1: Secure site access, confirm south-facing ridge or flat area with water access, mark utility setbacks.  
- [ ] Days 2–3: Acquire and position 20ft container; level foundation (gravel base + concrete pads or blocks). Reference designs/ for placement.  
- [ ] Day 4: Insulate walls, floor, and ceiling (closed-cell foam + vapor barrier). Target R-value for temp stability (vermi 15–25°C).  
- [ ] Day 5: Install baseline solar array (panels + mounting) and initial battery tie-in (Powerwall stub or equivalent). Test basic grid-tie fallback if needed.  
- [ ] Day 6: Rough-in plumbing — greywater collection lines from mock kitchen/bath, drainage, and effluent routing to vermi/RO.  
- [ ] Day 7: Complete safety baseline (electrical grounding, lightning protection, fire extinguishers, first aid kit, emergency shutoffs).  
**Week 1 Checkpoint**: Container is level, insulated, weather-tight, and safe. Photos uploaded to /images/.

### Week 2: Vermi Reactor Build & Inoculation (Days 8–14)
- [ ] Day 8: Build 0.6 m³ vermi bed/frame (wood or IBC tote modification, ~1 m² × 0.6 m). See designs/ for dimensions.  
- [ ] Day 9: Layer media — 10 cm perlite drainage base, then 55% coco coir / 35% biochar / 10% perlite mix (moisten to ~70% field capacity).  
- [ ] Day 10: Amend with 1 kg garden soil + beneficial microbes; adjust pH to 6.8–7.2.  
- [ ] Day 11: Introduce 1.2–2 kg Eisenia fetida (red wigglers); begin light feeding (kitchen scraps + 100 ml 1% molasses solution).  
- [ ] Days 12–14: Ramp feeding 20% per day while monitoring BOD, temperature, and odors. Harvest initial vermicast if ready.  
**Week 2 Checkpoint**: Vermi bed is active, worms healthy, no anaerobic odors, basic effluent ready for RO testing. Log initial data via ESP32.

### Week 3: RO System Install & Commissioning (Days 15–21)
- [ ] Day 15: Mount BW30 PRO-400/34 membrane in FRP pressure vessel; plumb pre-filter → high-pressure pump → ERD → RO module (reference Master-BOM).  
- [ ] Day 16: Install Atlas TDS/pH/flow sensors + ESP32 board; wire to Grok node and test basic logging script.  
- [ ] Day 17: Perform low-pressure flush (3 bar, 30 min drain); ramp pressure slowly to 9 bar (<0.7 bar/s).  
- [ ] Day 18: Run 1-hour full service cycle; verify first permeate TDS <6 ppm target.  
- [ ] Days 19–21: Integrate vermi effluent as feed; ramp greywater blend from 10% → 100%. Monitor flux (~18–19 LMH) and specific energy (~0.55 kWh/m³).  
**Week 3 Checkpoint**: RO producing clean permeate consistently; sensors feeding live data to Grok; energy and recovery metrics logged.

### Week 4: Full Closed-Loop Cycle & Grok Integration (Days 22–30)
- [ ] Days 22–25: Run daily full cycles; log vermicast harvest volumes, test basic biogas stub (methane capture if plumbed), prepare CSA sample output.  
- [ ] Day 26: Spawn initial Grok/Ara monitoring agent — set alarms (TDS >15 ppm → auto-shutdown, pH 6–8 range, flow anomalies).  
- [ ] Days 27–28: Use Grok pings for optimization (molasses dosing, pH adjustment, feed rates).  
- [ ] Day 29: Test first surplus distribution (vermicast/biogas credits or CSA drop). Update transparency dashboard (ForgeHub concept).  
- [ ] Day 30: Full 450 L/day milestone run. Document surplus food/energy metrics, upload data logs and photos.  
**Week 4 Checkpoint**: Node is live, self-sustaining closed-loop demonstrated, real metrics shared publicly (with disclaimer). Ready for visitors or replication scouting.

## Grok/Ara Tool-Calling Examples (for Week 4+)
- **Daily Optimization**: “Analyze today’s TDS, pH, flux, and energy data. Suggest optimal molasses dose and feed rate to keep NH₃ <6 ppm while maximizing vermicast output.”
- **Anomaly Response**: “Permeate TDS just spiked to 18 ppm. Diagnose likely cause and recommend immediate corrective action or shutdown sequence.”
- **Mars Analog Mode**: “Simulate this Earth node data under Mars conditions (low pressure, regolith sim feed, 38% gravity). What adjustments would improve recovery rate?”
- **Surplus Report**: “Generate a plain-language surplus summary for CSA drop: expected weekly vermicast, biogas yield, and food output in lbs.”

## Success Metrics Table

| Metric                        | Target                  | Notes / Verification                  |
|-------------------------------|-------------------------|---------------------------------------|
| Daily closed-loop water       | 450 L/day              | Permeate TDS <6 ppm                   |
| Vermicast production          | 10–20+ lbs/week        | Healthy worms, no odors               |
| RO specific energy            | ~0.55 kWh/m³           | Measured at 9 bar                     |
| Solar coverage                | ≥50% of daily load     | Surplus tracked in logs               |
| Grok alerts & optimizations   | 100% uptime on key alarms | Real-time via ESP32/Ara               |
| First local surplus           | CSA or P2P drop by Day 30 | Documented distribution               |

## Mars Analog Notes
- Treat the container as a **container bay mock** — log how vermiponics/RO performs with simulated regolith-amended feed or reduced pressure.  
- Use Grok to run “Mars mode” comparisons (gravity, atmosphere, radiation shielding implications).  
- Document lessons for Phase 3 and the Mars R&D roadmap (see `docs/06_Mars_Analog_RD_Roadmap.md`).

## Ongoing Safety & Monitoring Baselines
- **Alarms** (via Grok/ESP32): Permeate TDS >15 ppm (shutdown), pH outside 6–8, low/high flow, temp extremes, power anomalies.  
- **Daily Logs**: Temperature, pH, TDS, flux, energy consumption, worm activity notes.  
- **Weekly Reviews**: Adjust media/feeds if fouling occurs; inspect for leaks, structural integrity, or pest issues.  
- **Compliance**: All electrical/plumbing work inspected where required. Biogas handling follows local safety codes.  

**Next**: Phase 3 — automation task chaining, multi-node expansion, full homestead hybrid, and deeper Appalachia/Mars analog pilots.  

Forge nonstop till reality. Abundance is built one safe, documented step at a time. ❤️🥷🌱⚡️🪐♾️
