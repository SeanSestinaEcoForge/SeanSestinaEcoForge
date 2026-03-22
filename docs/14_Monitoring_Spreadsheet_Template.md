# EcoForge Monitoring Spreadsheet Template

**Version**: 1.0 – March 22, 2026  
**Status**: Locked core document in Master Archive v1.6

**Purpose**  
Simple, daily-use spreadsheet template for 1–2 operators to log all critical parameters, track trends, and generate 90-day test data. Designed for Container 1 and scalable to Premium Hub.  

### Workbook Structure (Create in Google Sheets or Excel)

**Tab 1: Daily Log** (One row per day – main entry sheet)

| Column | Field Name                  | Example / Target                     | Notes / Purpose |
|--------|-----------------------------|--------------------------------------|-----------------|
| A      | Date                        | 2026-03-23                          | Auto or manual |
| B      | Day #                       | 1, 2, 3…                            | 90-day test tracker |
| C      | Tilapia Tank Temp (°F)      | 82.5                                | 78–86 target |
| D      | DO (mg/L)                   | 6.2                                 | >5 target |
| E      | pH                          | 7.1                                 | 6.8–7.5 target |
| F      | Ammonia (ppm)               | 0.3                                 | <0.5 target |
| G      | Nitrite (ppm)               | 0.4                                 | <1 target |
| H      | Nitrate (ppm)               | 85                                  | 20–150 target |
| I      | EC (mS/cm)                  | 1.4                                 | 0.8–2.0 target |
| J      | Biofloc TSS (mg/L)          | 450                                 | 300–600 target |
| K      | Duckweed Harvest (lb)       | 1.8                                 | Daily yield |
| L      | Greens/Herbs Harvest (lb)   | 4.2                                 | Mars bay output |
| M      | Tilapia Feed (g)            | 120                                 | Pellets + duckweed |
| N      | Worm Tea Brewed? (Y/N)      | Y                                   | Nutrient cycle |
| O      | Notes / Observations        | "Fish active, slight pH dip"        | Anomalies, fixes |
| P      | Operator Initials           | DS / SS                             | Accountability |

**Tab 2: Weekly Summary** (One row per week – auto-calculate where possible)

| Column | Field Name                  | Formula / Example                     | Purpose |
|--------|-----------------------------|---------------------------------------|---------|
| A      | Week #                      | =WEEKNUM(Daily!A2)                   | Progress tracker |
| B      | Avg Temp (°F)               | =AVERAGE(Daily!C2:C8)                | Stability |
| C      | Avg DO (mg/L)               | =AVERAGE(Daily!D2:D8)                | Oxygen trend |
| D      | Avg Ammonia (ppm)           | =AVERAGE(Daily!F2:F8)                | Crash risk |
| E      | Max Ammonia Spike           | =MAX(Daily!F2:F8)                    | Worst-case |
| F      | Tilapia Survival (%)        | Manual or mortality calc             | Health |
| G      | Duckweed Doubling Rate      | Manual observation                   | Growth |
| H      | Total Greens Harvest (lb)   | =SUM(Daily!L2:L8)                    | Yield |
| I      | Biofloc TSS Avg             | =AVERAGE(Daily!J2:J8)                | Floc stability |
| J      | Weekly FCR                  | Feed / weight gain                   | Efficiency |
| K      | Low-Pressure Test?          | Y/N + duration                       | Mars analog |
| L      | Actions Taken               | "Increased aeration"                 | Troubleshooting |
| M      | Week Notes                  | Text                                 | Summary |

**Tab 3: 90-Day Closure Metrics** (Final summary dashboard – fill at Day 90)

| Metric                      | Target (Hardened) | Measured (Day 90) | Pass/Fail | Notes |
|-----------------------------|-------------------|-------------------|-----------|-------|
| Avg Ammonia Removal (%)     | >70%              | [enter]           |           |       |
| Water Recovery (%)          | >60%              | [enter]           |           |       |
| Nitrogen Balance (%)        | >60%              | [enter]           |           |       |
| Tilapia Survival (%)        | >85%              | [enter]           |           |       |
| Duckweed Avg Daily Harvest  | >0.5 lb/day       | [enter]           |           |       |
| Greens Total (lb)           | >500 lb           | [enter]           |           |       |
| System Uptime (%)           | >95%              | [enter]           |           |       |

**Tab 4: Troubleshooting Log**  
Columns: Date | Issue | Parameter | Action | Resolution Date | Resolved? (Y/N)

**Implementation Tips**  
- Use Google Sheets for sharing with Danny  
- Conditional formatting: Red if ammonia >0.5, DO <5, etc.  
- Add photos: Hyperlink column to images of fish, plants, floc  
- Backup: Export to PDF weekly  

**Retrieval Command**: “Pull EcoForge Monitoring Spreadsheet Template” or “Show EcoForge Document 14”

This document is now the official monitoring template reference.
