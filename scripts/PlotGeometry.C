
{
// load geometry
TGeoManager::Import("../geometry_output.gdml");

// increase visibility/detail if necessary
gGeoManager->SetVisLevel(4);

// find and style HDPE volume(s)
TObjArray* vols = gGeoManager->GetListOfVolumes();
for (int i=0; i < vols->GetEntries(); ++i) {
TGeoVolume* v = (TGeoVolume*)vols->At(i);
TString name = v->GetName();
if (name.Contains("HDPE")) {
	std::cout << "Found HDPE volume: " << name << std::endl;
	v->SetLineColor(kGreen+2); // green outline
	v->SetFillColor(kGreen+1); // green fill
	v->SetTransparency(0); // 0..100 : 0 opaque, 100 fully transparent
	v->SetVisibility(1); // ensure it is marked visible
	}
}

// Draw the top/world volume
gGeoManager->GetTopVolume()->Draw("ogl"); // try different options if needed
// e.g. ->Draw("ogl") or set camera as you like


}
