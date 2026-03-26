CHANGELOG — Light yield & analysis additions
===========================================

Date: 2025-09-14
Author: automated patch assistant (paired dev)

Summary
-------
This document records all code changes, compile and run steps, and outputs added while implementing an event-level light-yield estimate (detected photons at a 1x1 cm^2 PMT) and extending the per-event ntuple for more detailed diagnostics. The work also added per-source simulation runs and quick analysis plots.

High-level scope
-----------------
- Add event-level accumulation of scintillation-produced photons and detected photons.
- Expose PMT position in `DetectorConstruction` to allow geometric acceptance computation.
- Add per-event ntuple columns: eventID, edep, edepQuenched, lightYield (detected), producedPhotons.
- Run longer macros (1k/10k events) for multiple sources and save per-source ROOT files.
- Provide quick analysis script runs that generate PNG plots for MCA and quenched Edep per source.

Files changed (summary)
-----------------------
- include/DetectorConstruction.hh
  - Added `#include <G4ThreeVector.hh>` and accessor `GetPMTPosition()` (this accessor was previously added earlier in the session).
  - Purpose: Allow other modules to query PMT position for geometric acceptance.

- include/EventAction.hh
  - Added accumulators and accessors:
    - `void AddLightYield(double n)` (already present), `double GetLightYield() const`.
    - `void AddProducedPhotons(double n)` and `double GetProducedPhotons() const`.
  - Added private member `double fProducedPhotons = 0.0;`.
  - Purpose: Track produced and detected photons per event.

- src/EventAction.cc
  - BeginOfEventAction(): reset `fEdep`, `fEdepQuenched`, `fLightYield`, and `fProducedPhotons` to 0.
  - EndOfEventAction(): fill H1 histogram for MCA (existing), fill H1 for "LightYield" (existing), and now fill the per-event ntuple columns:
    - Column indices (as implemented): 0:eventID (I), 1:edep (D), 2:edepQuenched (D), 3:lightYield (D), 4:producedPhotons (D).
  - Purpose: Ensure per-event produced/detected photon counts are recorded alongside energy deposition.

- src/RunAction.cc
  - BeginOfRunAction(): Created H1 histogram `"LightYield"` (Detected photons). Added ntuple column `producedPhotons`.
  - Ntuple columns order (created): `eventID`, `edep`, `edepQuenched`, `lightYield`, `producedPhotons`.

- include/SteppingAction.hh
  - Confirmed present pointer members: `EventAction* fEvent`, `const DetectorConstruction* fDetector`, and `const G4LogicalVolume* fScintLV`.

- src/SteppingAction.cc
  - In the scintillator volume steps (existing selection), retained energy deposition and Birks quenching calculation.
  - New simple optical model per step:
    - photonsPerMeV = 10000 photons / MeV (constant, plastic scintillator order of magnitude).
    - producedPhotons = q * photonsPerMeV (q is Birks-quenched energy in MeVee).
    - Recorded produced photons per step with `fEvent->AddProducedPhotons(producedPhotons)`.
    - Simple geometric acceptance: PMT area (1.0 cm^2) divided by 4πr^2 where r is distance step->PMT (cm).
    - opticalEff = 0.20 (20% overall optical/quantum efficiency) applied to produce `detected` photons.
    - The code clamps very small distance to prevent singularities and ensures detected ∈ [0, producedPhotons].
    - Finally calls `fEvent->AddLightYield(detected)`.
  - Purpose: Fast per-step estimation of produced vs detected photons without running Geant4 optical photons.

Build and runtime steps used
---------------------------
All commands run inside the workspace. Commands shown are the exact commands executed during the session (macOS, zsh).

1) Build (from project root `G4Sim`):

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim/build
make -j2
```

- Output: the `BoratedScinNeutron` executable was produced in `build/`.

2) Short test run (100 events) to validate new outputs:

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim/build
./BoratedScinNeutron ../macros/test_small.mac
```

- This produced `mca.root` (created by G4AnalysisManager). The analysis script was run on this file during development and produced `MCA.png` and `EdepQuenched.png`.

3) Longer per-source runs (examples executed):
- The following macros were executed in sequence; after each run the produced `mca.root` was renamed so each source has its own file.

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim/build
./BoratedScinNeutron ../macros/ambe_1k.mac && mv mca.root mca_ambe.root
./BoratedScinNeutron ../macros/na22_1k.mac && mv mca.root mca_na22.root
./BoratedScinNeutron ../macros/sr90_1k.mac && mv mca.root mca_sr90.root
./BoratedScinNeutron ../macros/cs137.mac && mv mca.root mca_cs137.root
./BoratedScinNeutron ../macros/co60.mac && mv mca.root mca_co60.root
```

- Note: some macros use 1000 events (the `_1k` macros); one run used 10k events for `cs137` in my session (the macro file sets /run/beamOn accordingly). The code supports multi-threaded execution and will create per-thread temp files and merge them.

4) Per-source analysis (quick script `analysis/plot_mca_edep.py`):

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim
python3 analysis/plot_mca_edep.py build/mca_ambe.root
# move outputs so they don't overwrite each other
mv MCA.png MCA_ambe.png
mv EdepQuenched.png EdepQuenched_ambe.png
# repeated for other root files similarly
```

- The analysis script uses `uproot`, `numpy`, and `matplotlib` to read histograms and the `Events` ntuple, and saves PNG files.

Files produced during the session
--------------------------------
- Executable: `build/BoratedScinNeutron`
- Per-source ROOT files (examples):
  - `build/mca_ambe.root`
  - `build/mca_na22.root`
  - `build/mca_sr90.root`
  - `build/mca_cs137.root`
  - `build/mca_co60.root`
- Plots (project root):
  - `MCA_ambe.png`, `EdepQuenched_ambe.png`
  - `MCA_na22.png`, `EdepQuenched_na22.png`
  - `MCA_sr90.png`, `EdepQuenched_sr90.png`
  - `MCA_cs137.png`, `EdepQuenched_cs137.png`
  - `MCA_co60.png`, `EdepQuenched_co60.png`

Developer notes & rationale
---------------------------
- Optical model: a very fast geometric + efficiency model was chosen to avoid the heavy overhead of full `G4OpticalPhoton` tracking. This gives a per-event detected photon estimate suitable for quick studies. Tunable parameters are in the code and can be refined:
  - photonsPerMeV (default 10000)
  - PMT area (default 1 cm^2)
  - opticalEff (default 0.20)

- Potential improvements (future work):
  - Add attenuation length: detected *= exp(-r/atten_cm) and expose `atten_cm` as a tunable parameter.
  - Model angular dependence of PMT acceptance and include holder transparency / reflectivity.
  - Switch to Geant4 optical photon tracking if you require wavelength-dependent transport and detailed timing.

- Ntuple layout: keep the order consistent to simplify reading by `uproot` and scripts. If you change the ntuple columns, update analysis scripts accordingly.

How to reproduce locally (concise)
---------------------------------
1) Configure/build (assuming CMake config already present):

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim/build
cmake ..   # if needed
make -j2
```

2) Run a macro (example):

```bash
./BoratedScinNeutron ../macros/ambe_1k.mac
# results in mca.root
```

3) Run analysis (example):

```bash
cd /Users/ukose/sw/Work/Neutron3D/G4Sim
python3 analysis/plot_mca_edep.py build/mca_ambe.root
```

Appendix: quick diffs per file (high-level)
-------------------------------------------
- `include/EventAction.hh`
  - + AddProducedPhotons, +GetProducedPhotons, +fProducedPhotons
- `src/EventAction.cc`
  - +Reset fProducedPhotons in BeginOfEventAction
  - +Fill producedPhotons ntuple column in EndOfEventAction
- `src/RunAction.cc`
  - +CreateNtupleDColumn("producedPhotons")
- `src/SteppingAction.cc`
  - +producedPhotons calculation and fEvent->AddProducedPhotons(producedPhotons)
  - +geometric acceptance calculation and fEvent->AddLightYield(detected)
- `include/DetectorConstruction.hh`
  - +#include <G4ThreeVector.hh>

If you want, I can also:
- Add an `CHANGELOG` entry in git and create a small README appendix with recommended tuning values.
- Add attenuation and re-run all macros to compare results (I can do this next).

Status of TODO list
-------------------
- Draft summary document — in-progress -> completed (this file created).
- Verify build/run notes — completed (commands recorded above).
- Finalize and save report — completed (saved as `CHANGELOG_LIGHTYIELD.md`).

End of document
