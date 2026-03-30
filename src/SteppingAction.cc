#include "SteppingAction.hh"
#include "EventAction.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4EventManager.hh"
#include "G4Gamma.hh"
#include "G4Neutron.hh"
#include "G4ios.hh"
#include "G4SystemOfUnits.hh"

SteppingAction::SteppingAction(EventAction* eventAction)
: G4UserSteppingAction(),
  fEventAction(eventAction)
{}

SteppingAction::~SteppingAction() {}

void SteppingAction::UserSteppingAction(const G4Step* step) {
    auto track = step->GetTrack();
    auto preVol = step->GetPreStepPoint()->GetPhysicalVolume();
    auto postVol = step->GetPostStepPoint()->GetPhysicalVolume();
    G4String preName = preVol ? preVol->GetName() : "";
    G4String postName = postVol ? postVol->GetName() : "";

    // Always get the current EventAction from the event manager
    auto eventAction = static_cast<EventAction*>(
        G4EventManager::GetEventManager()->GetUserEventAction());
    if (!eventAction) return;

    // neutron capture in scintillator
    if (track->GetDefinition() == G4Neutron::Definition()) {
        if (step->GetPostStepPoint()->GetProcessDefinedStep() &&
            step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName() == "nCapture") {
            if (preName == "Scint" || postName == "Scint") {
                eventAction->SetCaptureFlag();
            }
        }
    }

    // Detect neutrons leaving the HDPE block into the world in +z direction.
    // In DetectorConstruction the HDPE PV is named "HDPE" and world is "World".
    if (track->GetDefinition() == G4Neutron::Definition()) {
        if (preName == "HDPE" && postName == "World") {
            // record kinetic energy in EventAction (MeV stored as G4double)
            G4double ke = track->GetKineticEnergy();
            eventAction->AddOutgoingNeutronEnergy(ke);
        }
    }

    // Remove gamma deposit scoring for NaI; now handled in NaISD
}
