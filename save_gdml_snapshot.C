{
  // save_gdml_snapshot.C - ROOT macro to import GDML, style HDPE, and save PNG
  TString gdml = "geometry_output.gdml";
  if (gSystem->AccessPathName(gdml)) {
    std::cout << "GDML file not found: " << gdml << std::endl;
    return;
  }
  TGeoManager* mgr = TGeoManager::Import(gdml);
  if (!mgr) {
    std::cout << "Failed to import GDML" << std::endl;
    return;
  }
  mgr->SetVisLevel(4);
  // style HDPE
  TObjArray* vols = mgr->GetListOfVolumes();
  for (int i=0;i<vols->GetEntries();++i){
    TGeoVolume* v = (TGeoVolume*)vols->At(i);
    TString name = v->GetName();
    if (name.Contains("HDPE")){
      v->SetLineColor(kGreen+2);
      v->SetFillColor(kGreen+1);
      v->SetTransparency(30);
      v->SetVisibility(1);
    }
  }
  TCanvas* c = new TCanvas("c", "geom", 800, 600);
  mgr->GetTopVolume()->Draw();
  c->Update();
  TString out = "build/opengl_snapshot_root.png";
  c->SaveAs(out);
  std::cout << "Wrote " << out << std::endl;
}
