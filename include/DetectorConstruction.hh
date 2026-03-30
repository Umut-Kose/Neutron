#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

class G4LogicalVolume;
class G4VPhysicalVolume;

#include "G4VSensitiveDetector.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"

class DetectorConstruction : public G4VUserDetectorConstruction {
public:
    DetectorConstruction();
    virtual ~DetectorConstruction();

    virtual G4VPhysicalVolume* Construct();
    virtual void ConstructSDandField();

private:
    void DefineMaterials();
    
    G4Material* fHDPE;
    G4Material* fBPlastic;
    G4Material* fNaI;
    G4Material* fWorldMaterial;

    G4LogicalVolume* fLogicNaI;
    G4LogicalVolume* fLogicScint;
};

#endif
