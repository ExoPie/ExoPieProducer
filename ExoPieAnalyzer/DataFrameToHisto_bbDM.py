import ROOT as ROOT
import argparse
from array import array
import numpy as np
from root_pandas import read_root
import time
import glob
import multiprocessing as mp
from functools import partial
from readpickle import addbdtscore
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('pdf')

# ----- start of clock
start = time.time()


def Phi_mpi_pi(x):
    kPI = np.array(3.14159265)
    kPI = kPI.repeat(len(x))
    kTWOPI = 2 * kPI
    while ((x.any() >= kPI).any()):
        x = x - kTWOPI
    while ((x.any() < -kPI).any()):
        x = x + kTWOPI
    return x


def DeltaPhi(phi1, phi2):
    phi = Phi_mpi_pi(phi1 - phi2)
    return abs(phi)


# ----- command line argument
usage = "python DataframeToHist.py -F -inDir directoryName -D outputDir "
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-i", "--inputfile",  dest="inputfile", default="myfiles.root")
parser.add_argument("-o", "--outputfile", dest="outputfile", default="out.root")
parser.add_argument("-F", "--farmout", action="store_true",  dest="farmout")
parser.add_argument("-inDir", "--inputDir", dest="inputDir", default=".")
parser.add_argument("-D", "--outputdir", dest="outputdir", default=".")

args = parser.parse_args()

if args.farmout == None:
    isfarmout = False
else:
    isfarmout = args.farmout

if args.inputDir and isfarmout:
    inDir = args.inputDir

outputdir = '.'
if args.outputdir:
    outputdir = str(args.outputdir)


infile = args.inputfile


args = parser.parse_args()


filename = 'OutputFiles/WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8.root'


def SetHist(HISTNAME, binning):
    h = ROOT.TH1F()
    if len(binning) == 3:
        h = ROOT.TH1F(HISTNAME, HISTNAME, binning[0], binning[1], binning[2])
    else:
        nBins = len(binning) - 1
        # h = ROOT.TH1F(HISTNAME, HISTNAME, binning[0], binning[1], binning[2])  ## make it variable binning histogram
        h = ROOT.TH1F(HISTNAME, HISTNAME, nBins, array('d', binning))
    return h


def VarToHist(df_var, df_weight, df_weight_den, df_weight_num, HISTNAME, binning):
    h_var = SetHist(HISTNAME, binning)
    weight = 1.0
    for value, weight, numerator, denominator in zip(df_var, df_weight, df_weight_num, df_weight_den):
        if 'weightJEC' in HISTNAME:
            denominator = 1.0
        if denominator != 0:
            scale = numerator/denominator
        if '_nPV' in HISTNAME and denominator!=0:
            scale = 1/denominator
        if weight <= 0.0: scale = 1.0
        if ApplyWeight: h_var.Fill(value, (weight * scale))
        if not ApplyWeight: h_var.Fill(value)
    return h_var


def getBinRange(nBins, xlow, xhigh):
    diff = float(xhigh - xlow) / float(nBins)
    binRange = [xlow + ij * diff for ij in range(nBins + 1)]
    return binRange

# def HistWrtter(df, inFile,treeName, mode="UPDATE"):
def HistWrtter(df, outfilename, treeName, limit_varSR, limit_varCR, mainBin, mode="UPDATE"):
    if 'preselR' in treeName:
        reg = treeName.split('_')[1]
    else:
        reg = treeName.split('_')[1] + '_' + treeName.split('_')[2]
    h_list = []

    if ('SR' in reg) or ('preselR' in reg) or ('QCDCR' in reg):
        # CENTRAL AND SYSTEMATICS FOR MET HISTOGRAM
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varSR, mainBin))
        # B-TAG SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightB"], df["weightB_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_eff_bUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightB"], df["weightB_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_eff_bDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightFakeB"], df["weightFakeB_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_fake_bUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightFakeB"], df["weightFakeB_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_fake_bDown", mainBin))
        # EWK SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEWK"], df["weightEWK_up"],  "h_reg_"+reg+"_"+limit_varSR+"_EWKUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEWK"], df["weightEWK_down"],  "h_reg_"+reg+"_"+limit_varSR+"_EWKDown", mainBin))
        # Top pT REWEIGHTING
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightTop"], df["weightTop_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_TopUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightTop"], df["weightTop_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_TopDown", mainBin))
        # MET Trigger SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMETtrig"], df["weightMETtrig_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_metUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMETtrig"], df["weightMETtrig_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_metDown", mainBin))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleTrig"], df["weightEleTrig_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_eleUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleTrig"], df["weightEleTrig_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_eleDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleID"], df["weightEleID_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleIDUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleID"], df["weightEleID_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleIDDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleRECO"], df["weightEleRECO_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleRECOUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightEleRECO"], df["weightEleRECO_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleRECODown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuID"], df["weightMuID_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuIDUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuID"], df["weightMuID_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuIDDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuISO"], df["weightMuISO_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuISOUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuISO"], df["weightMuISO_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuISODown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuTRK"], df["weightMuTRK_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuTRKUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightMuTRK"], df["weightMuTRK_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuTRKDown", mainBin))
        # pu WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightPU"], df["weightPU_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_PUDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightPU"], df["weightPU_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_PUUp", mainBin))
        # weightJEC SYSTEMATICS
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weight"], df["weightJEC_up"],  "h_reg_"+reg+"_"+limit_varSR+"_JECUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weight"], df["weightJEC_down"],  "h_reg_"+reg+"_"+limit_varSR+"_JECDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECAbsoluteUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECAbsoluteUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECAbsolute_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECBBEC1Up'], "h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1Up", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECEC2Up'], "h_reg_"+reg+"_"+limit_varSR+"_JECEC2Up", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECEC2_yearUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECEC2_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECFlavorQCDUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECFlavorQCDUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECHFUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECHFUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECHF_yearUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECHF_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECRelativeBalUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECRelativeBalUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearUp'], "h_reg_"+reg+"_"+limit_varSR+"_JECRelativeSample_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECAbsoluteDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECAbsoluteDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECAbsolute_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECBBEC1Down'], "h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1Down", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECEC2Down'], "h_reg_"+reg+"_"+limit_varSR+"_JECEC2Down", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECEC2_yearDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECEC2_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECFlavorQCDDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECFlavorQCDDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECHFDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECHFDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECHF_yearDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECHF_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECRelativeBalDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECRelativeBalDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearDown'], "h_reg_"+reg+"_"+limit_varSR+"_JECRelativeSample_yearDown", mainBin))
        # JER SYSTEMATICS
        h_list.append(VarToHist(df["MET_Res_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varSR+"_ResUp", mainBin))
        h_list.append(VarToHist(df["MET_Res_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varSR+"_ResDown", mainBin))
        h_list.append(VarToHist(df["MET_En_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varSR+"_EnUp", mainBin))
        h_list.append(VarToHist(df["MET_En_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varSR+"_EnDown", mainBin))
        # pdf and scale systematics
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df["weightscale_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_mu_scaleUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df["weightscale_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_mu_scaleDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df["weightpdf_up"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_pdfUp", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightcentral"], df["weightpdf_down"], "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_pdfDown", mainBin))
        # Prefire Systematics
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightPrefire"], df["weightPrefire_up"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_prefireDown", mainBin))
        h_list.append(VarToHist(df[limit_varSR], df["weight"], df["weightPrefire"], df["weightPrefire_down"],  "h_reg_"+reg+"_"+limit_varSR+"_CMSyear_prefireUp", mainBin))
        h_list.append(VarToHist(df["Njets_PassID"],  df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nJets", [10, 0, 10]))
        h_list.append(VarToHist(df["Nbjets_PassID"],  df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nBJets", [10, 0, 10]))
        h_list.append(VarToHist(df["NEle"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NEle", [10, 0, 10]))
        h_list.append(VarToHist(df["pfpatCaloMETPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfpatCaloMETPt", [30, 0, 1000]))
        h_list.append(VarToHist(df["pfpatCaloMETPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfpatCaloMETPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["pfTRKMETPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfTRKMETPt", [30, 0, 1000]))
        h_list.append(VarToHist(df["pfTRKMETPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfTRKMETPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["NMu"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NMu", [10, 0, 10]))
        h_list.append(VarToHist(df["NTau"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NTau", [10, 0, 10]))
        h_list.append(VarToHist(df["nPho"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nPho", [10, 0, 10]))
        h_list.append(VarToHist(df["Jet1Pt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Pt", [50, 30, 1000]))
        h_list.append(VarToHist(df["Jet1Eta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Eta", [30, -2.5, 2.5]))
        h_list.append(VarToHist(df["Jet1Phi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Phi", [30, -3.14, 3.14]))
        h_list.append(VarToHist(df["Jet1deepCSV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1deepCSV", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2Pt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Pt", [15, 30, 800]))
        h_list.append(VarToHist(df["Jet2Eta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Eta", [15, -2.5, 2.5]))
        h_list.append(VarToHist(df["Jet2Phi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Phi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["Jet2deepCSV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2deepCSV", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2NHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2NEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CMulti"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CMulti", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet2NMultiplicity"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NMultiplicity", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet1NHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1NEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CMulti"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CMulti", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet1NMultiplicity"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NMultiplicity", [15, 0, 50]))
        h_list.append(VarToHist(df["nPV"], df["weight"], df["weightPU"], df["weight"], "h_reg_"+reg+"_nPV", [70, 0, 70]))
        h_list.append(VarToHist(df["nPV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_PUnPV", [70, 0, 70]))
        if 'QCDCR' in reg:
            h_list.append(VarToHist(df["dPhi_jetMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_min_dPhi", [15, 0.0, 0.5]))
        else:
            h_list.append(VarToHist(df["dPhi_jetMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_min_dPhi", [15, 0.5, 3.2]))
        h_list.append(VarToHist(df["dPhiTrk_pfMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiTrk_pfMET", [15, -3.2, 3.2]))
        h_list.append(VarToHist(df["dPhiCalo_pfMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiCalo_pfMET", [15, -3.2, 3.2]))
        h_list.append(VarToHist(df["JetwithEta4p5"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_JetwithEta4p5", [15, 0.0, 10]))
        h_list.append(VarToHist(df["METPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_METPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["ratioPtJet21"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_ratioPtJet21", [20, 0, 1]))
        h_list.append(VarToHist(df["dPhiJet12"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiJet12", [15, -8, 8]))
        h_list.append(VarToHist(df["dEtaJet12"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dEtaJet12", [15, -8, 8]))
        h_list.append(VarToHist(df["rJet1PtMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_rJet1PtMET", [50, 0, 50]))
        h_list.append(VarToHist(df["delta_pfCalo"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_delta_pfCalo", [15, 0, 1.5]))
        if ('SR_1b' in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('SR_2b' in reg):
            h_list.append(VarToHist(df['MET'], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET", [750,250,1000]))
            h_list.append(VarToHist(df["isjet2EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet3"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
        elif ('preselR' in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
            h_list.append(VarToHist(df["isjet2EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet3"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
    else:
        h_list.append(VarToHist(df["MET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET", [30, 0, 1000]))
        # CENTRAL AND SYSTEMATICS FOR Recoil HISTOGRAM
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varCR, mainBin))
        # B-TAG SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightB"], df["weightB_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_eff_bUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightB"], df["weightB_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_eff_bDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightFakeB"], df["weightFakeB_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_fake_bUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightFakeB"], df["weightFakeB_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_fake_bDown", mainBin))
        # EWK SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEWK"], df["weightEWK_up"],  "h_reg_"+reg+"_"+limit_varCR+"_EWKUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEWK"], df["weightEWK_down"],  "h_reg_"+reg+"_"+limit_varCR+"_EWKDown", mainBin))
        # Top pT REWEIGHTING
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightTop"], df["weightTop_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_TopUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightTop"], df["weightTop_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_TopDown", mainBin))
        # MET Trigger SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightRecoiltrig"], df["weightRecoiltrig_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_metUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightRecoiltrig"], df["weightRecoiltrig_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_metDown", mainBin))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleTrig"], df["weightEleTrig_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_eleUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleTrig"], df["weightEleTrig_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_eleDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleID"], df["weightEleID_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleIDUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleID"], df["weightEleID_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleIDDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleRECO"], df["weightEleRECO_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleRECOUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightEleRECO"], df["weightEleRECO_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleRECODown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuID"], df["weightMuID_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuIDUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuID"], df["weightMuID_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuIDDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuISO"], df["weightMuISO_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuISOUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuISO"], df["weightMuISO_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuISODown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuTRK"], df["weightMuTRK_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuTRKUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightMuTRK"], df["weightMuTRK_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuTRKDown", mainBin))
        # pu WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightPU"], df["weightPU_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_PUDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightPU"], df["weightPU_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_PUUp", mainBin))
        # weightJEC SYSTEMATICS
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weight"], df["weightJEC_up"],  "h_reg_"+reg+"_"+limit_varCR+"_JECUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weight"], df["weightJEC_down"],  "h_reg_"+reg+"_"+limit_varCR+"_JECDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECAbsoluteUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECAbsoluteUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECAbsolute_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECBBEC1Up'], "h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1Up", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECEC2Up'], "h_reg_"+reg+"_"+limit_varCR+"_JECEC2Up", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECEC2_yearUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECEC2_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECFlavorQCDUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECFlavorQCDUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECHFUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECHFUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECHF_yearUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECHF_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECRelativeBalUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECRelativeBalUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearUp'], "h_reg_"+reg+"_"+limit_varCR+"_JECRelativeSample_yearUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECAbsoluteDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECAbsoluteDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECAbsolute_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECBBEC1Down'], "h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1Down", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECEC2Down'], "h_reg_"+reg+"_"+limit_varCR+"_JECEC2Down", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECEC2_yearDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECEC2_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECFlavorQCDDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECFlavorQCDDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECHFDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECHFDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECHF_yearDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECHF_yearDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECRelativeBalDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECRelativeBalDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearDown'], "h_reg_"+reg+"_"+limit_varCR+"_JECRelativeSample_yearDown", mainBin))
        # JER SYSTEMATICS
        h_list.append(VarToHist(df["Recoil_Res_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varCR+"_ResUp", mainBin))
        h_list.append(VarToHist(df["Recoil_Res_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varCR+"_ResDown", mainBin))
        h_list.append(VarToHist(df["Recoil_En_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varCR+"_EnUp", mainBin))
        h_list.append(VarToHist(df["Recoil_En_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_"+limit_varCR+"_EnDown", mainBin))
        # pdf and scale systematics
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df["weightscale_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_mu_scaleUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df["weightscale_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_mu_scaleDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df["weightpdf_up"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_pdfUp", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightcentral"], df["weightpdf_down"], "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_pdfDown", mainBin))
        # Prefire Systematics
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightPrefire"], df["weightPrefire_up"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_prefireDown", mainBin))
        h_list.append(VarToHist(df[limit_varCR], df["weight"], df["weightPrefire"], df["weightPrefire_down"],  "h_reg_"+reg+"_"+limit_varCR+"_CMSyear_prefireUp", mainBin))

        ###########################
        h_list.append(VarToHist(df["dPhiJet1Lep1"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiJet1Lep1", [15, 0, 5]))
        h_list.append(VarToHist(df["dPhi_lep1_MET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhi_lep1_MET", [15, 0, 5]))
        h_list.append(VarToHist(df["dPhi_lep2_MET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhi_lep2_MET", [15, 0, 5]))
        h_list.append(VarToHist(df["Jet1Pt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Pt", [50, 30, 1000]))
        h_list.append(VarToHist(df["Jet1Eta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Eta", [30, -2.5, 2.5]))
        h_list.append(VarToHist(df["Jet1Phi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1Phi", [30, -3.14, 3.14]))
        h_list.append(VarToHist(df["Jet1deepCSV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1deepCSV", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Njets_PassID"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nJets", [10, 0, 10]))
        h_list.append(VarToHist(df["Nbjets_PassID"],  df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nBJets", [10, 0, 10]))
        h_list.append(VarToHist(df["NEle"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NEle", [10, 0, 10]))
        h_list.append(VarToHist(df["pfpatCaloMETPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfpatCaloMETPt", [30, 0, 1000]))
        h_list.append(VarToHist(df["pfpatCaloMETPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfpatCaloMETPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["pfTRKMETPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfTRKMETPt", [30, 0, 1000]))
        h_list.append(VarToHist(df["pfTRKMETPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_pfTRKMETPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["NMu"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NMu", [10, 0, 10]))
        h_list.append(VarToHist(df["NTau"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_NTau", [10, 0, 10]))
        h_list.append(VarToHist(df["nPho"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_nPho", [10, 0, 10]))
        h_list.append(VarToHist(df["Jet2Pt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Pt", [15, 30, 800]))
        h_list.append(VarToHist(df["Jet2Eta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Eta", [15, -2.5, 2.5]))
        h_list.append(VarToHist(df["Jet2Phi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2Phi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["Jet2deepCSV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2deepCSV", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2NHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2NEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet2CMulti"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2CMulti", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet2NMultiplicity"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet2NMultiplicity", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet1NHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CHadEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CHadEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1NEmEF"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NEmEF", [15, 0, 1.1]))
        h_list.append(VarToHist(df["Jet1CMulti"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1CMulti", [15, 0, 50]))
        h_list.append(VarToHist(df["Jet1NMultiplicity"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Jet1NMultiplicity", [15, 0, 50]))
        h_list.append(VarToHist(df["nPV"], df["weight"], df["weightPU"], df["weight"], "h_reg_"+reg+"_nPV", [70, 0, 70]))
        h_list.append(VarToHist(df["nPV"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_PUnPV", [70, 0, 70]))
        h_list.append(VarToHist(df["METPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_METPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["RecoilPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_RecoilPhi", [15, -3.14, 3.14]))
        h_list.append(VarToHist(df["dPhi_jetMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_min_dPhi", [15, 0.5, 3.2]))
        h_list.append(VarToHist(df["dPhiTrk_pfMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiTrk_pfMET", [15, -3.2, 3.2]))
        h_list.append(VarToHist(df["dPhiCalo_pfMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiCalo_pfMET", [15, -3.2, 3.2]))
        h_list.append(VarToHist(df["JetwithEta4p5"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_JetwithEta4p5", [15, 0.0, 10]))  # min_dPhi)
        h_list.append(VarToHist(df["leadingLepPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep1_pT", [15, 30, 500]))
        h_list.append(VarToHist(df["leadingLepEta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep1_eta", [30, -2.5, 2.5]))
        h_list.append(VarToHist(df["leadingLepPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep1_Phi", [30, -3.14, 3.14]))
        if ('Wmunu' in reg) or ('Wenu' in reg) or ('Topmunu' in reg) or ('Topenu' in reg):
            h_list.append(VarToHist(df["Wmass"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Wmass", [16, 0, 160]))
            h_list.append(VarToHist(df["WpT"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_WpT", [15, 0, 700]))
        if 'Zmumu' in reg or 'Zee' in reg:
            h_list.append(VarToHist(df["Zmass"], df["weight"], df["weight"],df["weight"], "h_reg_"+reg+"_Zmass", [15, 60, 120]))
            h_list.append(VarToHist( df["ZpT"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_ZpT", [15, 0, 700]))
            h_list.append(VarToHist(df["subleadingLepPt"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep2_pT", [15, 30, 500]))
            h_list.append(VarToHist(df["subleadingLepEta"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep2_eta", [30, -2.5, 2.5]))
            h_list.append(VarToHist(df["subleadingLepPhi"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_lep2_Phi", [30, -3.14, 3.14]))
        if ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(VarToHist(df["ratioPtJet21"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_ratioPtJet21", [20, 0, 1]))
            h_list.append(VarToHist(df["dPhiJet12"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dPhiJet12", [15, -8, 8]))
            h_list.append(VarToHist(df["dEtaJet12"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_dEtaJet12", [15, -8, 8]))
        h_list.append(VarToHist(df["rJet1PtMET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_rJet1PtMET", [50, 0, 50]))
        h_list.append(VarToHist(df["delta_pfCalo"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_delta_pfCalo", [15, 0, 1.5]))
        if ('1b' in reg or '2j' in reg) and ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('WmunuCR_2b' in reg or 'WenuCR_2b' in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('2b' in reg or '3j' in reg):
            h_list.append(VarToHist(df['Recoil'], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil", [750,250,1000]))
            h_list.append(VarToHist(df["isjet2EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet3"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
    #outfilename = 'Output_'+inFile.split('/')[-1]
    fout = ROOT.TFile(outfilename, mode)
    for ih in h_list:
        ih.Write()


def emptyHistWritter(treeName, outfilename, limit_varSR, limit_varCR, mainBin, mode="UPDATE"):
    h_list = []
    if 'preselR' in treeName:
        reg = treeName.split('_')[1]
    else:
        reg = treeName.split('_')[1] + '_' + treeName.split('_')[2]
    if ('SR' in reg) or ('preselR' in reg) or ('QCDCR' in reg):
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR,mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_eff_bUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_eff_bDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_fake_bUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_fake_bDown", mainBin))
        # EWK SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_EWKUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_EWKDown", mainBin))
        # Top pT REWEIGHTING
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_TopUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_TopDown", mainBin))
        # MET Trigger SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_metUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_metDown", mainBin))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_eleUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_trig_eleDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleIDUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleIDDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleRECOUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_EleRECODown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuIDUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuIDDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuISOUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuISODown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuTRKUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_MuTRKDown", mainBin))
        # pu WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_PUUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_PUDown", mainBin))
        # weightJEC SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECAbsoluteUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECAbsolute_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1Up",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECEC2Up",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECEC2_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECFlavorQCDUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECHFUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECHF_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECRelativeBalUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECRelativeSample_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECAbsoluteDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECAbsolute_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1Down",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECBBEC1_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECEC2Down",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECEC2_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECFlavorQCDDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECHFDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECHF_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECRelativeBalDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_JECRelativeSample_yearDown",mainBin))
        # JER SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_ResUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_ResDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_EnUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_EnDown",mainBin))

        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_mu_scaleUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_mu_scaleDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_pdfUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_pdfDown", mainBin))

        # Prefire Systematics
        h_list.append(SetHist("h_reg_" + reg +"_"+limit_varSR+"_CMSyear_prefireDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varSR+"_CMSyear_prefireUp", mainBin))

        h_list.append(SetHist("h_reg_"+reg+"_nJets", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_nBJets", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_NEle", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_pfpatCaloMETPt", [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_pfpatCaloMETPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_pfTRKMETPt", [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_pfTRKMETPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_NMu", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_NTau", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_nPho", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Pt", [50, 30, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Eta", [30, -2.5, 2.5]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Phi", [30, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1deepCSV", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CMulti", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NMultiplicity", [15, 0, 50]))
        if 'QCDCR' in reg:
            h_list.append(SetHist("h_reg_"+reg+"_min_dPhi", [15, 0.0, 0.5]))
        else:
            h_list.append(SetHist("h_reg_"+reg+"_min_dPhi", [15, 0.5, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhiTrk_pfMET", [15, -3.2, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhiCalo_pfMET", [15, -3.2, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Pt", [15, 30, 800]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Eta", [15, -2.5, 2.5]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Phi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2deepCSV", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CMulti", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NMultiplicity", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_nPV", [70, 0, 70]))
        h_list.append(SetHist("h_reg_"+reg+"_PUnPV", [70, 0, 70]))

        h_list.append(SetHist("h_reg_"+reg+"_JetwithEta4p5", [15, 0.0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_METPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_ratioPtJet21", [20, 0, 1]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhiJet12", [15, -8, 8]))
        h_list.append(SetHist("h_reg_"+reg+"_dEtaJet12", [15, -8, 8]))
        h_list.append(SetHist("h_reg_"+reg+"_rJet1PtMET", [50, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_delta_pfCalo", [15, 0, 1.5]))
        if ('SR_1b' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('SR_2b' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_MET", [750, 250, 1000]))
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
        elif ('preselR' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
    else:
        h_list.append(SetHist("h_reg_"+reg+"_MET",   [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR,mainBin))
        # btag SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_eff_bUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_eff_bDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_fake_bUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_fake_bDown", mainBin))
        # EWK SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_EWKUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_EWKDown", mainBin))
        # Top pT REWEIGHTING
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_TopUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_TopDown", mainBin))
        # MET Trigger SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_metUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_metDown", mainBin))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_eleUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_trig_eleDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleIDUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleIDDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleRECOUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_EleRECODown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuIDUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuIDDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuISOUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuISODown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuTRKUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_MuTRKDown", mainBin))

        # pu WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_PUUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_PUDown", mainBin))
        # weightJEC SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECAbsoluteUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECAbsolute_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1Up",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECEC2Up",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECEC2_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECFlavorQCDUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECHFUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECHF_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECRelativeBalUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECRelativeSample_yearUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECAbsoluteDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECAbsolute_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1Down",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECBBEC1_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECEC2Down",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECEC2_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECFlavorQCDDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECHFDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECHF_yearDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECRelativeBalDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_JECRelativeSample_yearDown",mainBin))
        # JER SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_ResUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_ResDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_EnUp",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_EnDown",mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_mu_scaleUp", mainBin))
        h_list.append(SetHist("h_reg_" + reg +"_"+limit_varCR+"_CMSyear_mu_scaleDown", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_pdfUp", mainBin))
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_pdfDown", mainBin))
        # Prefire Systematics
        h_list.append(SetHist("h_reg_"+reg+"_"+limit_varCR+"_CMSyear_prefireDown", mainBin))
        h_list.append(SetHist("h_reg_" + reg +"_"+limit_varCR+"_CMSyear_prefireUp", mainBin))

        h_list.append(SetHist("h_reg_"+reg+"_dPhiJet1Lep1", [15, 0, 5]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhi_lep1_MET", [15, 0, 5]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhi_lep2_MET", [15, 0, 5]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Pt", [50, 30, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Eta", [30, -2.5, 2.5]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1Phi", [30, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1deepCSV", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1CMulti", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet1NMultiplicity", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Pt", [15, 30, 800]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Eta", [15, -2.5, 2.5]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2Phi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2deepCSV", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CHadEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NEmEF", [15, 0, 1.1]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2CMulti", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_Jet2NMultiplicity", [15, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_nPV", [70, 0, 70]))
        h_list.append(SetHist("h_reg_"+reg+"_PUnPV", [70, 0, 70]))
        h_list.append(SetHist("h_reg_"+reg+"_nJets", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_nBJets", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_NEle", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_pfpatCaloMETPt", [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_pfpatCaloMETPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_pfTRKMETPt", [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_pfTRKMETPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_NMu", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_NTau", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_nPho", [10, 0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_METPhi", [15, -3.14, 3.14]))
        h_list.append(SetHist("h_reg_"+reg+"_RecoilPhi", [15, -3.14, 3.14]))
        # mini_dPhi)
        h_list.append(SetHist("h_reg_"+reg+"_min_dPhi", [15, 0.5, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhiTrk_pfMET", [15, -3.2, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_dPhiCalo_pfMET", [15, -3.2, 3.2]))
        h_list.append(SetHist("h_reg_"+reg+"_JetwithEta4p5", [15, 0.0, 10]))
        h_list.append(SetHist("h_reg_"+reg+"_lep1_pT", [15, 30, 500]))
        h_list.append(SetHist("h_reg_"+reg+"_lep1_eta", [30, -2.5, 2.5]))
        h_list.append(SetHist("h_reg_"+reg+"_lep1_Phi", [30, -3.14, 3.14]))
        if ('Wmunu' in reg) or ('Wenu' in reg) or ('Topmunu' in reg) or ('Topenu' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_Wmass", [16, 0, 160]))
            h_list.append(SetHist("h_reg_"+reg+"_WpT", [15, 0, 700]))
        if 'Zmumu' in reg or 'Zee' in reg:
            h_list.append(SetHist("h_reg_"+reg+"_Zmass", [15, 60, 120]))
            h_list.append(SetHist("h_reg_"+reg+"_ZpT", [15, 0, 700]))
            h_list.append(SetHist("h_reg_"+reg+"_lep2_pT", [15, 30, 500]))
            h_list.append(SetHist("h_reg_"+reg+"_lep2_eta", [30, -2.5, 2.5]))
            h_list.append(SetHist("h_reg_"+reg+"_lep2_Phi", [30, -3.14, 3.14]))
        if ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(SetHist("h_reg_"+reg+"_ratioPtJet21", [20, 0, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_dPhiJet12", [15, -8, 8]))
            h_list.append(SetHist("h_reg_"+reg+"_dEtaJet12", [15, -8, 8]))
        if ('1b' in reg or '2j' in reg) and ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('WmunuCR_2b' in reg) or ('WenuCR_2b' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('2b' in reg or '3j' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_Recoil", [750, 250, 1000]))
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
        h_list.append(SetHist("h_reg_"+reg+"_rJet1PtMET", [50, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_delta_pfCalo", [15, 0, 1.5]))
    fout = ROOT.TFile(outfilename, mode)
    for ih in h_list:
        ih.Write()


'''
---------------------------------------------------------------
START MAKING HISTOGRAMS
---------------------------------------------------------------
'''

trees = ['bbDM_preselR', 'bbDM_SR_1b', 'bbDM_SR_2b', 'bbDM_ZeeCR_1b', 'bbDM_ZeeCR_2b', 'bbDM_ZmumuCR_1b', 'bbDM_ZmumuCR_2b', 'bbDM_ZeeCR_2j', 'bbDM_ZeeCR_3j', 'bbDM_ZmumuCR_2j', 'bbDM_ZmumuCR_3j', 'bbDM_WenuCR_1b', 'bbDM_WenuCR_2b', 'bbDM_WmunuCR_1b', 'bbDM_WmunuCR_2b', 'bbDM_TopenuCR_1b', 'bbDM_TopenuCR_2b', 'bbDM_TopmunuCR_1b', 'bbDM_TopmunuCR_2b', 'bbDM_QCDCR_1b', 'bbDM_QCDCR_2b']


# inputFilename=infile
filename = infile
ApplyWeight = True


def runFile(trees, filename):
    tf = ROOT.TFile(filename)
    h_reg_preselR_cutFlow = tf.Get('h_reg_preselR_cutFlow')
    h_reg_SR_1b_cutFlow = tf.Get('h_reg_SR_1b_cutFlow')
    h_reg_SR_2b_cutFlow = tf.Get('h_reg_SR_2b_cutFlow')
    h_reg_ZeeCR_1b_cutFlow = tf.Get('h_reg_ZeeCR_1b_cutFlow')
    h_reg_ZeeCR_2b_cutFlow = tf.Get('h_reg_ZeeCR_2b_cutFlow')
    h_reg_ZmumuCR_1b_cutFlow = tf.Get('h_reg_ZmumuCR_1b_cutFlow')
    h_reg_ZmumuCR_2b_cutFlow = tf.Get('h_reg_ZmumuCR_2b_cutFlow')
    h_reg_ZeeCR_2j_cutFlow = tf.Get('h_reg_ZeeCR_2j_cutFlow')
    h_reg_ZeeCR_3j_cutFlow = tf.Get('h_reg_ZeeCR_3j_cutFlow')
    h_reg_ZmumuCR_2j_cutFlow = tf.Get('h_reg_ZmumuCR_2j_cutFlow')
    h_reg_ZmumuCR_3j_cutFlow = tf.Get('h_reg_ZmumuCR_3j_cutFlow')
    h_reg_WenuCR_1b_cutFlow = tf.Get('h_reg_WenuCR_1b_cutFlow')
    h_reg_WenuCR_2b_cutFlow = tf.Get('h_reg_WenuCR_2b_cutFlow')
    h_reg_WmunuCR_1b_cutFlow = tf.Get('h_reg_WmunuCR_1b_cutFlow')
    h_reg_WmunuCR_2b_cutFlow = tf.Get('h_reg_WmunuCR_2b_cutFlow')
    h_reg_TopenuCR_1b_cutFlow = tf.Get('h_reg_TopenuCR_1b_cutFlow')
    h_reg_TopenuCR_2b_cutFlow = tf.Get('h_reg_TopenuCR_2b_cutFlow')
    h_reg_TopmunuCR_1b_cutFlow = tf.Get('h_reg_TopmunuCR_1b_cutFlow')
    h_reg_TopmunuCR_2b_cutFlow = tf.Get('h_reg_TopmunuCR_2b_cutFlow')
    h_reg_QCDCR_1b_cutFlow = tf.Get('h_reg_QCDCR_1b_cutFlow')
    h_reg_QCDCR_2b_cutFlow = tf.Get('h_reg_QCDCR_2b_cutFlow')
    global ApplyWeight
    if ('SingleElectron' in filename.split('/')[-1]) or ('MET' in filename.split('/')[-1]) or('EGamma' in filename.split('/')[-1]):
        ApplyWeight = False
    else:
        ApplyWeight = True
    print('ApplyWeight', ApplyWeight)
    h_total = tf.Get('h_total')
    h_total_weight = tf.Get('h_total_mcweight')
    outfilename = outputdir + '/Output_' +filename.split('/')[-1]
    for index, tree in enumerate(trees):
        # limit_varSR = 'MET'; limit_varCR = 'Recoil'; mainBin = [750,250,1000]
        # limit_varSR = limit_varCR = 'bdtscore'; mainBin = [200, -1, 1]
        if '_1b' in tree or 'presel' in tree or '_2j' in tree :
            limit_varSR = 'MET'; limit_varCR = 'Recoil'; mainBin = [750,250,1000]
        elif '_2b' in tree or '_3j' in tree:
            limit_varSR = limit_varCR = 'ctsValue'; mainBin = [200, 0, 1]
        tt = tf.Get(tree)
        nent = tt.GetEntries()
        if index == 0:
            mode = "RECREATE"
        if index > 0:
            mode = "UPDATE"
        if nent > 0:
            df = read_root(filename, tree)
            # score = addbdtscore(filename,tree)
            # df["bdtscore"]=score
            #df['del_minus'] = df.dPhi_jetMET - df.dPhiJet12
            #df['del_plus'] = abs(df.dPhi_jetMET + df.dPhiJet12 - np.pi)
            if ('_2b' in tree) or ('_3j' in tree):
                df['ctsValue'] = abs(np.tanh(df.dEtaJet12.div(2)))
            df['dPhiTrk_pfMET'] = DeltaPhi(df.METPhi, df.pfTRKMETPhi)
            df['dPhiCalo_pfMET'] = DeltaPhi(df.METPhi, df.pfpatCaloMETPhi)
            df['weightcentral'] = 1.0
            df = df[df.Jet1Pt > 0.0]
            if ('SR' not in tree) and ('QCDCR' not in tree) and ('preselR' not in tree):
                df['dPhiJet1Lep1'] = DeltaPhi(df.Jet1Phi, df.leadingLepPhi)
            # df = df[df.isak4JetBasedHemEvent == 0] #### only uncomment it for 2018 CD Era
            HistWrtter(df, outfilename, tree, limit_varSR, limit_varCR, mainBin, mode)
        else:
            emptyHistWritter(tree, outfilename, limit_varSR, limit_varCR, mainBin, mode)
    f = ROOT.TFile(outfilename, "UPDATE")
    h_reg_preselR_cutFlow.Write()
    h_reg_SR_1b_cutFlow.Write()
    h_reg_SR_2b_cutFlow.Write()
    h_reg_ZeeCR_1b_cutFlow.Write()
    h_reg_ZeeCR_2b_cutFlow.Write()
    h_reg_ZmumuCR_1b_cutFlow.Write()
    h_reg_ZmumuCR_2b_cutFlow.Write()
    h_reg_ZeeCR_2j_cutFlow.Write()
    h_reg_ZeeCR_3j_cutFlow.Write()
    h_reg_ZmumuCR_2j_cutFlow.Write()
    h_reg_ZmumuCR_3j_cutFlow.Write()
    h_reg_WenuCR_1b_cutFlow.Write()
    h_reg_WenuCR_2b_cutFlow.Write()
    h_reg_WmunuCR_1b_cutFlow.Write()
    h_reg_WmunuCR_2b_cutFlow.Write()
    h_reg_TopenuCR_1b_cutFlow.Write()
    h_reg_TopenuCR_2b_cutFlow.Write()
    h_reg_TopmunuCR_1b_cutFlow.Write()
    h_reg_TopmunuCR_2b_cutFlow.Write()
    h_reg_QCDCR_1b_cutFlow.Write()
    h_reg_QCDCR_2b_cutFlow.Write()
    h_total_weight.Write()
    h_total.Write()

if isfarmout:
    path = inDir
    files = glob.glob(path + '/*')

    def main():
        iterable = files
        pool = mp.Pool()
        func = partial(runFile, trees)
        pool.map(func, iterable)
        pool.close()
        pool.join()

    if __name__ == "__main__":
        main()

if not isfarmout:
    filename = infile
    print('running code for file:  ', filename)
    runFile(trees, filename)

stop = time.time()
print("%.4gs" % (stop - start))
