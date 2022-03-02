#!/usr/bin/env python
import os
import sys
import datetime
import sys, optparse
import ROOT as ROOT
import array
import string

from numpy import NaN

datestr = str(datetime.date.today().strftime("%d%m%Y"))

#command  python StackPlotter_syst.py  -y <Year>
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)

usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)
parser.add_option("-y", "--year", dest="year", default="Year")
(options, args) = parser.parse_args()
runOn2016 = False
runOn2017 = False
runOn2018 = False
if options.year == '2016':
    runOn2016 = True
elif options.year == '2017':
    runOn2017 = True
elif options.year == '2018':
    runOn2018 = True
else:
    print('Please provide on which year you want to run?')

if runOn2016:
    luminosity_ = '{0:.2f}'.format(35.81)
elif runOn2017:
    luminosity_ = '{0:.2f}'.format(41.50)
elif runOn2018:
    luminosity_ = '{0:.2f}'.format(59.64)

def SetCMSAxis(h, xoffset=1., yoffset=1.):
    h.GetXaxis().SetTitleSize(0.047)
    h.GetYaxis().SetTitleSize(0.047)

    print (type(h))
    if type(h) is ( (not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):  h.GetZaxis().SetTitleSize(0.047)

    h.GetXaxis().SetLabelSize(0.047)
    h.GetYaxis().SetLabelSize(0.047)
    if type(h) is ( (not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)): h.GetZaxis().SetLabelSize(0.047)

    h.GetXaxis().SetTitleOffset(xoffset)
    h.GetYaxis().SetTitleOffset(yoffset)
    return h

def ExtraText(text_,x_, y_):
    if not text_: print ("nothing provided as text to ExtraText, function crashing")
    ltx = ROOT.TLatex(x_,y_,text_)

    if len(text_)>0:
        ltx.SetTextFont(42)
        ltx.SetTextSize(0.049)
        #ltx.Draw(x_,y_,text_)
        ltx.Draw('same')
    return ltx

def myCanvas1D():
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 750, 600)
    c.SetBottomMargin(0.050)
    c.SetRightMargin(0.050)
    c.SetLeftMargin(0.050)
    c.SetTopMargin(0.050)
    c.SetTicky(1)
    c.SetGrid(1)
    return c

def SetLegend(coordinate_=[.50,.65,.90,.90],ncol=2):
    c_=coordinate_
    legend=ROOT.TLegend(c_[0], c_[1],c_[2],c_[3])
    legend.SetBorderSize(0)
    legend.SetNColumns(ncol)
    legend.SetLineColor(1)
    legend.SetLineStyle(1)
    legend.SetLineWidth(1)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetTextFont(62)
    legend.SetTextSize(0.055)
    return legend

def drawenergy1D(is2017, text_="Work in progress 2018", data=True):
    #pt = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt = ROOT.TPaveText(0.0877181,0.935,0.9580537,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)
    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize *0.7
    pt.SetTextSize(cmstextSize)
    text = pt.AddText(0.03,0.57,"#font[61]{CMS}")

    #pt1 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1 = ROOT.TPaveText(0.0877181,0.935,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.215,0.4,text_)
    text1 = pt1.AddText(0.17,0.4,text_)

    #pt2 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2 = ROOT.TPaveText(0.0877181,0.935,0.9580537,0.96,"brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)

    pavetext = ''
    if is2017 and data: pavetext = str(luminosity_)+' fb^{-1}'+" (13 TeV)"
    if (not is2017) and data: pavetext = str(luminosity_)+' fb^{-1}'+"(13 TeV)"

    if is2017 and not data: pavetext = "13 TeV"
    if (not is2017) and not data: pavetext = "13 TeV"

    if data: text3 = pt2.AddText(0.61,0.5,pavetext)
    if not data: text3 = pt2.AddText(0.61,0.5,pavetext)

    return [pt,pt1,pt2]


def CustomiseHistogram(h, titleX, titleY, color, lineStyle,title):
    h.SetMarkerColor(color)
    h.SetMarkerSize(1.0)
    h.SetLineColor(color)
    h.SetLineWidth(2)
    h.SetLineStyle(lineStyle)
    h = SetCMSAxis(h)
    h.GetYaxis().SetTitle(titleY)
    h.GetYaxis().SetTitleSize(0.06)
    h.GetYaxis().SetLabelSize(0.055)
    h.SetMaximum(h.GetMaximum()*10)
    # h.SetMinimum(1)
    h.SetTitle(title)
    return

def CustomiseRatio(h1,h2,h3,titleX):
    h1.SetMarkerSize(0.7)
    h1.SetMarkerStyle(20)
    h1.SetMarkerColor(ROOT.kRed)
    h1.SetLineColor(ROOT.kRed)
    h2.SetMarkerSize(0.7)
    h2.SetMarkerStyle(20)
    h2.SetMarkerColor(ROOT.kBlue)
    h2.SetLineColor(ROOT.kBlue)
    h3.SetMarkerSize(0.7)
    h3.SetMarkerStyle(20)
    h3.SetMarkerColor(ROOT.kBlack)
    h3.SetLineColor(ROOT.kBlack)
    h1 = SetCMSAxis(h1)
    for i in range(1,h3.GetNbinsX()+1):
        if h3.GetBinContent(i)==0.0:
            h3.SetBinContent(i,1.0)
            h1.SetBinContent(i,1.0)
            h2.SetBinContent(i,1.0)
    # h1.Draw("hist")
    # h2.Draw("hist same")
    # h3.Draw("hist same")
    # h1.SetMinimum(h1.Integral()/10)
    # h1.SetMaximum(h2.Integral()/10)

    print('min',h2.GetMinimum())
    print('max',h1.GetMaximum())

    min_bin = min([abs(h2.GetBinContent(i)) for i in  range(1,h2.GetNbinsX()+1)])
    max_bin = max([abs(h1.GetBinContent(i)) for i in  range(1,h1.GetNbinsX()+1)])
    # h1.SetMinimum(min_bin*1)
    # h1.SetMaximum(max_bin*1.1)
    h1.GetYaxis().SetRangeUser(min_bin/1.1,max_bin*1.1)

    # h1.SetMinimum(0.1)
    # h1.SetMaximum(1.9)
    ##xaxis##
    h1.GetXaxis().SetTitle(titleX)
    h1.GetXaxis().SetTitleSize(0.06)
    h1.GetXaxis().SetTitleOffset(0.8)
    h1.GetXaxis().SetLabelSize(0.05)
    ##yaxis##
    h1.GetYaxis().SetTitle('Systematic Uncertainity')
    h1.GetYaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitleOffset(0.8)
    h1.GetYaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetNdivisions(505)
    h1.Draw("hist")
    h2.Draw("hist same")
    h3.Draw("hist same")
    return

ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ForceStyle(1)
#ROOT.gStyle.SetGridStyle(2)

version = 'v16_12-02-01_cl68pdf'

uncertfile = open(version+".txt", "w")
uncertfile_binwise = open(version+".py", "w")
uncertfile_binwise.write("syst_dict = {")
CRSRPath = '/Users/ptiwari/cmsCERN/Documents/ExoPieCapper/plots_norm/'+version+'/bbDMRoot'
regions = ['SR_1b', 'SR_2b', 'ZmumuCR_2j', 'ZmumuCR_3j','TopmunuCR_2b', 'WmunuCR_1b', 'ZeeCR_2j', 'ZeeCR_3j', 'TopenuCR_2b', 'WenuCR_1b']

# regions = ['SR_2b', 'ZmumuCR_3j','TopmunuCR_2b', 'ZeeCR_3j', 'TopenuCR_2b']

bkg_dict = {'SR_1b':['ZJets','WJets','Top'], 'SR_2b':['ZJets','WJets','Top'], 'ZmumuCR_2j':['DYJets'], 'ZmumuCR_3j':['DYJets'],'TopmunuCR_2b':['Top'], 'WmunuCR_1b':['WJets'], 'ZeeCR_2j':['DYJets'], 'ZeeCR_3j':['DYJets'], 'TopenuCR_2b':['Top'], 'WenuCR_1b':['WJets']}
# regions = ['SR_1b', 'SR_2b']
backgrounds =['DIBOSON', 'ZJets', 'GJets', 'QCD', 'SMH', 'STop', 'Top', 'WJets', 'DYJets']

# backgrounds =['ZJets', 'SMH', 'STop', 'Top', 'WJets', 'DYJets']

# backgrounds =['STop', 'Top', 'WJets',]
systematics = ['CMSyear_eff_b', 'CMSyear_fake_b', 'CMSyear_trig_met', 'CMSyear_trig_ele', 'CMSyear_EleID', 'CMSyear_EleRECO', 'CMSyear_MuID', 'CMSyear_MuISO', 'CMSyear_MuTRK', 'CMSyear_PU', 'CMSyear_mu_scale', 'CMSyear_pdf', 'JECAbsolute', 'JECAbsolute_year', 'JECBBEC1', 'JECBBEC1_year', 'JECEC2', 'JECEC2_year', 'JECFlavorQCD', 'JECHF', 'JECHF_year', 'JECRelativeBal', 'JECRelativeSample_year', 'En']

# systematics = ['CMSyear_EleID']
# systematics = ['CMSyear_eff_b']

# backgrounds = ['STop']
# systematics = ['CMSyear_PU']

for jetprop in systematics:
    for process in backgrounds:
        for reg in regions:
        #   if process in bkg_dict[reg]: continue
          if 'e' in reg and 'CMSyear_Mu' in jetprop: continue
          if ('mu' in reg or 'SR' in reg) and ('CMSyear_Ele' in jetprop or 'CMSyear_trig_ele' in jetprop): continue
          if '_1b' in reg or '_2j' in reg:
            if 'SR' in reg:
              miss_En = 'MET'
              titleX = "E_{T}^{miss} (GeV)"
              if 'CMSyear_Ele' in jetprop or 'CMSyear_Mu' in jetprop or 'CMSyear_trig_ele' in jetprop: continue
              minX = 250; maxX =1000
            # elif 'CMSyear_EleID' in jetprop:
            #     miss_En = 'lep1_pT'
            #     titleX = "lepton1 p_{T}"
            #     minX = 30; maxX =500
            else:
                miss_En = 'Recoil'
                titleX = "Hadronic Recoil (GeV)"
                minX = 250; maxX =1000
          elif '_2b' in reg or '_3j' in reg:
            # if 'CMSyear_EleID' in jetprop:
            #     miss_En = 'lep1_pT'
            #     titleX = "lepton1 p_{T}"
            #     minX = 30; maxX =500
            # else:
            miss_En = 'ctsValue'
            titleX = "cos(#theta)*"
            minX = 0; maxX =1
            if ('SR' in reg) and ('CMSyear_Ele' in jetprop or 'CMSyear_Mu' in jetprop or 'CMSyear_trig_ele' in jetprop): continue
          #try:
          for syst in ['Up','Down']:
              exec("systematics_"+reg+"_"+miss_En+"_"+jetprop+syst+"_file = ROOT.TFile('"+CRSRPath+"/h_reg_"+reg+"_"+miss_En+"_"+jetprop+syst+".root')")
              exec(jetprop+"_"+reg+"_"+miss_En+syst+" = systematics_" +
                    reg+"_"+miss_En+"_"+jetprop+syst+"_file.Get('"+process+"')")

          exec("central_"+reg+"_"+jetprop+"_file = ROOT.TFile('"+CRSRPath+"/h_reg_"+reg+"_"+miss_En+".root')")
          exec(jetprop+"_"+reg+"_"+miss_En+"_central = central_" +
                reg+"_"+jetprop+"_file.Get('"+process+"')")
          colors = {
                  "up"     : ROOT.kRed,
                  "down"     : ROOT.kBlue,
                  "central" : ROOT.kBlack,
                  }
          titleY = "#Events"
          # Set Canvas
          c1 = myCanvas1D()
          c1_1 =  ROOT.TPad("c1_1","newpad",0,0,1,1)
          c1_1.SetBottomMargin(0.12)
          c1_1.SetTopMargin(0.08)
          c1_1.SetLeftMargin(0.12)
          c1_1.SetRightMargin(0.06)
          c1_1.SetLogy(0)
          c1_1.SetGrid(1)
          c1_1.Draw()
          c1_1.cd()
          exec("CustomiseHistogram("+jetprop+"_"+reg+"_"+miss_En+"Up, titleX, titleY, colors['up'], 1,'Up')")
          exec("CustomiseHistogram("+jetprop+"_"+reg+"_"+miss_En+"Down, titleX, titleY, colors['down'], 1,'Down')")
          exec("CustomiseHistogram("+jetprop+"_"+reg+"_"+miss_En+"_central, titleX, titleY, colors['central'], 1,'Central')")

          exec("upUnc = "+jetprop+"_"+reg+"_"+miss_En+"Up.Integral()")
          exec("downUnc = "+jetprop+"_"+reg+"_"+miss_En+"Down.Integral()")
          exec("centralUnc = "+jetprop+"_"+reg+"_"+miss_En+"_central.Integral()")

          uncertfile.write(jetprop+"_"+reg+"_"+miss_En+": ")
        #   if centralUnc<=0: centralUnc =1
          if centralUnc==0: continue
          uncertfile.write(str((max(abs(upUnc-centralUnc),abs(centralUnc-downUnc))/centralUnc)*100)+"\n")
          uncertfile_binwise.write("\'"+jetprop+"_"+reg+"_"+miss_En+"\':[")
          for i in [1,2,3,4]:
              exec("upUnc = "+jetprop+"_"+reg+"_"+miss_En+"Up.GetBinContent("+str(i)+")")
              exec("downUnc = "+jetprop+"_"+reg+"_"+miss_En+"Down.GetBinContent("+str(i)+")")
              exec("centralUnc = "+jetprop+"_" +reg+"_"+miss_En+"_central.GetBinContent("+str(i)+")")
              if centralUnc<=0: centralUnc =1
              uncertfile_binwise.write(str((max(abs(upUnc-centralUnc), abs(centralUnc-downUnc))/centralUnc)*1)+",")
          uncertfile_binwise.write('],\n')

          exec(jetprop+"_"+reg+"_"+miss_En+"Up.GetXaxis().SetRangeUser("+str(minX)+","+str(maxX)+")")
          exec(jetprop+"_"+reg+"_"+miss_En+"Down.GetXaxis().SetRangeUser("+str(minX)+","+str(maxX)+")")
          exec(jetprop+"_"+reg+"_"+miss_En+"_central.GetXaxis().SetRangeUser("+str(minX)+","+str(maxX)+")")
        #   print("ratioUp = "+jetprop+"_"+reg+"_"+miss_En+"Up.Clone()")
        #   print("ratioDown = "+jetprop+"_"+reg+"_"+miss_En+"Down.Clone()")
        #   print("ratioCentral = "+jetprop+"_"+reg+"_"+miss_En+"_central.Clone()")

          exec("ratioUp = "+jetprop+"_"+reg+"_"+miss_En+"Up.Clone()")
          exec("ratioDown = "+jetprop+"_"+reg+"_"+miss_En+"Down.Clone()")
          exec("ratioCentral = "+jetprop+"_"+reg+"_"+miss_En+"_central.Clone()")
          binUpCont = []
          binDownCont = []
          binCentralCont = []
          for i in range(1, 5):
              binUpCont.append(ratioUp.GetBinContent(i))
              binDownCont.append(ratioDown.GetBinContent(i))
              binCentralCont.append(ratioCentral.GetBinContent(i))
          print('binUpCont', binUpCont)
          print('binDownCont', binDownCont)
          print('\n')
          print('binCentralCont',binCentralCont)

          exec("ratioUp.Divide("+jetprop+"_"+reg+"_"+miss_En+"_central)")
          exec("ratioDown.Divide("+jetprop+"_"+reg+"_"+miss_En+"_central)")
          exec("ratioCentral.Divide("+jetprop+"_"+reg+"_"+miss_En+"_central)")
          print('\n')
          binUpCont = []
          binDownCont = []
          for i in range(1,5):
              binUpCont.append(ratioUp.GetBinContent(i))
              binDownCont.append(ratioDown.GetBinContent(i))
          print('binUpCont', binUpCont)
          print('binDownCont', binDownCont)
          exec("CustomiseRatio(ratioUp,ratioDown,ratioCentral, titleX)")

          leg  = SetLegend([0.7, 0.75, 0.98, 0.9],ncol=1)
          exec("leg.AddEntry("+jetprop+"_"+reg+"_"+miss_En+"Up, 'Up' , 'l')")
          exec("leg.AddEntry("+jetprop+"_"+reg+"_"+miss_En+"_central, 'Central' , 'l')")
          exec("leg.AddEntry("+jetprop+"_"+reg+"_"+miss_En+"Down, 'Down' , 'l')")
          leg.Draw("same")

          #texcms.Draw("same")
          #texCat.Draw("same")
          latex1 = ROOT.TLatex()
          latex1.SetNDC()
          latex1.SetTextSize(0.04)
          latex1.SetTextAlign(31)
          latex1.SetTextAlign(11)
          latex1.DrawLatex(0.15, .80, str(jetprop+'_'+process+'_'+reg).replace('year', options.year))

          pt = drawenergy1D(True, text_="Internal", data=True)
          for ipt in pt:
              ipt.Draw()

          c1.Update()
          c1.Draw()
          if not os.path.exists('outPlotDir/'+version+'/bbDMPng/'+reg):
              os.makedirs('outPlotDir/'+version+'/bbDMPng/'+reg)
          if not os.path.exists('outPlotDir/'+version+'/bbDMPdf/'+reg):
              os.makedirs('outPlotDir/'+version+'/bbDMPdf/'+reg)

          exec("c1.SaveAs('outPlotDir/"+version+"/bbDMPdf/"+reg+"/"+jetprop+"_"+reg+"_"+miss_En+"_"+process+".pdf')")
          exec("c1.SaveAs('outPlotDir/"+version+"/bbDMPng/" +reg+"/"+jetprop+"_"+reg+"_"+miss_En+"_"+process+".png')")
          c1.Close()
          exec("central_"+reg+"_"+jetprop+"_file.Close()")
          exec("systematics_"+reg+"_"+miss_En+"_"+jetprop+"Up_file.Close()")
          exec("systematics_"+reg+"_"+miss_En+"_"+jetprop+"Down_file.Close()")
uncertfile_binwise.write('}')
