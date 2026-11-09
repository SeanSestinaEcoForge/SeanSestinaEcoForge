"""Earth vs orbital solar yield stub (IDEA, cartoon multiplier; not a design number).

Run: python simulations/space_solar.py   (saves outputs/earth_vs_orbital_solar.png)
"""
import sys
from pathlib import Path

import matplotlib
if "--show" not in sys.argv:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

def solar_yield(base_watts: float, is_space: bool = False, glass_mass_kg: float = 10.0) -> tuple:
    """Simple solar yield simulation for Earth vs orbital (5x multiplier in space, no heavy glass).
    Inspired by Elon Musk/Dwarkesh Patel interview on space solar advantages."""
    if is_space:
        multiplier = 5.0  # 5x flux (no atmosphere/night)
        glass_mass_kg = 0.0  # No heavy glass needed in space
    else:
        multiplier = 1.0
    power = base_watts * multiplier
    return power, glass_mass_kg

if __name__ == "__main__":
    base = 1000.0  # Baseline watts per panel on Earth
    earth_power, earth_mass = solar_yield(base)
    space_power, space_mass = solar_yield(base, is_space=True)
    
    print(f"Earth: {earth_power} W, Glass mass: {earth_mass} kg")
    print(f"Orbital: {space_power} W, Glass mass: {space_mass} kg")
    
    # Simple bar chart viz
    labels = ['Earth', 'Orbital']
    powers = [earth_power, space_power]
    plt.bar(labels, powers)
    plt.ylabel('Power Yield (W)')
    plt.title('Earth vs Orbital Solar Yield')
    out = Path("outputs") / "earth_vs_orbital_solar.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out)
    print(f"Plot saved to {out}")
    if "--show" in sys.argv:
        plt.show()
    plt.close()
