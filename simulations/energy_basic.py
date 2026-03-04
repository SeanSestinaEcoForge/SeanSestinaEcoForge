# simulations/energy_basic.py
# Basic energy estimation for homestead solar setup
# Placeholder calculations - expand with real panel data, efficiency losses, etc.

import numpy as np  # if not already imported

# Step 1: Define key parameters (placeholders - adjust as needed)
panel_count = 20               # number of solar panels
panel_watts = 400              # watts per panel (e.g., 400W panels)
system_efficiency = 0.85       # overall system efficiency (inverter + losses)
sun_hours_per_day = 4.5        # average effective sun-hours (location-dependent)

# Step 2: Calculate total daily energy potential (fixed undefined name)
total_kwh_day = (panel_count * panel_watts * sun_hours_per_day * system_efficiency) / 1000

# Step 3: Effective usable energy (rounded for readability)
effective_kwh = round(total_kwh_day, 1)

# Step 4: Output results
print(f"Total theoretical daily energy from {panel_count} × {panel_watts}W panels:")
print(f"  - {total_kwh_day:.2f} kWh (before efficiency losses)")
print(f"Effective usable daily energy (after {system_efficiency*100:.0f}% efficiency):")
print(f"  - {effective_kwh} kWh (assuming {sun_hours_per_day} sun-hours)")

# Optional: Add more advanced calcs later (e.g., battery storage, load matching)
# battery_capacity_kwh = 10.0
# daily_surplus = max(0, effective_kwh - 15.0)  # example daily load 15 kWh
# print(f"Daily surplus to storage: {daily_surplus:.1f} kWh")
