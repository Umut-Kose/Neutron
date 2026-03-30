import numpy as np
import matplotlib.pyplot as plt

# Load data (energy in MeV, weight normalized to 1)
data = np.loadtxt("../AmBe_energy_spect.txt")
energy = data[:, 0]
weight = data[:, 1]

# Plot histogram-like spectrum
plt.figure(figsize=(8,5))
plt.step(energy, weight, where='mid', linewidth=1.8)
plt.fill_between(energy, weight, step='mid', alpha=0.3)

# Labels and formatting
plt.xlabel("Neutron Energy (MeV)", fontsize=12)
plt.ylabel("Normalized Weight", fontsize=12)
plt.title("AmBe Neutron Energy Spectrum", fontsize=14)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

