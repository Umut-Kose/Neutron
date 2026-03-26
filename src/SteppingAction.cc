#include "SteppingAction.hh"
#include "EventAction.hh"
#include "DetectorConstruction.hh"


#include <G4Step.hh>
#include <G4LogicalVolume.hh>
#include <G4TouchableHandle.hh>
#include <G4VPhysicalVolume.hh>
#include <G4ThreeVector.hh>
#include <G4SystemOfUnits.hh>

#include <cmath>


SteppingAction::SteppingAction(EventAction* evt, const DetectorConstruction* det)
: fEvent(evt), fDetector(det), fScintLV(det ? det->GetScintLV() : nullptr) {}


void SteppingAction::UserSteppingAction(const G4Step* step) {
// Defensive checks
if (!fScintLV) return;
auto* pre = step->GetPreStepPoint();
auto* lv = pre->GetTouchableHandle()->GetVolume()->GetLogicalVolume();
if (lv != fScintLV) return;


const double dE = step->GetTotalEnergyDeposit(); // MeV
const double dx = step->GetStepLength() / cm; // cm
if (dE <= 0.0 || dx <= 0.0) return;


// Accumulate raw edep
fEvent->AddEdep(dE);


// Minimal Birks quenching: dL/dx = dE/dx / (1 + kB * dE/dx)
const double dEdx = dE / dx; // MeV/cm
const double q = dE / (1.0 + fBirks_cm_per_MeV * dEdx); // MeVee approx
fEvent->AddEdepQuenched(q);

// Simple scintillation photon model and geometric collection to PMT
// Photons produced (approx): photonsPerMeV * quenched energy (MeVee)
const double photonsPerMeV = 10000.0; // photons / MeV (plastic scintillator order)
const double producedPhotons = q * photonsPerMeV;

// Record produced photons (total emitted) at event level
fEvent->AddProducedPhotons(producedPhotons);

// PMT geometric acceptance: fraction = A_pmt / (4*pi*r^2)
// PMT area ~1 cm^2 (1x1 cm)
const double pmtArea_cm2 = 1.0;
// Get position of step and PMT
const G4ThreeVector pos = pre->GetPosition();
const G4ThreeVector pmtPos = fDetector ? fDetector->GetPMTPosition() : G4ThreeVector();
double r_cm = (pos - pmtPos).mag() / cm; // distance in cm
if (r_cm < 0.01) r_cm = 0.01; // avoid singular behaviour (min 0.1 mm)
const double geomFraction = pmtArea_cm2 / (4.0 * M_PI * r_cm * r_cm);
const double opticalEff = 0.20; // overall optical/quantum efficiency
double detected = producedPhotons * geomFraction * opticalEff;
if (detected < 0.0) detected = 0.0;
if (detected > producedPhotons) detected = producedPhotons;

// Add to event-level light yield (as detected photons)
fEvent->AddLightYield(detected);
}
