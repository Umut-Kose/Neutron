#pragma once
#include <G4UserEventAction.hh>
class RunAction;
class G4Event;


class EventAction : public G4UserEventAction {
public:
explicit EventAction(RunAction* runAction);
~EventAction() override = default;
void BeginOfEventAction(const G4Event*) override;
void EndOfEventAction(const G4Event*) override;


// Accumulators called from SteppingAction
void AddEdep(double e) { fEdep += e; }
void AddEdepQuenched(double e) { fEdepQuenched += e; }
 void AddLightYield(double n) { fLightYield += n; }
 double GetLightYield() const { return fLightYield; }
 void AddProducedPhotons(double n) { fProducedPhotons += n; }
 double GetProducedPhotons() const { return fProducedPhotons; }


private:
RunAction* fRunAction = nullptr;
double fEdep = 0.0; // MeV
double fEdepQuenched = 0.0; // MeVee approximation
 double fLightYield = 0.0; // estimated detected photons
 double fProducedPhotons = 0.0; // produced photons in scintillator
};
