#include "BPlasticSD.hh"
#include "G4SystemOfUnits.hh"
#include "G4HCofThisEvent.hh"
#include "G4Step.hh"
#include "G4ThreeVector.hh"
#include "G4SDManager.hh"
#include "G4ios.hh"
#include "G4Track.hh"

BPlasticSD::BPlasticSD(const G4String& name)
    : G4VSensitiveDetector(name), fTotalEnergyDeposit(0.), fNeutronCount(0)
{
}

BPlasticSD::~BPlasticSD()
{
}

void BPlasticSD::Initialize(G4HCofThisEvent*)
{
    fTotalEnergyDeposit = 0.;
    fNeutronCount = 0;
}

G4bool BPlasticSD::ProcessHits(G4Step* step, G4TouchableHistory*)
{
    G4double edep = step->GetTotalEnergyDeposit();
    
    // Count neutrons entering the detector
    if (step->GetPreStepPoint()->GetStepStatus() == fGeomBoundary) {
        if (step->GetTrack()->GetDefinition()->GetParticleName() == "neutron") {
            fNeutronCount++;
        }
    }

    if (edep == 0.) return false;

    fTotalEnergyDeposit += edep;
    return true;
}

void BPlasticSD::EndOfEvent(G4HCofThisEvent*)
{
    if (fTotalEnergyDeposit > 0 || fNeutronCount > 0)
    {
        G4cout << "B-Plastic Energy Deposit: "
               << fTotalEnergyDeposit/keV << " keV" << G4endl
               << "Number of neutrons detected: "
               << fNeutronCount << G4endl;
    }
}