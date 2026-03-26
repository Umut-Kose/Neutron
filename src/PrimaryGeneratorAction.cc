#include "PrimaryGeneratorAction.hh"
#include <G4GeneralParticleSource.hh>
#include <G4Event.hh>
#include <G4ParticleDefinition.hh>
#include <G4ParticleTable.hh>
#include <G4SystemOfUnits.hh>

#include <fstream>
#include <sstream>
#include <random>
#include <algorithm>
#include <string>

static std::mt19937_64 rng_engine(std::random_device{}());


PrimaryGeneratorAction::PrimaryGeneratorAction() {
	fGPS = new G4GeneralParticleSource();

		// Try to load a spectrum file based on macro basename environment variable
		const char* mb = std::getenv("G4SIM_MACRO_BASENAME");
		bool loaded = false;
		if (mb) {
			std::string path = std::string("macros/") + mb + "_spectrum.txt";
			loaded = LoadSpectrum(path);
		}
		if (!loaded) {
			// fallback to AmBe default
			LoadSpectrum("macros/ambe_spectrum.txt");
		}
}


PrimaryGeneratorAction::~PrimaryGeneratorAction() { delete fGPS; }


bool PrimaryGeneratorAction::LoadSpectrum(const std::string& path) {
	std::ifstream in(path);
	if (!in.is_open()) return false;
		std::vector<double> energies;
		std::vector<double> weights;
	std::string line;
	while (std::getline(in, line)) {
		if (line.empty()) continue;
		if (line[0] == '#') continue;
		std::istringstream iss(line);
		double e, w;
		if (!(iss >> e >> w)) continue;
		energies.push_back(e);
		weights.push_back(w);
	}
	if (energies.empty()) return false;
	// build cumulative weights
		fSpectrumEnergies = energies;
		fSpectrumCumWeights.resize(weights.size());
		double s = 0.0;
		for (size_t i = 0; i < weights.size(); ++i) {
			s += weights[i];
			fSpectrumCumWeights[i] = s;
		}
		// normalize
		for (auto &c : fSpectrumCumWeights) c /= s;
		return true;
}

	double PrimaryGeneratorAction::SampleSpectrumEnergy() {
		if (fSpectrumEnergies.empty()) return 4.0; // fallback
		std::uniform_real_distribution<double> dist(0.0, 1.0);
		double r = dist(rng_engine);
		auto it = std::lower_bound(fSpectrumCumWeights.begin(), fSpectrumCumWeights.end(), r);
		size_t idx = std::distance(fSpectrumCumWeights.begin(), it);
		if (idx >= fSpectrumEnergies.size()) idx = fSpectrumEnergies.size() - 1;
		return fSpectrumEnergies[idx] * MeV; // return in internal units
	}

	void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event) {
	// If GPS particle is neutron and we have an AmBe spectrum, sample energy
	auto* particle = fGPS->GetCurrentSource()->GetParticleDefinition();
		if (particle && particle->GetParticleName() == "neutron" && !fSpectrumEnergies.empty()) {
			double E = SampleSpectrumEnergy();
		// set mono energy for this vertex
			fGPS->GetCurrentSource()->GetEneDist()->SetMonoEnergy(E / MeV); // set in MeV
	}

	fGPS->GeneratePrimaryVertex(event);
}
