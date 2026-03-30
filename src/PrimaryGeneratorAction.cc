#include "PrimaryGeneratorAction.hh"
#include "G4GeneralParticleSource.hh"
#include "G4Event.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction() {
    fParticleSource = new G4GeneralParticleSource();
}
PrimaryGeneratorAction::~PrimaryGeneratorAction() { delete fParticleSource; }
void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent) {
    fParticleSource->GeneratePrimaryVertex(anEvent);
}
