#include "RunAction.hh"
#include <G4AnalysisManager.hh>
#include <G4Run.hh>


RunAction::RunAction() : G4UserRunAction() {}
RunAction::~RunAction() {}


void RunAction::BeginOfRunAction(const G4Run*) {
auto* analysis = G4AnalysisManager::Instance();
analysis->SetDefaultFileType("root"); // use "csv" if you prefer CSV
analysis->SetFileName("mca");
analysis->SetVerboseLevel(1);
// Enable ntuple merging for multi-threaded runs so row-wise ntuples from
// worker threads are merged into the final output file.
analysis->SetNtupleMerging(true);
analysis->OpenFile();
// 4096-channel MCA from 0..4096 (channels)
fH1Id = analysis->CreateH1("MCA", "ADC channels", 4096, 0., 4096.);

// Light yield histogram (photons)
analysis->CreateH1("LightYield", "Detected photons", 500, 0., 50000.);


	// Per-event ntuple: store eventID, total Edep (MeV), quenched Edep (MeVee)
	analysis->CreateNtuple("Events", "Per-event data");
	analysis->CreateNtupleIColumn("eventID");
	analysis->CreateNtupleDColumn("edep");
	analysis->CreateNtupleDColumn("edepQuenched");
	analysis->CreateNtupleDColumn("lightYield");
	analysis->CreateNtupleDColumn("producedPhotons");
	analysis->FinishNtuple();
}


void RunAction::EndOfRunAction(const G4Run*) {
auto* analysis = G4AnalysisManager::Instance();
analysis->Write();
analysis->CloseFile();
}
