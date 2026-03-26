#include "ActionInitialization.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"
#include "SteppingAction.hh"
#include "DetectorConstruction.hh"
#include <G4RunManager.hh>


ActionInitialization::ActionInitialization() {}
ActionInitialization::~ActionInitialization() {}


void ActionInitialization::Build() const {

  auto* detector = static_cast<const DetectorConstruction*>(
    G4RunManager::GetRunManager()->GetUserDetectorConstruction());

  auto* runAction = new RunAction();
  SetUserAction(runAction);
  
  auto* eventAction = new EventAction(runAction);
  SetUserAction(eventAction);

  auto* steppingAction = new SteppingAction(eventAction, detector);
  SetUserAction(steppingAction);
  
  SetUserAction(new PrimaryGeneratorAction());
}


void ActionInitialization::BuildForMaster() const {
  SetUserAction(new RunAction());
}