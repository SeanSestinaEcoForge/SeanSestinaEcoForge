"""
aquaponics_vermiponics_enhanced_ph_alk.py - EcoForge (SIM, teaching model)

Enhanced aquaponics model with:
- Temperature dependence (Q10 scaling)
- Dissolved oxygen dynamics & crash thresholds
- Vermicomposting: organic solids decay -> ammonia release
- Alkalinity dynamics and a rough pH approximation with effects on nitrification

Labels: every output is SIM. Parameters are ASSUME example values for a 200 L
bench system, not MEASURED. The pH-from-alkalinity line is a rough linear
ASSUME approximation that ignores CO2/carbonate equilibrium; do not use it to
manage real fish. The tested garage-pilot model lives in ``api/``.

Safety: provided AS IS for experimental, educational, open-source research only.
Building or operating any EcoForge system carries serious risks (electrical,
biogas fire/explosion, chemical, biological, structural, flooding). You assume
100% of the risk. See DISCLAIMER.md and LICENSE (MIT) in the repository root.

Run (from the repository root):
    pip install -r requirements.txt
    python simulations/aquaponics_vermiponics_enhanced_ph_alk.py            # prints finals, saves PNG
    python simulations/aquaponics_vermiponics_enhanced_ph_alk.py --show     # also open a plot window

Tune params (e.g. T, k_worm_base, k_reaer) to match your real system.
"""
import argparse
from pathlib import Path

import numpy as np
from scipy.integrate import odeint

# Enhanced Aquaponics + Vermiponics Simulation
# States:
# y[0] = F   Fish biomass (kg)
# y[1] = P   Plant biomass (kg)
# y[2] = A   Ammonia-N (mg/L)
# y[3] = I   Nitrite-N (mg/L)
# y[4] = N   Nitrate-N (mg/L)
# y[5] = S   Organic solids in media (mg/L as N equivalent)
# y[6] = DO  Dissolved oxygen (mg/L)
# y[7] = Alk Alkalinity (mg/L CaCO3)

DEFAULT_OUTPUT = Path("outputs") / "aquaponics_vermiponics_enhanced_ph_alk.png"


def approx_pH(alk):
    """ASSUME: rough linear pH from alkalinity (mg/L CaCO3). Toy only."""
    return 6.2 + (alk / 100.0) * 0.6


def aquaponics_vermiponics_model(y, t, params):
    F, P, A, I, N, S, DO, Alk = y
    
    (V, T, Q10, r_feed_base, e_feed_to_solid, e_solid_to_ammonia,
     k1_max, Km1, k2_max, Km2, r_p_max, Km_p,
     r_f_base, K_f, r_p, K_p, m_f_base,
     k_worm_base, k_reaer, k_DO_fish, k_DO_bact, k_DO_decay,
     DO_crit, DO_half, alk_cons_amox, alk_add_uptake) = params
    
    # Temperature correction (Q10 = 2.0–3.0 typical for biological processes)
    Q = Q10 ** ((T - 20.0) / 10.0)
    
    # Approximate pH from alkalinity (rough linear approximation)
    pH = approx_pH(Alk)
    
    # pH factor for nitrification (decreases below pH 7.5, zero at 5.5)
    pH_fact = max(0.0, min(1.0, (pH - 5.5) / 2.0))
    
    # Fish dynamics
    r_f = r_f_base * Q
    m_f = m_f_base * (1 + (DO_crit - DO) / DO_half if DO < DO_crit else 0)
    dF_dt = r_f * F * (1 - F / K_f) - m_f * F
    
    # Feed → solids (uneaten + feces settle → organic pool)
    feed = r_feed_base * F * Q  # temperature affects appetite/metabolism
    dS_dt = e_feed_to_solid * feed * 1000 / V   # mg/L solids-N equiv
    
    # Vermicomposting: worms break down solids → ammonia
    worm_activity = k_worm_base * Q * (DO / (DO_half + DO))  # temp + DO limited
    dS_dt -= worm_activity * S
    dA_dt = worm_activity * S * e_solid_to_ammonia
    
    # Nitrification (DO, temp, and pH limited)
    nitr1 = k1_max * Q * (DO / (DO_half + DO)) * A / (Km1 + A) * pH_fact
    nitr2 = k2_max * Q * (DO / (DO_half + DO)) * I / (Km2 + I) * pH_fact
    dA_dt -= nitr1
    dI_dt = nitr1 - nitr2
    dN_dt = nitr2
    
    # Plant uptake (nitrate preferred, temp limited)
    uptake = r_p_max * P * Q * N / (Km_p + N)
    dP_dt = r_p * (uptake / 1000) * (1 - P / K_p)  # g/day
    dN_dt -= uptake / V
    
    # Alkalinity dynamics
    dAlk_dt = -alk_cons_amox * nitr1 + alk_add_uptake * (uptake / V)
    
    # Dissolved Oxygen dynamics
    reaer = k_reaer * (8.5 - DO)                    # saturation ~8.5 mg/L at 20°C
    fish_cons = k_DO_fish * F * Q / V
    bact_cons = 3.43 * nitr1 + 1.14 * nitr2        # correct O2 consumption for nitrification
    decay_cons = k_DO_decay * worm_activity * S     # adjusted for units (assuming k includes /V if needed)
    dDO_dt = reaer - fish_cons - bact_cons - decay_cons
    
    return [dF_dt, dP_dt, dA_dt, dI_dt, dN_dt, dS_dt, dDO_dt, dAlk_dt]

# Example parameters (ASSUME; 200 L system, ~20 °C base)
PARAMS = [
    200.0,      # V: volume (L)
    22.0,       # T: temperature (°C) — you can make this time-dependent later
    2.5,        # Q10: temperature sensitivity factor
    0.025,      # r_feed_base: feed rate (% body weight / day at 20°C)
    0.60,       # e_feed_to_solid: fraction of feed → settleable solids
    0.35,       # e_solid_to_ammonia: fraction of decayed solids → NH3-N
    3.0,        # k1_max: ammonia oxidation (mg N/L/day at 20°C)
    1.0,        # Km1
    6.0,        # k2_max: nitrite oxidation
    0.7,        # Km2
    0.8,        # r_p_max: nitrate uptake (mg N/g plant/day)
    12.0,       # Km_p
    0.015,      # r_f_base: fish growth (1/day at 20°C)
    12.0,       # K_f: carrying capacity (kg)
    0.008,      # r_p: plant growth scaling
    25.0,       # K_p: plant cap (kg)
    0.0015,     # m_f_base: base mortality (1/day)
    0.15,       # k_worm_base: worm decay rate (1/day at 20°C)
    0.8,        # k_reaer: reaeration coefficient (1/day)
    0.12,       # k_DO_fish: fish O2 consumption (mg/L per kg fish per day)
    0.0005,     # k_DO_bact: not used now
    0.0003,     # k_DO_decay: decay O2 demand scaling
    4.0,        # DO_crit: critical DO threshold (mg/L)
    2.0,        # DO_half: half-saturation for limitation
    7.14,       # alk_cons_amox: alkalinity consumption for ammonia oxidation (mg CaCO3/mg N)
    3.57        # alk_add_uptake: alkalinity addition from plant nitrate uptake (mg CaCO3/mg N)
]

# Initial conditions (ASSUME example): added initial Alk=150 mg/L
Y0 = [1.2, 0.8, 0.1, 0.0, 8.0, 5.0, 7.5, 150.0]
TEMPERATURE_INDEX = 1


def run_simulation(temperature=None, days=120, points_per_day=10):
    """Solve the model and return a dict of numpy arrays (all SIM).

    temperature: water temperature in deg C (default: the PARAMS value, 22 C).
    days: simulated horizon in days.
    """
    params = list(PARAMS)
    if temperature is not None:
        params[TEMPERATURE_INDEX] = float(temperature)
    t = np.linspace(0, days, int(days * points_per_day))
    solution = odeint(aquaponics_vermiponics_model, Y0, t, args=(params,))
    F, P, A, I, N, S, DO, Alk = solution.T
    return {
        "t": t, "fish": F, "plants": P, "ammonia": A, "nitrite": I,
        "nitrate": N, "solids": S, "DO": DO, "alkalinity": Alk,
        "pH_approx": approx_pH(Alk), "temperature": params[TEMPERATURE_INDEX],
    }


def plot_results(r, path=None, show=False):
    import matplotlib
    if not show:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = r["t"]
    fig, axs = plt.subplots(5, 1, figsize=(11, 16), sharex=True)
    fig.suptitle('Enhanced Aquaponics + Vermiponics SIM with pH/Alkalinity (120 days)')

    axs[0].plot(t, r["fish"], label='Fish biomass (kg)')
    axs[0].plot(t, r["plants"], label='Plant biomass (kg)')
    axs[0].legend(); axs[0].set_ylabel('Biomass')

    axs[1].plot(t, r["ammonia"], label='Ammonia-N'); axs[1].plot(t, r["nitrite"], label='Nitrite-N')
    axs[1].plot(t, r["nitrate"], label='Nitrate-N'); axs[1].plot(t, r["solids"], label='Organic solids')
    axs[1].legend(); axs[1].set_ylabel('Nutrients / Solids (mg/L)')

    axs[2].plot(t, r["DO"], 'tab:cyan', label='Dissolved Oxygen (mg/L)')
    axs[2].axhline(4.0, color='red', ls='--', alpha=0.6, label='Critical DO')
    axs[2].legend(); axs[2].set_ylabel('DO (mg/L)')

    axs[3].plot(t, r["alkalinity"], label='Alkalinity (mg/L CaCO3)')
    axs[3].legend(); axs[3].set_ylabel('Alkalinity')

    axs[4].plot(t, r["pH_approx"], label='Approx pH (ASSUME toy)', color='purple')
    axs[4].legend(); axs[4].set_ylabel('pH')
    axs[4].set_xlabel('Time (days)')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
    if show:
        plt.show()
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description="EcoForge enhanced aquaponics + vermiponics SIM")
    parser.add_argument("--days", type=float, default=120)
    parser.add_argument("--temperature", type=float, default=None, help="water temperature, deg C")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="PNG path ('' to skip saving)")
    parser.add_argument("--show", action="store_true", help="open an interactive plot window")
    args = parser.parse_args(argv)

    r = run_simulation(temperature=args.temperature, days=args.days)
    t = r["t"]
    print(f"Final values (day {t[-1]:.0f}) [SIM]:")
    print(f"  Fish: {r['fish'][-1]:.2f} kg")
    print(f"  Plants: {r['plants'][-1]:.2f} kg")
    print(f"  Nitrate: {r['nitrate'][-1]:.1f} mg/L")
    print(f"  DO: {r['DO'][-1]:.1f} mg/L")
    print(f"  Organic solids: {r['solids'][-1]:.1f} mg/L")
    print(f"  Alkalinity: {r['alkalinity'][-1]:.1f} mg/L")
    print(f"  Approx pH: {r['pH_approx'][-1]:.1f}")

    plot_results(r, path=args.out or None, show=args.show)
    if args.out:
        print(f"Plot saved to {args.out}")


if __name__ == "__main__":
    main()
