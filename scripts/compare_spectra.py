#!/usr/bin/env python3
"""
Compare AmBe neutron energy spectrum before and after HDPE moderation.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Physical setup
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_ambe_spectrum(filename):
    """Load the original AmBe neutron energy spectrum."""
    energies = []
    weights = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    energies.append(float(parts[0]))
                    weights.append(float(parts[1]))
                except ValueError:
                    continue
    
    return np.array(energies), np.array(weights)

def load_moderated_energies(filename):
    """Load neutron energies after HDPE moderation."""
    energies = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            try:
                energies.append(float(line))
            except ValueError:
                continue
    
    return np.array(energies)

def main():
    print("=" * 70)
    print("AmBe Neutron Spectrum: Before vs After HDPE Moderation")
    print("=" * 70)
    
    # Load original AmBe spectrum
    ambe_file = os.path.join(ROOT, 'ambe_spectrum.txt')
    E_orig, W_orig = load_ambe_spectrum(ambe_file)
    
    # Normalize weights
    W_orig = W_orig / W_orig.sum()
    
    print(f"\nOriginal AmBe Spectrum:")
    print(f"  Energy range: {E_orig.min():.4f} - {E_orig.max():.4f} MeV")
    print(f"  Number of points: {len(E_orig)}")
    print(f"  Mean energy: {np.average(E_orig, weights=W_orig):.3f} MeV")
    print(f"  Median energy: {E_orig[len(E_orig)//2]:.3f} MeV")
    
    # Load moderated spectrum
    moderated_files = {
        '5 cm HDPE': os.path.join(ROOT, 'neutron_energies_after_hdpe_5cm.txt'),
        '10 cm HDPE': os.path.join(ROOT, 'neutron_energies_after_hdpe_10cm.txt'),
        '15 cm HDPE': os.path.join(ROOT, 'neutron_energies_after_hdpe_15cm.txt'),
    }
    
    moderated_data = {}
    for label, filepath in moderated_files.items():
        if os.path.exists(filepath):
            energies = load_moderated_energies(filepath)
            moderated_data[label] = energies
            print(f"\n{label}:")
            print(f"  Energy range: {energies.min():.4e} - {energies.max():.4f} MeV")
            print(f"  Number of events: {len(energies)}")
            print(f"  Mean energy: {energies.mean():.3f} MeV")
            print(f"  Median energy: {np.median(energies):.3f} MeV")
    
    # Create comprehensive comparison plots
    fig = plt.figure(figsize=(16, 10))
    
    # Plot 1: Original spectrum (line plot)
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(E_orig, W_orig, 'o-', linewidth=2, markersize=6, label='AmBe Source', color='red')
    ax1.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax1.set_ylabel('Normalized Probability', fontsize=11)
    ax1.set_title('Original AmBe Neutron Spectrum', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Original spectrum (log scale)
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(E_orig, W_orig, 'o-', linewidth=2, markersize=6, label='AmBe Source', color='red')
    ax2.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax2.set_ylabel('Normalized Probability', fontsize=11)
    ax2.set_title('Original AmBe Spectrum (Log Scale)', fontsize=12, fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3, which='both')
    ax2.legend()
    
    # Plot 3: Moderated spectra histograms
    ax3 = plt.subplot(2, 3, 3)
    colors = ['blue', 'green', 'orange']
    for (label, energies), color in zip(moderated_data.items(), colors):
        counts, bins = np.histogram(energies, bins=100, range=(0, 12))
        counts_norm = counts / counts.sum() / (bins[1] - bins[0])
        bin_centers = (bins[:-1] + bins[1:]) / 2
        ax3.plot(bin_centers, counts_norm, '-', linewidth=2, label=label, color=color, alpha=0.7)
    
    ax3.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax3.set_ylabel('Probability Density (MeV⁻¹)', fontsize=11)
    ax3.set_title('After HDPE Moderation (Linear)', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_xlim(0, 12)
    
    # Plot 4: Combined comparison (linear)
    ax4 = plt.subplot(2, 3, 4)
    # Plot original as histogram for fair comparison
    orig_counts, orig_bins = np.histogram(np.repeat(E_orig, (W_orig * 1000).astype(int)), 
                                          bins=100, range=(0, 12))
    orig_counts_norm = orig_counts / orig_counts.sum() / (orig_bins[1] - orig_bins[0])
    orig_centers = (orig_bins[:-1] + orig_bins[1:]) / 2
    ax4.plot(orig_centers, orig_counts_norm, '-', linewidth=2.5, label='Before (AmBe)', 
             color='red', alpha=0.8)
    
    for (label, energies), color in zip(moderated_data.items(), colors):
        counts, bins = np.histogram(energies, bins=100, range=(0, 12))
        counts_norm = counts / counts.sum() / (bins[1] - bins[0])
        bin_centers = (bins[:-1] + bins[1:]) / 2
        ax4.plot(bin_centers, counts_norm, '-', linewidth=2, label=f'After ({label})', 
                color=color, alpha=0.7)
    
    ax4.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax4.set_ylabel('Probability Density (MeV⁻¹)', fontsize=11)
    ax4.set_title('Before vs After: Linear Scale', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    ax4.set_xlim(0, 12)
    
    # Plot 5: Combined comparison (log-log)
    ax5 = plt.subplot(2, 3, 5)
    for (label, energies), color in zip(moderated_data.items(), colors):
        bins = np.logspace(np.log10(max(energies.min(), 1e-9)), np.log10(energies.max()), 100)
        counts, _ = np.histogram(energies, bins=bins)
        counts_norm = counts / counts.sum() / np.diff(bins)
        bin_centers = np.sqrt(bins[:-1] * bins[1:])
        valid = counts > 0
        ax5.plot(bin_centers[valid], counts_norm[valid], '-', linewidth=2, 
                label=f'After ({label})', color=color, alpha=0.7)
    
    # Add original spectrum
    ax5.plot(E_orig, W_orig / (E_orig[1] - E_orig[0]), 'o-', linewidth=2.5, 
            markersize=6, label='Before (AmBe)', color='red', alpha=0.8)
    
    ax5.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax5.set_ylabel('Probability Density (MeV⁻¹)', fontsize=11)
    ax5.set_title('Before vs After: Log-Log Scale', fontsize=12, fontweight='bold')
    ax5.set_xscale('log')
    ax5.set_yscale('log')
    ax5.grid(True, alpha=0.3, which='both')
    ax5.legend()
    
    # Plot 6: Cumulative distribution functions
    ax6 = plt.subplot(2, 3, 6)
    # Original CDF
    E_sorted = np.sort(np.repeat(E_orig, (W_orig * 1000).astype(int)))
    cdf_orig = np.arange(1, len(E_sorted) + 1) / len(E_sorted)
    ax6.plot(E_sorted, cdf_orig, '-', linewidth=2.5, label='Before (AmBe)', 
            color='red', alpha=0.8)
    
    for (label, energies), color in zip(moderated_data.items(), colors):
        E_sorted = np.sort(energies)
        cdf = np.arange(1, len(E_sorted) + 1) / len(E_sorted)
        ax6.plot(E_sorted, cdf, '-', linewidth=2, label=f'After ({label})', 
                color=color, alpha=0.7)
    
    ax6.set_xlabel('Neutron Energy (MeV)', fontsize=11)
    ax6.set_ylabel('Cumulative Probability', fontsize=11)
    ax6.set_title('Cumulative Distribution Functions', fontsize=12, fontweight='bold')
    ax6.set_xscale('log')
    ax6.grid(True, alpha=0.3, which='both')
    ax6.legend()
    ax6.set_xlim(1e-9, 15)
    
    plt.tight_layout()
    
    output_file = os.path.join(ROOT, 'spectrum_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n{'='*70}")
    print(f"Figure saved to: {output_file}")
    print(f"{'='*70}")
    
    # Additional statistics
    if '10 cm HDPE' in moderated_data:
        E_mod = moderated_data['10 cm HDPE']
        print(f"\nModeration Effects (10 cm HDPE):")
        print(f"  Mean energy reduction: {np.average(E_orig, weights=W_orig):.3f} → {E_mod.mean():.3f} MeV")
        print(f"  Median energy reduction: {E_orig[len(E_orig)//2]:.3f} → {np.median(E_mod):.3f} MeV")
        
        # Count neutrons in different energy ranges
        thermal = np.sum(E_mod < 1e-6)  # < 1 eV
        epithermal = np.sum((E_mod >= 1e-6) & (E_mod < 0.1))  # 1 eV - 0.1 MeV
        fast = np.sum(E_mod >= 0.1)  # > 0.1 MeV
        
        print(f"\n  Energy distribution after moderation:")
        print(f"    Thermal (< 1 eV):       {thermal:6d} events ({100*thermal/len(E_mod):5.1f}%)")
        print(f"    Epithermal (1 eV-0.1 MeV): {epithermal:6d} events ({100*epithermal/len(E_mod):5.1f}%)")
        print(f"    Fast (> 0.1 MeV):       {fast:6d} events ({100*fast/len(E_mod):5.1f}%)")
    
    plt.show()

if __name__ == '__main__':
    main()
