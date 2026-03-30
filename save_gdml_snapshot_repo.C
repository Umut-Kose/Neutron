{
  TString gdml = "geometry_output.gdml";
  if (gSystem->AccessPathName(gdml)) { std::cout<<"GDML not found"<<std::endl; return; }
  TGeoManager* mgr = TGeoManager::Import(gdml);
  mgr->SetVisLevel(4);
  TObjArray* vols = mgr->GetListOfVolumes();
  for (int i=0;i<vols->GetEntries();++i){
    TGeoVolume* v = (TGeoVolume*)vols->At(i);
    TString name = v->GetName();
    if (name.Contains("HDPE")){
      v->SetLineColor(kGreen+2); v->SetFillColor(kGreen+1); v->SetTransparency(30); v->SetVisibility(1);
    }
  }
  TCanvas* c = new TCanvas("c2","geom2",1024,768);
  mgr->GetTopVolume()->Draw(); c->Update();
  TString out = "/Users/ukose/sw/Work/Neutron3D/Simulation/G4Sim/opengl_snapshot_root.png";
  c->SaveAs(out);
  std::cout<<"Wrote "<<out<<std::endl;
}
