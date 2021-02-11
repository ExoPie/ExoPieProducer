from pandas import DataFrame
# preselR dataframe
df_out_preselR = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'isjet1EtaMatch', 'M_Jet1Jet2', 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'weight', 'weightMET', 'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD', 'weightTop',
                                    'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightMET_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'MET_Res_up', 'MET_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'MET_En_down', 'MET_Res_down', 'weightJEC_down', 'weightMET_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
# SR dataframes
df_out_SR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'isjet1EtaMatch', 'M_Jet1Jet2', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'weight', 'weightMET', 'weightEle', 'weightMu', 'weightB', 'weightEWK',
                                  'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightMET_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'MET_Res_up', 'MET_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'MET_En_down', 'MET_Res_down', 'weightJEC_down', 'weightMET_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_SR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'weight', 'weightMET', 'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD',
                                  'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightMET_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'MET_Res_up', 'MET_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'MET_En_down', 'MET_Res_down', 'weightJEC_down', 'weightMET_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
# CR dataframes
df_out_ZeeCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Zmass', 'ZpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'subleadingLepPt', 'subleadingLepEta', 'subleadingLepPhi', 'weight', 'weightRecoil',
                                     'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_ZeeCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Zmass', 'ZpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2' , 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'subleadingLepPt', 'subleadingLepEta', 'subleadingLepPhi', 'weight', 'weightRecoil',
                                     'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_ZmumuCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Zmass', 'ZpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'subleadingLepPt', 'subleadingLepEta', 'subleadingLepPhi', 'weight', 'weightRecoil',
                                       'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_ZmumuCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Zmass', 'ZpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2' , 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'subleadingLepPt', 'subleadingLepEta', 'subleadingLepPhi', 'weight', 'weightRecoil',
                                       'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_WenuCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'rJet1PtMET', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB', 'weightEWK',
                                      'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_WenuCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB',
                                      'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_WmunuCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'rJet1PtMET', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB', 'weightEWK',
                                       'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_WmunuCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB',
                                       'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_TopenuCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB',
                                        'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_TopenuCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2' , 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu', 'weightB',
                                        'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_TopmunuCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2', 'isjet1EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu',
                                         'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_TopmunuCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'Recoil', 'RecoilPhi', 'Wmass', 'WpT', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet2' , 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'leadingLepPt', 'leadingLepEta', 'leadingLepPhi', 'weight', 'weightRecoil', 'weightEle', 'weightMu',
                                         'weightB', 'weightEWK', 'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightRecoil_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'Recoil_Res_up', 'Recoil_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'Recoil_En_down', 'Recoil_Res_down', 'weightJEC_down', 'weightRecoil_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_QCDCR_1b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'isjet1EtaMatch', 'M_Jet1Jet2', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'weight', 'weightMET', 'weightEle', 'weightMu', 'weightB', 'weightEWK',
                                  'weightQCD', 'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightMET_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'MET_Res_up', 'MET_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'MET_En_down', 'MET_Res_down', 'weightJEC_down', 'weightMET_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])
df_out_QCDCR_2b = DataFrame(columns=['run', 'lumi', 'event', 'MET', 'METPhi', 'pfMetCorrSig','pfpatCaloMETPt','pfpatCaloMETPhi','pfTRKMETPt','pfTRKMETPhi','delta_pfCalo', 'nPV', 'dPhi_jetMET', 'JetwithEta4p5', 'dPhi_lep1_MET', 'dPhi_lep2_MET', 'NTau', 'NEle', 'NMu', 'nPho', 'Njets_PassID', 'Nbjets_PassID', 'Jet1Pt', 'Jet1Eta', 'Jet1Phi', 'Jet1deepCSV','Jet1NHadEF', 'Jet1CHadEF', 'Jet1CEmEF', 'Jet1NEmEF', 'Jet1CMulti', 'Jet1NMultiplicity', 'Jet2Pt', 'Jet2Eta', 'Jet2Phi', 'Jet2deepCSV','Jet2NHadEF', 'Jet2CHadEF', 'Jet2CEmEF', 'Jet2NEmEF', 'Jet2CMulti', 'Jet2NMultiplicity', 'Jet3Pt', 'Jet3Eta', 'Jet3Phi', 'Jet3deepCSV', 'M_Jet1Jet3', 'isjet2EtaMatch', 'rJet1PtMET', 'ratioPtJet21', 'dPhiJet12', 'dEtaJet12', 'weight', 'weightMET', 'weightEle', 'weightMu', 'weightB', 'weightEWK', 'weightQCD',
                                  'weightTop', 'weightPU', 'weightPrefire', 'weightEleTrig','weightEleID','weightEleRECO','weightMuTRK','weightMuID','weightMET_up', 'weightEle_up', 'weightMu_up', 'weightB_up', 'weightEWK_up', 'weightQCD_up', 'weightTop_up', 'weightPU_up', 'weightPrefire_up', 'weightJEC_up', 'MET_Res_up', 'MET_En_up', 'weightscale_up', 'weightpdf_up','weightEleTrig_up','weightEleID_up','weightEleRECO_up','weightMuTRK_up','weightMuID_up','weightEleTrig_down','weightEleID_down','weightEleRECO_down','weightMuTRK_down','weightMuID_down','weightscale_down', 'weightpdf_down', 'MET_En_down', 'MET_Res_down', 'weightJEC_down', 'weightMET_down', 'weightEle_down', 'weightMu_down', 'weightB_down', 'weightEWK_down', 'weightQCD_down', 'weightTop_down', 'weightPU_down', 'weightPrefire_down','isak4JetBasedHemEvent', 'ismetphiBasedHemEvent1', 'ismetphiBasedHemEvent2','weightJECAbsoluteUp','weightJECAbsolute_yearUp','weightJECBBEC1Up','weightJECBBEC1_yearUp','weightJECEC2Up','weightJECEC2_yearUp','weightJECFlavorQCDUp','weightJECHFUp','weightJECHF_yearUp','weightJECRelativeBalUp','weightJECRelativeSample_yearUp','weightJECAbsoluteDown','weightJECAbsolute_yearDown','weightJECBBEC1Down','weightJECBBEC1_yearDown','weightJECEC2Down','weightJECEC2_yearDown','weightJECFlavorQCDDown','weightJECHFDown','weightJECHF_yearDown','weightJECRelativeBalDown','weightJECRelativeSample_yearDown'])