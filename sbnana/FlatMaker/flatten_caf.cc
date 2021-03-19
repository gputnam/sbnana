#include "sbnanaobj/StandardRecord/StandardRecord.h"
#include "sbnanaobj/StandardRecord/SRGlobal.h"

#include "sbnana/FlatMaker/FlatRecord.h"

#include "sbnana/CAFAna/Core/Progress.h"

#include "TFile.h"
#include "TH1.h"
#include "TSystem.h"
#include "TTree.h"

#include <iostream>

int main(int argc, char** argv)
{
  if(argc != 3){
    std::cout << "Usage: convert_to_flat input.events.root output.flat.root"
              << std::endl;
    return 1;
  }

  const std::string inname = argv[1];
  const std::string outname = argv[2];

  TFile* fin = TFile::Open(inname.c_str());

  TTree* tr = (TTree*)fin->Get("recTree");
  if(!tr){
    std::cout << "Couldn't find tree 'recTree' in " << inname << std::endl;
    return 1;
  }

  caf::StandardRecord* event = 0;
  tr->SetBranchAddress("rec", &event);

  // LZ4 is the fastest format to decompress. I get 3x faster loading with
  // this compared to the default, and the files are only slightly larger.
  TFile fout(outname.c_str(), "RECREATE", "",
             ROOT::CompressionSettings(ROOT::kLZ4, 1));

  TTree* trout = new TTree("recTree", "recTree");
  // On NOvA, had trouble with memory usage (because several trees are open at
  // once?). Setting the maximum buffer usage (per tree) to 3MB (10x less than
  // default) fixed it. But it doesn't seem necessary for now on SBN.
  //  trout->SetAutoFlush(-3*1000*1000);

  flat::Flat<caf::StandardRecord> rec(trout, "rec", "", 0);//policy);

  ana::Progress prog("Converting '"+inname+"' to '"+outname+"'");
  for(int i = 0; i < tr->GetEntries(); ++i){
    prog.SetProgress(double(i)/tr->GetEntries());

    tr->GetEntry(i);

    rec.Clear();
    rec.Fill(*event);
    trout->Fill();
  }
  prog.Done();

  trout->Write();

  // Don't bother with a flat version for now, this info is tiny and read once
  TTree* globalIn = (TTree*)fin->Get("globalTree");
  if(globalIn){
    // Copy globalTree verbatim from input to output
    caf::SRGlobal global;
    caf::SRGlobal* pglobal = &global;
    globalIn->SetBranchAddress("global", &pglobal);
    fout.cd();
    TTree globalOut("globalTree", "globalTree");
    globalOut.Branch("global", "caf::SRGlobal", &global);
    assert(globalIn->GetEntries() == 1);
    // TODO check that the globalTree is the same in every file
    globalIn->GetEntry(0);
    globalOut.Fill();
    globalOut.Write();
  }

  TH1* hPOT = (TH1*)fin->Get("TotalPOT");
  TH1* hEvts = (TH1*)fin->Get("TotalEvents");
  fout.cd();
  hPOT->Write("TotalPOT");
  hEvts->Write("TotalEvents");

  return 0;
}
