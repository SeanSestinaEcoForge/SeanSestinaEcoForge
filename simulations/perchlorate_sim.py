import numpy as np
import matplotlib.pyplot as plt

perch_levels = [0, 0.1, 0.5, 1.0]
yield_reduction = [0, 10, 40, 70]
mitigation_microbes = 0.6
time_months = np.linspace(0, 12, 12)

def yield_curve(reduction, mitigation=1.0):
    base_yield = 100
    return base_yield * (1 - (reduction / 100) * mitigation) * (1 - 0.01 * time_months)

curves = {}
for level, red in zip(perch_levels, yield_reduction):
    curves[level] = yield_curve(red, mitigation_microbes)

plt.figure(figsize=(10,6))
for level, curve in curves.items():
    plt.plot(time_months, curve, label=f'{level}% Perchlorate')
plt.xlabel('Months')
plt.ylabel('Relative Yield (%)')
plt.title('EcoForge Perchlorate Tolerance Simulation')
plt.legend()
plt.grid(True)
plt.savefig('perch_plot.png')
plt.close()

print("Month 6 Yield at 0.5%:", round(curves[0.5][6], 2))
