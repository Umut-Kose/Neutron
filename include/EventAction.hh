#ifndef EventAction_h
#define EventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"
#include <fstream>
#include <vector>

class G4Run;

class EventAction : public G4UserEventAction {
public:
    EventAction();
    virtual ~EventAction();

    virtual void BeginOfEventAction(const G4Event*);
    virtual void EndOfEventAction(const G4Event*);

    // Write outgoing neutron energies at end of run
    void WriteOutgoingNeutrons(const G4Run* run);

    void SetCaptureFlag() { fCapture = true; }
    void AddGammaEdep(G4double e) { fGammaEdep += e; }
    void AddOutgoingNeutronEnergy(G4double e) { fOutgoingEnergies.push_back(e); }

    // run-level collection of outgoing neutron energies (MeV)
    static std::vector<G4double> fOutgoingEnergies;

private:
    bool fCapture;
    G4double fGammaEdep;

    static std::ofstream fOut;
};

#endif
