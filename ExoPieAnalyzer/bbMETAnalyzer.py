#!/usr/bin/env python
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

## for parallel threads in interactive running
from multiprocessing import Process
import multiprocessing as mp

dummyArr = numpy.array([-9999.0], dtype=numpy.float64)

isCondor = True

isJetSel = True

###swith off the CR which you do not want to run
zee_cr = True
zmumu_cr = True
wenu_cr = True
wmunu_cr = True
topenu_cr = True
topmunu_cr = True

runInteractive = False
testing = True
## from commonutils
if isCondor:
    sys.path.append('ExoPieUtils/commonutils/')
else:
    sys.path.append('../../ExoPieUtils/commonutils/')
#import MathUtils as mathutil
from MathUtils import *
import BooleanUtils as boolutil

## from analysisutils
if isCondor:
    sys.path.append('ExoPieUtils/analysisutils/')
else:
    sys.path.append('../../ExoPieUtils/analysisutils/')

import analysis_utils as anautil

sys.path.append('ana_configs')
import variables as var
import outvars_bbDM as out
import getRecoil as getRecoil
from getJECUnc import getJECSourceUnc
## from analysisutils
if isCondor:
    sys.path.append('ExoPieUtils/scalefactortools/')
else:
    sys.path.append('../../ExoPieUtils/scalefactortools/')


year_file = open("Year.py", "w")

######################################################################################################
## All import are done before this
######################################################################################################

## ----- start of clock
start = time.clock()


## ----- command line argument
usage = "analyzer for bb+DM (istestging) "
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-i", "--inputfile", dest="inputfile", default="myfiles.txt")
parser.add_argument("-inDir", "--inputDir", dest="inputDir", default=".")
parser.add_argument("-isMP", "--isMultiProc", action="store_true", dest="isMultiProc")
parser.add_argument("-o", "--outputfile", dest="outputfile", default="out.root")
parser.add_argument("-D", "--outputdir", dest="outputdir", default=".")
parser.add_argument("-F", "--farmout", action="store_true", dest="farmout")
parser.add_argument("-I", "--interact", action="store_true", dest="interact")
parser.add_argument("-T", "--testing", action="store_true",  dest="testing")
parser.add_argument("-y", "--year", dest="year", default="Year")

args = parser.parse_args()

if args.farmout == None:
    isfarmout = False
else:
    isfarmout = args.farmout

if args.interact == None:
    runInteractive = False
else:
    runInteractive = args.interact

if args.testing == None:
    istest = False
else:
    istest = args.testing

if args.isMultiProc == None:
    isMultiProc = False
else:
    isMultiProc = args.isMultiProc

if args.year == '2016':
    print('code is running for 2016')
    year_file.write('era="2016"')
elif args.year == '2017':
    print('code is running for 2017')
    year_file.write('era="2017"')
elif args.year == '2018':
    print('code is running for 2018')
    year_file.write('era="2018"')
else:
    print('please provide year')
    sys.exit()
year_file.close()

if isfarmout or runInteractive:
    infile = args.inputfile
elif isMultiProc:
    infile = args.inputDir
else:
    print("No input file or input directory is provided for analyser")

if args.outputdir:
    outputdir = str(args.outputdir)

def TextToList(textfile):
    return([iline.rstrip() for iline in open(textfile)])

import ana_weight as wgt
from Year import era

def getJECWeight(ep_THINjetCorrUnc):
    JECWeight_up = 1.0
    JECWeight_down = 1.0
    for corr in ep_THINjetCorrUnc:
        JECWeight_up *= (1+corr)
        JECWeight_down *= (1-corr)
    return JECWeight_up, JECWeight_down

def weight_(common_weight, ep_pfMetCorrPt, ep_ZmumuRecoil, ep_WmunuRecoil, nEle, ep_elePt, ep_eleEta, ep_eleIsPTight, nMu, ep_muPt, ep_muEta, ep_isTightMuon):
    tot_weight = 1.0
    weightMETtrig = 1.0
    weightEle = [1.0,1.0,1.0]
    weightMu = [1.0,1.0,1.0,1.0]
    weightRecoiltrig = 1.0
    weightEleTrig = 1.0
    weightMETtrig_up = 1.0
    weightEle_up = [1.0,1.0,1.0]
    weightMu_up = [1.0,1.0,1.0,1.0]
    weightRecoiltrig_up = 1.0
    weightEleTrig_up = 1.0
    weightMETtrig_down = 1.0
    weightEle_down = [1.0,1.0,1.0]
    weightMu_down = [1.0,1.0,1.0,1.0]
    weightRecoiltrig_down = 1.0
    weightEleTrig_down = 1.0

    if (nEle == 0 and nMu == 0):
        if ep_pfMetCorrPt > 250:
            weightMETtrig, weightMETtrig_up, weightMETtrig_down = wgt.getMETtrig_First(
                ep_pfMetCorrPt, 'R')
        tot_weight = weightMETtrig*common_weight

    if (nEle > 0 and nMu == 0):
        weightEleTrig = wgt.eletrig_weight(ep_elePt[0], ep_eleEta[0])[0]
        if (nEle == 1):
            weightEle, weightEle_up, weightEle_down = wgt.ele_weight(
                ep_elePt[0], ep_eleEta[0], 'T')
            weightEleTrig, weightEleTrig_up, weightEleTrig_down = wgt.eletrig_weight(
                ep_elePt[0], ep_eleEta[0])
            tot_weight = weightEle[0]*common_weight*weightEleTrig
        if (nEle == 2):
            weightEle[0] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[0][0] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[0][0]
            weightEle_up[0] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[1][0] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[1][0]
            weightEle_down[0] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[2][0] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[2][0]

            weightEle[1] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[0][1] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[0][1]
            weightEle_up[1] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[1][1] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[1][1]
            weightEle_down[1] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[2][1] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[2][1]

            weightEle[2] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[0][2] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[0][2]
            weightEle_up[2] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[1][2] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[1][2]
            weightEle_down[2] = wgt.ele_weight(ep_elePt[0], ep_eleEta[0], 'T')[2][2] * wgt.ele_weight(ep_elePt[1], ep_eleEta[1], 'L')[2][2]

            weightEleTrig = wgt.eletrig_weight(ep_elePt[0], ep_eleEta[0])[0]
            weightEleTrig_up = wgt.eletrig_weight(ep_elePt[0], ep_eleEta[0])[1]
            weightEleTrig_down = wgt.eletrig_weight(ep_elePt[0], ep_eleEta[0])[2]

            tot_weight = weightEle[0]*common_weight*weightEleTrig

    if (nEle == 0 and nMu == 1):
        weightMu, weightMu_up, weightMu_down = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')
        if ep_WmunuRecoil > 250:
            weightRecoiltrig, weightRecoiltrig_up, weightRecoiltrig_down = wgt.getMETtrig_First(ep_WmunuRecoil, 'R')
        tot_weight = weightMu[0]*common_weight*weightRecoiltrig
    if (nEle == 0 and nMu == 2):
        weightMu[0] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[0][0]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[0][0]
        weightMu_up[0] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[1][0]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[1][0]
        weightMu_down[0] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[2][0]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[2][0]

        weightMu[1] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[0][1]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[0][1]
        weightMu_up[1] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[1][1]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[1][1]
        weightMu_down[1] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[2][1]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[2][1]

        weightMu[2] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[0][2]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[0][2]
        weightMu_up[2] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[1][2]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[1][2]
        weightMu_down[2] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[2][2]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[2][2]

        weightMu[3] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[0][3]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[0][3]
        weightMu_up[3] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[1][3]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[1][3]
        weightMu_down[3] = wgt.mu_weight(ep_muPt[0], ep_muEta[0], 'T')[2][3]*wgt.mu_weight(ep_muPt[1], ep_muEta[1], 'L')[2][3]

        if ep_ZmumuRecoil > 250:
            weightRecoiltrig, weightRecoiltrig_up, weightRecoiltrig_down = wgt.getMETtrig_First(ep_ZmumuRecoil, 'R')
        tot_weight = weightMu[0]*common_weight*weightRecoiltrig

    ele_wgt = [weightEle[0]*weightEleTrig, weightEle_up[0]*weightEleTrig_up, weightEle_down[0]*weightEleTrig_down]
    ele_trig = weightEleTrig, weightEleTrig_up, weightEleTrig_down
    ele_id =  [weightEle[1], weightEle_up[1], weightEle_down[1]]
    ele_reco =  [weightEle[2], weightEle_up[2], weightEle_down[2]]
    mu_wgt = [weightMu[0], weightMu_up[0], weightMu_down[0]]
    muID_wgt = [weightMu[1], weightMu_up[1], weightMu_down[1]]
    muISO_wgt = [weightMu[2], weightMu_up[2], weightMu_down[2]]
    mutrk_wgt = [weightMu[3], weightMu_up[3], weightMu_down[3]]
    met_wgt = [weightMETtrig, weightMETtrig_up, weightMETtrig_down]
    recoil_wgt = [weightRecoiltrig, weightRecoiltrig_up, weightRecoiltrig_down]
    return tot_weight, weightEleTrig, ele_wgt, mu_wgt, recoil_wgt, met_wgt, ele_trig,ele_id,ele_reco,mutrk_wgt,muID_wgt,muISO_wgt

dummy = -9999.0

def runbbdm(txtfile):

    print('txtfile', txtfile)
    infile_ = []
    outfilename = ""
    prefix = "Skimmed_"
    ikey_ = ""

    if runInteractive:
        print("running for ", txtfile)
        infile_ = [txtfile]
        outfilename = 'Analysis_'+txtfile
        print('outfilename',  outfilename)

    if isfarmout:
        infile_ = TextToList(txtfile)
        prefix_ = ''
        if outputdir != '.':
            prefix_ = outputdir+'/'
        print("prefix_", prefix_)
        outfilename = prefix_+'Analysis_'+txtfile.split('/')[-1].replace('.txt', '.root')
        print('outfilename',  outfilename)

    if isMultiProc:
        print("running for ", txtfile)
        infile_ = [txtfile]
        outfilename = 'Analysis_'+txtfile
        print('outfilename',  outfilename)


    ## define global dataframes
    df_out_preselR = out.df_out_preselR

    df_out_SR_1b = out.df_out_SR_1b
    df_out_SR_2b = out.df_out_SR_2b

    df_out_ZeeCR_1b = out.df_out_ZeeCR_1b
    df_out_ZeeCR_2b = out.df_out_ZeeCR_2b
    df_out_ZmumuCR_1b = out.df_out_ZmumuCR_1b
    df_out_ZmumuCR_2b = out.df_out_ZmumuCR_2b

    df_out_ZeeCR_2j = out.df_out_ZeeCR_2j
    df_out_ZeeCR_3j = out.df_out_ZeeCR_3j
    df_out_ZmumuCR_2j = out.df_out_ZmumuCR_2j
    df_out_ZmumuCR_3j = out.df_out_ZmumuCR_3j

    df_out_WenuCR_1b = out.df_out_WenuCR_1b
    df_out_WenuCR_2b = out.df_out_WenuCR_2b
    df_out_WmunuCR_1b = out.df_out_WmunuCR_1b
    df_out_WmunuCR_2b = out.df_out_WmunuCR_2b

    df_out_TopenuCR_1b = out.df_out_TopenuCR_1b
    df_out_TopenuCR_2b = out.df_out_TopenuCR_2b
    df_out_TopmunuCR_1b = out.df_out_TopmunuCR_1b
    df_out_TopmunuCR_2b = out.df_out_TopmunuCR_2b

    df_out_QCDbCR_1b = out.df_out_QCDbCR_1b
    df_out_QCDbCR_2b = out.df_out_QCDbCR_2b

    df_out_QCDcCR_1b = out.df_out_QCDcCR_1b
    df_out_QCDcCR_2b = out.df_out_QCDcCR_2b

    df_out_QCDaCR_1b = out.df_out_QCDaCR_1b
    df_out_QCDaCR_2b = out.df_out_QCDaCR_2b

    h_total = TH1F('h_total', 'h_total', 2, 0, 2)
    h_total_mcweight = TH1F('h_total_mcweight', 'h_total_mcweight', 2, 0, 2)
    h_eventCounter = TH1F('h_eventCounter', 'h_eventCounter', 2, 0.5, 2.5)

    h_reg_preselR_cutFlow = TH1F(
        "h_reg_preselR_cutFlow", "h_reg_preselR_cutFlow", 7, 0, 7)

    h_reg_SR_1b_cutFlow = TH1F(
        "h_reg_SR_1b_cutFlow", "h_reg_SR_1b_cutFlow", 7, 0, 7)
    h_reg_SR_2b_cutFlow = TH1F(
        "h_reg_SR_2b_cutFlow", "h_reg_SR_2b_cutFlow", 7, 0, 7)

    h_reg_ZeeCR_1b_cutFlow = TH1F(
        "h_reg_ZeeCR_1b_cutFlow", "h_reg_ZeeCR_1b_cutFlow", 11, 0, 11)
    h_reg_ZeeCR_2b_cutFlow = TH1F(
        "h_reg_ZeeCR_2b_cutFlow", "h_reg_ZeeCR_2b_cutFlow", 11, 0, 11)
    h_reg_ZmumuCR_1b_cutFlow = TH1F(
        "h_reg_ZmumuCR_1b_cutFlow", "h_reg_ZmumuCR_1b_cutFlow", 11, 0, 11)
    h_reg_ZmumuCR_2b_cutFlow = TH1F(
        "h_reg_ZmumuCR_2b_cutFlow", "h_reg_ZmumuCR_2b_cutFlow", 11, 0, 11)

    h_reg_ZeeCR_2j_cutFlow = TH1F(
        "h_reg_ZeeCR_2j_cutFlow", "h_reg_ZeeCR_2j_cutFlow", 11, 0, 11)
    h_reg_ZeeCR_3j_cutFlow = TH1F(
        "h_reg_ZeeCR_3j_cutFlow", "h_reg_ZeeCR_3j_cutFlow", 11, 0, 11)
    h_reg_ZmumuCR_2j_cutFlow = TH1F(
        "h_reg_ZmumuCR_2j_cutFlow", "h_reg_ZmumuCR_2j_cutFlow", 11, 0, 11)
    h_reg_ZmumuCR_3j_cutFlow = TH1F(
        "h_reg_ZmumuCR_3j_cutFlow", "h_reg_ZmumuCR_3j_cutFlow", 11, 0, 11)

    h_reg_WenuCR_1b_cutFlow = TH1F(
        "h_reg_WenuCR_1b_cutFlow", "h_reg_WenuCR_1b_cutFlow", 11, 0, 11)
    h_reg_WenuCR_2b_cutFlow = TH1F(
        "h_reg_WenuCR_2b_cutFlow", "h_reg_WenuCR_2b_cutFlow", 11, 0, 11)
    h_reg_WmunuCR_1b_cutFlow = TH1F(
        "h_reg_WmunuCR_1b_cutFlow", "h_reg_WmunuCR_1b_cutFlow", 11, 0, 11)
    h_reg_WmunuCR_2b_cutFlow = TH1F(
        "h_reg_WmunuCR_2b_cutFlow", "h_reg_WmunuCR_2b_cutFlow", 11, 0, 11)

    h_reg_TopenuCR_1b_cutFlow = TH1F(
        "h_reg_TopenuCR_1b_cutFlow", "h_reg_TopenuCR_1b_cutFlow", 11, 0, 11)
    h_reg_TopenuCR_2b_cutFlow = TH1F(
        "h_reg_TopenuCR_2b_cutFlow", "h_reg_TopenuCR_2b_cutFlow", 11, 0, 11)
    h_reg_TopmunuCR_1b_cutFlow = TH1F(
        "h_reg_TopmunuCR_1b_cutFlow", "h_reg_TopmunuCR_1b_cutFlow", 11, 0, 11)
    h_reg_TopmunuCR_2b_cutFlow = TH1F(
        "h_reg_TopmunuCR_2b_cutFlow", "h_reg_TopmunuCR_2b_cutFlow", 11, 0, 11)

    h_reg_QCDbCR_1b_cutFlow = TH1F(
        "h_reg_QCDbCR_1b_cutFlow", "h_reg_QCDbCR_1b_cutFlow", 7, 0, 7)
    h_reg_QCDbCR_2b_cutFlow = TH1F(
        "h_reg_QCDbCR_2b_cutFlow", "h_reg_QCDbCR_2b_cutFlow", 7, 0, 7)

    h_reg_QCDcCR_1b_cutFlow = TH1F(
        "h_reg_QCDcCR_1b_cutFlow", "h_reg_QCDcCR_1b_cutFlow", 7, 0, 7)
    h_reg_QCDcCR_2b_cutFlow = TH1F(
        "h_reg_QCDcCR_2b_cutFlow", "h_reg_QCDcCR_2b_cutFlow", 7, 0, 7)

    h_reg_QCDaCR_1b_cutFlow = TH1F(
        "h_reg_QCDaCR_1b_cutFlow", "h_reg_QCDaCR_1b_cutFlow", 7, 0, 7)
    h_reg_QCDaCR_2b_cutFlow = TH1F(
        "h_reg_QCDaCR_2b_cutFlow", "h_reg_QCDaCR_2b_cutFlow", 7, 0, 7)

    for infl in infile_:
        f_tmp = TFile.Open(infl, 'READ')
        h_tmp = f_tmp.Get('h_total')
        h_tmp_weight = f_tmp.Get('h_total_mcweight')
        h_tmp_count = f_tmp.Get('h_eventCounter')
        h_total.Add(h_tmp)
        h_total_mcweight.Add(h_tmp_weight)
        h_eventCounter.Add(h_tmp_count)

    filename = infile_
    ieve = 0
    icount = 0
    preselRcount = 0.0
    SR1bcount = 0.0
    SR2bcount = 0.0
    ZeeCR1bcount = 0.0
    ZeeCR2bcount = 0.0
    ZeeCR2jcount = 0.0
    ZeeCR3jcount = 0.0
    ZmumuCR1bcount = 0.0
    ZmumuCR2bcount = 0.0
    ZmumuCR2jcount = 0.0
    ZmumuCR3jcount = 0.0
    WenuCR1bcount = 0.0
    WenuCR2bcount = 0.0
    WmunuCR1bcount = 0.0
    WmunuCR2bcount = 0.0
    TopenuCR1bcount = 0.0
    TopenuCR2bcount = 0.0
    TopmunuCR1bcount = 0.0
    TopmunuCR2bcount = 0.0
    QCDbCR1bcount = 0.0
    QCDbCR2bcount = 0.0
    QCDaCR1bcount = 0.0
    QCDaCR2bcount = 0.0
    QCDcCR1bcount = 0.0
    QCDcCR2bcount = 0.0


    allvars_bbDM = var.allvars_bbDM
    if era == '2018':
        allvars_bbDM.append('st_isak4JetBasedHemEvent')
        allvars_bbDM.append('st_ismetphiBasedHemEvent1')
        allvars_bbDM.append('st_ismetphiBasedHemEvent2')
    for df in read_root(filename, 'outTree', columns=allvars_bbDM, chunksize=125000):
        if era == '2016' or era == '2017':
            df['st_isak4JetBasedHemEvent'] = False
            df['st_ismetphiBasedHemEvent1'] = False
            df['st_ismetphiBasedHemEvent2'] = False
        for ep_runId, ep_lumiSection, ep_eventId, \
            ep_prefiringweight, ep_prefiringweightup, ep_prefiringweightdown,\
            ep_scaleWeightUP, ep_scaleWeightDOWN, ep_pdfWeightUP, ep_pdfWeightDOWN,\
            ep_pfMetCorrPt, ep_pfMetCorrPhi, ep_pfMetUncJetResUp, ep_pfMetUncJetResDown, ep_pfMetUncJetEnUp, ep_pfMetUncJetEnDown, \
            ep_pfMetCorrSig, ep_pfpatCaloMETPt, ep_pfpatCaloMETPhi, ep_pfTRKMETPt, ep_pfTRKMETPhi, \
            ep_WenuPhi, ep_WmunuPhi, ep_ZeePhi, ep_ZmumuPhi, \
            ep_ZeeRecoil, ep_ZmumuRecoil, ep_WenuRecoil, ep_WmunuRecoil, \
            ep_Zeemass, ep_Zmumumass, ep_Wenumass, ep_Wmunumass, \
            ep_isData, \
            ep_THINnJet, ep_THINjetPx, ep_THINjetPy, ep_THINjetPz, ep_THINjetEnergy, \
            ep_THINjetDeepCSV, ep_THINjetHadronFlavor, ep_THINjetNPV, \
            ep_THINjetCorrUnc, ep_THINjetUncSources, ep_THINPUjetIDTight,\
            ep_THINjetNHadEF, ep_THINjetCHadEF, ep_THINjetCEmEF, ep_THINjetNEmEF,  \
            ep_THINjetCMulti, ep_THINjetNMultiplicity, \
            ep_nEle, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, \
            ep_eleIsPassTight, ep_eleIsPassLoose, ep_eleCharge, \
            ep_nPho, ep_phoIsPassTight, ep_phoPx, ep_phoPy, ep_phoPz, ep_phoEnergy, \
            ep_nMu, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_isTightMuon, ep_muCharge, \
            ep_nTau_DRBased_EleMuVeto, ep_nTau_discBased_looseElelooseMuVeto, ep_nTau_discBased_looseEleTightMuVeto, ep_nTau_discBased_mediumElelooseMuVeto, ep_nTau_discBased_TightEleTightMuVeto,\
            ep_pu_nTrueInt, ep_pu_nPUVert, \
            ep_THINjetNPV, \
            ep_mcweight, ep_genParPt, ep_genParSample, eletrigdecision, mutrigdecision, mettrigdecision, \
            ep_isak4JetBasedHemEvent, ep_ismetphiBasedHemEvent1, ep_ismetphiBasedHemEvent2 \
            in zip(df.st_runId, df.st_lumiSection, df.st_eventId,
                   df.st_prefiringweight, df.st_prefiringweightup, df.st_prefiringweightdown,
                   df.st_scaleWeightUP, df.st_scaleWeightDOWN, df.st_pdfWeightUP, df.st_pdfWeightDOWN,
                   df.st_pfMetCorrPt, df.st_pfMetCorrPhi, df.st_pfMetUncJetResUp, df.st_pfMetUncJetResDown,
                   df.st_pfMetUncJetEnUp, df.st_pfMetUncJetEnDown,
                   df.st_pfMetCorrSig, df.st_pfpatCaloMETPt, df.st_pfpatCaloMETPhi,
                   df.st_pfTRKMETPt, df.st_pfTRKMETPhi,
                   df.WenuPhi, df.WmunuPhi, df.ZeePhi, df.ZmumuPhi,
                   df.ZeeRecoil, df.ZmumuRecoil, df.WenuRecoil, df.WmunuRecoil,
                   df.ZeeMass, df.ZmumuMass, df.Wenumass, df.Wmunumass,
                   df.st_isData,
                   df.st_THINnJet, df.st_THINjetPx, df.st_THINjetPy, df.st_THINjetPz, df.st_THINjetEnergy,
                   df.st_THINjetDeepCSV, df.st_THINjetHadronFlavor, df.st_THINjetNPV,
                   df.st_THINjetCorrUnc, df.st_THINjetUncSources, df.st_THINPUjetIDTight,
                   df.st_THINjetNHadEF, df.st_THINjetCHadEF, df.st_THINjetCEmEF, df.st_THINjetNEmEF,
                   df.st_THINjetCMulti, df.st_THINjetNMultiplicity,
                   df.st_nEle, df.st_elePx, df.st_elePy, df.st_elePz, df.st_eleEnergy,
                   df.st_eleIsPassTight, df.st_eleIsPassLoose, df.st_eleCharge,
                   df.st_nPho, df.st_phoIsPassTight, df.st_phoPx, df.st_phoPy, df.st_phoPz, df.st_phoEnergy,
                   df.st_nMu, df.st_muPx, df.st_muPy, df.st_muPz, df.st_muEnergy, df.st_isTightMuon, df.st_muCharge,
                   df.st_nTau_DRBased_EleMuVeto, df.st_nTau_discBased_looseElelooseMuVeto, df.st_nTau_discBased_looseEleTightMuVeto, df.st_nTau_discBased_mediumElelooseMuVeto, df.st_nTau_discBased_TightEleTightMuVeto,
                   df.st_pu_nTrueInt, df.st_pu_nPUVert,
                   df.st_THINjetNPV,
                   df.mcweight, df.st_genParPt, df.st_genParSample, df.st_eletrigdecision, df.st_mutrigdecision, df.st_mettrigdecision, df.st_isak4JetBasedHemEvent, df.st_ismetphiBasedHemEvent1, df.st_ismetphiBasedHemEvent2):
            ieve = ieve + 1
            if ieve % 10000 == 0:
                print("Processed", ieve, "Events")

            if ep_isak4JetBasedHemEvent:
                ep_isak4JetBasedHemEvent = 1
            else:
                ep_isak4JetBasedHemEvent = 0

            if ep_ismetphiBasedHemEvent1:
                ep_ismetphiBasedHemEvent1 = 1
            else:
                ep_ismetphiBasedHemEvent1 = 0

            if ep_ismetphiBasedHemEvent2:
                ep_ismetphiBasedHemEvent1 = 1
            else:
                ep_ismetphiBasedHemEvent1 = 0

            ispreselR = False

            isSR1b = False
            isQCDbCR1b = False
            isQCDaCR1b = False
            isQCDcCR1b = False
            is1bCRWenu = False
            is1bCRWmunu = False
            is1bCRZee = False
            is1bCRZmumu = False
            is2jCRZee = False
            is2jCRZmumu = False
            is1bCRTopenu = False
            is1bCRTopmunu = False

            isSR2b = False
            isQCDbCR2b = False
            isQCDaCR2b = False
            isQCDcCR2b = False
            is2bCRWenu = False
            is2bCRWmunu = False
            is2bCRZee = False
            is2bCRZmumu = False
            is3jCRZee = False
            is3jCRZmumu = False
            is2bCRTopenu = False
            is2bCRTopmunu = False

            #deepCSV_Med = 0.8484  # for old DMsimp sample, this deepcsv means CSVv2
            if era == '2016':
                deepCSV_Med = 0.6321
            elif era == '2017':
                deepCSV_Med = 0.4941
            elif era == '2018':
                deepCSV_Med = 0.4184

            '''
            -------------------------------------------------------------------------------
            electron VARS
            -------------------------------------------------------------------------------
            '''
            ep_nEle_ = [ij for ij in range(ep_nEle) if (ep_eleIsPassLoose[ij])]
            ep_nEle_index = len(ep_nEle_)
            ep_elePt = [getPt(ep_elePx[ij], ep_elePy[ij]) for ij in ep_nEle_]
            ep_eleEta = [getEta(ep_elePx[ij], ep_elePy[ij], ep_elePz[ij]) for ij in ep_nEle_]
            ep_elePhi = [getPhi(ep_elePx[ij], ep_elePy[ij]) for ij in ep_nEle_]
            ep_eleIsPTight = [ep_eleIsPassTight[ij] for ij in ep_nEle_]
            if era == "2016":
                minElePt = 30.0
            else:
                minElePt = 35.0

            '''
            -------------------------------------------------------------------------------
            muon VARS
            -------------------------------------------------------------------------------
            '''
            ep_muPt = [getPt(ep_muPx[ij], ep_muPy[ij]) for ij in range(ep_nMu)]
            ep_muEta = [getEta(ep_muPx[ij], ep_muPy[ij], ep_muPz[ij]) for ij in range(ep_nMu)]
            ep_muPhi = [getPhi(ep_muPx[ij], ep_muPy[ij]) for ij in range(ep_nMu)]
            minMuPt = 30.0
            '''

            -------------------------------------------------------------------------------
            photon VARS
            -------------------------------------------------------------------------------
            '''
            ep_phoPt = [getPt(ep_phoPx[ij], ep_phoPy[ij]) for ij in range(ep_nPho)]
            ep_phoEta = [getEta(ep_phoPx[ij], ep_phoPy[ij], ep_phoPz[ij]) for ij in range(ep_nPho)]
            ep_phoPhi = [getPhi(ep_phoPx[ij], ep_phoPy[ij]) for ij in range(ep_nPho)]
            # nPho = ep_nPho

            '''
            -------------------------------------------------------------------------------
            THIN JET VARS
            -------------------------------------------------------------------------------
            '''
            ep_THINjetEta_ = [getEta(ep_THINjetPx[ij], ep_THINjetPy[ij], ep_THINjetPz[ij]) for ij in range(ep_THINnJet)]

            JetwithEta4p5 = ep_THINnJet
            ep_THINjetEta = [ep_THINjetEta_[i] for i in range(len(ep_THINjetEta_)) if abs(ep_THINjetEta_[i]) < 2.5]
            ep_THINjetEta_index = [i for i in range(len(ep_THINjetEta_)) if abs(ep_THINjetEta_[i]) < 2.5]
            ep_THINjetPt = [getPt(ep_THINjetPx[ij], ep_THINjetPy[ij]) for ij in ep_THINjetEta_index]
            ep_THINjetPhi = [getPhi(ep_THINjetPx[ij], ep_THINjetPy[ij]) for ij in ep_THINjetEta_index]
            ep_THINjetHadronFlavor = [ep_THINjetHadronFlavor[ij] for ij in ep_THINjetEta_index]
            ep_THINjetDeepCSV = [ep_THINjetDeepCSV[ij] for ij in ep_THINjetEta_index]
            if era == '2016':
                ep_THINbjets_Cond = [bool(ep_THINjetDeepCSV[ij] > deepCSV_Med and abs(ep_THINjetEta[ij]) < 2.4) for ij in range(len(ep_THINjetEta_index))]
            else:
                ep_THINbjets_Cond = [bool(ep_THINjetDeepCSV[ij] > deepCSV_Med and abs(ep_THINjetEta[ij]) < 2.5) for ij in range(len(ep_THINjetEta_index))]
            ep_THINnJet = len(ep_THINjetPt)
            nBjets = len([ij for ij in ep_THINbjets_Cond if ij])

            if len(ep_THINjetPt) == 0:
                continue
            JetHT = sum(ep_THINjetPt)
            min_dPhi_jet_MET = min(
                [DeltaPhi(jet_phi, ep_pfMetCorrPhi) for jet_phi in ep_THINjetPhi])

            pho_pt15_eta2p5 = boolutil.logical_and2((ep_phoPt > 15.0), (numpy.abs(ep_phoEta) < 2.5))
            jet_pt30_eta2p5 = boolutil.logical_and2((ep_THINjetPt > 30.0), (numpy.abs(ep_THINjetEta) < 2.5))
            pass_pho_index_cleaned=[]
            if ep_nPho > 0:
                cleanedPhoton = anautil.jetcleaning(pho_pt15_eta2p5, jet_pt30_eta2p5, ep_phoEta, ep_THINjetEta, ep_phoPhi, ep_THINjetPhi, 0.4)
                pass_pho_index_cleaned = boolutil.WhereIsTrue(cleanedPhoton)
            nPho = len(pass_pho_index_cleaned)

            Jet2Pt = dummy
            Jet2Eta = dummy
            Jet2Phi = dummy
            Jet2deepCSV = dummy
            Jet3Pt = dummy
            Jet3Eta = dummy
            Jet3Phi = dummy
            Jet3deepCSV = dummy
            isjet1EtaMatch = 0.0
            isjet2EtaMatch = 0.0
            M_Jet1Jet2 = dummy
            pT_Jet1Jet2 = dummy
            eta_Jet1Jet2 = dummy
            phi_Jet1Jet2 = dummy
            dRJet12 = dummy
            M_Jet1Jet3 = dummy
            ratioPtJet21 = dummy
            dPhiJet12 = dummy
            dEtaJet12 = dummy
            dPhiJet13 = dummy
            rJet1PtMET = dummy
            Jet2NHadEF = dummy
            Jet2CHadEF = dummy
            Jet2CEmEF = dummy
            Jet2NEmEF = dummy
            Jet2CMulti = dummy
            Jet2NMultiplicity = dummy
            dPhi_lep1_MET = dummy
            dPhi_lep2_MET = dummy
            prod_cat = dummy

            '''
            -------------------------------------------------------------------------------
            HADRONIC RECOIL
            -------------------------------------------------------------------------------
            '''
            #======   usage: ZRecoil_Phi_Zmass(nEle, eleCharge_, elepx_, elepy_, elepz_, elee_,met_,metphi_)=====
            ep_ZeeRecoil, ep_ZeeRecoil_dPhi, ep_Zeemass = getRecoil.ZRecoil_Phi_Zmass(
                ep_nEle_index, ep_eleCharge, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, ep_pfMetCorrPt, ep_pfMetCorrPhi)
            ep_ZeeRecoilResUp, ep_ZeeRecoil_dPhiResUp, ep_ZeemassResUp = getRecoil.ZRecoil_Phi_Zmass(
                ep_nEle_index, ep_eleCharge, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, ep_pfMetUncJetResUp, ep_pfMetCorrPhi)
            ep_ZeeRecoilResDown, ep_ZeeRecoil_dPhiResDown, ep_ZeemassResDown = getRecoil.ZRecoil_Phi_Zmass(
                ep_nEle_index, ep_eleCharge, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, ep_pfMetUncJetResDown, ep_pfMetCorrPhi)
            ep_ZeeRecoilEnUp, ep_ZeeRecoil_dPhiEnUp, ep_ZeemassEnUp = getRecoil.ZRecoil_Phi_Zmass(
                ep_nEle_index, ep_eleCharge, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, ep_pfMetUncJetEnUp, ep_pfMetCorrPhi)
            ep_ZeeRecoilEnDown, ep_ZeeRecoil_dPhiEnDown, ep_ZeemassEnDown = getRecoil.ZRecoil_Phi_Zmass(
                ep_nEle_index, ep_eleCharge, ep_elePx, ep_elePy, ep_elePz, ep_eleEnergy, ep_pfMetUncJetEnDown, ep_pfMetCorrPhi)

            ep_ZmumuRecoil, ep_ZmumuRecoil_dPhi, ep_Zmumumass = getRecoil.ZRecoil_Phi_Zmass(
                ep_nMu, ep_muCharge, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_pfMetCorrPt, ep_pfMetCorrPhi)
            ep_ZmumuRecoilResUp, ep_ZmumuRecoil_dPhiResUp, ep_ZmumumassResUp = getRecoil.ZRecoil_Phi_Zmass(
                ep_nMu, ep_muCharge, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_pfMetUncJetResUp, ep_pfMetCorrPhi)
            ep_ZmumuRecoilResDown, ep_ZmumuRecoil_dPhiResDown, ep_ZmumumassResDown = getRecoil.ZRecoil_Phi_Zmass(
                ep_nMu, ep_muCharge, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_pfMetUncJetResDown, ep_pfMetCorrPhi)
            ep_ZmumuRecoilEnUp, ep_ZmumuRecoil_dPhiEnUp, ep_ZmumumassEnUp = getRecoil.ZRecoil_Phi_Zmass(
                ep_nMu, ep_muCharge, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_pfMetUncJetEnUp, ep_pfMetCorrPhi)
            ep_ZmumuRecoilEnDown, ep_ZmumuRecoil_dPhiEnDown, ep_ZmumumassEnDown = getRecoil.ZRecoil_Phi_Zmass(
                ep_nMu, ep_muCharge, ep_muPx, ep_muPy, ep_muPz, ep_muEnergy, ep_pfMetUncJetEnDown, ep_pfMetCorrPhi)

            ep_WenuRecoil, ep_WenuRecoil_dPhi, ep_Wenumass = getRecoil.WRecoil_Phi_Wmass(
                ep_nEle_index, ep_elePt, ep_elePhi, ep_elePx, ep_elePy, ep_pfMetCorrPt, ep_pfMetCorrPhi)
            ep_WenuRecoilResUp, ep_WenuRecoil_dPhiResUp, ep_WenumassResUp = getRecoil.WRecoil_Phi_Wmass(
                ep_nEle_index, ep_elePt, ep_elePhi, ep_elePx, ep_elePy, ep_pfMetUncJetResUp, ep_pfMetCorrPhi)
            ep_WenuRecoilResDown, ep_WenuRecoil_dPhiResDown, ep_WenumassResDown = getRecoil.WRecoil_Phi_Wmass(
                ep_nEle_index, ep_elePt, ep_elePhi, ep_elePx, ep_elePy, ep_pfMetUncJetResDown, ep_pfMetCorrPhi)
            ep_WenuRecoilEnUp, ep_WenuRecoil_dPhiEnUp, ep_WenumassEnUp = getRecoil.WRecoil_Phi_Wmass(
                ep_nEle_index, ep_elePt, ep_elePhi, ep_elePx, ep_elePy, ep_pfMetUncJetEnUp, ep_pfMetCorrPhi)
            ep_WenuRecoilEnDown, ep_WenuRecoil_dPhiEnDown, ep_WenumassEnDown = getRecoil.WRecoil_Phi_Wmass(
                ep_nEle_index, ep_elePt, ep_elePhi, ep_elePx, ep_elePy, ep_pfMetUncJetEnDown, ep_pfMetCorrPhi)

            ep_WmunuRecoil, ep_WmunuRecoil_dPhi, ep_Wmunumass = getRecoil.WRecoil_Phi_Wmass(
                ep_nMu, ep_muPt, ep_muPhi, ep_muPx, ep_muPy, ep_pfMetCorrPt, ep_pfMetCorrPhi)
            ep_WmunuRecoilResUp, ep_WmunuRecoil_dPhiResUp, ep_WmunumassResUp = getRecoil.WRecoil_Phi_Wmass(
                ep_nMu, ep_muPt, ep_muPhi, ep_muPx, ep_muPy, ep_pfMetUncJetResUp, ep_pfMetCorrPhi)
            ep_WmunuRecoilResDown, ep_WmunuRecoil_dPhiResDown, ep_WmunumassResDown = getRecoil.WRecoil_Phi_Wmass(
                ep_nMu, ep_muPt, ep_muPhi, ep_muPx, ep_muPy, ep_pfMetUncJetResDown, ep_pfMetCorrPhi)
            ep_WmunuRecoilEnUp, ep_WmunuRecoil_dPhiEnUp, ep_WmunumassEnUp = getRecoil.WRecoil_Phi_Wmass(
                ep_nMu, ep_muPt, ep_muPhi, ep_muPx, ep_muPy, ep_pfMetUncJetEnUp, ep_pfMetCorrPhi)
            ep_WmunuRecoilEnDown, ep_WmunuRecoil_dPhiEnDown, ep_WmunumassEnDown = getRecoil.WRecoil_Phi_Wmass(
                ep_nMu, ep_muPt, ep_muPhi, ep_muPx, ep_muPy, ep_pfMetUncJetEnDown, ep_pfMetCorrPhi)

            if (ep_pfMetCorrPt < 250.0) and (ep_ZeeRecoil < 250.0) and (ep_ZmumuRecoil < 250.0) and (ep_WenuRecoil < 250.0) and (ep_WmunuRecoil < 250.0):
                continue

            '''
            -------------------------------------------------------------------------------
            ADDITIONAL MET VARS
            -------------------------------------------------------------------------------
            '''
            delta_pfCaloSR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_pfMetCorrPt
            delta_pfCaloZeeCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_ZeeRecoil
            delta_pfCaloZmumuCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_ZmumuRecoil
            delta_pfCaloWenuCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_WenuRecoil
            delta_pfCaloWmunuCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_WmunuRecoil
            delta_pfCaloTopenuCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_WenuRecoil
            delta_pfCaloTopmunuCR = abs(
                ep_pfpatCaloMETPt-ep_pfMetCorrPt)/ep_WmunuRecoil

            '''
            -------------------------------------------------------------------------------
            CR VARS
            -------------------------------------------------------------------------------
            '''
            if ep_nEle_index == 2:
                ZpT_ee = math.sqrt((ep_elePx[0]+ep_elePx[1])*(ep_elePx[0]+ep_elePx[1]) + (
                    ep_elePy[0]+ep_elePy[1])*(ep_elePy[0]+ep_elePy[1]))
            if ep_nMu == 2:
                ZpT_mumu = math.sqrt((ep_muPx[0]+ep_muPx[1])*(ep_muPx[0]+ep_muPx[1]) + (
                    ep_muPy[0]+ep_muPy[1])*(ep_muPy[0]+ep_muPy[1]))

            if ep_nEle_index == 1:
                WpT_enu = math.sqrt((ep_pfMetCorrPt*math.cos(ep_pfMetCorrPhi) + ep_elePx[0])**2 + (
                    ep_pfMetCorrPt*math.sin(ep_pfMetCorrPhi) + ep_elePy[0])**2)
            if ep_nMu == 1:
                WpT_munu = math.sqrt((ep_pfMetCorrPt*math.cos(ep_pfMetCorrPhi) + ep_muPx[0])**2 + (
                    ep_pfMetCorrPt*math.sin(ep_pfMetCorrPhi) + ep_muPy[0])**2)

            '''
            --------------------------------------------------------------------------------
            COMMON WEIGHT CALCULATION FOR ALL REGIONS
            --------------------------------------------------------------------------------
            '''
            weight = presel_weight = weightPU = weightB = weightFakeB = weightEWK = weightQCD = weightTop = weightEleTrig = weightEle = weightMu = weightMETtrig = weightRecoiltrig = weightPrefire = -999.0
            weightB_up = weightEWK_up = weightQCD_up = weightTop_up = weightJEC_up = weightEleTrig_up = weightEle_up = weightMu_up = weightMETtrig_up = weightRecoiltrig_up = weightPU_up = weightJEC_up = weightPrefire_up = weightscale_up = weightpdf_up = 1.0
            weightB_down = weightEWK_down = weightQCD_down = weightTop_down = weightJEC_down = weightEleTrig_down = weightEle_down = weightMu_down = weightMETtrig_down = weightRecoiltrig_down = weightPU_down = weightJEC_down = weightPrefire_down = weightscale_down = weightpdf_down = 1.0
            if ep_isData:
                weight = presel_weight = weightPU = weightB = weightFakeB = weightEWK = weightQCD = weightTop = weightEleTrig = weightEle = weightMu = weightMETtrig = weightRecoiltrig = weightPrefire = weightEleTrig= weightEleID= weightEleRECO= weightMuTRK= weightMuID = weightMuISO = 1.0
                weightB_up = weightFakeB_up = weightEWK_up = weightQCD_up = weightTop_up = weightJEC_up = weightEleTrig_up = weightEle_up = weightMu_up = weightMETtrig_up = weightRecoiltrig_up = weightPU_up = weightJEC_up = weightPrefire_up = weightscale_up = weightpdf_up = weightEleTrig_up= weightEleID_up= weightEleRECO_up= weightMuTRK_up= weightMuID_up = weightMuISO_up = 1.0
                weightB_down = weightFakeB_down = weightEWK_down = weightQCD_down = weightTop_down = weightJEC_down = weightEleTrig_down = weightEle_down = weightMu_down = weightMETtrig_down = weightRecoiltrig_down = weightPU_down = weightJEC_down = weightPrefire_down = weightscale_down = weightpdf_down = weightEleTrig_down= weightEleID_down= weightEleRECO_down= weightMuTRK_down= weightMuID_down = weightMuISO_down =1.0
            else:
                [weightB, weightFakeB], [weightB_up, weightFakeB_up], [weightB_down, weightFakeB_down] = wgt.getBTagSF(ep_THINnJet, ep_THINjetPt, ep_THINjetEta, ep_THINjetHadronFlavor, ep_THINjetDeepCSV, 'MWP')
                weightPU, weightPU_up, weightPU_down  = wgt.puweight(ep_pu_nTrueInt)
                weightscale_up  = ep_scaleWeightUP
                weightpdf_up = ep_pdfWeightUP
                weightscale_down = ep_scaleWeightDOWN
                weightpdf_down = ep_pdfWeightDOWN
                weightEWK = 1.0
                weightQCD = 1.0
                weightTop = 1.0
                if ep_genParSample == 23 and len(ep_genParPt) > 0:
                    weightEWK = wgt.getEWKZ(ep_genParPt[0])
                    weightEWK_up = wgt.getEWKZ(ep_genParPt[0])*1.5
                    weightEWK_down = wgt.getEWKZ(ep_genParPt[0])*0.5
                    weightQCD = wgt.getQCDZ(ep_genParPt[0])
                    weightQCD_up = wgt.getQCDZ(ep_genParPt[0])
                    weightQCD_down = wgt.getQCDZ(ep_genParPt[0])
                if ep_genParSample == 24 and len(ep_genParPt) > 0:
                    weightEWK = wgt.getEWKW(ep_genParPt[0])
                    weightEWK_up = wgt.getEWKW(ep_genParPt[0])*1.5
                    weightEWK_down = wgt.getEWKW(ep_genParPt[0])*0.5
                    weightQCD = wgt.getQCDW(ep_genParPt[0])
                    weightQCD_up = wgt.getQCDW(ep_genParPt[0])
                    weightQCD_down = wgt.getQCDW(ep_genParPt[0])
                if ep_genParSample == 6 and len(ep_genParPt) > 0:
                    weightTop, weightTop_up, weightTop_down = wgt.getTopPtReWgt(
                        ep_genParPt[0], ep_genParPt[1])
                weightPrefire = ep_prefiringweight
                weightPrefire_up = ep_prefiringweightup
                weightPrefire_down = ep_prefiringweightdown
                common_weight = ep_mcweight * weightB * weightFakeB * weightEWK * weightQCD * weightTop * weightPU * weightPrefire
                presel_weight = ep_mcweight * weightEWK * weightQCD * weightTop * weightPU * weightPrefire
                weight, weightEleTrig, ele_wgt, mu_wgt, recoil_wgt, met_wgt, ele_trig,ele_id,ele_reco,mutrk_wgt, muID_wgt, muISO_wgt = weight_(
                    common_weight, ep_pfMetCorrPt, ep_ZmumuRecoil, ep_WmunuRecoil, ep_nEle_index, ep_elePt, ep_eleEta, ep_eleIsPTight, ep_nMu, ep_muPt, ep_muEta, ep_isTightMuon)
                weightEle,weightEle_up, weightEle_down= ele_wgt
                weightMu,weightMu_up,weightMu_down = mu_wgt
                weightRecoiltrig, weightRecoiltrig_up, weightRecoiltrig_down = recoil_wgt
                weightMETtrig, weightMETtrig_up, weightMETtrig_down = met_wgt
                weightJEC_up, weightJEC_down = getJECWeight(ep_THINjetCorrUnc)
                weightEleTrig, weightEleTrig_up, weightEleTrig_down = ele_trig
                weightEleID, weightEleID_up,weightEleID_down  = ele_id
                weightEleRECO, weightEleRECO_up, weightEleRECO_down = ele_reco
                weightMuTRK, weightMuTRK_up, weightMuTRK_down = mutrk_wgt
                weightMuID, weightMuID_up, weightMuID_down = muID_wgt
                weightMuISO, weightMuISO_up, weightMuISO_down = muISO_wgt
            JECSourceUp, JECSourceDown = getJECSourceUnc(ep_THINnJet, ep_THINjetUncSources, index=False)

            '''
            --------------------------------------------------------------------------------
            Preselection REGION
            --------------------------------------------------------------------------------
            '''
            h_reg_preselR_cutFlow.AddBinContent(1, presel_weight)
            if mettrigdecision:
                h_reg_preselR_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                if (ep_pfMetCorrPt > 250. and delta_pfCaloSR < 0.5):
                    h_reg_preselR_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    if True:
                        h_reg_preselR_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        if (min_dPhi_jet_MET > 0.5):
                            h_reg_preselR_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            if (ep_THINjetPt[0] > 100.):
                                h_reg_preselR_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (ep_THINbjets_Cond[0]):
                                    h_reg_preselR_cutFlow.AddBinContent(
                                        7, weight)
                                    ispreselR = True
                                    preselRcount += 1
                                    if ep_THINnJet >= 2:
                                        ratioPtJet21 = (
                                            ep_THINjetPt[1]/ep_THINjetPt[0])
                                        dPhiJet12 = DeltaPhi(
                                            ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        dEtaJet12 = (
                                            ep_THINjetEta[0]-ep_THINjetEta[1])
                                        rJet1PtMET = (
                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                            prod_cat = 2
                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                            prod_cat = 1
                                        else:
                                            prod_cat = 0
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                            isjet1EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                            isjet1EtaMatch = -1
                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                        Jet2CMulti = ep_THINjetCMulti[1]
                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                    if ep_THINnJet >= 3 :
                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                            isjet2EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                            isjet2EtaMatch = -1
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]

            '''
            --------------------------------------------------------------------------------
            SIGNAL REGION
            --------------------------------------------------------------------------------
            '''
            h_reg_SR_1b_cutFlow.AddBinContent(1, presel_weight)
            h_reg_SR_2b_cutFlow.AddBinContent(1, presel_weight)
            if mettrigdecision:
                h_reg_SR_1b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                h_reg_SR_2b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                if (ep_pfMetCorrPt > 250. and delta_pfCaloSR < 0.5):
                    h_reg_SR_1b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    h_reg_SR_2b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    if (ep_nEle_index == 0) and (ep_nMu == 0) and (nPho == 0) and (ep_nTau_discBased_TightEleTightMuVeto == 0):
                        h_reg_SR_1b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        h_reg_SR_2b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        if (min_dPhi_jet_MET > 0.5):
                            h_reg_SR_1b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            h_reg_SR_2b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            if isJetSel:
                                jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_1b:
                                h_reg_SR_1b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                    h_reg_SR_1b_cutFlow.AddBinContent(7, weight)
                                    isSR1b = True
                                    SR1bcount += 1
                                    rJet1PtMET = (
                                        ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    if ep_THINnJet == 2:
                                        Jet2Pt = ep_THINjetPt[1]
                                        Jet2Eta = ep_THINjetEta[1]
                                        Jet2Phi = ep_THINjetPhi[1]
                                        Jet2deepCSV = ep_THINjetDeepCSV[1]
                                        ratioPtJet21 = (
                                            ep_THINjetPt[1]/ep_THINjetPt[0])
                                        dPhiJet12 = DeltaPhi(
                                            ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        dEtaJet12 = (
                                            ep_THINjetEta[0]-ep_THINjetEta[1])
                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                            prod_cat = 2
                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                            prod_cat = 1
                                        else:
                                            prod_cat = 0
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                            isjet1EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                            isjet1EtaMatch = -1
                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                        Jet2CMulti = ep_THINjetCMulti[1]
                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                            if isJetSel:
                                jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_2b:
                                h_reg_SR_2b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                    h_reg_SR_2b_cutFlow.AddBinContent(7, weight)
                                    isSR2b = True
                                    SR2bcount += 1
                                    M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                    if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                        prod_cat = 2
                                    elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                        prod_cat = 1
                                    else:
                                        prod_cat = 0
                                    rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    Jet2NHadEF = ep_THINjetNHadEF[1]
                                    Jet2CHadEF = ep_THINjetCHadEF[1]
                                    Jet2CEmEF = ep_THINjetCEmEF[1]
                                    Jet2NEmEF = ep_THINjetNEmEF[1]
                                    Jet2CMulti = ep_THINjetCMulti[1]
                                    Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                    if ep_THINnJet == 3:
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                            isjet2EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                            isjet2EtaMatch = -1
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]

            '''
            --------------------------------------------------------------------------------
            ZEE CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if zee_cr:
                h_reg_ZeeCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_ZeeCR_2b_cutFlow.AddBinContent(1, presel_weight)
                if eletrigdecision:
                    h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    if (ep_nMu == 0):
                        h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig)
                        h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            if (ep_nEle_index == 2) and nPho == 0:
                                h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                if (ep_elePt[0] > minElePt) and (ep_eleIsPTight[0]):
                                    h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    if (ep_ZeeRecoil > 250. and delta_pfCaloZeeCR < 0.5):
                                        h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            if (ep_Zeemass >= 70 and ep_Zeemass <= 110):
                                                h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_ZeeCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZeeCR1bcount += 1
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        is1bCRZee = True
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_ZeeCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZeeCR2bcount += 1
                                                        is2bCRZee = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINnJet == 3:
                                                            M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                            dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                                isjet2EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                                isjet2EtaMatch = -1
                                                            Jet3Pt = ep_THINjetPt[2]
                                                            Jet3Eta = ep_THINjetEta[2]
                                                            Jet3Phi = ep_THINjetPhi[2]
                                                            Jet3deepCSV = ep_THINjetDeepCSV[2]

            '''
            --------------------------------------------------------------------------------
            ZMUMU CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if zmumu_cr:
                h_reg_ZmumuCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_ZmumuCR_2b_cutFlow.AddBinContent(1, presel_weight)
                if mettrigdecision:
                    h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    if (ep_nEle_index == 0) and (nPho == 0):
                        h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            if (ep_nMu == 2):
                                h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                if (ep_muPt[0] > minMuPt) and (ep_isTightMuon[0]):
                                    h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    if (ep_ZmumuRecoil > 250. and delta_pfCaloZmumuCR < 0.5):
                                        h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            if (ep_Zmumumass >= 70 and ep_Zmumumass <= 110):
                                                h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_ZmumuCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZmumuCR1bcount += 1
                                                        is1bCRZmumu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_ZmumuCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZmumuCR2bcount += 1
                                                        is2bCRZmumu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINnJet == 3:
                                                            M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                            dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                                isjet2EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                                isjet2EtaMatch = -1
                                                            Jet3Pt = ep_THINjetPt[2]
                                                            Jet3Eta = ep_THINjetEta[2]
                                                            Jet3Phi = ep_THINjetPhi[2]
                                                            Jet3deepCSV = ep_THINjetDeepCSV[2]
            '''
            --------------------------------------------------------------------------------
            ZEE NoB CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if zee_cr:
                h_reg_ZeeCR_2j_cutFlow.AddBinContent(1, presel_weight)
                h_reg_ZeeCR_3j_cutFlow.AddBinContent(1, presel_weight)
                if eletrigdecision:
                    h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    if (ep_nMu == 0):
                        h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig)
                        h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            if (ep_nEle_index == 2) and nPho == 0:
                                h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                if (ep_elePt[0] > minElePt) and (ep_eleIsPTight[0]):
                                    h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    if (ep_ZeeRecoil > 250. and delta_pfCaloZeeCR < 0.5):
                                        h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            if (ep_Zeemass >= 70 and ep_Zeemass <= 110):
                                                h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if True:
                                                        h_reg_ZeeCR_2j_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZeeCR2jcount += 1
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        is2jCRZee = True
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if True:
                                                        h_reg_ZeeCR_3j_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZeeCR3jcount += 1
                                                        is3jCRZee = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINnJet == 3:
                                                            M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                            dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                                isjet2EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                                isjet2EtaMatch = -1
                                                            Jet3Pt = ep_THINjetPt[2]
                                                            Jet3Eta = ep_THINjetEta[2]
                                                            Jet3Phi = ep_THINjetPhi[2]
                                                            Jet3deepCSV = ep_THINjetDeepCSV[2]
            '''
            --------------------------------------------------------------------------------
            ZMUMU NoB CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if zmumu_cr:
                h_reg_ZmumuCR_2j_cutFlow.AddBinContent(1, presel_weight)
                h_reg_ZmumuCR_3j_cutFlow.AddBinContent(1, presel_weight)
                if mettrigdecision:
                    h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    if (ep_nEle_index == 0) and (nPho == 0):
                        h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            if (ep_nMu == 2):
                                h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                if (ep_muPt[0] > minMuPt) and (ep_isTightMuon[0]):
                                    h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    if (ep_ZmumuRecoil > 250. and delta_pfCaloZmumuCR < 0.5):
                                        h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            if (ep_Zmumumass >= 70 and ep_Zmumumass <= 110):
                                                h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if True:
                                                        h_reg_ZmumuCR_2j_cutFlow.AddBinContent(
                                                            11, weight)
                                                        ZmumuCR2jcount += 1
                                                        is2jCRZmumu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_ZmumuCR_3j_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if True:
                                                        h_reg_ZmumuCR_3j_cutFlow.AddBinContent(11, weight)
                                                        ZmumuCR3jcount += 1
                                                        is3jCRZmumu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINnJet == 3:
                                                            M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                            dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                                isjet2EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                                isjet2EtaMatch = -1
                                                            Jet3Pt = ep_THINjetPt[2]
                                                            Jet3Eta = ep_THINjetEta[2]
                                                            Jet3Phi = ep_THINjetPhi[2]
                                                            Jet3deepCSV = ep_THINjetDeepCSV[2]
            '''
            --------------------------------------------------------------------------------
            WENU CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if wenu_cr:
                h_reg_WenuCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_WenuCR_2b_cutFlow.AddBinContent(1, presel_weight)
                if eletrigdecision:
                    h_reg_WenuCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    h_reg_WenuCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    if (ep_nMu == 0):
                        h_reg_WenuCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig*weightEle)
                        h_reg_WenuCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig*weightEle)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            if (ep_nEle_index == 1) and (nPho == 0):
                                h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                if (ep_elePt[0] > minElePt) and (ep_eleIsPTight[0]):
                                    h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    if (ep_WenuRecoil > 250. and ep_pfMetCorrPt > 100 and delta_pfCaloWenuCR < 0.5):
                                        h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            if (ep_Wenumass >= 0 and ep_Wenumass <= 160):
                                                h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet == 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_WenuCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        WenuCR1bcount += 1
                                                        is1bCRWenu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet == 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                                        10, weight)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_WenuCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        WenuCR2bcount += 1
                                                        is2bCRWenu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                            isjet1EtaMatch = 1
                                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                            isjet1EtaMatch = -1
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
            '''
            --------------------------------------------------------------------------------
            WMUNU CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if wmunu_cr:
                h_reg_WmunuCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                    1, presel_weight*weightRecoiltrig)
                if mettrigdecision:
                    h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    if (ep_nEle_index == 0) and nPho == 0:
                        h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            if (ep_nMu == 1):
                                h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                if (ep_muPt[0] > minMuPt) and (ep_isTightMuon[0]):
                                    h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    if (ep_WmunuRecoil > 250. and ep_pfMetCorrPt > 100 and delta_pfCaloWmunuCR < 0.5):
                                        h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            if (ep_Wmunumass >= 0 and ep_Wmunumass <= 160):
                                                h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet == 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_WmunuCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        WmunuCR1bcount += 1
                                                        is1bCRWmunu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet == 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                                        10, weight)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_WmunuCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        WmunuCR2bcount += 1
                                                        is2bCRWmunu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                            isjet1EtaMatch = 1
                                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                            isjet1EtaMatch = -1
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
            '''
            --------------------------------------------------------------------------------
            TOPENU CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if topenu_cr:
                h_reg_TopenuCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_TopenuCR_2b_cutFlow.AddBinContent(1, presel_weight)
                if eletrigdecision:
                    h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightEleTrig)
                    if (ep_nMu == 0):
                        h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig*weightEle)
                        h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightEleTrig*weightEle)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightEleTrig*weightEle)
                            if (ep_nEle_index == 1) and nPho == 0:
                                h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightEleTrig*weightEle)
                                if (ep_elePt[0] > minElePt) and (ep_eleIsPTight[0]):
                                    h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightEleTrig*weightEle)
                                    if (ep_WenuRecoil > 250. and delta_pfCaloTopenuCR < 0.5):
                                        h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightEleTrig*weightEle)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightEleTrig*weightEle)
                                            if (ep_Wenumass >= 0 and ep_Wenumass <= 160):
                                                h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightEleTrig*weightEle)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightEleTrig*weightEle)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_TopenuCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        TopenuCR1bcount += 1
                                                        is1bCRTopenu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet > 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 2) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                                        10, weight)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_TopenuCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        TopenuCR2bcount += 1
                                                        is2bCRTopenu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                            isjet2EtaMatch = 1
                                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                            isjet2EtaMatch = -1
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        Jet3Pt = ep_THINjetPt[2]
                                                        Jet3Eta = ep_THINjetEta[2]
                                                        Jet3Phi = ep_THINjetPhi[2]
                                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
            '''
            --------------------------------------------------------------------------------
            TOPMUNU CONTROL REGION
            --------------------------------------------------------------------------------
            '''
            if topmunu_cr:
                h_reg_TopmunuCR_1b_cutFlow.AddBinContent(1, presel_weight)
                h_reg_TopmunuCR_2b_cutFlow.AddBinContent(1, presel_weight)
                if mettrigdecision:
                    h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                        2, presel_weight*weightRecoiltrig)
                    if (ep_nEle_index == 0) and nPho == 0:
                        h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig*weightMu)
                        h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                            3, presel_weight*weightRecoiltrig*weightMu)
                        if (ep_nTau_discBased_TightEleTightMuVeto == 0):
                            h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                4, presel_weight*weightRecoiltrig*weightMu)
                            if (ep_nMu == 1):
                                h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                    5, presel_weight*weightRecoiltrig*weightMu)
                                if (ep_muPt[0] > minMuPt) and (ep_isTightMuon[0]):
                                    h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                        6, presel_weight*weightRecoiltrig*weightMu)
                                    if (ep_WmunuRecoil > 250. and delta_pfCaloTopmunuCR < 0.5):
                                        h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                            7, presel_weight*weightRecoiltrig*weightMu)
                                        if (min_dPhi_jet_MET > 0.5):
                                            h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                                8, presel_weight*weightRecoiltrig*weightMu)
                                            if (ep_Wmunumass >= 0 and ep_Wmunumass <= 160):
                                                h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                                    9, presel_weight*weightRecoiltrig*weightMu)
                                                if isJetSel:
                                                    jet_con_1b = (ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_1b:
                                                    h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                                        h_reg_TopmunuCR_1b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        TopmunuCR1bcount += 1
                                                        is1bCRTopmunu = True
                                                        rJet1PtMET = (
                                                            ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        if ep_THINnJet == 2:
                                                            Jet2Pt = ep_THINjetPt[1]
                                                            Jet2Eta = ep_THINjetEta[1]
                                                            Jet2Phi = ep_THINjetPhi[1]
                                                            Jet2deepCSV = ep_THINjetDeepCSV[1]
                                                            ratioPtJet21 = (
                                                                ep_THINjetPt[1]/ep_THINjetPt[0])
                                                            dPhiJet12 = DeltaPhi(
                                                                ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            dEtaJet12 = (
                                                                ep_THINjetEta[0]-ep_THINjetEta[1])
                                                            M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                            dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                            if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                                prod_cat = 2
                                                            elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                                prod_cat = 1
                                                            else:
                                                                prod_cat = 0
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                                                isjet1EtaMatch = 1
                                                            if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                                                isjet1EtaMatch = -1
                                                            Jet2NHadEF = ep_THINjetNHadEF[1]
                                                            Jet2CHadEF = ep_THINjetCHadEF[1]
                                                            Jet2CEmEF = ep_THINjetCEmEF[1]
                                                            Jet2NEmEF = ep_THINjetNEmEF[1]
                                                            Jet2CMulti = ep_THINjetCMulti[1]
                                                            Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                if isJetSel:
                                                    jet_con_2b = (ep_THINnJet > 2) and (ep_THINjetPt[0] > 100.)
                                                else:
                                                    jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 2) and (ep_THINjetPt[0] > 100.)
                                                if jet_con_2b:
                                                    h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                                        10, presel_weight*weightRecoiltrig*weightMu)
                                                    if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                                        h_reg_TopmunuCR_2b_cutFlow.AddBinContent(
                                                            11, weight)
                                                        TopmunuCR2bcount += 1
                                                        is2bCRTopmunu = True
                                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                                        rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                                            prod_cat = 2
                                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                                            prod_cat = 1
                                                        else:
                                                            prod_cat = 0
                                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                                            isjet2EtaMatch = 1
                                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                                            isjet2EtaMatch = -1
                                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                                        Jet2CMulti = ep_THINjetCMulti[1]
                                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                                        Jet3Pt = ep_THINjetPt[2]
                                                        Jet3Eta = ep_THINjetEta[2]
                                                        Jet3Phi = ep_THINjetPhi[2]
                                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
            '''
            --------------------------------------------------------------------------------
            QCDb REGION
            --------------------------------------------------------------------------------
            '''
            h_reg_QCDbCR_1b_cutFlow.AddBinContent(1, presel_weight)
            h_reg_QCDbCR_2b_cutFlow.AddBinContent(1, presel_weight)
            if mettrigdecision:
                h_reg_QCDbCR_1b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                h_reg_QCDbCR_2b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                if (ep_pfMetCorrPt > 250. and delta_pfCaloSR < 0.5):
                    h_reg_QCDbCR_1b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    h_reg_QCDbCR_2b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    if (ep_nEle_index == 0) and (ep_nMu == 0) and (nPho == 0) and (ep_nTau_discBased_TightEleTightMuVeto == 0):
                        h_reg_QCDbCR_1b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        h_reg_QCDbCR_2b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        if (min_dPhi_jet_MET < 0.5):
                            h_reg_QCDbCR_1b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            h_reg_QCDbCR_2b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            if isJetSel:
                                jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_1b:
                                h_reg_QCDbCR_1b_cutFlow.AddBinContent(6, presel_weight*weightMETtrig)
                                if (ep_THINbjets_Cond[0]) and (nBjets == 1):
                                    h_reg_QCDbCR_1b_cutFlow.AddBinContent(7, weight)
                                    isQCDbCR1b = True
                                    QCDbCR1bcount += 1
                                    rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    if ep_THINnJet == 2:
                                        Jet2Pt = ep_THINjetPt[1]
                                        Jet2Eta = ep_THINjetEta[1]
                                        Jet2Phi = ep_THINjetPhi[1]
                                        Jet2deepCSV = ep_THINjetDeepCSV[1]
                                        ratioPtJet21 = (
                                            ep_THINjetPt[1]/ep_THINjetPt[0])
                                        dPhiJet12 = DeltaPhi(
                                            ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        dEtaJet12 = (
                                            ep_THINjetEta[0]-ep_THINjetEta[1])
                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                            prod_cat = 2
                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                            prod_cat = 1
                                        else:
                                            prod_cat = 0
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                            isjet1EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                            isjet1EtaMatch = -1
                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                        Jet2CMulti = ep_THINjetCMulti[1]
                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                            if isJetSel:
                                jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_2b:
                                h_reg_QCDbCR_2b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (ep_THINbjets_Cond[0]) and ep_THINbjets_Cond[1] and (nBjets == 2):
                                    h_reg_QCDbCR_2b_cutFlow.AddBinContent(7, weight)
                                    isQCDbCR2b = True
                                    QCDbCR2bcount += 1
                                    M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                    if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                        prod_cat = 2
                                    elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                        prod_cat = 1
                                    else:
                                        prod_cat = 0
                                    rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    Jet2NHadEF = ep_THINjetNHadEF[1]
                                    Jet2CHadEF = ep_THINjetCHadEF[1]
                                    Jet2CEmEF = ep_THINjetCEmEF[1]
                                    Jet2NEmEF = ep_THINjetNEmEF[1]
                                    Jet2CMulti = ep_THINjetCMulti[1]
                                    Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                    if ep_THINnJet == 3:
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                            isjet2EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                            isjet2EtaMatch = -1
            '''
            --------------------------------------------------------------------------------
            QCDa REGION
            --------------------------------------------------------------------------------
            '''
            h_reg_QCDaCR_1b_cutFlow.AddBinContent(1, presel_weight)
            h_reg_QCDaCR_2b_cutFlow.AddBinContent(1, presel_weight)
            if mettrigdecision:
                h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                    2, presel_weight*weightMETtrig)
                h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                    2, presel_weight*weightMETtrig)
                if (ep_pfMetCorrPt > 250. and delta_pfCaloSR < 0.5):
                    h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    if (ep_nEle_index == 0) and (ep_nMu == 0) and (nPho == 0) and (ep_nTau_discBased_TightEleTightMuVeto == 0):
                        h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        if (min_dPhi_jet_MET < 0.5):
                            h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            if isJetSel:
                                jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_1b:
                                h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (nBjets == 0):
                                    h_reg_QCDaCR_1b_cutFlow.AddBinContent(
                                        7, weight)
                                    isQCDaCR1b = True
                                    QCDaCR1bcount += 1
                                    rJet1PtMET = (
                                        ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    if ep_THINnJet == 2:
                                        Jet2Pt = ep_THINjetPt[1]
                                        Jet2Eta = ep_THINjetEta[1]
                                        Jet2Phi = ep_THINjetPhi[1]
                                        Jet2deepCSV = ep_THINjetDeepCSV[1]
                                        ratioPtJet21 = (
                                            ep_THINjetPt[1]/ep_THINjetPt[0])
                                        dPhiJet12 = DeltaPhi(
                                            ep_THINjetPhi[0], ep_THINjetPhi[1])
                                        dEtaJet12 = (
                                            ep_THINjetEta[0]-ep_THINjetEta[1])
                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[
                                                             0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[
                                                              0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        eta_Jet1Jet2 = dijetEta(
                                            ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        phi_Jet1Jet2 = dijetPhi(
                                            ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        dRJet12 = Delta_R(
                                            ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0], ep_THINjetPhi[1])
                                        if ep_THINjetHadronFlavor[0] == 5 and ep_THINjetHadronFlavor[1] == 5:
                                            prod_cat = 2
                                        elif (ep_THINjetHadronFlavor[0] == 5 and ep_THINjetHadronFlavor[1] != 5) or (ep_THINjetHadronFlavor[0] != 5 and ep_THINjetHadronFlavor[1] == 5):
                                            prod_cat = 1
                                        else:
                                            prod_cat = 0
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                            isjet1EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                            isjet1EtaMatch = -1
                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                        Jet2CMulti = ep_THINjetCMulti[1]
                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                            if isJetSel:
                                jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_2b:
                                h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (nBjets == 1) or (nBjets == 0):
                                    h_reg_QCDaCR_2b_cutFlow.AddBinContent(
                                        7, weight)
                                    isQCDaCR2b = True
                                    QCDaCR2bcount += 1
                                    M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],
                                                            ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],
                                                            ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    dRJet12 = Delta_R(
                                        ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0], ep_THINjetPhi[1])
                                    if ep_THINjetHadronFlavor[0] == 5 and ep_THINjetHadronFlavor[1] == 5:
                                        prod_cat = 2
                                    elif (ep_THINjetHadronFlavor[0] == 5 and ep_THINjetHadronFlavor[1] != 5) or (ep_THINjetHadronFlavor[0] != 5 and ep_THINjetHadronFlavor[1] == 5):
                                        prod_cat = 1
                                    else:
                                        prod_cat = 0
                                    rJet1PtMET = (
                                        ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    Jet2NHadEF = ep_THINjetNHadEF[1]
                                    Jet2CHadEF = ep_THINjetCHadEF[1]
                                    Jet2CEmEF = ep_THINjetCEmEF[1]
                                    Jet2NEmEF = ep_THINjetNEmEF[1]
                                    Jet2CMulti = ep_THINjetCMulti[1]
                                    Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                    if ep_THINnJet == 3:
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                        dPhiJet13 = DeltaPhi(
                                            ep_THINjetPhi[0], ep_THINjetPhi[2])
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                            isjet2EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                            isjet2EtaMatch = -1
            '''
            --------------------------------------------------------------------------------
            QCDc REGION
            --------------------------------------------------------------------------------
            '''
            h_reg_QCDcCR_1b_cutFlow.AddBinContent(1, presel_weight)
            h_reg_QCDcCR_2b_cutFlow.AddBinContent(1, presel_weight)
            if mettrigdecision:
                h_reg_QCDcCR_1b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                h_reg_QCDcCR_2b_cutFlow.AddBinContent(2, presel_weight*weightMETtrig)
                if (ep_pfMetCorrPt > 250. and delta_pfCaloSR < 0.5):
                    h_reg_QCDcCR_1b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    h_reg_QCDcCR_2b_cutFlow.AddBinContent(
                        3, presel_weight*weightMETtrig)
                    if (ep_nEle_index == 0) and (ep_nMu == 0) and (nPho == 0) and (ep_nTau_discBased_TightEleTightMuVeto == 0):
                        h_reg_QCDcCR_1b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        h_reg_QCDcCR_2b_cutFlow.AddBinContent(
                            4, presel_weight*weightMETtrig)
                        if (min_dPhi_jet_MET > 0.5):
                            h_reg_QCDcCR_1b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            h_reg_QCDcCR_2b_cutFlow.AddBinContent(
                                5, presel_weight*weightMETtrig)
                            if isJetSel:
                                jet_con_1b = (ep_THINnJet <= 2) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_1b = (ep_THINnJet <= 8 and ep_THINnJet >= 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_1b:
                                h_reg_QCDcCR_1b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (nBjets == 0):
                                    h_reg_QCDcCR_1b_cutFlow.AddBinContent(7, weight)
                                    isQCDcCR1b = True
                                    QCDcCR1bcount += 1
                                    rJet1PtMET = (
                                        ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    if ep_THINnJet == 2:
                                        Jet2Pt = ep_THINjetPt[1]
                                        Jet2Eta = ep_THINjetEta[1]
                                        Jet2Phi = ep_THINjetPhi[1]
                                        Jet2deepCSV = ep_THINjetDeepCSV[1]
                                        ratioPtJet21 = (
                                            ep_THINjetPt[1]/ep_THINjetPt[0])
                                        dPhiJet12 = DeltaPhi(
                                            ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        dEtaJet12 = (
                                            ep_THINjetEta[0]-ep_THINjetEta[1])
                                        M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                        dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                        if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                            prod_cat = 2
                                        elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                            prod_cat = 1
                                        else:
                                            prod_cat = 0
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] > 0:
                                            isjet1EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[1] < 0:
                                            isjet1EtaMatch = -1
                                        Jet2NHadEF = ep_THINjetNHadEF[1]
                                        Jet2CHadEF = ep_THINjetCHadEF[1]
                                        Jet2CEmEF = ep_THINjetCEmEF[1]
                                        Jet2NEmEF = ep_THINjetNEmEF[1]
                                        Jet2CMulti = ep_THINjetCMulti[1]
                                        Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                            if isJetSel:
                                jet_con_2b = (ep_THINnJet <= 3 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            else:
                                jet_con_2b = (ep_THINnJet <= 8 and ep_THINnJet > 1) and (ep_THINjetPt[0] > 100.)
                            if jet_con_2b:
                                h_reg_QCDcCR_2b_cutFlow.AddBinContent(
                                    6, presel_weight*weightMETtrig)
                                if (nBjets == 1) or (nBjets == 0):
                                    h_reg_QCDcCR_2b_cutFlow.AddBinContent(7, weight)
                                    isQCDcCR2b = True
                                    QCDcCR2bcount += 1
                                    M_Jet1Jet2 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    pT_Jet1Jet2 = dijetPt(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    eta_Jet1Jet2 = dijetEta(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    phi_Jet1Jet2 = dijetPhi(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0], ep_THINjetPx[1], ep_THINjetPy[1], ep_THINjetPz[1], ep_THINjetEnergy[1])
                                    dRJet12 = Delta_R(ep_THINjetEta[0], ep_THINjetEta[1], ep_THINjetPhi[0],ep_THINjetPhi[1])
                                    if ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]==5:
                                        prod_cat = 2
                                    elif (ep_THINjetHadronFlavor[0]==5 and ep_THINjetHadronFlavor[1]!=5) or (ep_THINjetHadronFlavor[0]!=5 and ep_THINjetHadronFlavor[1]==5):
                                        prod_cat = 1
                                    else:
                                        prod_cat = 0
                                    rJet1PtMET = (ep_THINjetPt[0]/ep_pfMetCorrPt)
                                    Jet2NHadEF = ep_THINjetNHadEF[1]
                                    Jet2CHadEF = ep_THINjetCHadEF[1]
                                    Jet2CEmEF = ep_THINjetCEmEF[1]
                                    Jet2NEmEF = ep_THINjetNEmEF[1]
                                    Jet2CMulti = ep_THINjetCMulti[1]
                                    Jet2NMultiplicity = ep_THINjetNMultiplicity[1]
                                    if ep_THINnJet == 3:
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
                                        M_Jet1Jet3 = InvMass(ep_THINjetPx[0], ep_THINjetPy[0], ep_THINjetPz[0], ep_THINjetEnergy[0],ep_THINjetPx[2], ep_THINjetPy[2], ep_THINjetPz[2], ep_THINjetEnergy[2])
                                        dPhiJet13 = DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[2])
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] > 0:
                                            isjet2EtaMatch = 1
                                        if ep_THINjetEta[0]*ep_THINjetEta[2] < 0:
                                            isjet2EtaMatch = -1
                                        Jet3Pt = ep_THINjetPt[2]
                                        Jet3Eta = ep_THINjetEta[2]
                                        Jet3Phi = ep_THINjetPhi[2]
                                        Jet3deepCSV = ep_THINjetDeepCSV[2]
            if ispreselR:
                df_out_preselR = df_out_preselR.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF': float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF': float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF': float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF': float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti': float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity': float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch':float(isjet2EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('ispreselR')
            if isSR1b:
                df_out_SR_1b = df_out_SR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('isSR1b')
            if isSR2b:
                df_out_SR_2b = df_out_SR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('isSR2b')
            if is1bCRZee:
                df_out_ZeeCR_1b = df_out_ZeeCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZeeCR),
                    'Recoil': float(ep_ZeeRecoil),
                    'RecoilPhi': float(ep_ZeeRecoil_dPhi),
                    'Zmass': float(ep_Zeemass),
                    'ZpT': float(ZpT_ee),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_elePhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'subleadingLepPt': float(ep_elePt[1]),
                    'subleadingLepEta': float(ep_eleEta[1]),
                    'subleadingLepPhi': float(ep_elePhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZeeRecoilResUp),
                    'Recoil_En_up': float(ep_ZeeRecoilEnUp),
                    'Recoil_En_down': float(ep_ZeeRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZeeRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRZee')
            if is2bCRZee:
                df_out_ZeeCR_2b = df_out_ZeeCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZeeCR),
                    'Recoil': float(ep_ZeeRecoil),
                    'RecoilPhi': float(ep_ZeeRecoil_dPhi),
                    'Zmass': float(ep_Zeemass),
                    'ZpT': float(ZpT_ee),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_elePhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'subleadingLepPt': float(ep_elePt[1]),
                    'subleadingLepEta': float(ep_eleEta[1]),
                    'subleadingLepPhi': float(ep_elePhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZeeRecoilResUp),
                    'Recoil_En_up': float(ep_ZeeRecoilEnUp),
                    'Recoil_En_down': float(ep_ZeeRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZeeRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRZee')

            if is1bCRZmumu:
                df_out_ZmumuCR_1b = df_out_ZmumuCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZmumuCR),
                    'Recoil': float(ep_ZmumuRecoil),
                    'RecoilPhi': float(ep_ZmumuRecoil_dPhi),
                    'Zmass': float(ep_Zmumumass),
                    'ZpT': float(ZpT_mumu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_muPhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'subleadingLepPt': float(ep_muPt[1]),
                    'subleadingLepEta': float(ep_muEta[1]),
                    'subleadingLepPhi': float(ep_muPhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZmumuRecoilResUp),
                    'Recoil_En_up': float(ep_ZmumuRecoilEnUp),
                    'Recoil_En_down': float(ep_ZmumuRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZmumuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRZmumu')
            if is2bCRZmumu:
                df_out_ZmumuCR_2b = df_out_ZmumuCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZmumuCR),
                    'Recoil': float(ep_ZmumuRecoil),
                    'RecoilPhi': float(ep_ZmumuRecoil_dPhi),
                    'Zmass': float(ep_Zmumumass),
                    'ZpT': float(ZpT_mumu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_muPhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'subleadingLepPt': float(ep_muPt[1]),
                    'subleadingLepEta': float(ep_muEta[1]),
                    'subleadingLepPhi': float(ep_muPhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZmumuRecoilResUp),
                    'Recoil_En_up': float(ep_ZmumuRecoilEnUp),
                    'Recoil_En_down': float(ep_ZmumuRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZmumuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRZmumu')
            if is2jCRZee:
                df_out_ZeeCR_2j = df_out_ZeeCR_2j.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZeeCR),
                    'Recoil': float(ep_ZeeRecoil),
                    'RecoilPhi': float(ep_ZeeRecoil_dPhi),
                    'Zmass': float(ep_Zeemass),
                    'ZpT': float(ZpT_ee),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_elePhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'subleadingLepPt': float(ep_elePt[1]),
                    'subleadingLepEta': float(ep_eleEta[1]),
                    'subleadingLepPhi': float(ep_elePhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZeeRecoilResUp),
                    'Recoil_En_up': float(ep_ZeeRecoilEnUp),
                    'Recoil_En_down': float(ep_ZeeRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZeeRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2jCRZee')
            if is3jCRZee:
                df_out_ZeeCR_3j = df_out_ZeeCR_3j.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZeeCR),
                    'Recoil': float(ep_ZeeRecoil),
                    'RecoilPhi': float(ep_ZeeRecoil_dPhi),
                    'Zmass': float(ep_Zeemass),
                    'ZpT': float(ZpT_ee),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_elePhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'subleadingLepPt': float(ep_elePt[1]),
                    'subleadingLepEta': float(ep_eleEta[1]),
                    'subleadingLepPhi': float(ep_elePhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZeeRecoilResUp),
                    'Recoil_En_up': float(ep_ZeeRecoilEnUp),
                    'Recoil_En_down': float(ep_ZeeRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZeeRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is3jCRZee')

            if is2jCRZmumu:
                df_out_ZmumuCR_2j = df_out_ZmumuCR_2j.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZmumuCR),
                    'Recoil': float(ep_ZmumuRecoil),
                    'RecoilPhi': float(ep_ZmumuRecoil_dPhi),
                    'Zmass': float(ep_Zmumumass),
                    'ZpT': float(ZpT_mumu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_muPhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'subleadingLepPt': float(ep_muPt[1]),
                    'subleadingLepEta': float(ep_muEta[1]),
                    'subleadingLepPhi': float(ep_muPhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZmumuRecoilResUp),
                    'Recoil_En_up': float(ep_ZmumuRecoilEnUp),
                    'Recoil_En_down': float(ep_ZmumuRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZmumuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2jCRZmumu')
            if is3jCRZmumu:
                df_out_ZmumuCR_3j = df_out_ZmumuCR_3j.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloZmumuCR),
                    'Recoil': float(ep_ZmumuRecoil),
                    'RecoilPhi': float(ep_ZmumuRecoil_dPhi),
                    'Zmass': float(ep_Zmumumass),
                    'ZpT': float(ZpT_mumu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(DeltaPhi(ep_muPhi[1],ep_pfMetCorrPhi)),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'subleadingLepPt': float(ep_muPt[1]),
                    'subleadingLepEta': float(ep_muEta[1]),
                    'subleadingLepPhi': float(ep_muPhi[1]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_ZmumuRecoilResUp),
                    'Recoil_En_up': float(ep_ZmumuRecoilEnUp),
                    'Recoil_En_down': float(ep_ZmumuRecoilEnDown),
                    'Recoil_Res_down': float(ep_ZmumuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is3jCRZmumu')
            if is1bCRWenu:
                df_out_WenuCR_1b = df_out_WenuCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloWenuCR),
                    'Recoil': float(ep_WenuRecoil),
                    'RecoilPhi': float(ep_WenuRecoil_dPhi),
                    'Wmass': float(ep_Wenumass),
                    'WpT': float(WpT_enu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(dummy),
                    'Jet2CHadEF':float(dummy),
                    'Jet2CEmEF':float(dummy),
                    'Jet2NEmEF':float(dummy),
                    'Jet2CMulti':float(dummy),
                    'Jet2NMultiplicity': float(dummy),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'rJet1PtMET': float(rJet1PtMET),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WenuRecoilResUp),
                    'Recoil_En_up': float(ep_WenuRecoilEnUp),
                    'Recoil_En_down': float(ep_WenuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WenuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRWenu')
            if is2bCRWenu:
                df_out_WenuCR_2b = df_out_WenuCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloWenuCR),
                    'Recoil': float(ep_WenuRecoil),
                    'RecoilPhi': float(ep_WenuRecoil_dPhi),
                    'Wmass': float(ep_Wenumass),
                    'WpT': float(WpT_enu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WenuRecoilResUp),
                    'Recoil_En_up': float(ep_WenuRecoilEnUp),
                    'Recoil_En_down': float(ep_WenuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WenuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRWenu')

            if is1bCRWmunu:
                df_out_WmunuCR_1b = df_out_WmunuCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloWmunuCR),
                    'Recoil': float(ep_WmunuRecoil),
                    'RecoilPhi': float(ep_WmunuRecoil_dPhi),
                    'Wmass': float(ep_Wmunumass),
                    'WpT': float(WpT_munu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(dummy),
                    'Jet2CHadEF':float(dummy),
                    'Jet2CEmEF':float(dummy),
                    'Jet2NEmEF':float(dummy),
                    'Jet2CMulti':float(dummy),
                    'Jet2NMultiplicity':float(dummy),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'rJet1PtMET': float(rJet1PtMET),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WmunuRecoilResUp),
                    'Recoil_En_up': float(ep_WmunuRecoilEnUp),
                    'Recoil_En_down': float(ep_WmunuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WmunuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRWmunu')
            if is2bCRWmunu:
                df_out_WmunuCR_2b = df_out_WmunuCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloWmunuCR),
                    'Recoil': float(ep_WmunuRecoil),
                    'RecoilPhi': float(ep_WmunuRecoil_dPhi),
                    'Wmass': float(ep_Wmunumass),
                    'WpT': float(WpT_munu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WmunuRecoilResUp),
                    'Recoil_En_up': float(ep_WmunuRecoilEnUp),
                    'Recoil_En_down': float(ep_WmunuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WmunuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRWmunu')
            if is1bCRTopenu:
                df_out_TopenuCR_1b = df_out_TopenuCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloTopenuCR),
                    'Recoil': float(ep_WenuRecoil),
                    'RecoilPhi': float(ep_WenuRecoil_dPhi),
                    'Wmass': float(ep_Wenumass),
                    'WpT': float(WpT_enu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WenuRecoilResUp),
                    'Recoil_En_up': float(ep_WenuRecoilEnUp),
                    'Recoil_En_down': float(ep_WenuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WenuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRTopenu')
            if is2bCRTopenu:
                df_out_TopenuCR_2b = df_out_TopenuCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloTopenuCR),
                    'Recoil': float(ep_WenuRecoil),
                    'RecoilPhi': float(ep_WenuRecoil_dPhi),
                    'Wmass': float(ep_Wenumass),
                    'WpT': float(WpT_enu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_elePhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_elePt[0]),
                    'leadingLepEta': float(ep_eleEta[0]),
                    'leadingLepPhi': float(ep_elePhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WenuRecoilResUp),
                    'Recoil_En_up': float(ep_WenuRecoilEnUp),
                    'Recoil_En_down': float(ep_WenuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WenuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRTopenu')
            if is1bCRTopmunu:
                df_out_TopmunuCR_1b = df_out_TopmunuCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloTopmunuCR),
                    'Recoil': float(ep_WmunuRecoil),
                    'RecoilPhi': float(ep_WmunuRecoil_dPhi),
                    'Wmass': float(ep_Wmunumass),
                    'WpT': float(WpT_munu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WmunuRecoilResUp),
                    'Recoil_En_up': float(ep_WmunuRecoilEnUp),
                    'Recoil_En_down': float(ep_WmunuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WmunuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is1bCRTopmunu')
            if is2bCRTopmunu:
                df_out_TopmunuCR_2b = df_out_TopmunuCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloTopmunuCR),
                    'Recoil': float(ep_WmunuRecoil),
                    'RecoilPhi': float(ep_WmunuRecoil_dPhi),
                    'Wmass': float(ep_Wmunumass),
                    'WpT': float(WpT_munu),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'dPhi_lep1_MET': float(DeltaPhi(ep_muPhi[0],ep_pfMetCorrPhi)),
                    'dPhi_lep2_MET': float(dPhi_lep2_MET),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0], ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'leadingLepPt': float(ep_muPt[0]),
                    'leadingLepEta': float(ep_muEta[0]),
                    'leadingLepPhi': float(ep_muPhi[0]),
                    'weight': float(weight),
                    'weightRecoiltrig': float(weightRecoiltrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightRecoiltrig_up': float(weightRecoiltrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'Recoil_Res_up': float(ep_WmunuRecoilResUp),
                    'Recoil_En_up': float(ep_WmunuRecoilEnUp),
                    'Recoil_En_down': float(ep_WmunuRecoilEnDown),
                    'Recoil_Res_down': float(ep_WmunuRecoilResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightRecoiltrig_down': float(weightRecoiltrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('is2bCRTopmunu')
            if isQCDbCR1b:
                df_out_QCDbCR_1b = df_out_QCDbCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF':float(Jet2NHadEF),
                    'Jet2CHadEF':float(Jet2CHadEF),
                    'Jet2CEmEF':float(Jet2CEmEF),
                    'Jet2NEmEF':float(Jet2NEmEF),
                    'Jet2CMulti':float(Jet2CMulti),
                    'Jet2NMultiplicity':float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('isQCDbCR1b')
            if isQCDbCR2b:
                df_out_QCDbCR_2b = df_out_QCDbCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float( ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float( ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float( ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float( ep_pfTRKMETPt),
                    'pfTRKMETPhi': float( ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF':float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF':float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF':float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF':float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti':float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity':float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0],ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up':float(weightscale_up),
                    'weightpdf_up':float(weightpdf_up),
                    'weightscale_down':float(weightscale_down),
                    'weightpdf_down':float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig' : float(weightEleTrig),
                    'weightEleID' : float(weightEleID),
                    'weightEleRECO' : float(weightEleRECO),
                    'weightMuTRK' : float(weightMuTRK),
                    'weightMuID' : float(weightMuID),
                    'weightMuISO' : float(weightMuISO),
                    'weightEleTrig_up' : float(weightEleTrig_up),
                    'weightEleID_up' : float(weightEleID_up),
                    'weightEleRECO_up' : float(weightEleRECO_up),
                    'weightMuTRK_up' : float(weightMuTRK_up),
                    'weightMuID_up' : float(weightMuID_up),
                    'weightMuISO_up' : float(weightMuISO_up),
                    'weightEleTrig_down' : float(weightEleTrig_down),
                    'weightEleID_down' : float(weightEleID_down),
                    'weightEleRECO_down' : float(weightEleRECO_down),
                    'weightMuTRK_down' : float(weightMuTRK_down),
                    'weightMuID_down' : float(weightMuID_down),
                    'weightMuISO_down' : float(weightMuISO_down),
                    'weightscale_down' : float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp':float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp':float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up':float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp':float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up':float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp':float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp':float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp':float(JECSourceUp['HF']),
                    'weightJECHF_yearUp':float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp':float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp':float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown':float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown':float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down':float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown':float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down':float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown':float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown':float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown':float(JECSourceDown['HF']),
                    'weightJECHF_yearDown':float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown':float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown':float(JECSourceDown['RelativeSample_year']),
                }, ignore_index = True)
            if istest:
                print('isQCDbCR2b')
            if isQCDaCR1b:
                df_out_QCDaCR_1b = df_out_QCDaCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float(ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float(ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float(ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float(ep_pfTRKMETPt),
                    'pfTRKMETPhi': float(ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF': float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF': float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF': float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF': float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti': float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity': float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF': float(Jet2NHadEF),
                    'Jet2CHadEF': float(Jet2CHadEF),
                    'Jet2CEmEF': float(Jet2CEmEF),
                    'Jet2NEmEF': float(Jet2NEmEF),
                    'Jet2CMulti': float(Jet2CMulti),
                    'Jet2NMultiplicity': float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up': float(weightscale_up),
                    'weightpdf_up': float(weightpdf_up),
                    'weightscale_down': float(weightscale_down),
                    'weightpdf_down': float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig': float(weightEleTrig),
                    'weightEleID': float(weightEleID),
                    'weightEleRECO': float(weightEleRECO),
                    'weightMuTRK': float(weightMuTRK),
                    'weightMuID': float(weightMuID),
                    'weightMuISO': float(weightMuISO),
                    'weightEleTrig_up': float(weightEleTrig_up),
                    'weightEleID_up': float(weightEleID_up),
                    'weightEleRECO_up': float(weightEleRECO_up),
                    'weightMuTRK_up': float(weightMuTRK_up),
                    'weightMuID_up': float(weightMuID_up),
                    'weightMuISO_up': float(weightMuISO_up),
                    'weightEleTrig_down': float(weightEleTrig_down),
                    'weightEleID_down': float(weightEleID_down),
                    'weightEleRECO_down': float(weightEleRECO_down),
                    'weightMuTRK_down': float(weightMuTRK_down),
                    'weightMuID_down': float(weightMuID_down),
                    'weightMuISO_down': float(weightMuISO_down),
                    'weightscale_down': float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp': float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp': float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up': float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp': float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up': float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp': float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp': float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp': float(JECSourceUp['HF']),
                    'weightJECHF_yearUp': float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp': float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp': float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown': float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown': float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down': float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown': float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down': float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown': float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown': float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown': float(JECSourceDown['HF']),
                    'weightJECHF_yearDown': float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown': float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown': float(JECSourceDown['RelativeSample_year']),
                }, ignore_index=True)
            if istest:
                print('isQCDaCR1b')
            if isQCDaCR2b:
                df_out_QCDaCR_2b = df_out_QCDaCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float(ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float(ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float(ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float(ep_pfTRKMETPt),
                    'pfTRKMETPhi': float(ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF': float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF': float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF': float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF': float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti': float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity': float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0], ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up': float(weightscale_up),
                    'weightpdf_up': float(weightpdf_up),
                    'weightscale_down': float(weightscale_down),
                    'weightpdf_down': float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig': float(weightEleTrig),
                    'weightEleID': float(weightEleID),
                    'weightEleRECO': float(weightEleRECO),
                    'weightMuTRK': float(weightMuTRK),
                    'weightMuID': float(weightMuID),
                    'weightMuISO': float(weightMuISO),
                    'weightEleTrig_up': float(weightEleTrig_up),
                    'weightEleID_up': float(weightEleID_up),
                    'weightEleRECO_up': float(weightEleRECO_up),
                    'weightMuTRK_up': float(weightMuTRK_up),
                    'weightMuID_up': float(weightMuID_up),
                    'weightMuISO_up': float(weightMuISO_up),
                    'weightEleTrig_down': float(weightEleTrig_down),
                    'weightEleID_down': float(weightEleID_down),
                    'weightEleRECO_down': float(weightEleRECO_down),
                    'weightMuTRK_down': float(weightMuTRK_down),
                    'weightMuID_down': float(weightMuID_down),
                    'weightMuISO_down': float(weightMuISO_down),
                    'weightscale_down': float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp': float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp': float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up': float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp': float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up': float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp': float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp': float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp': float(JECSourceUp['HF']),
                    'weightJECHF_yearUp': float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp': float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp': float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown': float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown': float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down': float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown': float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down': float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown': float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown': float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown': float(JECSourceDown['HF']),
                    'weightJECHF_yearDown': float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown': float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown': float(JECSourceDown['RelativeSample_year']),
                }, ignore_index=True)
            if istest:
                print('isQCDaCR2b')
            if isQCDcCR1b:
                df_out_QCDcCR_1b = df_out_QCDcCR_1b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float(ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float(ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float(ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float(ep_pfTRKMETPt),
                    'pfTRKMETPhi': float(ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NTau': float(ep_nTau_discBased_TightEleTightMuVeto),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF': float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF': float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF': float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF': float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti': float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity': float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(Jet2Pt),
                    'Jet2Eta': float(Jet2Eta),
                    'Jet2Phi': float(Jet2Phi),
                    'Jet2deepCSV': float(Jet2deepCSV),
                    'Jet2NHadEF': float(Jet2NHadEF),
                    'Jet2CHadEF': float(Jet2CHadEF),
                    'Jet2CEmEF': float(Jet2CEmEF),
                    'Jet2NEmEF': float(Jet2NEmEF),
                    'Jet2CMulti': float(Jet2CMulti),
                    'Jet2NMultiplicity': float(Jet2NMultiplicity),
                    'Jet3Pt': float(dummy),
                    'Jet3Eta': float(dummy),
                    'Jet3Phi': float(dummy),
                    'Jet3deepCSV': float(dummy),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'isjet1EtaMatch': float(isjet1EtaMatch),
                    'ratioPtJet21': float(ratioPtJet21),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(dPhiJet12),
                    'dEtaJet12': float(dEtaJet12),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up': float(weightscale_up),
                    'weightpdf_up': float(weightpdf_up),
                    'weightscale_down': float(weightscale_down),
                    'weightpdf_down': float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig': float(weightEleTrig),
                    'weightEleID': float(weightEleID),
                    'weightEleRECO': float(weightEleRECO),
                    'weightMuTRK': float(weightMuTRK),
                    'weightMuID': float(weightMuID),
                    'weightMuISO': float(weightMuISO),
                    'weightEleTrig_up': float(weightEleTrig_up),
                    'weightEleID_up': float(weightEleID_up),
                    'weightEleRECO_up': float(weightEleRECO_up),
                    'weightMuTRK_up': float(weightMuTRK_up),
                    'weightMuID_up': float(weightMuID_up),
                    'weightMuISO_up': float(weightMuISO_up),
                    'weightEleTrig_down': float(weightEleTrig_down),
                    'weightEleID_down': float(weightEleID_down),
                    'weightEleRECO_down': float(weightEleRECO_down),
                    'weightMuTRK_down': float(weightMuTRK_down),
                    'weightMuID_down': float(weightMuID_down),
                    'weightMuISO_down': float(weightMuISO_down),
                    'weightscale_down': float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp': float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp': float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up': float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp': float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up': float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp': float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp': float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp': float(JECSourceUp['HF']),
                    'weightJECHF_yearUp': float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp': float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp': float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown': float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown': float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down': float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown': float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down': float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown': float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown': float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown': float(JECSourceDown['HF']),
                    'weightJECHF_yearDown': float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown': float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown': float(JECSourceDown['RelativeSample_year']),
                }, ignore_index=True)
            if istest:
                print('isQCDcCR1b')
            if isQCDcCR2b:
                df_out_QCDcCR_2b = df_out_QCDcCR_2b.append({
                    'run': float(ep_runId),
                    'lumi': float(ep_lumiSection),
                    'event': float(ep_eventId),
                    'nPV': float(ep_THINjetNPV),
                    'MET': float(ep_pfMetCorrPt),
                    'METPhi': float(ep_pfMetCorrPhi),
                    'pfMetCorrSig': float(ep_pfMetCorrSig),
                    'pfpatCaloMETPt': float(ep_pfpatCaloMETPt),
                    'pfpatCaloMETPhi': float(ep_pfpatCaloMETPhi),
                    'pfTRKMETPt': float(ep_pfTRKMETPt),
                    'pfTRKMETPhi': float(ep_pfTRKMETPhi),
                    'delta_pfCalo': float(delta_pfCaloSR),
                    'dPhi_jetMET': float(min_dPhi_jet_MET),
                    'JetwithEta4p5': float(JetwithEta4p5),
                    'NEle': float(ep_nEle_index),
                    'NMu': float(ep_nMu),
                    'nPho': float(nPho),
                    'Njets_PassID': float(ep_THINnJet),
                    'Nbjets_PassID': float(nBjets),
                    'JetHT': float(JetHT),
                    'Jet1Pt': float(ep_THINjetPt[0]),
                    'Jet1Eta': float(ep_THINjetEta[0]),
                    'Jet1Phi': float(ep_THINjetPhi[0]),
                    'Jet1deepCSV': float(ep_THINjetDeepCSV[0]),
                    'Jet1NHadEF': float(ep_THINjetNHadEF[0]),
                    'Jet1CHadEF': float(ep_THINjetCHadEF[0]),
                    'Jet1CEmEF': float(ep_THINjetCEmEF[0]),
                    'Jet1NEmEF': float(ep_THINjetNEmEF[0]),
                    'Jet1CMulti': float(ep_THINjetCMulti[0]),
                    'Jet1NMultiplicity': float(ep_THINjetNMultiplicity[0]),
                    'Jet2Pt': float(ep_THINjetPt[1]),
                    'Jet2Eta': float(ep_THINjetEta[1]),
                    'Jet2Phi': float(ep_THINjetPhi[1]),
                    'Jet2deepCSV': float(ep_THINjetDeepCSV[1]),
                    'Jet3Pt': float(Jet3Pt),
                    'Jet3Eta': float(Jet3Eta),
                    'Jet3Phi': float(Jet3Phi),
                    'Jet3deepCSV': float(Jet3deepCSV),
                    'M_Jet1Jet2': float(M_Jet1Jet2),
                    'prod_cat': int(prod_cat),
                    'pT_Jet1Jet2': float(pT_Jet1Jet2),
                    'eta_Jet1Jet2': float(eta_Jet1Jet2),
                    'phi_Jet1Jet2': float(phi_Jet1Jet2),
                    'dRJet12': float(dRJet12),
                    'dPhiJet13': float(dPhiJet13),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'ratioPtJet21': float(ep_THINjetPt[1] / ep_THINjetPt[0]),
                    'rJet1PtMET': float(rJet1PtMET),
                    'dPhiJet12': float(DeltaPhi(ep_THINjetPhi[0], ep_THINjetPhi[1])),
                    'dEtaJet12': float(ep_THINjetEta[0] - ep_THINjetEta[1]),
                    'isjet2EtaMatch': float(isjet2EtaMatch),
                    'M_Jet1Jet3': float(M_Jet1Jet3),
                    'weight': float(weight),
                    'weightMETtrig': float(weightMETtrig),
                    'weightEle': float(weightEle),
                    'weightMu': float(weightMu),
                    'weightB': float(weightB),
                    'weightFakeB': float(weightFakeB),
                    'weightEWK': float(weightEWK),
                    'weightQCD': float(weightQCD),
                    'weightTop': float(weightTop),
                    'weightPU': float(weightPU),
                    'weightPrefire': float(weightPrefire),
                    'weightMETtrig_up': float(weightMETtrig_up),
                    'weightEle_up': float(weightEle_up),
                    'weightMu_up': float(weightMu_up),
                    'weightB_up': float(weightB_up),
                    'weightFakeB_up': float(weightFakeB_up),
                    'weightEWK_up': float(weightEWK_up),
                    'weightQCD_up': float(weightQCD_up),
                    'weightTop_up': float(weightTop_up),
                    'weightPU_up': float(weightPU_up),
                    'weightPrefire_up': float(weightPrefire_up),
                    'weightJEC_up': float(weightJEC_up),
                    'MET_Res_up': float(ep_pfMetUncJetResUp),
                    'MET_En_up': float(ep_pfMetUncJetEnUp),
                    'MET_En_down': float(ep_pfMetUncJetEnDown),
                    'MET_Res_down': float(ep_pfMetUncJetResDown),
                    'weightJEC_down': float(weightJEC_down),
                    'weightMETtrig_down': float(weightMETtrig_down),
                    'weightEle_down': float(weightEle_down),
                    'weightMu_down': float(weightMu_down),
                    'weightB_down': float(weightB_down),
                    'weightFakeB_down': float(weightFakeB_down),
                    'weightEWK_down': float(weightEWK_down),
                    'weightQCD_down': float(weightQCD_down),
                    'weightTop_down': float(weightTop_down),
                    'weightPU_down': float(weightPU_down),
                    'weightscale_up': float(weightscale_up),
                    'weightpdf_up': float(weightpdf_up),
                    'weightscale_down': float(weightscale_down),
                    'weightpdf_down': float(weightpdf_down),
                    'weightPrefire_down': float(weightPrefire_down),
                    'weightEleTrig': float(weightEleTrig),
                    'weightEleID': float(weightEleID),
                    'weightEleRECO': float(weightEleRECO),
                    'weightMuTRK': float(weightMuTRK),
                    'weightMuID': float(weightMuID),
                    'weightMuISO': float(weightMuISO),
                    'weightEleTrig_up': float(weightEleTrig_up),
                    'weightEleID_up': float(weightEleID_up),
                    'weightEleRECO_up': float(weightEleRECO_up),
                    'weightMuTRK_up': float(weightMuTRK_up),
                    'weightMuID_up': float(weightMuID_up),
                    'weightMuISO_up': float(weightMuISO_up),
                    'weightEleTrig_down': float(weightEleTrig_down),
                    'weightEleID_down': float(weightEleID_down),
                    'weightEleRECO_down': float(weightEleRECO_down),
                    'weightMuTRK_down': float(weightMuTRK_down),
                    'weightMuID_down': float(weightMuID_down),
                    'weightMuISO_down': float(weightMuISO_down),
                    'weightscale_down': float(weightscale_down),
                    'isak4JetBasedHemEvent': int(ep_isak4JetBasedHemEvent),
                    'ismetphiBasedHemEvent1': int(ep_ismetphiBasedHemEvent1),
                    'ismetphiBasedHemEvent2': int(ep_ismetphiBasedHemEvent2),
                    'weightJECAbsoluteUp': float(JECSourceUp['Absolute']),
                    'weightJECAbsolute_yearUp': float(JECSourceUp['Absolute_year']),
                    'weightJECBBEC1Up': float(JECSourceUp['BBEC1']),
                    'weightJECBBEC1_yearUp': float(JECSourceUp['BBEC1_year']),
                    'weightJECEC2Up': float(JECSourceUp['EC2']),
                    'weightJECEC2_yearUp': float(JECSourceUp['EC2_year']),
                    'weightJECFlavorQCDUp': float(JECSourceUp['FlavorQCD']),
                    'weightJECHFUp': float(JECSourceUp['HF']),
                    'weightJECHF_yearUp': float(JECSourceUp['HF_year']),
                    'weightJECRelativeBalUp': float(JECSourceUp['RelativeBal']),
                    'weightJECRelativeSample_yearUp': float(JECSourceUp['RelativeSample_year']),
                    'weightJECAbsoluteDown': float(JECSourceDown['Absolute']),
                    'weightJECAbsolute_yearDown': float(JECSourceDown['Absolute_year']),
                    'weightJECBBEC1Down': float(JECSourceDown['BBEC1']),
                    'weightJECBBEC1_yearDown': float(JECSourceDown['BBEC1_year']),
                    'weightJECEC2Down': float(JECSourceDown['EC2']),
                    'weightJECEC2_yearDown': float(JECSourceDown['EC2_year']),
                    'weightJECFlavorQCDDown': float(JECSourceDown['FlavorQCD']),
                    'weightJECHFDown': float(JECSourceDown['HF']),
                    'weightJECHF_yearDown': float(JECSourceDown['HF_year']),
                    'weightJECRelativeBalDown': float(JECSourceDown['RelativeBal']),
                    'weightJECRelativeSample_yearDown': float(JECSourceDown['RelativeSample_year']),
                }, ignore_index=True)
            if istest:
                print('isQCDcCR2b')
    outfilenameis = outfilename
    for df in [df_out_preselR, df_out_SR_1b, df_out_SR_2b, df_out_ZeeCR_1b, df_out_ZeeCR_2b, df_out_ZmumuCR_1b, df_out_ZmumuCR_2b, df_out_ZeeCR_2j, df_out_ZeeCR_3j, df_out_ZmumuCR_2j, df_out_ZmumuCR_3j, df_out_WenuCR_1b, df_out_WenuCR_2b, df_out_WmunuCR_1b, df_out_WmunuCR_2b, df_out_TopenuCR_1b, df_out_TopenuCR_2b, df_out_TopmunuCR_1b, df_out_TopmunuCR_2b, df_out_QCDbCR_1b, df_out_QCDbCR_2b, df_out_QCDaCR_1b, df_out_QCDaCR_2b, df_out_QCDcCR_1b, df_out_QCDcCR_2b]:
        if df.empty:
            for col in df.columns:
                df[col] = dummyArr

    df_out_preselR.to_root(outfilenameis, key='bbDM_preselR', mode='w')

    df_out_SR_1b.to_root(outfilenameis, key='bbDM_SR_1b', mode='a')
    df_out_SR_2b.to_root(outfilenameis, key='bbDM_SR_2b', mode='a')

    df_out_ZeeCR_1b.to_root(outfilenameis, key='bbDM_ZeeCR_1b', mode='a')
    df_out_ZeeCR_2b.to_root(outfilenameis, key='bbDM_ZeeCR_2b', mode='a')
    df_out_ZmumuCR_1b.to_root(outfilenameis, key='bbDM_ZmumuCR_1b', mode='a')
    df_out_ZmumuCR_2b.to_root(outfilenameis, key='bbDM_ZmumuCR_2b', mode='a')

    df_out_ZeeCR_2j.to_root(outfilenameis, key='bbDM_ZeeCR_2j', mode='a')
    df_out_ZeeCR_3j.to_root(outfilenameis, key='bbDM_ZeeCR_3j', mode='a')
    df_out_ZmumuCR_2j.to_root(outfilenameis, key='bbDM_ZmumuCR_2j', mode='a')
    df_out_ZmumuCR_3j.to_root(outfilenameis, key='bbDM_ZmumuCR_3j', mode='a')

    df_out_WenuCR_1b.to_root(outfilenameis, key='bbDM_WenuCR_1b', mode='a')
    df_out_WenuCR_2b.to_root(outfilenameis, key='bbDM_WenuCR_2b', mode='a')
    df_out_WmunuCR_1b.to_root(outfilenameis, key='bbDM_WmunuCR_1b', mode='a')
    df_out_WmunuCR_2b.to_root(outfilenameis, key='bbDM_WmunuCR_2b', mode='a')

    df_out_TopenuCR_1b.to_root(outfilenameis, key='bbDM_TopenuCR_1b', mode='a')
    df_out_TopenuCR_2b.to_root(outfilenameis, key='bbDM_TopenuCR_2b', mode='a')
    df_out_TopmunuCR_1b.to_root(outfilenameis, key='bbDM_TopmunuCR_1b', mode='a')
    df_out_TopmunuCR_2b.to_root(outfilenameis, key='bbDM_TopmunuCR_2b', mode='a')

    df_out_QCDbCR_1b.to_root(outfilenameis, key='bbDM_QCDbCR_1b', mode='a')
    df_out_QCDbCR_2b.to_root(outfilenameis, key='bbDM_QCDbCR_2b', mode='a')

    df_out_QCDaCR_1b.to_root(outfilenameis, key='bbDM_QCDaCR_1b', mode='a')
    df_out_QCDaCR_2b.to_root(outfilenameis, key='bbDM_QCDaCR_2b', mode='a')

    df_out_QCDcCR_1b.to_root(outfilenameis, key='bbDM_QCDcCR_1b', mode='a')
    df_out_QCDcCR_2b.to_root(outfilenameis, key='bbDM_QCDcCR_2b', mode='a')

    print('\n============SR cutflow============')
    print('SR1bcount', SR1bcount, 'SR2bcount', SR2bcount)
    print('============SR cutflow============')

    print('\n============Z cutflow============')
    print('ZeeCR1bcount', ZeeCR1bcount, 'ZeeCR2bcount', ZeeCR2bcount)
    print('ZmumuCR1bcount', ZmumuCR1bcount, 'ZmumuCR2bcount', ZmumuCR2bcount)

    print('\n============Z cutflow============')
    print('ZeeCR2jcount', ZeeCR2jcount, 'ZeeCR3jcount', ZeeCR3jcount)
    print('ZmumuCR2jcount', ZmumuCR2jcount, 'ZmumuCR3jcount', ZmumuCR3jcount)

    print('\n============W cutflow============')
    print('WenuCR1bcount', WenuCR1bcount, 'WenuCR2bcount', WenuCR2bcount)
    print('WmunuCR1bcount', WmunuCR1bcount, 'WmunuCR2bcount', WmunuCR2bcount)

    print('\n============Top cutflow============')
    print('TopenuCR1bcount', TopenuCR1bcount, 'TopenuCR2bcount', TopenuCR2bcount)
    print('TopmunuCR1bcount', TopmunuCR1bcount, 'TopmunuCR2bcount', TopmunuCR2bcount)

    print('\n============QCD cutflow============')
    print('QCDbCR1bcount', QCDbCR1bcount, 'QCDbCR2bcount', QCDbCR2bcount)

    print('\n============QCD cutflow============')
    print('QCDcCR1bcount', QCDcCR1bcount, 'QCDcCR2bcount', QCDcCR2bcount)

    print('\n============QCD cutflow============')
    print('QCDaCR1bcount', QCDaCR1bcount, 'QCDaCR2bcount', QCDaCR2bcount)


    cfsr_list = {1: 'presel', 2: 'trigger', 3: 'MET',
                 4: 'nLep', 5: 'min_dPhi', 6: 'nJet', 7: 'nBjets'}
    #cfcr_list = {1:'presel',2:'trigger',3:'MET',4:'nLep',5:'Recoil',6:'min_dPhi',7:'Z/W mass',8:'nJet',9:'nBjets'}
    cfcr_list = {1: 'presel', 2: 'trigger', 3: 'lep_veto', 4: 'tau_veto', 5: 'sel_lep',
                 6: 'sel_lep_Pt_tight', 7: 'Recoil', 8: 'min_dPhi', 9: 'Z/W mass', 10: 'nJet', 11: 'nBjets'}
    for i in [1, 2, 3, 4, 5, 6, 7]:
        h_reg_preselR_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_SR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_SR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDbCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDbCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDcCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDcCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDaCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
        h_reg_QCDaCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfsr_list[i])
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        h_reg_ZeeCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZeeCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZmumuCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZmumuCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZeeCR_2j_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZeeCR_3j_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZmumuCR_2j_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_ZmumuCR_3j_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_WenuCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_WenuCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_WmunuCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_WmunuCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_TopenuCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_TopenuCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_TopmunuCR_1b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
        h_reg_TopmunuCR_2b_cutFlow.GetXaxis().SetBinLabel(i, cfcr_list[i])
    h_reg_preselR_cutFlow.SetEntries(1)
    h_reg_SR_1b_cutFlow.SetEntries(1)
    h_reg_SR_2b_cutFlow.SetEntries(1)
    h_reg_ZeeCR_1b_cutFlow.SetEntries(1)
    h_reg_ZeeCR_2b_cutFlow.SetEntries(1)
    h_reg_ZmumuCR_1b_cutFlow.SetEntries(1)
    h_reg_ZmumuCR_2b_cutFlow.SetEntries(1)
    h_reg_ZeeCR_2j_cutFlow.SetEntries(1)
    h_reg_ZeeCR_3j_cutFlow.SetEntries(1)
    h_reg_ZmumuCR_2j_cutFlow.SetEntries(1)
    h_reg_ZmumuCR_3j_cutFlow.SetEntries(1)
    h_reg_WenuCR_1b_cutFlow.SetEntries(1)
    h_reg_WenuCR_2b_cutFlow.SetEntries(1)
    h_reg_WmunuCR_1b_cutFlow.SetEntries(1)
    h_reg_WmunuCR_2b_cutFlow.SetEntries(1)
    h_reg_TopenuCR_1b_cutFlow.SetEntries(1)
    h_reg_TopenuCR_2b_cutFlow.SetEntries(1)
    h_reg_TopmunuCR_1b_cutFlow.SetEntries(1)
    h_reg_TopmunuCR_2b_cutFlow.SetEntries(1)
    h_reg_QCDbCR_1b_cutFlow.SetEntries(1)
    h_reg_QCDbCR_2b_cutFlow.SetEntries(1)
    h_reg_QCDcCR_1b_cutFlow.SetEntries(1)
    h_reg_QCDcCR_2b_cutFlow.SetEntries(1)
    h_reg_QCDaCR_1b_cutFlow.SetEntries(1)
    h_reg_QCDaCR_2b_cutFlow.SetEntries(1)
    print('===============================\n')
    print("output written to ", outfilename)
    outfile = TFile(outfilenameis, 'UPDATE')
    outfile.cd()
    h_total_mcweight.Write()
    h_total.Write()
    h_eventCounter.Write()
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
    h_reg_QCDbCR_1b_cutFlow.Write()
    h_reg_QCDbCR_2b_cutFlow.Write()
    h_reg_QCDcCR_1b_cutFlow.Write()
    h_reg_QCDcCR_2b_cutFlow.Write()
    h_reg_QCDaCR_1b_cutFlow.Write()
    h_reg_QCDaCR_2b_cutFlow.Write()
    outfile.Write()
    outfile.Close()

    end = time.clock()
    print("%.4gs" % (end-start))


if __name__ == '__main__':
    if (isfarmout or runInteractive) and not isMultiProc:
        runbbdm(infile)
    if isMultiProc and not (isfarmout or runInteractive):
        files  = [f for f in os.listdir(infile) if f.endswith(".root")]
        n = mp.cpu_count()  # submit n txt files at a time, make equal to cores
        final = [files[i * n:(i + 1) * n] for i in range((len(files) + n - 1) // n)]
        if istest:
            runbbdm, final[0]
        else:
            for i in range(len(final)):
                try:
                    pool = mp.Pool(mp.cpu_count())
                    pool.map(runbbdm, final[i])
                    pool.close()
                    pool.join()
                except Exception as e:
                    print(e)
                    print("Corrupt file inside input txt file is detected! Skipping this txt file:  ", final[i])
                    continue
