"""Conservative arithmetic check only, never an electrical safety certificate."""
from .configuration import values

def power_budget(c, req):
    p = values(c["power"])
    light = p["tent_rated_W"] * req.tent_fraction
    fixed = sum(p[k] for k in ["heaters_W","tent_fan_W","clip_fans_W","cube_fan_W","pump_W","air_W","backup_air_AC_W","pi_network_UPS_W","seedling_W"])
    pilot = fixed + light
    life_support = sum(p[k] for k in ["pump_W","air_W","backup_air_AC_W","pi_network_UPS_W"])
    # Solar charging replaces the grid life-support branch only when user explicitly models that wiring.
    grid = pilot + p["overhead_LED_W"] + req.space_heater_W
    if req.station_charging:
        grid += req.wall_charge_W - life_support
    known = grid
    if req.other_loads_W is not None:
        grid += req.other_loads_W
    limit = req.circuit_amps * p["voltage"] * p["continuous_fraction"]
    violations = []
    if grid > limit: violations.append("Continuous budget exceeded")
    if req.tent_fraction > p["tent_cap_fraction"]: violations.append("Tent light exceeds pilot 60% cap")
    if req.space_heater_W > 0: violations.append("No space heater permitted on the pilot circuit")
    charge_cap = p['wall_charge_cap_15A_W'] if req.circuit_amps == 15 else values(c["solar"])["wall_charge_cap_W"]
    if req.station_charging and req.wall_charge_W > charge_cap: violations.append("Station wall charging exceeds caution-first cap for this circuit")
    missing = []
    if req.other_loads_W is None: missing.append("Other garage loads unknown; headroom is provisional")
    if not req.electrical_gate_confirmed: missing.append("Wire/fuse/GFCI inspection not confirmed; no water before this gate")
    return {"label":"CALC","source":"garage-pilot-v2.md §6/§13; pilot-v2.json peak ratings (not measured draw)",
            "pilot_peak_W":round(pilot,3),"known_grid_peak_W":round(known,3),"modeled_total_W":round(grid,3),
            "continuous_limit_W":limit,"provisional_headroom_W":round(limit-grid,3),
            "status":"FAIL" if violations else ("INCOMPLETE" if missing else "WITHIN_MODELED_BUDGET"),
            "violations":violations,"unknowns":missing,"inputs_label":"ASSUME user scenario (inspection confirmation is an assertion, not verification)",
            "advisory":"Arithmetic only: unknown startup/inrush loads, breaker sharing and wiring can still make this unsafe. Never backfeed; no actuator control.",
            "solar":c["solar"]}
