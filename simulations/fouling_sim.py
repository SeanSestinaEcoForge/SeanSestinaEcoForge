import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

time_days = np.linspace(0, 365, 365)
initial_flow = 2.0
fouling_rate_base = 0.005
mitigation_pc = 0.7
mitigation_clean = 0.9

def fouling_curve(rate, mitigation=1.0):
    return initial_flow * np.exp(-rate * mitigation * time_days)

base_curve = fouling_curve(fouling_rate_base)
pc_curve = fouling_curve(fouling_rate_base, mitigation_pc)

clean_curve = pc_curve.copy()
for day in range(30, 366, 30):
    if day < len(clean_curve):
        recovery_factor = (mitigation_clean * initial_flow) / clean_curve[day - 1]
        clean_curve[day:] *= recovery_factor

plt.figure(figsize=(10,6))
plt.plot(time_days, base_curve, label='Base (Non-PC)')
plt.plot(time_days, pc_curve, label='PC Emitters')
plt.plot(time_days, clean_curve, label='PC + Monthly Clean')
plt.xlabel('Days')
plt.ylabel('Flow Rate (L/h)')
plt.title('EcoForge Drip Line Fouling Simulation')
plt.legend()
plt.grid(True)
os.makedirs('outputs', exist_ok=True)
plt.savefig(os.path.join('outputs', 'fouling_plot.png'))
plt.close()

print("Day 90 Base:", round(base_curve[90], 2))
print("Day 90 PC + Clean:", round(clean_curve[90], 2))
print("Plot saved to outputs/fouling_plot.png")
