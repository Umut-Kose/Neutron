#include "RunAction.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "EventAction.hh"

RunAction::RunAction()
: G4UserRunAction()
{ }

RunAction::~RunAction()
{ }

void RunAction::BeginOfRunAction(const G4Run*)
{
    // Optional: Add initialization code here
}

void RunAction::EndOfRunAction(const G4Run*)
{
    // Write outgoing neutron energies if any
    auto evt = const_cast<EventAction*>(static_cast<const EventAction*>(G4RunManager::GetRunManager()->GetUserEventAction()));
    if (evt) {
        evt->WriteOutgoingNeutrons(nullptr);
    }
}
