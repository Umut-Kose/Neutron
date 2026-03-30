#include "EventAction.hh"
#include "G4Event.hh"
#include <iomanip>
#include "G4SystemOfUnits.hh"
#include "G4ios.hh"
#include "G4RunManager.hh"

// define static member for outgoing neutron energies
std::vector<G4double> EventAction::fOutgoingEnergies;

// define static member
std::ofstream EventAction::fOut;

EventAction::EventAction()
: G4UserEventAction(), fCapture(false), fGammaEdep(0.)
{
    if (!fOut.is_open()) {
        fOut.open("results.csv");
        fOut << "EventID,Capture,GammaDetected,GammaEnergy_keV\n";
    }
}

EventAction::~EventAction() {}

void EventAction::BeginOfEventAction(const G4Event*) {
    fCapture = false;
    fGammaEdep = 0.;
}

void EventAction::EndOfEventAction(const G4Event* evt) {
    G4int id = evt->GetEventID();
    G4int gammaDetected = (fGammaEdep > 0.) ? 1 : 0;
    G4cout << "Event " << id << ": Capture=" << (fCapture ? 1 : 0)
           << ", GammaDetected=" << gammaDetected
           << ", GammaEnergy_keV=" << fGammaEdep/keV << G4endl;
    fOut << id << ","
         << (fCapture ? 1 : 0) << ","
         << gammaDetected << ","
         << fGammaEdep/keV
         << "\n";
}

void EventAction::WriteOutgoingNeutrons(const G4Run* run)
{
    if (fOutgoingEnergies.empty()) return;
    std::ofstream fout("neutron_energies_after_hdpe.txt");
    fout << "# kinetic_energy_MeV\n";
    for (auto e : fOutgoingEnergies) fout << e/MeV << "\n";
    fout.close();
    G4cout << "Wrote neutron_energies_after_hdpe.txt (" << fOutgoingEnergies.size() << " entries)" << G4endl;
}
