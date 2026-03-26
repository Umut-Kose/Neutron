#include "DetectorConstruction.hh"


#include <G4Box.hh>
#include <G4LogicalVolume.hh>
#include <G4NistManager.hh>
#include <G4PVPlacement.hh>
#include <G4SubtractionSolid.hh>
#include <G4SystemOfUnits.hh>
#include <G4Material.hh>
#include <G4Element.hh>
#include <G4ThreeVector.hh>


DetectorConstruction::DetectorConstruction() : G4VUserDetectorConstruction() {}


void DetectorConstruction::DefineMaterials() {
auto* nist = G4NistManager::Instance();
nist->FindOrBuildMaterial("G4_AIR");
nist->FindOrBuildMaterial("G4_POLYETHYLENE");
nist->FindOrBuildMaterial("G4_Pyrex_Glass");


// Elements
auto* elH = new G4Element("Hydrogen","H", 1., 1.00794*g/mole);
auto* elC = new G4Element("Carbon", "C", 6., 12.011*g/mole);
// Natural boron (≈19.9% B-10, 80.1% B-11)
auto* elB10= new G4Isotope("B10", 5,10, 10.0129*g/mole);
auto* elB11= new G4Isotope("B11", 5,11, 11.0093*g/mole);
auto* elBnat= new G4Element("Boron","B", 2);
elBnat->AddIsotope(elB10, 19.9*perCent);
elBnat->AddIsotope(elB11, 80.1*perCent);


// Approximate EJ-254 as PVT (C,H) with 5% natural B by mass
auto* EJ254 = new G4Material("EJ254_5B", 1.026*g/cm3, 3);
EJ254->AddElement(elC, 0.878); // mass fractions (approx)
EJ254->AddElement(elH, 0.072);
EJ254->AddElement(elBnat, 0.050); // 5% B by mass
}


G4VPhysicalVolume* DetectorConstruction::Construct() {
DefineMaterials();
auto* nist = G4NistManager::Instance();


// World
auto worldSize = 50*cm;
auto* solidWorld = new G4Box("World", worldSize, worldSize, worldSize);
auto* logicWorld = new G4LogicalVolume(solidWorld, nist->FindOrBuildMaterial("G4_AIR"), "World");
auto* physWorld = new G4PVPlacement(nullptr, {}, logicWorld, "World", nullptr, false, 0);


// Scintillator bar: 1x1x5 cm3 (half-lengths)
auto* solidBar = new G4Box("ScintBar", 0.5*cm, 0.5*cm, 2.5*cm);
fScintLV = new G4LogicalVolume(solidBar, G4Material::GetMaterial("EJ254_5B"), "ScintLV");
new G4PVPlacement(nullptr, {}, fScintLV, "ScintBar", logicWorld, false, 0);


// Black holder: 1 mm thick shell created by subtracting the scintillator solid
// from a slightly larger outer box to avoid overlaps.
auto* solidOuter = new G4Box("HolderOuter", 0.6*cm, 0.6*cm, 2.6*cm);
// Use the existing scintillator solid (solidBar) as the inner subtraction shape so
// the shell fits tightly around the bar with ~1 mm thickness.
auto* solidShell = new G4SubtractionSolid("HolderShell", solidOuter, solidBar, 0, G4ThreeVector(0,0,0));
auto* logicShell = new G4LogicalVolume(solidShell, nist->FindOrBuildMaterial("G4_POLYETHYLENE"), "HolderLV");
new G4PVPlacement(nullptr, {}, logicShell, "Holder", logicWorld, false, 0);


// PMT window (1 mm) in front of -Z face (just for geometry completeness)
auto* solidWin = new G4Box("PMTWin", 0.5*cm, 0.5*cm, 0.05*cm);
auto* logicWin = new G4LogicalVolume(solidWin, nist->FindOrBuildMaterial("G4_Pyrex_Glass"), "PMTWinLV");
G4ThreeVector pmtPos(0,0,-(2.5*cm + 0.05*cm));
new G4PVPlacement(nullptr, pmtPos, logicWin, "PMTWin", logicWorld, false, 0);
fPMTPos = pmtPos;


return physWorld;
}
