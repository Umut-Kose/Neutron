#include "EventAction.hh"
#include "RunAction.hh"
#include <G4AnalysisManager.hh>
#include <G4Event.hh>


EventAction::EventAction(RunAction* runAction) : fRunAction(runAction) {}


void EventAction::BeginOfEventAction(const G4Event*) {
fEdep = 0.0;
fEdepQuenched = 0.0;
fLightYield = 0.0;
fProducedPhotons = 0.0;
}


void EventAction::EndOfEventAction(const G4Event* event) {
// Fast MCA mapping (minimal): 1 keVee per channel, simple Gaussian smearing
const double keVee = fEdepQuenched * 1000.0; // MeV -> keVee
const double keVperCh = 1.0; // 1 keV/channel (adjust later)
const double sigmaCh = 0.4; // electronics resolution (channels)
double ch = keVee / keVperCh;


// clip and fill
if (ch < 0) return;
if (ch > 4095) ch = 4095;


auto* analysis = G4AnalysisManager::Instance();
	analysis->FillH1(fRunAction->GetMCAId(), ch);

	// Fill light yield histogram
	analysis->FillH1(analysis->GetH1Id("LightYield"), fLightYield);

	// Fill per-event ntuple using provided event pointer
	const G4int evtID = event ? event->GetEventID() : -1;
	analysis->FillNtupleIColumn(0, 0, evtID);
	analysis->FillNtupleDColumn(0, 1, fEdep);
	analysis->FillNtupleDColumn(0, 2, fEdepQuenched);
	analysis->FillNtupleDColumn(0, 3, fLightYield);
	analysis->FillNtupleDColumn(0, 4, fProducedPhotons);
	analysis->AddNtupleRow(0);
}
