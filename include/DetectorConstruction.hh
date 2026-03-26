#pragma once
#include <G4VUserDetectorConstruction.hh>
#include <globals.hh>
#include <G4ThreeVector.hh>


class G4LogicalVolume;
class G4VPhysicalVolume;
class G4Material;


class DetectorConstruction : public G4VUserDetectorConstruction {
public:
DetectorConstruction();
~DetectorConstruction() override = default;


G4VPhysicalVolume* Construct() override;


// Access to the scintillator logical volume (for stepping)
G4LogicalVolume* GetScintLV() const { return fScintLV; }
// PMT position in world coordinates
G4ThreeVector GetPMTPosition() const { return fPMTPos; }


private:
void DefineMaterials();


private:
G4LogicalVolume* fScintLV = nullptr;
G4ThreeVector fPMTPos{0,0,0};
};