#!/usr/bin/env python3
"""
Time-of-Flight (ToF) Analysis for AmBe Source with HDPE Moderator

Estimates the ToF difference between 4.5 MeV gamma rays and moderated neutrons
reaching PMTs placed at front and back of HDPE block.

Setup:
- AmBe source inside 10 cm HDPE block
- PMT positions: back (before HDPE) and front (20 cm from source, after HDPE)
- Gamma: 4.5 MeV from AmBe
- Neutrons: Initial spectrum from AmBe, moderated through HDPE
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Physical constants
c_light = 299792458  # m/s (speed of light)
neutron_mass = 939.565  # MeV/c^2

def neutron_velocity(E_MeV):
    """
    Calculate neutron velocity from kinetic energy using relativistic formula.
    For low energies (<10 MeV), classical approximation is sufficient.
    
    v = c * sqrt(1 - 1/(1 + E/m_n)^2)
    
    For non-relativistic (E << m_n):
    v ≈ sqrt(2*E/m_n) * c
    """
    # Classical approximation (valid for neutrons up to ~10 MeV)
    v = c_light * np.sqrt(2 * E_MeV / neutron_mass)
    return v  # m/s

def gamma_velocity():
    """Photons always travel at speed of light"""
    return c_light  # m/s

def time_of_flight(distance_m, velocity_m_per_s):
    """Calculate time of flight in nanoseconds"""
    return distance_m / velocity_m_per_s * 1e9  # ns

def estimate_moderated_spectrum_stats(data_file):
    """
    Load neutron energies after HDPE moderation and calculate statistics.
    """
    if not os.path.exists(data_file):
        print(f"Warning: {data_file} not found. Using analytical estimates.")
        return None
    
    energies = []
    with open(data_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            try:
                energies.append(float(line))
            except ValueError:
                continue
    
    if not energies:
        return None
    
    energies = np.array(energies)
    return {
        'mean': np.mean(energies),
        'median': np.median(energies),
        'std': np.std(energies),
        'min': np.min(energies),
        'max': np.max(energies),
        'energies': energies
    }

def main():
    print("=" * 70)
    print("AmBe Source + HDPE Moderator: Time-of-Flight Analysis")
    print("=" * 70)
    
    # Geometry setup
    hdpe_thickness = 0.10  # 10 cm = 0.10 m
    pmt_distance = 0.20  # Both PMTs ~20 cm from source
    
    # Source is inside the 10 cm HDPE block
    # Both PMTs are placed ~20 cm away from the source
    # Back PMT: behind the source (gamma travels through ~5 cm HDPE, neutrons minimal HDPE)
    # Front PMT: in front of source (both gamma and neutrons travel through ~5 cm HDPE)
    source_position = 0.0  # m (reference point)
    back_pmt_distance = pmt_distance  # ~20 cm
    front_pmt_distance = pmt_distance  # ~20 cm
    
    # Path through HDPE
    hdpe_path_back = hdpe_thickness / 2  # ~5 cm for gamma going back
    hdpe_path_front = hdpe_thickness / 2  # ~5 cm for particles going forward
    
    print(f"\nGeometry:")
    print(f"  HDPE thickness: {hdpe_thickness*100:.1f} cm")
    print(f"  Source position: inside HDPE block (center)")
    print(f"  Back PMT distance from source: {back_pmt_distance*100:.1f} cm")
    print(f"  Front PMT distance from source: {front_pmt_distance*100:.1f} cm")
    print(f"  HDPE path to back PMT: ~{hdpe_path_back*100:.1f} cm")
    print(f"  HDPE path to front PMT: ~{hdpe_path_front*100:.1f} cm")
    print(f"  Note: Neutrons are moderated through the full {hdpe_thickness*100:.1f} cm HDPE")
    
    # Gamma ray (4.5 MeV) - travels at speed of light
    E_gamma = 4.5  # MeV
    v_gamma = gamma_velocity()
    
    tof_gamma_back = time_of_flight(back_pmt_distance, v_gamma)
    tof_gamma_front = time_of_flight(front_pmt_distance, v_gamma)
    
    print(f"\n{'='*70}")
    print(f"GAMMA RAY (4.5 MeV)")
    print(f"{'='*70}")
    print(f"  Velocity: {v_gamma:.6e} m/s (c)")
    print(f"  ToF to back PMT ({back_pmt_distance*100:.1f} cm): {tof_gamma_back:.4f} ns")
    print(f"  ToF to front PMT ({front_pmt_distance*100:.1f} cm): {tof_gamma_front:.4f} ns")
    
    # Load moderated neutron spectrum
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_file = os.path.join(ROOT, 'neutron_energies_after_hdpe_10cm.txt')
    
    stats = estimate_moderated_spectrum_stats(data_file)
    
    print(f"\n{'='*70}")
    print(f"MODERATED NEUTRONS (after 10 cm HDPE)")
    print(f"{'='*70}")
    
    if stats:
        print(f"  Loaded {len(stats['energies'])} neutron events")
        print(f"  Energy statistics (MeV):")
        print(f"    Mean: {stats['mean']:.4f}")
        print(f"    Median: {stats['median']:.4f}")
        print(f"    Std Dev: {stats['std']:.4f}")
        print(f"    Min: {stats['min']:.4e}")
        print(f"    Max: {stats['max']:.4f}")
        
        # Calculate velocities and ToF for various energy ranges
        # Thermal neutrons (~0.025 eV at room temp)
        E_thermal = 0.025e-6  # MeV
        # Epithermal (~1 eV)
        E_epithermal = 1e-6  # MeV
        # Fast neutrons (typical moderated: 0.1 - 1 MeV)
        E_fast_low = 0.1  # MeV
        E_fast_high = 1.0  # MeV
        
        energies_to_test = {
            'Thermal (0.025 eV)': E_thermal,
            'Epithermal (1 eV)': E_epithermal,
            'Fast-low (0.1 MeV)': E_fast_low,
            'Fast-high (1 MeV)': E_fast_high,
            'Mean energy': stats['mean'],
            'Median energy': stats['median'],
        }
        
        print(f"\n  Velocity and ToF for representative energies:")
        print(f"  {'Energy Type':<25} {'E (MeV)':<12} {'v (m/s)':<12} {'ToF Back (ns)':<15} {'ToF Front (ns)':<15}")
        print(f"  {'-'*85}")
        
        tof_results = {}
        for label, E in energies_to_test.items():
            v = neutron_velocity(E)
            tof_back = time_of_flight(back_pmt_distance, v)
            tof_front = time_of_flight(front_pmt_distance, v)
            tof_results[label] = {
                'energy': E,
                'velocity': v,
                'tof_back': tof_back,
                'tof_front': tof_front
            }
            print(f"  {label:<25} {E:<12.4e} {v:<12.2f} {tof_back:<15.2f} {tof_front:<15.2f}")
    
    else:
        # Analytical estimates if file not found
        print("  Using analytical estimates:")
        # After ~10 cm HDPE, neutrons are significantly moderated
        # Typical energies: 0.1 keV to 1 MeV
        energies_to_test = {
            'Thermal (0.025 eV)': 0.025e-6,
            'Epithermal (1 eV)': 1e-6,
            'Fast (0.1 MeV)': 0.1,
            'Fast (1 MeV)': 1.0,
        }
        
        tof_results = {}
        for label, E in energies_to_test.items():
            v = neutron_velocity(E)
            tof_back = time_of_flight(back_pmt_distance, v)
            tof_front = time_of_flight(front_pmt_distance, v)
            tof_results[label] = {
                'energy': E,
                'velocity': v,
                'tof_back': tof_back,
                'tof_front': tof_front
            }
    
    # Calculate time differences (gamma - neutron)
    print(f"\n{'='*70}")
    print(f"TIME DIFFERENCES: Neutron ToF - Gamma ToF (Δt)")
    print(f"{'='*70}")
    print(f"  (Positive values mean neutron arrives later than gamma)")
    print(f"\n  BACK PMT (20 cm from source):")
    print(f"    Gamma ToF: {tof_gamma_back:.4f} ns")
    print(f"  {'Neutron Type':<25} {'Neutron ToF (ns)':<20} {'Δt (ns)':<15}")
    print(f"  {'-'*65}")
    
    for label, result in tof_results.items():
        dt_back = result['tof_back'] - tof_gamma_back
        print(f"  {label:<25} {result['tof_back']:<20.2f} {dt_back:<15.2f}")
    
    print(f"\n  FRONT PMT (20 cm from source):")
    print(f"    Gamma ToF: {tof_gamma_front:.4f} ns")
    print(f"  {'Neutron Type':<25} {'Neutron ToF (ns)':<20} {'Δt (ns)':<15}")
    print(f"  {'-'*65}")
    
    for label, result in tof_results.items():
        dt_front = result['tof_front'] - tof_gamma_front
        print(f"  {label:<25} {result['tof_front']:<20.2f} {dt_front:<15.2f}")
    
    # Create visualization
    if stats:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Energy spectrum histogram
        ax = axes[0, 0]
        ax.hist(stats['energies'], bins=100, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Neutron Energy (MeV)')
        ax.set_ylabel('Counts')
        ax.set_title('Neutron Energy Spectrum after 10 cm HDPE')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        
        # 2. Energy spectrum (log scale)
        ax = axes[0, 1]
        ax.hist(stats['energies'], bins=np.logspace(np.log10(max(stats['min'], 1e-9)), 
                                                     np.log10(stats['max']), 100), 
                alpha=0.7, edgecolor='black')
        ax.set_xlabel('Neutron Energy (MeV)')
        ax.set_ylabel('Counts')
        ax.set_title('Neutron Energy Spectrum (log scale)')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        
        # 3. ToF comparison - Back PMT
        ax = axes[1, 0]
        labels_short = [l.split('(')[0].strip() for l in tof_results.keys()]
        tof_back_values = [r['tof_back'] for r in tof_results.values()]
        
        bars = ax.barh(labels_short, tof_back_values, alpha=0.7, edgecolor='black')
        ax.axvline(tof_gamma_back, color='red', linestyle='--', linewidth=2, label='Gamma (4.5 MeV)')
        ax.set_xlabel('Time of Flight (ns)')
        ax.set_title(f'ToF to Back PMT (~{back_pmt_distance*100:.0f} cm from source)')
        ax.set_xscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. ToF comparison - Front PMT
        ax = axes[1, 1]
        tof_front_values = [r['tof_front'] for r in tof_results.values()]
        
        bars = ax.barh(labels_short, tof_front_values, alpha=0.7, edgecolor='black')
        ax.axvline(tof_gamma_front, color='red', linestyle='--', linewidth=2, label='Gamma (4.5 MeV)')
        ax.set_xlabel('Time of Flight (ns)')
        ax.set_title(f'ToF to Front PMT (~{front_pmt_distance*100:.0f} cm from source)')
        ax.set_xscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_file = os.path.join(ROOT, 'tof_analysis.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n{'='*70}")
        print(f"Figure saved to: {output_file}")
        print(f"{'='*70}")
        
        plt.show()
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Setup: AmBe source inside 10 cm HDPE, both PMTs at ~20 cm distance")
    print(f"\nFor typical moderated neutrons (~0.1-1 MeV):")
    print(f"  - Gamma (4.5 MeV) arrives in ~0.67 ns at both PMTs")
    print(f"  - Fast neutrons (1 MeV) arrive in ~14.5 ns")
    print(f"  - Slow neutrons (0.1 MeV) arrive in ~45.7 ns")
    print(f"  - Thermal neutrons (0.025 eV) arrive in ~91.5 μs")
    print(f"\nTime difference (Δt = neutron - gamma) at 20 cm:")
    print(f"  - Fast neutrons (~1 MeV): ~14 ns delay")
    print(f"  - Moderated neutrons (~0.3 MeV median): ~27 ns delay")
    print(f"  - Slow neutrons (~0.1 MeV): ~45 ns delay")
    print(f"  - Thermal neutrons (~0.025 eV): ~91 μs delay")
    print(f"\nKey insight: Since both PMTs are equidistant (~20 cm),")
    print(f"the ToF difference is the SAME for both detectors!")
    print(f"This can be used for particle identification (PID) and")
    print(f"gamma-neutron discrimination in coincidence measurements.")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
