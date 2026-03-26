#pragma once
#include <G4VUserPrimaryGeneratorAction.hh>
#include <vector>
#include <string>
class G4GeneralParticleSource;
class G4Event;


class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction {
public:
PrimaryGeneratorAction();
~PrimaryGeneratorAction() override;
void GeneratePrimaries(G4Event* event) override;
private:
G4GeneralParticleSource* fGPS = nullptr;
// Generic spectrum
std::vector<double> fSpectrumEnergies; // MeV
std::vector<double> fSpectrumCumWeights; // cumulative weights for sampling
bool LoadSpectrum(const std::string& path);
double SampleSpectrumEnergy();
};