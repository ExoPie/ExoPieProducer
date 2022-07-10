#!/usr/bin/env python
import os
import sys
import datetime
import sys, optparse
import ROOT
import numpy as np

datestr = str(datetime.date.today().strftime("%d%m%Y"))

#command  python StackPlotter_syst.py  -y <Year>
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)

usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)
parser.add_option("-D", "--pDir", type="string", dest="rootFileDir", help="histogram dir")
parser.add_option("-y", "--year", dest="year", default="Year")
parser.add_option("-v", "--version", type="string",dest="Version", help="version of histograms")
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
  luminosity_ = '{0:.2f}'.format(35.82)
elif runOn2017:
  luminosity_ = '{0:.2f}'.format(41.50)
elif runOn2018:
  luminosity_ = '{0:.2f}'.format(59.64)

if options.Version == None:
  print('Please provide which version of histograms are being plotted')
  sys.exit()
else:
  histVersion = options.Version

if options.rootFileDir == None:
  print('Please provide histogram directory name')
  sys.exit()
else:
    filepath = options.rootFileDir

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
  c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 650, 600)
  c.SetBottomMargin(0.050)
  c.SetRightMargin(0.050)
  c.SetLeftMargin(0.050)
  c.SetTopMargin(0.050)
  # c.SetTicky(1)
  # c.SetGrid(0)
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
  text = pt.AddText(0.07,0.57,"#font[61]{CMS}")

  #pt1 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
  pt1 = ROOT.TPaveText(0.0877181,0.935,0.9580537,0.96,"brNDC")
  pt1.SetBorderSize(0)
  pt1.SetTextAlign(12)
  pt1.SetFillStyle(0)
  pt1.SetTextFont(52)

  pt1.SetTextSize(preliminarytextfize)
  #text1 = pt1.AddText(0.215,0.4,text_)
  text1 = pt1.AddText(0.22,0.4,text_)

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
  h1.SetMarkerColor(ROOT.kBlack)
  h1.SetLineColor(ROOT.kBlack)
  h1.SetLineWidth(2)
  h2.SetMarkerSize(0.7)
  h2.SetMarkerStyle(20)
  h2.SetMarkerColor(ROOT.kRed)
  h2.SetLineColor(ROOT.kRed)
  h2.SetLineWidth(2)
  h3.SetMarkerSize(0.7)
  h3.SetMarkerStyle(20)
  h3.SetMarkerColor(ROOT.kBlue)
  h3.SetLineColor(ROOT.kBlue)
  h3.SetLineWidth(2)
  h1 = SetCMSAxis(h1)

  binmax = np.max([h2.GetBinContent(i) for i in range(1,5)])
  binmin = np.min([h3.GetBinContent(i) for i in range(1, 5)])
  print(h1.GetName(), binmin, binmax)
  print([h2.GetBinContent(i) for i in range(1, 5)])
  print([h3.GetBinContent(i) for i in range(1, 5)])
  if binmax < binmin:
    binmax, binmin = binmin, binmax
  print(h1.GetName(), binmin, binmax)
  if 'JEC' in h1.GetName() or 'trig_met' in h1.GetName():
    if 'JECEC2' in h1.GetName() and 'year' not in h1.GetName():
      h1.SetMinimum(0.999*binmin)
      h1.SetMaximum(1.001*binmax)
    elif 'JECHF' in h1.GetName() and 'year' not in h1.GetName():
      h1.SetMinimum(0.9992*binmin)
      h1.SetMaximum(1.0008*binmax)
    elif 'JECHF_201' in h1.GetName():
      h1.SetMinimum(0.9995*binmin)
      h1.SetMaximum(1.0005*binmax)
    elif 'JECRelativeBal' in h1.GetName():
      if '2018' in options.year:
        h1.SetMinimum(0.95*binmin)
        h1.SetMaximum(1.05*binmax)
      else:
        h1.SetMinimum(0.985*binmin)
        h1.SetMaximum(1.015*binmax)
    elif 'JECRelativeSample_201' in h1.GetName():
      if '2018' in h1.GetName():
        h1.SetMinimum(0.95*binmin)
        h1.SetMaximum(1.05*binmax)
      else:
        h1.SetMinimum(0.985*binmin)
        h1.SetMaximum(1.015*binmax)
    else:
      h1.SetMinimum(0.99*binmin)
      h1.SetMaximum(1.01*binmax)
  else:
    h1.SetMinimum(0.8*binmin)
    h1.SetMaximum(1.2*binmax)

  ##xaxis##
  h1.GetXaxis().SetTitle(titleX)
  h1.GetXaxis().SetTitleSize(0.06)
  h1.GetXaxis().SetTitleOffset(0.8)
  h1.GetXaxis().SetLabelSize(0.05)
  ##yaxis##
  h1.GetYaxis().SetTitle('Systematic Uncertainity')
  h1.GetYaxis().SetTitleSize(0.06)
  h1.GetYaxis().SetTitleOffset(1.4)
  h1.GetYaxis().SetLabelSize(0.05)
  h1.Draw("hist")
  h2.Draw("hist same")
  h3.Draw("hist same")
  # h1.GetYaxis().SetNdivisions(505)
  # h1.GetXaxis().SetNdivisions(505)
  return

ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ForceStyle(1)

regions = ['SR_1b', 'SR_2b', 'ZmumuCR_2j', 'ZmumuCR_3j','TopmunuCR_2b', 'WmunuCR_1b', 'ZeeCR_2j', 'ZeeCR_3j', 'TopenuCR_2b', 'WenuCR_1b']
bkg_process = ['STop', 'Top', 'WJets']
systmatics = ['JECAbsolute', 'JECAbsolute_year', 'JECBBEC1', 'JECBBEC1_year', 'JECEC2', 'JECEC2_year', 'JECFlavorQCD', 'JECHF', 'JECHF_year', 'JECRelativeSample_year', 'JECRelativeBal', 'CMSyear_eff_b', 'CMSyear_fake_b', 'EWK', 'CMSyear_Top', 'CMSyear_trig_met', 'CMSyear_trig_ele', 'CMSyear_EleID', 'CMSyear_EleRECO', 'CMSyear_MuID', 'CMSyear_MuISO', 'CMSyear_MuTRK', 'CMSyear_PU', 'En']

# systmatics = ['JECRelativeSample_year']
for reg in regions:
  if '_1b' in reg or '_2j' in reg:
    if 'SR' in reg:
      limitVar = 'MET'
      titleX = "E_{T}^{miss} (GeV)"
    else:
      limitVar = 'Recoil'
      titleX = "Hadronic Recoil (GeV)"
    minX = 250; maxX =1000
  elif '_2b' in reg or '_3j' in reg:
    limitVar = 'ctsValue'
    titleX = "cos(#theta)*"
    minX = 0; maxX =1
  histC_file = ROOT.TFile(filepath+'/h_reg_'+reg+'_'+limitVar+'.root','r')
  for proc_ in bkg_process:
    histC = histC_file.Get(proc_)
    for syst_ in systmatics:
      if ('CMSyear_Ele' in syst_ or 'CMSyear_Mu' in syst_ or 'CMSyear_trig_ele' in syst_) and ('SR' in reg):
        continue
      histU_file = ROOT.TFile(filepath+'/h_reg_'+reg+'_'+limitVar+'_'+syst_+'Up.root','r')
      histD_file = ROOT.TFile(filepath+'/h_reg_'+reg+'_'+limitVar+'_'+syst_+'Down.root','r')
      histU = histU_file.Get(proc_)
      histD = histD_file.Get(proc_)

      ratioU = histU.Clone()
      ratioD = histD.Clone()
      ratioC = histC.Clone()

      ratioU.SetName(syst_.replace('year',options.year)+'Up_'+reg+'_'+limitVar+'_'+proc_)
      ratioD.SetName(syst_.replace('year',options.year)+'Down_'+reg+'_'+limitVar+'_'+proc_)
      ratioC.SetName(syst_.replace('year',options.year)+'Central_'+reg+'_'+limitVar+'_'+proc_)

      ratioU.Divide(ratioC)
      ratioD.Divide(ratioC)
      ratioC.Divide(ratioC)
      titleY = "#Events"
      # Set Canvas
      c1 = myCanvas1D()
      c1_1 =  ROOT.TPad("c1_1","newpad",0,0,1,1)
      c1_1.SetBottomMargin(0.12)
      c1_1.SetTopMargin(0.08)
      c1_1.SetLeftMargin(0.16)
      c1_1.SetRightMargin(0.06)
      c1_1.SetLogy(0)
      # c1_1.SetGrid(0)
      c1_1.Draw()
      c1_1.cd()
      CustomiseRatio(ratioC, ratioU, ratioD, titleX)
      leg  = SetLegend([0.7, 0.75, 0.98, 0.9],ncol=1)
      leg.AddEntry(ratioU, 'Up' , 'l')
      leg.AddEntry(ratioC, 'Central' , 'l')
      leg.AddEntry(ratioD, 'Down' , 'l')

      leg.Draw("same")

      #texcms.Draw("same")
      #texCat.Draw("same")
      latex1 = ROOT.TLatex()
      latex1.SetNDC()
      latex1.SetTextSize(0.04)
      latex1.SetTextAlign(31)
      latex1.SetTextAlign(11)
      lup = str(syst_).replace('year', options.year)
      ldown = str(proc_+'_'+reg)
      latex1.DrawLatex(0.30, .85, '#splitline{'+lup+'}{'+ldown+'}')

      pt = drawenergy1D(True, text_="Internal", data=True)
      for ipt in pt:
          ipt.Draw()

      c1.Update()
      c1.Draw()

      if not os.path.exists('outPlotDir/'+histVersion+'/bbDMPng/'+reg):
        os.makedirs('outPlotDir/'+histVersion+'/bbDMPng/'+reg)
      if not os.path.exists('outPlotDir/'+histVersion+'/bbDMPdf/'+reg):
        os.makedirs('outPlotDir/'+histVersion+'/bbDMPdf/'+reg)


      c1.SaveAs('outPlotDir/'+histVersion+'/bbDMPng/'+reg+'/'+syst_+'_'+reg+'_'+limitVar+'_'+proc_+'.png')
      c1.SaveAs('outPlotDir/'+histVersion+'/bbDMPdf/'+reg+'/'+syst_+'_'+reg+'_'+limitVar+'_'+proc_+'.pdf')
      histU_file.Close()
      histD_file.Close()
      c1.Close()
  histC_file.Close()
