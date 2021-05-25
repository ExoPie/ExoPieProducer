from ROOT import TFile, TTree, TH1F, TH1D, TH1, TCanvas, TChain, TGraphAsymmErrors, TMath, TH2D, TLorentzVector, AddressOf, gROOT, TNamed
import ROOT as ROOT
import os
import traceback
import sys
import optparse
import argparse
from array import array
import math
import numpy as numpy
import pandas
from root_pandas import read_root
from pandas import DataFrame, concat
from pandas import Series
import time
import glob
import multiprocessing as mp
from functools import partial
# import matplotlib
# import matplotlib.pyplot as plt
# matplotlib.use('pdf')

# ----- start of clock
start = time.time()


def Phi_mpi_pi(x):
    kPI = numpy.array(3.14159265)
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
    h = TH1F()
    if len(binning) == 3:
        h = TH1F(HISTNAME, HISTNAME, binning[0], binning[1], binning[2])
    else:
        nBins = len(binning) - 1
        # h = TH1F(HISTNAME, HISTNAME, binning[0], binning[1], binning[2])  ## make it variable binning histogram
        h = TH1F(HISTNAME, HISTNAME, nBins, array('d', binning))
    return h


def VarToHist(df_var, df_weight, df_weight_den, df_weight_num, HISTNAME, binning):
    h_var = SetHist(HISTNAME, binning)
    weight = 1.0
    weightPU = 1.0
    btag = 1.0
    for ij in df_var.index:
        value = df_var[ij]
        weight = df_weight[ij]
        #prefire_wgt = df["weightPrefire"][ij]
        # print df
        numerator = df_weight_num[ij]
        if 'weightJEC' in HISTNAME:
            denominator = 1
        else:
            denominator = df_weight_den[ij]
        if denominator==0:
            denominator = 1
            scale = 1
        else:
            scale = numerator/denominator
        if '_nPV' in HISTNAME:
            scale = 1/denominator
        if weight == 0.0:
            scale = 1.0
        if ApplyWeight:
            h_var.Fill(value, (weight * scale))
        if not ApplyWeight:
            h_var.Fill(value)

    # h_var = SetHist(HISTNAME, binning)
    # if '_nPV' in HISTNAME:
    #     weight = df_weight * (1 / df_weight_den)
    # else:
    #     weight = df_weight * (df_weight_num / df_weight_den)

    # if len(binning) > 3:
    #     ## variable binning overflow tested, so MET/Recoil are safe.
    #     binning.append(10000)  # to take care of overflow
    #     n, bins, patches = plt.hist(
    #   df_var, binning, histtype='step', weights=weight)
    # if len(binning) == 3:
    #     ## uniform bin overflow is not tested
    #     binning.append(binning[-1]*3)  # to take care of overflow
    #     n, bins, patches = plt.hist(df_var, binning[0], range=(
    #         binning[1], binning[2]), histtype='step', weights=weight)
    # n = list(n)
    # n_last = n[-1]
    # n.remove(n_last)
    # n[-1] = n[-1] + n_last

    # for ibin in range(len((n))):
    #     h_var.SetBinContent(ibin+1, n[ibin])

    return h_var


def getBinRange(nBins, xlow, xhigh):
    diff = float(xhigh - xlow) / float(nBins)
    binRange = [xlow + ij * diff for ij in range(nBins + 1)]
    return binRange

# def HistWrtter(df, inFile,treeName, mode="UPDATE"):


def HistWrtter(df, outfilename, treeName, mode="UPDATE"):
    h_list = []
    if 'preselR' in treeName:
        reg = treeName.split('_')[1]
    else:
        reg = treeName.split('_')[1] + '_' + treeName.split('_')[2]
    if ('SR' in reg) or ('preselR' in reg) or ('QCDCR' in reg):
        # CENTRAL AND SYSTEMATICS FOR MET HISTOGRAM
        h_list.append(VarToHist(df["MET"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET", [750,250,1000]))
        # B-TAG SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightB"], df["weightB_up"],  "h_reg_"+reg+"_MET_CMSyear_eff_bUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightB"], df["weightB_down"],  "h_reg_"+reg+"_MET_CMSyear_eff_bDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightFakeB"], df["weightFakeB_up"],  "h_reg_"+reg+"_MET_CMSyear_fake_bUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightFakeB"], df["weightFakeB_down"],  "h_reg_"+reg+"_MET_CMSyear_fake_bDown", [750,250,1000]))
        # EWK SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEWK"], df["weightEWK_up"],  "h_reg_"+reg+"_MET_EWKUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEWK"], df["weightEWK_down"],  "h_reg_"+reg+"_MET_EWKDown", [750,250,1000]))
        # Top pT REWEIGHTING
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightTop"], df["weightTop_up"],  "h_reg_"+reg+"_MET_CMSyear_TopUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightTop"], df["weightTop_down"],  "h_reg_"+reg+"_MET_CMSyear_TopDown", [750,250,1000]))
        # MET Trigger SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMETtrig"], df["weightMETtrig_up"],  "h_reg_"+reg+"_MET_CMSyear_METtrigUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMETtrig"], df["weightMETtrig_down"],  "h_reg_"+reg+"_MET_CMSyear_METtrigDown", [750,250,1000]))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleTrig"], df["weightEleTrig_up"], "h_reg_"+reg+"_MET_CMSyear_EletrigUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleTrig"], df["weightEleTrig_down"], "h_reg_"+reg+"_MET_CMSyear_EletrigDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleID"], df["weightEleID_up"], "h_reg_"+reg+"_MET_CMSyear_EleIDUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleID"], df["weightEleID_down"], "h_reg_"+reg+"_MET_CMSyear_EleIDDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleRECO"], df["weightEleRECO_up"], "h_reg_"+reg+"_MET_CMSyear_EleRECOUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightEleRECO"], df["weightEleRECO_down"], "h_reg_"+reg+"_MET_CMSyear_EleRECODown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuID"], df["weightMuID_up"], "h_reg_"+reg+"_MET_CMSyear_MuIDUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuID"], df["weightMuID_down"], "h_reg_"+reg+"_MET_CMSyear_MuIDDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuISO"], df["weightMuISO_up"], "h_reg_"+reg+"_MET_CMSyear_MuISOUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuISO"], df["weightMuISO_down"], "h_reg_"+reg+"_MET_CMSyear_MuISODown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuTRK"], df["weightMuTRK_up"], "h_reg_"+reg+"_MET_CMSyear_MuTRKUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightMuTRK"], df["weightMuTRK_down"], "h_reg_"+reg+"_MET_CMSyear_MuTRKDown", [750,250,1000]))
        # pu WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightPU"], df["weightPU_up"],  "h_reg_"+reg+"_MET_CMSyear_PUDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightPU"], df["weightPU_down"],  "h_reg_"+reg+"_MET_CMSyear_PUUp", [750,250,1000]))
        # weightJEC SYSTEMATICS
        h_list.append(VarToHist(df["MET"], df["weight"], df["weight"], df["weightJEC_up"],  "h_reg_"+reg+"_MET_JECUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weight"], df["weightJEC_down"],  "h_reg_"+reg+"_MET_JECDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECAbsoluteUp'], "h_reg_"+reg+"_MET_JECAbsoluteUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearUp'], "h_reg_"+reg+"_MET_JECAbsolute_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECBBEC1Up'], "h_reg_"+reg+"_MET_JECBBEC1Up", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearUp'], "h_reg_"+reg+"_MET_JECBBEC1_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECEC2Up'], "h_reg_"+reg+"_MET_JECEC2Up", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECEC2_yearUp'], "h_reg_"+reg+"_MET_JECEC2_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECFlavorQCDUp'], "h_reg_"+reg+"_MET_JECFlavorQCDUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECHFUp'], "h_reg_"+reg+"_MET_JECHFUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECHF_yearUp'], "h_reg_"+reg+"_MET_JECHF_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECRelativeBalUp'], "h_reg_"+reg+"_MET_JECRelativeBalUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearUp'], "h_reg_"+reg+"_MET_JECRelativeSample_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECAbsoluteDown'], "h_reg_"+reg+"_MET_JECAbsoluteDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearDown'], "h_reg_"+reg+"_MET_JECAbsolute_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECBBEC1Down'], "h_reg_"+reg+"_MET_JECBBEC1Down", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearDown'], "h_reg_"+reg+"_MET_JECBBEC1_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECEC2Down'], "h_reg_"+reg+"_MET_JECEC2Down", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECEC2_yearDown'], "h_reg_"+reg+"_MET_JECEC2_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECFlavorQCDDown'], "h_reg_"+reg+"_MET_JECFlavorQCDDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECHFDown'], "h_reg_"+reg+"_MET_JECHFDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECHF_yearDown'], "h_reg_"+reg+"_MET_JECHF_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECRelativeBalDown'], "h_reg_"+reg+"_MET_JECRelativeBalDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearDown'], "h_reg_"+reg+"_MET_JECRelativeSample_yearDown", [750,250,1000]))
        # JER SYSTEMATICS
        h_list.append(VarToHist(df["MET_Res_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET_ResUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET_Res_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET_ResDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET_En_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET_EnUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET_En_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_MET_EnDown", [750,250,1000]))
        # pdf and scale systematics
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df["weightscale_up"], "h_reg_"+reg+"_MET_CMSyear_mu_scaleUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df["weightscale_down"], "h_reg_"+reg+"_MET_CMSyear_mu_scaleDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df["weightpdf_up"], "h_reg_"+reg+"_MET_CMSyear_pdfUp", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightcentral"], df["weightpdf_down"], "h_reg_"+reg+"_MET_CMSyear_pdfDown", [750,250,1000]))
        # Prefire Systematics
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightPrefire"], df["weightPrefire_up"],  "h_reg_"+reg+"_MET_CMSyear_prefireDown", [750,250,1000]))
        h_list.append(VarToHist(df["MET"], df["weight"], df["weightPrefire"], df["weightPrefire_down"],  "h_reg_"+reg+"_MET_CMSyear_prefireUp", [750,250,1000]))
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
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil", [750,250,1000]))
        # B-TAG SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightB"], df["weightB_up"],  "h_reg_"+reg+"_Recoil_CMSyear_eff_bUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightB"], df["weightB_down"],  "h_reg_"+reg+"_Recoil_CMSyear_eff_bDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightFakeB"], df["weightFakeB_up"],  "h_reg_"+reg+"_Recoil_CMSyear_fake_bUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightFakeB"], df["weightFakeB_down"],  "h_reg_"+reg+"_Recoil_CMSyear_fake_bDown", [750,250,1000]))
        # EWK SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEWK"], df["weightEWK_up"],  "h_reg_"+reg+"_Recoil_EWKUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEWK"], df["weightEWK_down"],  "h_reg_"+reg+"_Recoil_EWKDown", [750,250,1000]))
        # Top pT REWEIGHTING
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightTop"], df["weightTop_up"],  "h_reg_"+reg+"_Recoil_CMSyear_TopUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightTop"], df["weightTop_down"],  "h_reg_"+reg+"_Recoil_CMSyear_TopDown", [750,250,1000]))
        # MET Trigger SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightRecoiltrig"], df["weightRecoiltrig_up"],  "h_reg_"+reg+"_Recoil_CMSyear_METtrigUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightRecoiltrig"], df["weightRecoiltrig_down"],  "h_reg_"+reg+"_Recoil_CMSyear_METtrigDown", [750,250,1000]))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleTrig"], df["weightEleTrig_up"], "h_reg_"+reg+"_Recoil_CMSyear_EletrigUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleTrig"], df["weightEleTrig_down"], "h_reg_"+reg+"_Recoil_CMSyear_EletrigDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleID"], df["weightEleID_up"], "h_reg_"+reg+"_Recoil_CMSyear_EleIDUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleID"], df["weightEleID_down"], "h_reg_"+reg+"_Recoil_CMSyear_EleIDDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleRECO"], df["weightEleRECO_up"], "h_reg_"+reg+"_Recoil_CMSyear_EleRECOUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightEleRECO"], df["weightEleRECO_down"], "h_reg_"+reg+"_Recoil_CMSyear_EleRECODown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuID"], df["weightMuID_up"], "h_reg_"+reg+"_Recoil_CMSyear_MuIDUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuID"], df["weightMuID_down"], "h_reg_"+reg+"_Recoil_CMSyear_MuIDDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuISO"], df["weightMuISO_up"], "h_reg_"+reg+"_Recoil_CMSyear_MuISOUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuISO"], df["weightMuISO_down"], "h_reg_"+reg+"_Recoil_CMSyear_MuISODown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuTRK"], df["weightMuTRK_up"], "h_reg_"+reg+"_Recoil_CMSyear_MuTRKUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightMuTRK"], df["weightMuTRK_down"], "h_reg_"+reg+"_Recoil_CMSyear_MuTRKDown", [750,250,1000]))
        # pu WEIGHT SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightPU"], df["weightPU_up"],  "h_reg_"+reg+"_Recoil_CMSyear_PUDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightPU"], df["weightPU_down"],  "h_reg_"+reg+"_Recoil_CMSyear_PUUp", [750,250,1000]))
        # weightJEC SYSTEMATICS
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weight"], df["weightJEC_up"],  "h_reg_"+reg+"_Recoil_JECUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weight"], df["weightJEC_down"],  "h_reg_"+reg+"_Recoil_JECDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECAbsoluteUp'], "h_reg_"+reg+"_Recoil_JECAbsoluteUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearUp'], "h_reg_"+reg+"_Recoil_JECAbsolute_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECBBEC1Up'], "h_reg_"+reg+"_Recoil_JECBBEC1Up", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearUp'], "h_reg_"+reg+"_Recoil_JECBBEC1_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECEC2Up'], "h_reg_"+reg+"_Recoil_JECEC2Up", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECEC2_yearUp'], "h_reg_"+reg+"_Recoil_JECEC2_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECFlavorQCDUp'], "h_reg_"+reg+"_Recoil_JECFlavorQCDUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECHFUp'], "h_reg_"+reg+"_Recoil_JECHFUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECHF_yearUp'], "h_reg_"+reg+"_Recoil_JECHF_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECRelativeBalUp'], "h_reg_"+reg+"_Recoil_JECRelativeBalUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearUp'], "h_reg_"+reg+"_Recoil_JECRelativeSample_yearUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECAbsoluteDown'], "h_reg_"+reg+"_Recoil_JECAbsoluteDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECAbsolute_yearDown'], "h_reg_"+reg+"_Recoil_JECAbsolute_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECBBEC1Down'], "h_reg_"+reg+"_Recoil_JECBBEC1Down", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECBBEC1_yearDown'], "h_reg_"+reg+"_Recoil_JECBBEC1_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECEC2Down'], "h_reg_"+reg+"_Recoil_JECEC2Down", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECEC2_yearDown'], "h_reg_"+reg+"_Recoil_JECEC2_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECFlavorQCDDown'], "h_reg_"+reg+"_Recoil_JECFlavorQCDDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECHFDown'], "h_reg_"+reg+"_Recoil_JECHFDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECHF_yearDown'], "h_reg_"+reg+"_Recoil_JECHF_yearDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECRelativeBalDown'], "h_reg_"+reg+"_Recoil_JECRelativeBalDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df['weightJECRelativeSample_yearDown'], "h_reg_"+reg+"_Recoil_JECRelativeSample_yearDown", [750,250,1000]))
        # JER SYSTEMATICS
        h_list.append(VarToHist(df["Recoil_Res_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil_ResUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil_Res_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil_ResDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil_En_up"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil_EnUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil_En_down"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_Recoil_EnDown", [750,250,1000]))
        # pdf and scale systematics
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df["weightscale_up"], "h_reg_"+reg+"_Recoil_CMSyear_mu_scaleUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df["weightscale_down"], "h_reg_"+reg+"_Recoil_CMSyear_mu_scaleDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df["weightpdf_up"], "h_reg_"+reg+"_Recoil_CMSyear_pdfUp", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightcentral"], df["weightpdf_down"], "h_reg_"+reg+"_Recoil_CMSyear_pdfDown", [750,250,1000]))
        # Prefire Systematics
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightPrefire"], df["weightPrefire_up"],  "h_reg_"+reg+"_Recoil_CMSyear_prefireDown", [750,250,1000]))
        h_list.append(VarToHist(df["Recoil"], df["weight"], df["weightPrefire"], df["weightPrefire_down"],  "h_reg_"+reg+"_Recoil_CMSyear_prefireUp", [750,250,1000]))

        ###########################
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
        if ('1b' in reg) and ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('WmunuCR_2b' in reg or 'WenuCR_2b' in reg):
            h_list.append(VarToHist(df["isjet1EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet2"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('2b' in reg):
            h_list.append(VarToHist(df["isjet2EtaMatch"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(VarToHist(df["M_Jet1Jet3"], df["weight"], df["weight"], df["weight"], "h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
    #outfilename = 'Output_'+inFile.split('/')[-1]
    fout = TFile(outfilename, mode)
    for ih in h_list:
        ih.Write()


def emptyHistWritter(treeName, outfilename, mode="UPDATE"):
    h_list = []
    if 'preselR' in treeName:
        reg = treeName.split('_')[1]
    else:
        reg = treeName.split('_')[1] + '_' + treeName.split('_')[2]
    if ('SR' in reg) or ('preselR' in reg) or ('QCDCR' in reg):
        h_list.append(SetHist("h_reg_"+reg+"_MET",[750,250,1000]))

        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_eff_bUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_eff_bDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_fake_bUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_fake_bDown", [750,250,1000]))
        # EWK SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_EWKUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_EWKDown", [750,250,1000]))
        # Top pT REWEIGHTING
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_TopUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_TopDown", [750,250,1000]))
        # MET Trigger SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_METtrigUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_METtrigDown", [750,250,1000]))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EletrigUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EletrigDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EleIDUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EleIDDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EleRECOUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_EleRECODown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuIDUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuIDDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuISOUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuISODown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuTRKUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_MuTRKDown", [750,250,1000]))
        # pu WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_PUUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_PUDown", [750,250,1000]))
        # weightJEC SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_JECUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_JECDown", [750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECAbsoluteUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECAbsolute_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECBBEC1Up',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECBBEC1_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECEC2Up',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECEC2_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECFlavorQCDUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECHFUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECHF_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECRelativeBalUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECRelativeSample_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECAbsoluteDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECAbsolute_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECBBEC1Down',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECBBEC1_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECEC2Down',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECEC2_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECFlavorQCDDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECHFDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECHF_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECRelativeBalDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_MET_JECRelativeSample_yearDown',[750,250,1000]))
        # JER SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_MET_ResUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_ResDown",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_EnUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_EnDown",[750,250,1000]))

        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_mu_scaleUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_mu_scaleDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_pdfUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_pdfDown", [750,250,1000]))

        # Prefire Systematics
        h_list.append(SetHist("h_reg_" + reg +"_MET_CMSyear_prefireDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_MET_CMSyear_prefireUp", [750,250,1000]))

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
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
        elif ('preselR' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
    else:
        h_list.append(SetHist("h_reg_"+reg+"_MET",   [30, 0, 1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil",[750,250,1000]))
        # btag SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_eff_bUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_eff_bDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_fake_bUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_fake_bDown", [750,250,1000]))
        # EWK SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_EWKUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_EWKDown", [750,250,1000]))
        # Top pT REWEIGHTING
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_TopUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_TopDown", [750,250,1000]))
        # MET Trigger SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_METtrigUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_METtrigDown", [750,250,1000]))
        # LEPTON WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EletrigUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EletrigDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EleIDUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EleIDDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EleRECOUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_EleRECODown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuIDUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuIDDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuISOUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuISODown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuTRKUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_MuTRKDown", [750,250,1000]))

        # pu WEIGHT SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_PUUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_PUDown", [750,250,1000]))
        # weightJEC SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_JECUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_JECDown", [750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECAbsoluteUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECAbsolute_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECBBEC1Up',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECBBEC1_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECEC2Up',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECEC2_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECFlavorQCDUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECHFUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECHF_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECRelativeBalUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECRelativeSample_yearUp',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECAbsoluteDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECAbsolute_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECBBEC1Down',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECBBEC1_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECEC2Down',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECEC2_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECFlavorQCDDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECHFDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECHF_yearDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECRelativeBalDown',[750,250,1000]))
        h_list.append(SetHist('h_reg_'+reg+'_Recoil_JECRelativeSample_yearDown',[750,250,1000]))
        # JER SYSTEMATICS
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_ResUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_ResDown",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_EnUp",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_EnDown",[750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_mu_scaleUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_" + reg +"_Recoil_CMSyear_mu_scaleDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_pdfUp", [750,250,1000]))
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_pdfDown", [750,250,1000]))
        # Prefire Systematics
        h_list.append(SetHist("h_reg_"+reg+"_Recoil_CMSyear_prefireDown", [750,250,1000]))
        h_list.append(SetHist("h_reg_" + reg +"_Recoil_CMSyear_prefireUp", [750,250,1000]))

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
        if ('1b' in reg) and ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('WmunuCR_2b' in reg) or ('WenuCR_2b' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet1EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet2", [100, 0, 2000]))
        elif ('2b' in reg):
            h_list.append(SetHist("h_reg_"+reg+"_isjet2EtaMatch", [3, -1, 1]))
            h_list.append(SetHist("h_reg_"+reg+"_M_Jet1Jet3", [100, 0, 2000]))
        h_list.append(SetHist("h_reg_"+reg+"_rJet1PtMET", [50, 0, 50]))
        h_list.append(SetHist("h_reg_"+reg+"_delta_pfCalo", [15, 0, 1.5]))
    fout = TFile(outfilename, mode)
    for ih in h_list:
        ih.Write()


'''
---------------------------------------------------------------
START MAKING HISTOGRAMS
---------------------------------------------------------------
'''

trees = ['bbDM_preselR', 'bbDM_SR_1b', 'bbDM_SR_2b', 'bbDM_ZeeCR_1b', 'bbDM_ZeeCR_2b', 'bbDM_ZmumuCR_1b', 'bbDM_ZmumuCR_2b', 'bbDM_WenuCR_1b', 'bbDM_WenuCR_2b', 'bbDM_WmunuCR_1b', 'bbDM_WmunuCR_2b', 'bbDM_TopenuCR_1b', 'bbDM_TopenuCR_2b', 'bbDM_TopmunuCR_1b', 'bbDM_TopmunuCR_2b', 'bbDM_QCDCR_1b', 'bbDM_QCDCR_2b']

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
    outfilename = outputdir + '/' + 'Output_' + filename.split('/')[-1]
    for index, tree in enumerate(trees):
        #print ('tree',tree)
        tt = tf.Get(tree)
        nent = tt.GetEntries()
        if index == 0:
            mode = "RECREATE"
        if index > 0:
            mode = "UPDATE"
        if nent > 0:
            df = read_root(filename, tree)
            df['dPhiTrk_pfMET'] = DeltaPhi(df.METPhi, df.pfTRKMETPhi)
            df['dPhiCalo_pfMET'] = DeltaPhi(df.METPhi, df.pfpatCaloMETPhi)
            df['weightcentral'] = 1
            HistWrtter(df, outfilename, tree, mode)
        else:
            emptyHistWritter(tree, outfilename, mode)
    f = TFile(outfilename, "UPDATE")
    h_reg_preselR_cutFlow.Write()
    h_reg_SR_1b_cutFlow.Write()
    h_reg_SR_2b_cutFlow.Write()
    h_reg_ZeeCR_1b_cutFlow.Write()
    h_reg_ZeeCR_2b_cutFlow.Write()
    h_reg_ZmumuCR_1b_cutFlow.Write()
    h_reg_ZmumuCR_2b_cutFlow.Write()
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