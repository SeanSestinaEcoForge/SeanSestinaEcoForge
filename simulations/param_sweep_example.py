"""Temperature sweep of the enhanced aquaponics SIM: final nitrate vs water temperature.

Run from the repository root:
    python simulations/param_sweep_example.py
Outputs are SIM (teaching model, ASSUME parameters), not MEASURED.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aquaponics_vermiponics_enhanced_ph_alk import run_simulation  # noqa: E402


def main():
    temps = np.linspace(15, 35, 21)  # 15–35 °C
    nitrates = []
    for temp in temps:
        results = run_simulation(temperature=temp, days=30)
        nitrates.append(results["nitrate"][-1])

    print("Final nitrate after 30 days [SIM]:")
    for temp, nitrate in zip(temps[::5], nitrates[::5]):
        print(f"  {temp:4.0f} °C -> {nitrate:5.1f} mg/L")

    plt.plot(temps, nitrates, marker="o")
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Final Nitrate-N after 30 days (mg/L, SIM)")
    plt.title("Temperature Sensitivity – Nitrate Production (SIM)")
    plt.grid(True)
    out = Path("outputs") / "temp_nitrate_sweep.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    plt.close()
    print(f"Plot saved to {out}")


if __name__ == "__main__":
    main()
