#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4VisExecutive.hh"
#include "G4UIExecutive.hh"
#include "Shielding.hh"

#include "DetectorConstruction.hh"
#include "ActionInitialization.hh"

#include <memory>
#include <stdexcept>

int main(int argc,char** argv) {
    try {
        std::unique_ptr<G4UIExecutive> ui;
        if (argc == 1) {
            ui = std::make_unique<G4UIExecutive>(argc, argv);
        }

        // Initialize the run manager
        std::unique_ptr<G4RunManager> runManager = std::make_unique<G4RunManager>();

        // Set mandatory initialization classes
        runManager->SetUserInitialization(new DetectorConstruction());
        runManager->SetUserInitialization(new Shielding());
        runManager->SetUserInitialization(new ActionInitialization());

        runManager->Initialize();

        // Initialize visualization
        std::unique_ptr<G4VisExecutive> visManager = std::make_unique<G4VisExecutive>();
        visManager->Initialize();

        // Get the pointer to the UI manager (singleton - don't delete)
        G4UImanager* UImanager = G4UImanager::GetUIpointer();

        if (!ui) {
            // Batch mode
            UImanager->ApplyCommand("/control/execute " + G4String(argv[1]));
        } else {
            // Interactive mode
            UImanager->ApplyCommand("/control/execute run.mac");
            ui->SessionStart();
        }

        return 0;
    }
    catch (const std::exception& e) {
        G4cerr << "Error: " << e.what() << G4endl;
        return 1;
    }
    catch (...) {
        G4cerr << "Error: Unknown exception caught" << G4endl;
        return 1;
    }
}
