import os
import sys
sys.path.append('../../ExoPieUtils/commonutils/')

import MathUtils as mathutil
from MathUtils import *


def getSel_boosted(nEle,nTightEle,isTightEle,nMu,nTightMu,isTightMuon,nTau,nPho,\
                  nBjets,cleaned_ak4jets,nFatJet,nFatJet_SBand,nFatJet_ZCR,pfMet,mini_ak4jet_MET_dPhi,\
                  ZeeRecoil,min_ak4jets_ZeeRecoil_dPhi,ZeeMass,ZmumuRecoil,min_ak4jets_ZmumuRecoil_dPhi,ZmumuMass,\
                  WenuRecoil,min_ak4jets_WenuRecoil_dPhi,WenuMass,WmunuRecoil,min_ak4jets_WmunuRecoil_dPhi,WmunuMass):
    cuts ={}
    baseline       = cleaned_ak4jets >=0 and nTau==0 and nFatJet==1# and nPho==0
    baseline_ZCR  = cleaned_ak4jets >=0 and nTau==0 and nFatJet_ZCR==1# and nPho==0       
    baseline_SBand= cleaned_ak4jets >=0 and nTau==0 and nFatJet_SBand==1# and nPho==0
   
    cuts['boosted_signal'] = baseline and nMu+nEle==0 and nBjets==0 and pfMet > 200.0 and mini_ak4jet_MET_dPhi > 0.4
    cuts['boosted_SBand']  = baseline_SBand and nMu+nEle==0 and nBjets==0 and pfMet > 200.0 and mini_ak4jet_MET_dPhi > 0.4
    cuts['boosted_tm']     = False
    cuts['boosted_te']     = False
    cuts['boosted_wmn']    = False
    cuts['boosted_wen']    = False
    cuts['boosted_zee']    = False
    cuts['boosted_zmm']    = False
    if nEle==1 and nMu==0:
        cuts['boosted_te']         = baseline and nBjets==1 and nMu==0 and nEle==1 and nTightEle==1 and WenuRecoil > 200.0 and min_ak4jets_WenuRecoil_dPhi > 0.4 and pfMet > 50
        cuts['boosted_wen']        = baseline and nBjets==0 and nMu==0 and nEle==1 and nTightEle==1 and WenuRecoil > 200.0 and min_ak4jets_WenuRecoil_dPhi > 0.4 and pfMet > 50

    if nEle==0 and nMu==1:
        cuts['boosted_tm']         = baseline and nBjets==1 and nEle==0 and nMu==1 and nTightMu==1 and WmunuRecoil > 200.0 and min_ak4jets_WmunuRecoil_dPhi > 0.4 and pfMet > 50.
        cuts['boosted_wmn']        = baseline and nBjets==0 and nEle==0 and nMu==1 and nTightMu==1 and WmunuRecoil > 200.0 and min_ak4jets_WmunuRecoil_dPhi > 0.4 and pfMet > 50.

    
    if nEle==2 and nMu==0:
        #print 'ZEE_boosted==:','baseline',baseline,'nBjets',nBjets,'isTightEle',isTightEle,'ZeeRecoil',ZeeRecoil,'ZeeMass',ZeeMass
        cuts['boosted_zee']        = baseline_ZCR and nBjets==0 and nMu==0 and nEle==2 and (isTightEle[0] or isTightEle[1]) and ZeeRecoil > 200.0 and ZeeMass > 60.0 and ZeeMass < 120.0
    if nEle==0 and nMu==2:
        cuts['boosted_zmm']        = baseline_ZCR and nBjets==0 and nEle==0 and nMu==2 and (isTightMuon[0] or isTightMuon[1]) and ZmumuRecoil > 200.0 and ZmumuMass > 60.0 and ZmumuMass < 120.0
    
    return cuts



def getSel_resolved(nEle,nTightEle,isTightEle,nMu,nTightMu,isTightMuon,nTau,nPho,\
                   nBjets,nak4jets,ak4CSV,ak4pt,ak4eta,pfMet,mini_ak4jet_MET_dPhi,h_mass,\
                   ZeeRecoil,min_ak4jets_ZeeRecoil_dPhi,ZeeMass,ZmumuRecoil,min_ak4jets_ZmumuRecoil_dPhi,ZmumuMass,WenuRecoil,\
                   min_ak4jets_WenuRecoil_dPhi,WenuMass,WmunuRecoil,min_ak4jets_WmunuRecoil_dPhi,WmunuMass):
    MWP = 0.4941 
    cuts ={}
    jetCond = True
    if nak4jets>1: jetCond = ak4CSV[0] > MWP and ak4CSV[1] > MWP and ak4pt[0] > 50 and (abs(ak4eta[0]) < 2.5)


    baseline       = nak4jets >= 2 and nTau==0 and jetCond #and h_mass > 100.0 and h_mass < 150.0 # and nPho==0
   
    cuts['resolved_signal'] = baseline and nMu+nEle==0 and pfMet > 200.0 and mini_ak4jet_MET_dPhi > 0.4
    cuts['resolved_tm']     = False
    cuts['resolved_te']     = False
    cuts['resolved_wmn']    = False
    cuts['resolved_wen']    = False
    cuts['resolved_zee']    = False
    cuts['resolved_zmm']    = False

    if nEle==1 and nMu==0:
        cuts['resolved_te']         = baseline and nBjets==2 and nMu==0 and nEle==1 and nTightEle==1 and WenuRecoil > 200.0 and min_ak4jets_WenuRecoil_dPhi > 0.4 and pfMet > 50.0 and h_mass > 100.0 and h_mass < 150.0
        #cuts['boosted_wen']        = baseline and nBjets==2 and nMu==0 and nEle==1 and nTightEle==1 and WenuRecoil > 200.0 and min_ak4jets_WenuRecoil_dPhi > 0.4 and pfMet > 50

    if nEle==0 and nMu==1:
        cuts['resolved_tm']         = baseline and nBjets==2 and nEle==0 and nMu==1 and nTightMu==1 and WmunuRecoil > 200.0 and min_ak4jets_WmunuRecoil_dPhi > 0.4 and pfMet > 50.0 and h_mass > 100.0 and h_mass < 150.0
        #cuts['boosted_wmn']        = baseline and nBjets==2 and nEle==0 and nMu==1 and nTightMu==1 and WmunuRecoil > 200.0 and min_ak4jets_WmunuRecoil_dPhi > 0.4 and pfMet > 50.

    
    if nEle==2 and nMu==0:
        
        cuts['resolved_zee']        = baseline and nBjets==2 and nMu==0 and nEle==2 and (isTightEle[0] or isTightEle[1]) and ZeeRecoil > 200.0 and min_ak4jets_ZeeRecoil_dPhi > 0.4 and ZeeMass > 60.0 and ZeeMass < 120.0
    if nEle==0 and nMu==2:
        cuts['resolved_zmm']        = baseline and nBjets==2 and nEle==0 and nMu==2 and (isTightMuon[0] or isTightMuon[1]) and ZmumuRecoil > 200.0 and min_ak4jets_ZmumuRecoil_dPhi > 0.4 and ZmumuMass > 60.0 and ZmumuMass < 120.0
    
    return cuts





def ZRecoil_Phi_Zmass(nEle, eleCharge_, elepx_, elepy_, elepz_, elee_,met_,metphi_):
    dummy=-9999.0
    ZeeRecoilPt=dummy; ZeerecoilPhi=-10.0; Zee_mass=dummy
    if nEle == 2:
        iele1=0
        iele2=1
        if eleCharge_[iele1]*eleCharge_[iele2]<0:
            Zee_mass = InvMass(elepx_[iele1],elepy_[iele1],elepz_[iele1],elee_[iele1],elepx_[iele2],elepy_[iele2],elepz_[iele2],elee_[iele2])
            zeeRecoilPx = -( met_*math.cos(metphi_) + elepx_[iele1] + elepx_[iele2])
            zeeRecoilPy = -( met_*math.sin(metphi_) + elepy_[iele1] + elepy_[iele2])
            ZeeRecoilPt =  math.sqrt(zeeRecoilPx**2  +  zeeRecoilPy**2)
            ZeerecoilPhi = mathutil.ep_arctan(zeeRecoilPx,zeeRecoilPy)
    return ZeeRecoilPt, ZeerecoilPhi, Zee_mass

def WRecoil_Phi_Wmass(nEle,elept,elephi,elepx_,elepy_,met_,metphi_):
    dummy=-9999.0
    WenuRecoilPt=dummy; WenurecoilPhi=-10.0;  We_mass=dummy; 
    if nEle == 1:
        We_mass = MT(elept[0],met_, DeltaPhi(elephi[0],metphi_)) #transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)}
        WenuRecoilPx = -( met_*math.cos(metphi_) + elepx_[0])
        WenuRecoilPy = -( met_*math.sin(metphi_) + elepy_[0])
        WenuRecoilPt = math.sqrt(WenuRecoilPx**2  +  WenuRecoilPy**2)
        WenurecoilPhi = mathutil.ep_arctan(WenuRecoilPx,WenuRecoilPy)
    return WenuRecoilPt, WenurecoilPhi, We_mass

