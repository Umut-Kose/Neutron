#pragma once
#include <G4UserSteppingAction.hh>

class EventAction;
class DetectorConstruction;
class G4Step;
class G4LogicalVolume;

class SteppingAction : public G4UserSteppingAction {
public:
  SteppingAction(EventAction* evt, const DetectorConstruction* det);
  ~SteppingAction() override = default;

  void UserSteppingAction(const G4Step* step) override;

private:
  EventAction* fEvent = nullptr;
    const DetectorConstruction* fDetector = nullptr;  // ✅ Add this line
  const G4LogicalVolume* fScintLV = nullptr;

  const double fBirks_cm_per_MeV = 0.0125; // typical for PVT
};
