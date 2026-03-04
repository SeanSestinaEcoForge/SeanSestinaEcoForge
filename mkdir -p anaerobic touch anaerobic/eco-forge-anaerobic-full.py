# eco-forge-anaerobic-full.py
# Full anaerobic digestion simulation with 3-stage upgrade and additives print
# Fixed all F821 undefined name errors

import numpy as np
from scipy.integrate import odeint
import pandas as pd

# Placeholder for your digester ODE function (define if not already in file)
def digester_ode(y, t, args):
    # Your ODE equations here - placeholder example
    S_ac, X_ac, VFA, TAN, H2S, CH4_rate = y
    # ... implement kinetics ...
    dS_ac_dt = 0.0  # example
    dX_ac_dt = 0.0
    dVFA_dt = 0.0
    dTAN_dt = 0.0
    dH2S_dt = 0.0
    dCH4_rate_dt = 0.0
    return [dS_ac_dt, dX_ac_dt, dVFA_dt, dTAN_dt, dH2S_dt, dCH4_rate_dt]

# Placeholder for stage_sep function (define if missing)
def stage_sep(F_to, y_to, theta):
    # Your separation logic here - placeholder returns
    F_r = F_to * 0.5
    y_r = y_to
    F_p = F_to - F_r
    y_p = y_to * 0.8
    area = 10.0  # m² placeholder
    return F_r, y_r, F_p, y_p, area

# 3-stage upgrade function (from your screenshot - cleaned)
def upgrade_3stage(F_feed, y_CH4_feed, theta=[0.62, 0.58, 0.52]):
    F_rec = 0.0
    y_rec = y_CH4_feed
    area_total = 0.0
    
    for th in theta:
        F_to = F_feed + F_rec
        y_to = (F_feed * y_CH4_feed + F_rec * y_rec) / F_to if F_to > 0 else 0
        
        F_r, y_r, F_p, y_p, area = stage_sep(F_to, y_to, th)
        area_total += area
        
        F_rec = F_r
        y_rec = y_r
    
    biomethane = F_r
    purity = y_r * 100
    recovery = (biomethane * y_r) / (F_feed * y_CH4_feed) * 100 if F_feed > 0 else 0
    energy = 0.30 + 0.05 * (1 - 0.25)  # kWh/Nm³ example
    
    return {
        'biomethane_nm3h': biomethane,
        'purity_pct': purity,
        'recovery_pct': recovery,
        'area_m2': area_total,
        'energy_kwh_nm3': energy
    }

# Full simulation run - fixed undefined names in print
def run_full():
    print("EcoForge Anaerobic Full Run Starting...")
    
    # Fixed F821 undefined names - placeholders (replace with real calcs later)
    use_biochar = True
    use_hydrochar = False
    biochar_g_per_L = 0.0      # TODO: derive from steady-state or args
    hydrochar_g_per_L = 0.0    # TODO: derive from steady-state or args
    
    print(f"Additives: Biochar {use_biochar} ({biochar_g_per_L} g/L) | Hydrochar {use_hydrochar} ({hydrochar_g_per_L} g/L)")
    
    t = np.linspace(0, 90, 901)
    y0 = [1.5, 0.8, 0.4, 800, 12, 0.0]
    args = (45.0, 50.0, 1000.0)
    
    sol = odeint(digester_ode, y0, t, args=args)
    
    df = pd.DataFrame(sol, columns=['S_ac', 'X_ac', 'VFA', 'TAN', 'H2S', 'CH4_rate'])
    df['time'] = t
    df['pH'] = 7.2 - 0.8 * np.log10(1 + df['VFA']/1.5 + 0.01)
    df['biogas_nm3h'] = df['CH4_rate'] * 0.35 / 0.58
    df['y_CH4'] = 0.58 - 0.05 * (df['VFA']/4.0) + 0.02 * np.random.normal(0, 0.02, len(df))
    
    steady = df.iloc[-200:]
    avg_biogas = steady['biogas_nm3h'].mean()
    avg_y = steady['y_CH4'].mean()
    
    print(f"Average biogas production: {avg_biogas:.2f} Nm³/h")
    print(f"Average CH4 yield: {avg_y:.2f}")

# Run it if script executed directly
if __name__ == "__main__":
    run_full()
