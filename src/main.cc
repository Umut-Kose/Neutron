#include <G4RunManagerFactory.hh>
#include <G4UImanager.hh>
#include <G4UIExecutive.hh>
#include <G4VisExecutive.hh>
#include <G4RandomTools.hh>
#include <Randomize.hh>


#include <FTFP_BERT_HP.hh>


#include "DetectorConstruction.hh"
#include "PrimaryGeneratorAction.hh"
#include "ActionInitialization.hh"
#include "RunAction.hh"
#include "EventAction.hh"
#include "SteppingAction.hh"
#include <cstdlib>
#include <string>


int main(int argc, char** argv) {
// Random seed
CLHEP::HepRandom::setTheEngine(new CLHEP::RanluxEngine);
CLHEP::HepRandom::setTheSeed(time(nullptr));


auto* runManager = G4RunManagerFactory::CreateRunManager(G4RunManagerType::Default);


// Mandatory initialization classes
auto* det = new DetectorConstruction();
runManager->SetUserInitialization(det);
runManager->SetUserInitialization(new FTFP_BERT_HP);


// User actions are set via ActionInitialization (required for MT run manager)
runManager->SetUserInitialization(new ActionInitialization());


runManager->Initialize();


G4UImanager* UImanager = G4UImanager::GetUIpointer();


if (argc == 1) {
auto* ui = new G4UIExecutive(argc, argv);
auto* visManager = new G4VisExecutive();
visManager->Initialize();


UImanager->ApplyCommand("/control/execute macros/init_vis.mac");
ui->SessionStart();


delete visManager;
delete ui;
} else {
// Batch mode: argv[1] is a macro path
G4String command = "/control/execute ";
G4String fileName = argv[1];
// export the macro basename so the generator can locate a matching spectrum file
{
	std::string fname = fileName;
	// strip path
	auto pos = fname.find_last_of("/");
	if (pos != std::string::npos) fname = fname.substr(pos + 1);
	// strip extension
	auto dot = fname.find_last_of('.');
	std::string base = (dot == std::string::npos) ? fname : fname.substr(0, dot);
	setenv("G4SIM_MACRO_BASENAME", base.c_str(), 1);
}
UImanager->ApplyCommand(command + fileName);
}


delete runManager;
return 0;
}