# Time-of-Flight Analysis: AmBe Source with HDPE Moderator

## Setup
- **AmBe source**: Placed at center of 10 cm HDPE block
- **HDPE thickness**: 10 cm (moderator)
- **PMT positions**:
  - Back PMT: 5 cm from source (at back edge of HDPE)
  - Front PMT: 25 cm from source (20 cm away from HDPE block)
- **Particles**:
  - Gamma: 4.5 MeV (from AmBe)
  - Neutrons: Initial spectrum from AmBe, moderated through HDPE

## Moderated Neutron Spectrum (after 10 cm HDPE)
Based on 30,466 simulated neutron events:
- **Mean energy**: 1.83 MeV
- **Median energy**: 0.29 MeV
- **Energy range**: 0.45 neV to 10.73 MeV
- **Standard deviation**: 2.51 MeV

The wide distribution shows a mix of:
- Fast neutrons (>0.1 MeV): still retain significant energy
- Epithermal neutrons (eV range): partially moderated
- Thermal neutrons (<0.1 eV): fully thermalized

## Time-of-Flight Results

### Gamma Ray (4.5 MeV)
| PMT Location | Distance | ToF |
|-------------|----------|-----|
| Back PMT | 5 cm | **0.17 ns** |
| Front PMT | 25 cm | **0.83 ns** |

### Moderated Neutrons

| Energy Type | Energy | Back PMT ToF | Front PMT ToF |
|------------|--------|--------------|---------------|
| Thermal (0.025 eV) | 25 neV | 22.9 μs | 114.3 μs |
| Epithermal (1 eV) | 1 μeV | 3.6 μs | 18.1 μs |
| Fast-low (0.1 MeV) | 0.1 MeV | 11.4 ns | 57.2 ns |
| Fast-high (1 MeV) | 1 MeV | 3.6 ns | 18.1 ns |
| **Mean energy** | **1.83 MeV** | **2.7 ns** | **13.4 ns** |
| **Median energy** | **0.29 MeV** | **6.7 ns** | **33.6 ns** |

## Time Difference (Δt = Neutron ToF - Gamma ToF)

### Back PMT (5 cm from source)
| Neutron Type | Δt (delay relative to gamma) |
|-------------|------------------------------|
| Thermal (0.025 eV) | 22.9 μs |
| Epithermal (1 eV) | 3.6 μs |
| Fast-low (0.1 MeV) | 11.3 ns |
| Fast-high (1 MeV) | 3.4 ns |
| **Mean energy** | **2.5 ns** |
| **Median energy** | **6.5 ns** |

### Front PMT (25 cm from source)
| Neutron Type | Δt (delay relative to gamma) |
|-------------|------------------------------|
| Thermal (0.025 eV) | 114.3 μs |
| Epithermal (1 eV) | 18.1 μs |
| Fast-low (0.1 MeV) | 56.3 ns |
| Fast-high (1 MeV) | 17.2 ns |
| **Mean energy** | **12.5 ns** |
| **Median energy** | **32.7 ns** |

## Key Findings

1. **Neutron Energy Distribution After 10 cm HDPE**:
   - Most neutrons retain significant energy (median ~0.3 MeV)
   - Wide energy distribution from thermal to ~10 MeV
   - Mean energy (1.83 MeV) > Median (0.29 MeV) indicates skewed distribution

2. **ToF Separation for Particle Identification**:
   - **Fast neutrons (>1 MeV)**: 3-17 ns delay
   - **Moderated neutrons (0.1-1 MeV)**: 11-57 ns delay
   - **Thermal neutrons (<0.1 eV)**: 3.6-114 μs delay

3. **Practical Implications**:
   - **Front PMT** provides ~5x better ToF separation than back PMT
   - Time difference of ~12-33 ns for typical moderated neutrons is easily measurable with modern PMTs (ns resolution)
   - Can use ToF for **gamma-neutron discrimination**
   - Can also estimate neutron energy from ToF measurement

4. **Detector Configuration**:
   - Coincidence between back and front PMTs can confirm neutron detection
   - Longer distance to front PMT improves energy resolution through ToF
   - Typical detector timing resolution (1-2 ns) is sufficient for discrimination

## Applications

1. **Particle Identification (PID)**:
   - Use Δt to distinguish gamma rays from neutrons
   - Gamma: prompt signal (< 1 ns)
   - Neutrons: delayed signal (2-100 ns for fast/moderated, μs for thermal)

2. **Neutron Energy Estimation**:
   - ToF measurement provides direct energy estimate
   - Better energy resolution with longer flight path (front PMT)

3. **Coincidence Measurements**:
   - Use both PMTs to reject background
   - Confirm neutron events with consistent ToF between detectors

## Visualization

See `tof_analysis.png` for:
- Neutron energy spectrum after HDPE moderation (linear and log scale)
- ToF comparison between gamma and different neutron energies
- Separate plots for back and front PMT configurations
