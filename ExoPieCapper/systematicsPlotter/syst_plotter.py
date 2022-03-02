#!/usr/bin/env python
import os
import sys
import datetime
import sys, optparse
import ROOT as ROOT
import array
import string

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
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 650, 600)
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
    legend.SetTextFont(42)
    legend.SetTextSize(0.020)
    return legend

def drawenergy1D(is2017, text_="Work in progress 2018", data=True):
    #pt = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt = ROOT.TPaveText(0.0877181,0.95,0.9580537,0.96,"brNDC")
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
    pt1 = ROOT.TPaveText(0.0877181,0.95,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.215,0.4,text_)
    text1 = pt1.AddText(0.15,0.4,text_)

    #pt2 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2 = ROOT.TPaveText(0.0877181,0.95,0.9580537,0.96,"brNDC")
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

    if data: text3 = pt2.AddText(0.68,0.5,pavetext)
    if not data: text3 = pt2.AddText(0.68,0.5,pavetext)

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
    h1.Draw("P e1")
    h2.Draw("P e1 same")
    h3.Draw("P e1 same")
    h1.SetMinimum(0.849)
    h1.SetMaximum(1.159)
    h1.GetXaxis().SetTitle(titleX)
    h1.GetXaxis().SetTitleSize(0.16)
    h1.GetXaxis().SetLabelSize(0.14)
    h1.GetYaxis().SetTitle()
    h1.GetYaxis().SetLabelSize(0.12)
    h1.GetYaxis().SetNdivisions(505)
    return

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetFrameLineWidth(3)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gROOT.ForceStyle(1)
ROOT.gStyle.SetImageScaling(3.)
#ROOT.gStyle.SetGridStyle(2)
uncertfile = open("outTextDir/v17_12-00-02.txt", "w")
CRSRPath = '/Users/ptiwari/cernBox/Documents/ExoPieCapper/plots_norm/v17_12-00-04/bbDMRoot/'

systs_= ['CMSyear_eff_b', 'CMSyear_fake_b', 'EWK', 'CMSyear_Top', 'CMSyear_trig_met', 'CMSyear_trig_ele', 'CMSyear_EleID', 'CMSyear_EleRECO', 'CMSyear_MuID', 'CMSyear_MuISO', 'CMSyear_MuTRK', 'CMSyear_PU', 'En', 'CMSyear_mu_scale', 'CMSyear_pdf', 'CMSyear_prefire', 'JECAbsolute', 'JECAbsolute_year', 'JECBBEC1', 'JECBBEC1_year', 'JECEC2', 'JECEC2_year', 'JECFlavorQCD', 'JECHF', 'JECHF_year', 'JECRelativeBal', 'JECRelativeSample_year']
# regions = ['SR_1b','ZmumuCR_1b','TopmunuCR_1b','WmunuCR_1b','ZeeCR_1b','TopenuCR_1b','WenuCR_1b']
regions = ['SR_2b','ZmumuCR_3j','TopmunuCR_2b','WmunuCR_2b','ZeeCR_3j','TopenuCR_2b','WenuCR_2b']

syst_up = {}
syst_central = {}
syst_down = {}

for syst in systs_:
    reg_up = {}
    reg_down = {}
    reg_central = {}
    file_up = {}
    file_down = {}
    file_central = {}
    colors_up = {}
    colors_down = {}
    i = 0
    for reg in regions:
        if '_1b' in reg or '_2j' in reg:
            if 'SR' in reg:
                miss_En = '_MET'
                titleX = "E_{T}^{miss} (GeV)"
            else:
                miss_En = '_Recoil'
                titleX = "Hadronic Recoil (GeV)"
        elif '_2b' in reg or '_3j' in reg:
            miss_En = '_ctsValue'
            titleX = "cos(#theta)*"

        file_up.update({reg: ROOT.TFile(CRSRPath+'h_reg_'+reg+miss_En+'_'+syst+'Up.root')})
        file_central.update({reg:ROOT.TFile(CRSRPath+'h_reg_'+reg+miss_En+'.root')})
        file_down.update({reg:ROOT.TFile(CRSRPath+'h_reg_'+reg+miss_En+'_'+syst+'Down.root')})
        reg_up.update({reg: file_up[reg].Get('bkgSum')})
        reg_central.update({reg: file_central[reg].Get('bkgSum')})
        reg_down.update({reg: file_down[reg].Get('bkgSum')})
        colors_up.update({reg: ROOT.kRed + i})
        colors_down.update({reg:ROOT.kBlue+ i})
        i+=1
    # Set Canvas
    titleY = " "
    c1 = myCanvas1D()
    c1.SetBottomMargin(0.10)
    c1.SetTopMargin(0.08)
    c1.SetLeftMargin(0.12)
    c1.SetRightMargin(0.06)
    c1.SetLogy(0)
    c1.SetGrid(1)
    c1.Draw()
    c1.cd()
    leg  = SetLegend([0.2, 0.85, 0.95, 0.6],ncol=3)
    syst_nt_SR = any([i for i in ['CMSyear_trig_ele', 'CMSyear_EleID', 'CMSyear_EleRECO', 'CMSyear_MuID', 'CMSyear_MuISO', 'CMSyear_MuTRK'] if i in syst])
    unc = []
    for reg in regions:
        if syst_nt_SR and 'SR' in reg: continue
        for bin in range(1, reg_central[reg].GetXaxis().GetNbins()+1):
            frac_up = (reg_up[reg].GetBinContent(
                bin) - reg_central[reg].GetBinContent(bin))/reg_central[reg].GetBinContent(bin)
            frac_down = (reg_central[reg].GetBinContent(
                bin) - reg_down[reg].GetBinContent(bin))/reg_central[reg].GetBinContent(bin)
            unc.append(max(abs(frac_up), abs(frac_down)))
    max_= max(unc)*100; min_= min(unc)*100
    if (max_- min_) < 2.0:
        uncertfile.write(syst+' '+"{0:.2f}".format(max_)+'%\n')
    elif (max_ - min_) > 2.0 and min_ < 1.0:
        uncertfile.write(syst+' '+"{0:.2f}".format(min_)+'-'+str(int(max_))+'%\n')
    elif (max_ - min_) > 2.0 and min_ >= 1.0:
        uncertfile.write(syst+' '+str(int(min_))+'-'+str(int(max_))+'%\n')
    for reg in regions:
        if syst_nt_SR and 'SR' in reg: continue
        CustomiseHistogram(reg_up[reg],titleX, titleY, colors_up[reg], 1,'Up')
        CustomiseHistogram(reg_central[reg],titleX, titleY, 1, 1,'Central')
        CustomiseHistogram(reg_down[reg],titleX, titleY, colors_down[reg], 1,'Down')
        reg_up[reg].Divide(reg_central[reg])
        leg.AddEntry(reg_up[reg],reg+'Up','l')
        reg_up[reg].SetMinimum(min(unc)*0.9)
        reg_up[reg].SetMaximum(max(unc)*1.1)
        reg_up[reg].GetYaxis().CenterTitle()
        reg_up[reg].Draw("hist same")
        reg_down[reg].Divide(reg_central[reg])
        leg.AddEntry(reg_down[reg],reg+'Down','l')
        reg_down[reg].Draw("hist same")
        reg_central[reg].Divide(reg_central[reg])
        reg_central[reg].Draw("hist same")
    c1.cd()
    leg.Draw("same")
    pt = drawenergy1D(True, text_="Internal", data=True)
    for ipt in pt: ipt.Draw()
    t2d = ExtraText(str(syst), 0.20, 0.20)
    t2d.SetTextSize(0.06)
    t2d.SetTextAlign(12)
    t2d.SetNDC(ROOT.kTRUE)
    t2d.SetTextFont(42)
    t2d.Draw("same")
    c1.Update()
    if not os.path.exists('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPng/'):
        os.makedirs('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPng/')
    if not os.path.exists('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPdf/'):
        os.makedirs('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPdf/')
    c1.SaveAs('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPdf/'+syst+'.pdf')
    c1.SaveAs('syst_plots/'+datestr+'_'+str(options.year)+'/bbDMPng/'+syst+'.png')
    c1.Close()
