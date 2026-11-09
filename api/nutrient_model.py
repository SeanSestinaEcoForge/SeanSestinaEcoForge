"""SIM: unit-corrected v4 N equations, wired to the draft garage loop.

State concentrations: mg N/L. Rate g N/day / water m³ == mg N/L/day.
No pH/DO/yield forecast and no automatically returned vermi sludge/leachate.
"""
import base64
from io import BytesIO
from threading import Lock
import os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".tmp" / "matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from .configuration import values

PLOT_LOCK = Lock()
LIMITATIONS = [
    "SIM, not measured: well-mixed water, constant volume maintained by attended top-up.",
    "No DO, pH, KH, worm-growth, fish-growth or food-yield prediction. Read real sensors.",
    "Mass balance is dissolved model N only, not total feed N; solids mineralization/denitrification are not modeled.",
    "Temperature changes nitrification only; feed and plant uptake stay fixed.",
    "No automatic feed ramp/stop or dosing. Start only after fishless-cycle and electrical gates.",
    "NO2 and NO3 outputs are mg N/L. Confirm test-kit/protocol reporting basis before alarm comparison.",
    "Side-stream dewatered sludge goes to worms; no unmeasured leachate return or double-counted N credit.",
    "DWC biofilm credit excluded until measured; top-up nitrate is an unverified scenario assumption.",
]

def run_simulation(c, days, feed_g_day, temp_C, precycled, initial):
    b, p, f = (values(c[s]) for s in ["biofilter", "plants", "fish"])
    V_L = sum(values(c["volumes_L"]).values())
    V_m3 = V_L / 1000
    media_area = b["media_L"] / 1000 * b["media_ssa_m2_per_m3"]
    area = media_area + b["dwc_nitrification_credit_m2"]
    r_tan = b["STR_ref_g_m2_d"] * b["theta_TAN"] ** (temp_C - b["T_ref_C"]) * b["long_term_factor"]
    r_no2 = b["SNR_ref_g_m2_d"] * b["theta_NO2"] ** (temp_C - b["T_ref_C"]) * b["long_term_factor"]
    tan_in = feed_g_day * f["protein_fraction"] * f["TAN_per_kg_protein"]
    planted = min(p["bed_area_m2"], max(p["min_planted_m2"], feed_g_day / p["frr_planting_g_m2_d"]))
    w = values(c["water"])
    makeup_N = w["topup_L_day"] * w["makeup_nitrate_N_mg_L"] / 1000
    sim = values(c["simulation"])
    y = [initial["TAN"], initial["NO2"], initial["NO3"], 0., 0., 0.]
    # Cumulative state: feed TAN, plant uptake, makeup N (all g N).
    def accl(day):
        return 1.0 if precycled else min(1., b["acclimation_start_frac"] + (1-b["acclimation_start_frac"]) * day / b["acclimation_days"])
    def rhs(t, y):
        A, I, N = [max(0., z) for z in y[:3]]
        af = accl(t)
        ox1 = r_tan * area * af * A / (b["K_TAN_mg_L"] + A)
        ox2 = r_no2 * area * af * I / (b["K_NO2_mg_L"] + I)
        uptake = p["uptake_max_gN_m2_d"] * planted * N / (p["K_NO3_mg_L"] + N)
        return [(tan_in-ox1)/V_m3, (ox1-ox2)/V_m3,
                (ox2-uptake+makeup_N)/V_m3, tan_in, uptake, makeup_N]
    sol = solve_ivp(rhs, (0, days), y, t_eval=list(range(days+1)),
                    max_step=sim["solver_max_step_day"], rtol=sim["solver_rtol"], atol=sim["solver_atol"])
    if not sol.success:
        raise RuntimeError("Numerical integration failed: " + sol.message)
    rows = [dict(day=int(t), TAN_N_mg_L=float(z[0]), nitrite_N_mg_L=float(z[1]),
                 nitrate_N_mg_L=float(z[2]), cumulative_feed_TAN_g=float(z[3]),
                 cumulative_plant_uptake_g=float(z[4]), cumulative_makeup_N_g=float(z[5]),
                 cumulative_topup_L=float(t*w["topup_L_day"])) for t,z in zip(sol.t, sol.y.T)]
    last = sol.y[:, -1]
    storage = (sum(last[:3])-sum(y[:3])) * V_m3
    residual = storage - (last[3] + last[5] - last[4])
    return {"label":"SIM", "source":"model/sim-nutrient-v4.py equations + configs/pilot-v2.json",
            "config":c["name"], "units":{"nutrients":"mg N/L", "mass_balance":"g N", "volume":"L"},
            "inputs":{"days":days,"feed_g_day":feed_g_day,"temp_C":temp_C,"precycled":precycled,"initial_mg_N_L":initial},
            "input_provenance":"ASSUME scenario overrides; defaults retain labels/sources from /config",
            "derived":{"label":"CALC", "source":"pilot-v2 working volumes, K1 bulk SSA and feed N equation",
                       "total_water_L":V_L,"media_area_m2":media_area,"planted_m2":planted,"feed_TAN_g_day":tan_in},
            "rows":rows,"mass_balance":{"label":"CALC","source":"SIM N ledger, storage minus inputs plus outputs",
                       "feed_TAN_g":float(last[3]),"makeup_N_g":float(last[5]),"plant_uptake_g":float(last[4]),
                       "storage_change_g":float(storage),"residual_g":float(residual)},
            "limitations":LIMITATIONS}

def plot_png(result):
    with PLOT_LOCK:
        fig, axes = plt.subplots(3,1,figsize=(9,8),sharex=True)
        rows = result["rows"]
        try:
            for ax, key, label in zip(axes, ["TAN_N_mg_L","nitrite_N_mg_L","nitrate_N_mg_L"],
                                      ["TAN-N", "Nitrite-N", "Nitrate-N"]):
                ax.plot([r["day"] for r in rows],[r[key] for r in rows],label=label)
                ax.set_ylabel("mg N/L"); ax.legend(); ax.grid(alpha=.2)
            axes[-1].set_xlabel("SIM day (not a field measurement)")
            fig.suptitle(f"Garage Pilot v2 — SIM, {result['derived']['total_water_L']:.1f} L\n"
                         f"{result['inputs']['feed_g_day']} g/day fixed feed, {result['inputs']['temp_C']} °C; not operating approval")
            fig.tight_layout(); buf = BytesIO(); fig.savefig(buf, format="png", dpi=130)
            return buf.getvalue()
        finally:
            plt.close(fig)
