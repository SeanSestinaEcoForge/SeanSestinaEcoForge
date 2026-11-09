"""
EcoForge Biogas / Anaerobic Digestion Simulation
ODE-based model for methane production, digestate return, and integration with vermiponics.

Labels: SIM teaching model; parameters are ASSUME household-scale examples, not MEASURED.
Simplification: methane is not mass-coupled to organic-matter loss.

Run from the repository root:
    python simulations/sim_biogas_digestion.py            # prints results
    python simulations/sim_biogas_digestion.py --plot     # also saves outputs/biogas_digestion.png
"""
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

def biogas_ode(t, y, params):
    """
    State variables:
    y[0] = Organic matter (kg)
    y[1] = Methane produced (m³)
    y[2] = Digestate nitrogen (kg N)
    y[3] = Temperature (°C)
    """
    OM, CH4, N_digestate, Temp = y
    k_hyd = params['k_hyd']          # hydrolysis rate (1/day)
    k_meth = params['k_meth']        # methanogenesis rate (1/day)
    Y_CH4 = params['Y_CH4']          # methane yield (m³/kg OM)
    N_content = params['N_content']  # nitrogen fraction in OM
    T_opt = params['T_opt']          # optimal temp (°C)
    T_sens = params['T_sens']        # temperature sensitivity

    # Temperature effect
    temp_factor = np.exp(-((Temp - T_opt)**2) / (2 * T_sens**2))

    # Rates
    dOM = -k_hyd * OM * temp_factor
    dCH4 = Y_CH4 * k_meth * OM * temp_factor
    dN = N_content * (-dOM)          # nitrogen released to digestate
    dTemp = 0.0                      # temperature held constant for now (can add heating later)

    return [dOM, dCH4, dN, dTemp]

# Default parameters (tuned for household-scale digester)
params = {
    'k_hyd': 0.25,      # hydrolysis rate
    'k_meth': 0.18,     # methanogenesis rate
    'Y_CH4': 0.45,      # m³ CH4 per kg OM destroyed
    'N_content': 0.035, # kg N per kg OM
    'T_opt': 35.0,      # mesophilic optimum
    'T_sens': 8.0       # temperature sensitivity
}

# Initial conditions
y0 = [50.0, 0.0, 0.0, 35.0]   # 50 kg OM start, 35°C

# Time span (30 days)
t_span = (0, 30)
t_eval = np.linspace(0, 30, 301)

# Solve
sol = solve_ivp(biogas_ode, t_span, y0, args=(params,), t_eval=t_eval, method='RK45')

# Results
days = sol.t
OM = sol.y[0]
CH4_total = sol.y[1]
N_digestate = sol.y[2]
Temp = sol.y[3]

print("=== Biogas Simulation Results (30 days) [SIM] ===")
print(f"Total methane produced: {CH4_total[-1]:.2f} m³")
print(f"Energy from methane: {CH4_total[-1] * 6.0:.1f} kWh")  # ~6 kWh per m³ CH4
print(f"Final digestate nitrogen: {N_digestate[-1]:.2f} kg N")
print(f"Average daily methane: {CH4_total[-1]/30:.3f} m³/day")

# Optional plot (pass --plot to save a PNG; never blocks)
if "--plot" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.plot(days, CH4_total, label='Cumulative Methane (m³)')
    plt.plot(days, N_digestate, label='Digestate N (kg)')
    plt.xlabel('Days')
    plt.ylabel('Value')
    plt.legend()
    plt.title('EcoForge Biogas Digestion SIM')
    plt.grid(True)
    out = Path("outputs") / "biogas_digestion.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    plt.close()
    print(f"Plot saved to {out}")
