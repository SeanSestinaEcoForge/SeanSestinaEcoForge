import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Aquaponics Simulation Model
# This is a simple ODE-based model for an aquaponics system.
# It simulates the dynamics of fish biomass, plant biomass, and nutrient cycles:
# - Fish produce ammonia (waste) based on feed and growth.
# - Nitrifying bacteria convert ammonia to nitrite, then nitrite to nitrate.
# - Plants uptake nitrate for growth, cleaning the water.
# 
# Assumptions:
# - Closed-loop system with constant volume (e.g., 200 gallons water).
# - Simple logistic growth for fish and plants.
# - Michaelis-Menten kinetics for bacterial conversion and plant uptake.
# - No temperature, pH, or oxygen effects modeled (can be added later).
# - Parameters are approximate; tune based on real data.
# 
# Variables:
# y[0] = F: Fish biomass (kg)
# y[1] = P: Plant biomass (kg)
# y[2] = A: Ammonia concentration (mg/L NH3-N)
# y[3] = I: Nitrite concentration (mg/L NO2-N)
# y[4] = N: Nitrate concentration (mg/L NO3-N)
# 
# Parameters (example values for a small family-scale system):
# - V: System water volume (liters)
# - r_feed: Daily feed rate as % of fish biomass (0.02 = 2%)
# - e_ammonia: Ammonia excretion rate from feed (0.03 = 3% of feed becomes ammonia-N)
# - k1_max: Max ammonia oxidation rate by Nitrosomonas (mg/L/day)
# - Km1: Half-saturation constant for ammonia (mg/L)
# - k2_max: Max nitrite oxidation rate by Nitrobacter (mg/L/day)
# - Km2: Half-saturation constant for nitrite (mg/L)
# - r_p_max: Max plant nitrate uptake rate (mg/g plant/day)
# - Km_p: Half-saturation for plant uptake (mg/L)
# - r_f: Fish growth rate (1/day)
# - K_f: Fish carrying capacity (kg)
# - r_p: Plant growth rate coefficient (1/day)
# - K_p: Plant carrying capacity (kg)
# - m_f: Fish mortality rate (1/day)
# 
# References/Inspiration:
# - Based on models from papers like "Modelling an Aquaponic Ecosystem Using Ordinary Differential Equations" (Bobak & Kunze, 2016)
# - Standard nitrification kinetics from wastewater treatment models
# - Simplified for educational/simulation purposes

def aquaponics_model(y, t, params):
    F, P, A, I, N = y
    V, r_feed, e_ammonia, k1_max, Km1, k2_max, Km2, r_p_max, Km_p, r_f, K_f, r_p, K_p, m_f = params
    
    # Fish dynamics: logistic growth minus mortality
    dF_dt = r_f * F * (1 - F / K_f) - m_f * F
    
    # Ammonia production: from fish feed/waste
    feed = r_feed * F  # daily feed (kg/day)
    dA_dt = (e_ammonia * feed * 1000) / V  # convert to mg/L NH3-N (assuming 1kg feed ~1000g)
    
    # Bacterial conversion: Michaelis-Menten
    nitrosomonas_rate = k1_max * A / (Km1 + A)
    nitrobacter_rate = k2_max * I / (Km2 + I)
    dA_dt -= nitrosomonas_rate
    dI_dt = nitrosomonas_rate - nitrobacter_rate
    dN_dt = nitrobacter_rate
    
    # Plant dynamics: growth based on nitrate uptake (logistic cap)
    uptake_rate = r_p_max * P * N / (Km_p + N)  # mg/day
    dP_dt = r_p * (uptake_rate / 1000)  # convert mg to g for biomass
    dP_dt *= (1 - P / K_p)  # logistic limit
    dN_dt -= uptake_rate / V  # remove from water (mg/L)
    
    return [dF_dt, dP_dt, dA_dt, dI_dt, dN_dt]

# Example parameters for a 200L system
params = [
    200,      # V: volume (L)
    0.02,     # r_feed: feed % of biomass/day
    0.03,     # e_ammonia: ammonia-N from feed
    2.0,      # k1_max: max ammonia oxid (mg/L/day)
    1.0,      # Km1 (mg/L)
    5.0,      # k2_max: max nitrite oxid (mg/L/day)
    0.5,      # Km2 (mg/L)
    0.5,      # r_p_max: max uptake (mg N/g plant/day)
    10.0,     # Km_p (mg/L)
    0.01,     # r_f: fish growth rate (1/day)
    10.0,     # K_f: fish capacity (kg)
    0.005,    # r_p: plant growth coeff (g/mg N)
    20.0,     # K_p: plant capacity (kg)
    0.001     # m_f: fish mortality (1/day)
]

# Initial conditions
y0 = [
    1.0,      # F: initial fish (1 kg)
    0.5,      # P: initial plants (0.5 kg)
    0.0,      # A: initial ammonia (mg/L)
    0.0,      # I: initial nitrite
    5.0       # N: initial nitrate (seeded)
]

# Time points (simulate 100 days)
t = np.linspace(0, 100, 1000)

# Solve ODE
solution = odeint(aquaponics_model, y0, t, args=(params,))

# Unpack results
F, P, A, I, N = solution.T

# Plot results
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle('Aquaponics Simulation')

axs[0].plot(t, F, label='Fish Biomass (kg)')
axs[0].plot(t, P, label='Plant Biomass (kg)')
axs[0].set_ylabel('Biomass')
axs[0].legend()

axs[1].plot(t, A, label='Ammonia (mg/L)')
axs[1].plot(t, I, label='Nitrite (mg/L)')
axs[1].plot(t, N, label='Nitrate (mg/L)')
axs[1].set_ylabel('Nutrients')
axs[1].legend()

axs[2].plot(t, A + I + N, label='Total N (mg/L)')
axs[2].set_ylabel('Total Nitrogen')
axs[2].set_xlabel('Time (days)')
axs[2].legend()

plt.tight_layout()
plt.show()

# To run: Save as aquaponics_sim.py and execute in Python environment with numpy, scipy, matplotlib.
# Tune parameters based on your real system (e.g., measure actual ammonia production).
# Extensions: Add temperature dependence, pH effects, vermicomposting (e.g., extra organic breakdown term), or stochastic noise.
