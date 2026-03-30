#ifndef NaISD_h
#define NaISD_h 1

#include "G4VSensitiveDetector.hh"
#include "G4HCofThisEvent.hh"
#include "G4Step.hh"
#include "G4TouchableHistory.hh"

class NaISD : public G4VSensitiveDetector
{
public:
    NaISD(const G4String& name);
    virtual ~NaISD();

    virtual void Initialize(G4HCofThisEvent* hce);
    virtual G4bool ProcessHits(G4Step* step, G4TouchableHistory* history);
    virtual void EndOfEvent(G4HCofThisEvent* hce);

private:
    G4double fTotalEnergyDeposit;
};

#endif