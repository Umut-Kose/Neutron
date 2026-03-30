#include "NaISD.hh"
#include "G4SystemOfUnits.hh"
#include "G4HCofThisEvent.hh"
#include "G4Step.hh"
#include "G4ThreeVector.hh"
#include "G4SDManager.hh"
#include "G4ios.hh"
#include "G4EventManager.hh"
#include "EventAction.hh"

NaISD::NaISD(const G4String& name)
    : G4VSensitiveDetector(name), fTotalEnergyDeposit(0.)
{
}

NaISD::~NaISD()
{
}

void NaISD::Initialize(G4HCofThisEvent*)
{
    fTotalEnergyDeposit = 0.;
}

G4bool NaISD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep == 0.) return false;

    fTotalEnergyDeposit += edep;
    return true;
}

void NaISD::EndOfEvent(G4HCofThisEvent*)
{
    if (fTotalEnergyDeposit > 0)
    {
        G4cout << "NaI Energy Deposit: "
               << fTotalEnergyDeposit/keV << " keV" << G4endl;
    }
    // Pass energy deposit to EventAction
    auto eventAction = static_cast<EventAction*>(
        G4EventManager::GetEventManager()->GetUserEventAction());
    if (eventAction) {
        eventAction->AddGammaEdep(fTotalEnergyDeposit);
    }
}