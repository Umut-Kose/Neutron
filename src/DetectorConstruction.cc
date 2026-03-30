#include "DetectorConstruction.hh"
#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

#include "NaISD.hh"
#include "BPlasticSD.hh"
#include "G4SDManager.hh"

#include "G4VisAttributes.hh"
#include "G4Colour.hh"
// GDML writer
#include "G4GDMLParser.hh"

// prototype for helper
static void writeGDML(G4VPhysicalVolume* world);

DetectorConstruction::DetectorConstruction() : 
    fHDPE(nullptr),
    fBPlastic(nullptr),
    fNaI(nullptr),
    fWorldMaterial(nullptr),
    fLogicNaI(nullptr),
    fLogicScint(nullptr)
{
    DefineMaterials();
}

DetectorConstruction::~DetectorConstruction() {}

void DetectorConstruction::DefineMaterials() {
    auto nist = G4NistManager::Instance();

    // World material
    fWorldMaterial = nist->FindOrBuildMaterial("G4_AIR");

    // HDPE: approx density 0.95 g/cm3
    auto H = nist->FindOrBuildElement("H");
    auto C = nist->FindOrBuildElement("C");
    fHDPE = new G4Material("HDPE", 0.95*g/cm3, 2);
    fHDPE->AddElement(C, 2);
    fHDPE->AddElement(H, 4);

    // Boron-loaded plastic (simplified: 5% B by mass)
    auto B = nist->FindOrBuildElement("B");
    fBPlastic = new G4Material("BPlastic", 1.02*g/cm3, 3);
    fBPlastic->AddElement(C, 0.85);
    fBPlastic->AddElement(H, 0.10);
    fBPlastic->AddElement(B, 0.05);

    // NaI
    fNaI = nist->FindOrBuildMaterial("G4_SODIUM_IODIDE");
}

G4VPhysicalVolume* DetectorConstruction::Construct() {

    // World
    auto solidWorld = new G4Box("World", 100*cm, 100*cm, 100*cm);
    auto logicWorld = new G4LogicalVolume(solidWorld, fWorldMaterial, "World");
    auto physWorld = new G4PVPlacement(nullptr, {}, logicWorld, "World", 0, false, 0);

    // World visualization
    G4VisAttributes* worldVis = new G4VisAttributes(G4Colour(1.0, 1.0, 1.0, 0.1));
    worldVis->SetVisibility(true);
    logicWorld->SetVisAttributes(worldVis);

    // HDPE block (half-extent)
    auto solidBlock = new G4Box("HDPE", 15*cm, 15*cm, 15*cm);
    auto logicBlock = new G4LogicalVolume(solidBlock, fHDPE, "HDPE");
    G4VisAttributes* hdpeVis = new G4VisAttributes(G4Colour(0.0, 1.0, 1.0, 0.3));
    hdpeVis->SetForceSolid(true);
    logicBlock->SetVisAttributes(hdpeVis);
    new G4PVPlacement(nullptr, {}, logicBlock, "HDPE", logicWorld, false, 0);

    // Boron plastic scintillator (1x1x5 cm bar along z axis)
    // The HDPE block half-extent is 15 cm; place the scintillator on +z side,
    // with its 1x1 cm face facing the source and located 10 cm away from the HDPE surface.
    // HDPE +z surface is at +15 cm from origin, so scintillator front face center at +25 cm.
    // We model the scintillator as a box with half-extents 0.5 x 0.5 x 2.5 cm (length along z).
    auto solidScint = new G4Box("Scint", 0.5*cm, 0.5*cm, 2.5*cm);
    fLogicScint = new G4LogicalVolume(solidScint, fBPlastic, "Scint");
    G4VisAttributes* scintVis = new G4VisAttributes(G4Colour(0.0, 0.0, 1.0, 0.5));
    scintVis->SetForceSolid(true);
    fLogicScint->SetVisAttributes(scintVis);
    // position so that the front face (smaller z) is at +25 cm, center of box is at +25 - 2.5 cm = +22.5 cm
    G4double scint_front_z = 15.0*cm + 10.0*cm; // 25 cm
    G4double scint_center_z = scint_front_z - 2.5*cm;
    G4ThreeVector posScint(0, 0, scint_center_z);
    new G4PVPlacement(nullptr, posScint, fLogicScint, "Scint", logicWorld, false, 0);

    // Small PMT coupling volume placed immediately behind (on +z side) of the scintillator
    // Simple model: 1x1x1 cm cube, centered on scintillator backside.
    auto solidPMT = new G4Box("PMT", 0.5*cm, 0.5*cm, 0.5*cm);
    // Use vacuum/air for PMT placeholder
    auto pmtMaterial = fWorldMaterial;
    auto logicPMT = new G4LogicalVolume(solidPMT, pmtMaterial, "PMT");
    G4VisAttributes* pmtVis = new G4VisAttributes(G4Colour(0.3,0.3,0.3,0.6));
    pmtVis->SetForceSolid(true);
    logicPMT->SetVisAttributes(pmtVis);
    // scintillator back face center z is scint_center_z + 2.5 cm; place PMT center at back + 0.5 cm
    G4double pmt_center_z = scint_center_z + 2.5*cm + 0.5*cm;
    G4ThreeVector posPMT(0, 0, pmt_center_z);
    new G4PVPlacement(nullptr, posPMT, logicPMT, "PMT", logicWorld, false, 0);

    // NaI detector (3x3x3 cm cube placed on +y side (top) of the Scintillator)
    auto solidNaI = new G4Box("NaI", 1.5*cm, 1.5*cm, 1.5*cm);
    fLogicNaI = new G4LogicalVolume(solidNaI, fNaI, "NaI");
    G4VisAttributes* naiVis = new G4VisAttributes(G4Colour(1.0, 0.0, 0.0, 0.5));
    naiVis->SetForceSolid(true);
    fLogicNaI->SetVisAttributes(naiVis);
    // Place NaI above (+y) the scintillator; scintillator center z = scint_center_z
    // Put NaI center at y = 0.5 cm (scint half y) + 1.5 cm (NaI half y) + 1.0 cm gap = 3.0 cm
    G4double nai_center_y = 0.5*cm + 1.5*cm + 1.0*cm; // 3.0 cm
    G4ThreeVector posNaI(0, nai_center_y, scint_center_z);
    new G4PVPlacement(nullptr, posNaI, fLogicNaI, "NaI", logicWorld, false, 0);

    // (Source marker removed)

    // attempt to write GDML file for inspection
    writeGDML(physWorld);

    return physWorld;
}

// write GDML helper (optional)
void writeGDML(G4VPhysicalVolume* world) {
    try {
        // remove existing file if present to avoid G4GDML throwing
        const char* gdml_name = "geometry_output.gdml";
        std::remove(gdml_name);
        G4GDMLParser parser;
        parser.Write(gdml_name, world);
    } catch(...) {
        G4cout << "Warning: GDML write failed" << G4endl;
    }
}

void DetectorConstruction::ConstructSDandField() {
    G4SDManager* sdManager = G4SDManager::GetSDMpointer();
    auto naiSD = new NaISD("NaISD");
    auto bplasticSD = new BPlasticSD("BPlasticSD");
    sdManager->AddNewDetector(naiSD);
    sdManager->AddNewDetector(bplasticSD);
    if (fLogicNaI) fLogicNaI->SetSensitiveDetector(naiSD);
    if (fLogicScint) fLogicScint->SetSensitiveDetector(bplasticSD);
}
