# In this at the end of filevector I am putting the dirname
# so loop over n-1 files and n will give the name of the output dir.

# In legend also the n element will give the name for the ratio plot y axis label.
#edited by Monika Mittal
#Script for ratio plot
import sys

import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv.append( '-b-' )


from ROOT import TFile, TH1F, gDirectory, TCanvas, TPad, TProfile,TGraph, TGraphAsymmErrors
from ROOT import TH1D, TH1, TH1I
from ROOT import gStyle
from ROOT import gROOT
from ROOT import TStyle
from ROOT import TLegend
from ROOT import TMath
from ROOT import TPaveText
from ROOT import TLatex

import os
colors=[1,2,4,5,8,9,11,41,46,30,12,28,20,32,1,2,4,5,8,9,11,41,46,30,12,28,20,32]
markerStyle=[23,21,22,20,24,25,26,27,28,29,20,21,22,23,23,21,22,20,24,25,26,27,28,29,20,21,22,23]
linestyle=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]


def DrawOverlap(fileVec, histVec, titleVec, legendtext, pngname, outputdirname, logstatus=[0, 0], xRange=[-99999, 99999, 1],):

    gStyle.SetOptTitle(0)
    gStyle.SetOptStat(0)
    gStyle.SetTitleOffset(1.1,"Y");
    #gStyle.SetTitleOffset(1.9,"X");
    gStyle.SetLineWidth(3)
    gStyle.SetFrameLineWidth(3);

    i=0

    histList_=[]
    histList=[]
    histList1=[]
    maximum=[]

    ## Legend
    leg = TLegend(0.4, 0.70, 0.89, 0.89)#,NULL,"brNDC");
    leg.SetBorderSize(0)
    leg.SetNColumns(1)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.03)

    c = TCanvas("c1", "c1",0,0,500,500)
    c.SetBottomMargin(0.15)
    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.02)
    c.SetLogy(logstatus[1])
    c.SetLogx(logstatus[0])
    print ("you have provided "+str(len(fileVec))+" files and "+str(len(histVec))+" histograms to make a overlapping plot" )
    print ("opening rootfiles")
    c.cd()

    ii=0
    inputfile={}
    print (str(fileVec[(len(fileVec)-1)]))

    for ifile_ in range(len(fileVec)):
        print ("opening file  "+fileVec[ifile_])
        inputfile[ifile_] = TFile( fileVec[ifile_] )
        print( "fetching histograms")
        for ihisto_ in range(len(histVec)):
            print ("printing histo "+str(histVec[ihisto_]))
            histo = inputfile[ifile_].Get(histVec[ihisto_])
            histo_total_weight = inputfile[ifile_].Get('h_total_mcweight')
            histo.Rebin(30)
            # histo.Scale(1/histo.Integral())
            histo.Scale(1/histo_total_weight.Integral())
            #status_ = type(histo) is TGraphAsymmErrors
            histList.append(histo)
            # for ratio plot as they should nt be normalize
            histList1.append(histo)
            #print histList[ii].Integral()
            #histList[ii].Rebin(xRange[2])
            #histList[ii].Scale(1.0/histList[ii].Integral())
            maximum.append(histList[ii].GetMaximum())
            maximum.sort()
            ii=ii+1

    print( histList)
    for ih in range(len(histList)):
        tt = type(histList[ih])
        # if logstatus[1] == 1 :
        #     histList[ih].SetMaximum(1.0) #1.4 for log
        #     # histList[ih].SetMinimum(0.001) #1.4 for log
        # if logstatus[1] == 0 :
        #     histList[ih].SetMaximum(0.4) #1.4 for log
        #     histList[ih].SetMinimum(0.001) #1.4 for log
        # # print "graph_status =" ,(tt is TGraphAsymmErrors)
        # # print "hist status =", (tt is TH1D) or (tt is TH1F)
        if ih == 0 :
            if tt is TGraphAsymmErrors :
                histList[ih].Draw("APL")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("hist")
        if ih > 0 :
            #histList[ih].SetLineWidth(2)
            if tt is TGraphAsymmErrors :
                histList[ih].Draw("PL same")
            if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
                histList[ih].Draw("hist same")

        if tt is TGraphAsymmErrors :
            histList[ih].SetMaximum(100)
            histList[ih].SetMarkerColor(colors[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetLineWidth(2)
            histList[ih].SetMarkerStyle(markerStyle[ih])
            histList[ih].SetMarkerSize(1)
            leg.AddEntry(histList[ih],legendtext[ih],"PL")
        if (tt is TH1D) or (tt is TH1F) or (tt is TH1) or (tt is TH1I) :
            histList[ih].SetLineStyle(linestyle[ih])
            histList[ih].SetLineColor(colors[ih])
            histList[ih].SetLineWidth(3)
            leg.AddEntry(histList[ih],legendtext[ih],"L")
        histList[ih].GetYaxis().SetTitle(titleVec[1])
        histList[ih].GetYaxis().SetTitleSize(0.052)
        histList[ih].GetYaxis().SetTitleOffset(1.1)
        histList[ih].GetYaxis().SetTitleFont(42)
        histList[ih].GetYaxis().SetLabelFont(42)
        histList[ih].GetYaxis().SetLabelSize(.052)
        histList[ih].GetXaxis().SetRangeUser(xRange[0],xRange[1])
        #     histList[ih].GetXaxis().SetLabelSize(0.0000);

        histList[ih].GetXaxis().SetTitle(titleVec[0])
        histList[ih].GetXaxis().SetLabelSize(0.052)
        histList[ih].GetXaxis().SetTitleSize(0.052)
        #histList[ih].GetXaxis().SetTitleOffset(1.14)
        histList[ih].GetXaxis().SetTitleFont(42)

        histList[ih].GetXaxis().SetLabelFont(42)
        histList[ih].GetYaxis().SetLabelFont(42)
        histList[ih].GetXaxis().SetNdivisions(507)
        #histList[ih].GetXaxis().SetMoreLogLabels();
        #histList[ih].GetXaxis().SetNoExponent();
        #histList[ih].GetTGaxis().SetMaxDigits(3);

        i=i+1
    pt = TPaveText(0.01,0.92,0.95,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(42)
    pt.SetTextSize(0.046)
    text = pt.AddText(0.12,0.35,"CMS Internal                     41.5 fb^{-1} (2017) ")
    #text = pt.AddText(0.6,0.5,"41.5 fb^{-1} (2017) ")
    pt.Draw()

    leg.Draw()
    if not os.path.exists(outputdirname):
        os.makedirs(outputdirname)
    histname=outputdirname+'/'+pngname
    c.SaveAs(histname+'.png')
    c.SaveAs(histname+'.pdf')
    c.Close()


print ("calling the plotter")
dir_pref = '/Users/ptiwari/cernBox/Documents/ExoPieCapper/inputDirs/'
files = []
legend = []
mA_list = [600]
# ma_list = [10, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 700, 750, 1000]
ma_list = [500]
for mA_ in mA_list:
    for ma_ in ma_list:
        if ma_ < mA_:
          files.append(
              dir_pref+'df_output_v17_12-00-03_genMCwgt/bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_'+str(ma_)+'_mA_'+str(mA_)+'.root')
          files.append(dir_pref+'df_out_v16_12-00-03_genMCwgt/bbDM_2HDMa_LO_5f_Ma'+str(ma_)+
                       '_MChi1_MA'+str(mA_)+'_tanb35_sint_0p7_MH_600_MHC_600_TuneCP3_13TeV-madgraph-pythia8.root')
          legend.append('ma'+str(ma_)+'_2017')
          legend.append('ma'+str(ma_)+'_2016')

# # files = [dir_pref+'df_output_v17_12-00-03_1bMET_2bCTS/bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_10_mA_600.root',
# #          dir_pref+'df_output_v17_12-00-03_1bMET_2bCTS/bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_10_mchi_1.root']

# files = [dir_pref+'df_output_v17_12-00-03_genMCwgt/bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_10_mA_600.root',
#          dir_pref+'df_output_v17_12-00-03_genMCwgt/bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_10_mchi_1.root']

# legend = ['ma10_2HDM+a_2017', 'ma10_DMSimp_2017' ]

# histoname_list = ['h_reg_SR_1b_MET', 'h_reg_SR_2b_MET']


histoname_list = ['h_reg_SR_1b_MET', 'h_reg_SR_2b_ctsValue']

# histoname_list = ['h_reg_SR_1b_MET']

# histoname = 'h_reg_SR_1b_MET'
# histoname = 'h_reg_SR_2b_ctsValue'

for histoname in histoname_list:
    if '1b' in histoname:
        xtitle = 'p_{T}^{miss} GeV'
        # filename = '1bMET_Comp_eff_DMSIMP2017'
        filename = '1bMET_Comp_eff_2HDMa_16_17'
        xaxisrange = [250, 600]
    elif '2b' in histoname:
        xtitle = 'cos(#theta)*'
        # filename = '2bCTSComp_norm'
        xaxisrange = [0, 1]
        # xtitle = 'p_{T}^{miss} GeV'
        # filename = '2bMET_Comp_eff_DMSIMP2017'
        filename = '2bCTS_Comp_eff_2HDMa_16_17'
        # xaxisrange = [250, 600]
    ytitle = ''
    print(histoname)
    DrawOverlap(files, [histoname], [xtitle, ytitle], legend, filename, 'signalComp', [0, 0], xaxisrange)

