#!/usr/bin/env python
# coding: utf-8
##Usage: python crSummary_postfit_perProc.py -i inputRootFile/fitDiagnostics_C_2017_fit_CRonly_result_checkscombo2017.root -d b -c 2b -t v17_12-00-04 -y 2017
import os
import sys
import ROOT as ROOT
import optparse
from array import array
import datetime
import math

usage = "usage: python crSummary_postfit.py -i <input root file> -d <b or s> -c <1b or 2b> -t <output file tag> -y <year>"
parser = optparse.OptionParser(usage)

parser.add_option("-i", "--infile", type="string", dest="rootFileDir", help="input fit file")
parser.add_option("-d", "--fit_dir", type="string", dest="fit_dir",help="shapes_fit_b or shapes_fit_s")
parser.add_option("-c", "--category", type="string", dest="cat", help="1b or 2b")
parser.add_option("-t", "--tag", type="string", dest="tag", help="output file tag")
parser.add_option("-y", "--year", type="string", dest="year", help="year of histogram")

(options, args) = parser.parse_args()

if options.rootFileDir == None:
    print('Please provide input file name')
    sys.exit()
else:
    input_file = options.rootFileDir

if options.fit_dir == None:
    print('Please provide which fit directory to use (s or b)')
    sys.exit()
else:
    fit_dir = str('shapes_fit_'+options.fit_dir)

if options.cat == None:
    print('Please provide which category to use (1b or 2b)')
    sys.exit()
else:
    cat = str(options.cat)

if options.tag == None:
    print('Please provide output tag')
    sys.exit()
else:
    tag = str(options.tag)

if options.year == None:
    print('Please provide year')
    sys.exit()
else:
    year = str(options.year)

###year####
if year == '2016':
    luminosity_ = '{0:.2f}'.format(35.82)
elif year == '2017':
    luminosity_ = '{0:.2f}'.format(41.50)
elif year == '2018':
    luminosity_ = '{0:.2f}'.format(59.64)
elif year == 'run2':
    luminosity_ = '{0:.2f}'.format(137.00)
else:
    print('Please provide on which year you want to run?')



def SetCanvas():
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 650, 600)
#     c = ROOT.TCanvas()
    c.SetBottomMargin(0.050)
    c.SetRightMargin(0.050)
    c.SetLeftMargin(0.050)
    c.SetTopMargin(0.050)
    return c

def SetCMSAxis(h, xoffset=1., yoffset=1.):
    h.GetXaxis().SetTitleSize(0.047)
    h.GetYaxis().SetTitleSize(0.047)
    if type(h) is ( (not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetTitleSize(0.047)

    h.GetXaxis().SetLabelSize(0.047)
    h.GetYaxis().SetLabelSize(0.047)
    if type(h) is ( (not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetLabelSize(0.047)

    h.GetXaxis().SetTitleOffset(xoffset)
    h.GetYaxis().SetTitleOffset(yoffset)

    h.GetYaxis().CenterTitle()
    return h

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
    legend.SetTextSize(0.035)
    return legend


def drawenergy1D(is2017, text_="Work in progress 2018", data=True):
    #pt = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt = ROOT.TPaveText(0.04297181,0.953,0.9580537,0.96,"brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)

    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize *0.7
    pt.SetTextSize(cmstextSize)
    text = pt.AddText(0.09,0.57,"#font[60]{CMS}")

    #pt1 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1 = ROOT.TPaveText(0.16,0.95,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.215,0.4,text_)
    text1 = pt1.AddText(0.11,0.4,text_)

    #pt2 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2 = ROOT.TPaveText(0.557181,0.95,0.9580537,0.96,"brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)

    pavetext = ''
    if is2017 and data: pavetext = str(luminosity_)+' fb^{-1}'+"(13 TeV)"
    if (not is2017) and data: pavetext = str(luminosity_)+' fb^{-1}'+"(13 TeV)"

    if is2017 and not data: pavetext = "13 TeV"
    if (not is2017) and not data: pavetext = "13 TeV"

    if data: text3 = pt2.AddText(0.2,0.5,pavetext)
    if not data: text3 = pt2.AddText(0.85,0.5,pavetext)

    return [pt,pt1,pt2]

def getLatex():
    latex =  ROOT.TLatex()
    latex.SetNDC();
    latex.SetTextSize(0.04);
    latex.SetTextAlign(31);
    latex.SetTextAlign(11);
    latex.SetTextColor(1);
    return latex


def ExtraText(text_, x_, y_):
    if not text_:
        print("nothing provided as text to ExtraText, function crashing")
    ltx = ROOT.TLatex(x_, y_, text_)

    if len(text_) > 0:
        ltx.SetTextFont(62)
        ltx.SetTextSize(0.019)
        #ltx.Draw(x_,y_,text_)
        ltx.Draw('same')
    return ltx


def getGraph(n,x,y,lc,mc,ms):
    gr =ROOT.TGraph(n,x,y)
    gr.SetFillColor(4)
    #gr.SetFillStyle(3004)
    gr.SetLineColor(4)
    gr.SetLineWidth(2)
    gr.SetMarkerStyle(ms)
    gr.SetMarkerSize(1.5)
    gr.SetLineColor(lc)
    gr.SetLineWidth(1)
    gr.SetMarkerColor(mc)
    gr.GetYaxis().SetTitle("Signal Efficiency")
    gr.GetXaxis().SetTitle("M_{a} (GeV)")
    return gr

def getHisto(hist,ls,lc,mc,ms):
    gr = hist#.Clone('gr')
    gr.SetLineStyle(ls)
    gr.SetLineWidth(2)
    gr.SetMarkerStyle(ms)
    gr.SetMarkerSize(1)
    gr.SetLineColor(lc)
    gr.SetMarkerColor(mc)
    return gr

def bins_list(n_reg,firstBin,bdiff=[50,100,150,450]):
    bin_list = [firstBin, ]
    bin_val = firstBin
    for i in range(n_reg):
        for j in bdiff:
            bin_val+=j
            bin_list.append(bin_val)
    return bin_list

datestr = str(datetime.date.today().strftime("%d%m%Y"))

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetFrameLineWidth(3)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gROOT.ForceStyle(1)
ROOT.gStyle.SetImageScaling(3.)


in_file = ROOT.TFile(input_file)
if not os.path.exists('outPlotDir'): os.makedirs('outPlotDir')




if cat == '1b':
    region = ['SR']#, 'ZMUMU', 'ZEE', 'WMU', 'WE']
elif cat == '2b':
    region = ['SR']#, 'ZMUMU', 'ZEE', 'TOPMU', 'TOPE']

contribution =  ['qcd','diboson','singlet','smh','tt','wjets','zjets','dyjets']

leg_entry = {'diboson':'WW/WZ/ZZ','zjets':'Z(#nu#nu)+jets','gjets':'#gamma+jets','qcd':'QCD','smh':'SMH','singlet':'Single t','tt':'t#bar{t}','wjets':'W(l#nu)+jets','dyjets':'Z(ll)+jets','data':'Data','prefit':'Prefit','postfit':'Postfit'}

hist_color = {'diboson':ROOT.kBlue+1,'zjets':ROOT.kAzure-4,'GJets':ROOT.kCyan-8,'qcd':ROOT.kGray+2,'smh':ROOT.kYellow-6,'singlet':ROOT.kOrange+2,'tt':ROOT.kOrange-1,'wjets':ROOT.kViolet-2,'dyjets':ROOT.kGreen+1,'data':ROOT.kBlack,'prefit':ROOT.kRed+2,'postfit':ROOT.kBlack}


for cont in contribution:
  for reg in region:
    reg = 'cat_'+cat+'_'+reg
    print(reg+'/'+cont)
    histo_postfit = in_file.Get('shapes_fit_b/'+reg+'/'+cont)
    histo_prefit = in_file.Get('shapes_prefit/'+reg+'/'+cont)
    errors = {}
    for i in range(1,5):
        errors.update({i:math.sqrt((histo_prefit.GetBinError(i)/histo_prefit.GetBinContent(i))**2 + (histo_postfit.GetBinError(i)/histo_postfit.GetBinContent(i))**2)})
    histo_postfit.Divide(histo_prefit)
    histo_postfit.Sumw2()
    print('\n')
    for i in range(1, 5):
        print(histo_postfit.GetBinError(i), errors[i]*histo_postfit.GetBinContent(i))
    c1 = SetCanvas()
    c1.cd()
    ##Upper PAD##
    c1_1 = ROOT.TPad("c1_1", "c1_1", 0., 0.0, 1., 1.)
    c1_1.SetBottomMargin(0.15)
    c1_1.SetTopMargin(0.08)
    c1_1.SetLeftMargin(0.16)
    c1_1.SetRightMargin(0.05)
    c1_1.SetLogy(0)
    c1_1.SetGridx(0)
    c1_1.Draw()
    c1_1.cd()
    legend = SetLegend([.55,.60,.95,.88],ncol=3)
    legend.SetTextSize(0.06)
    legend.AddEntry(histo_postfit, cont, "f")
    histo_postfit.Draw('HIST E1')
    ##################################
    histo_postfit.GetYaxis().SetLabelSize(0.05)
    histo_postfit.GetYaxis().SetTitleSize(0.075)
    histo_postfit.GetYaxis().SetTitleOffset(1.0)
    histo_postfit.GetXaxis().SetLabelSize(0.05)
    histo_postfit.GetXaxis().SetTitleSize(0.075)
    histo_postfit.GetXaxis().SetTitleOffset(0.82)
    histo_postfit.SetLineWidth(2)
    histo_postfit.SetLineColor(1)
    max_error = max([histo_postfit.GetBinError(i) for i in range(1, 5)])
    histo_postfit.SetMaximum((histo_postfit.GetMaximum()+max_error)*1.15)
    histo_postfit.SetMinimum((histo_postfit.GetMinimum()-max_error)/1.15)
    histo_postfit.GetXaxis().SetNdivisions(505)
    # histo_postfit.GetYaxis().SetNdivisions(505)

    c1_1.Modified()
    histo_postfit.GetYaxis().SetTitle("postfit/prefit")
    if '1b' in cat:
      histo_postfit.GetXaxis().SetTitle('p_{T}^{miss} (GeV)')
    elif '2b' in cat:
      histo_postfit.GetXaxis().SetTitle("cos(#theta)*")
    c1.cd()
    t2d = ExtraText(leg_entry[cont]+' in SR '+str(cat), 0.55, 0.80)
    t2d.SetTextSize(0.05)
    t2d.SetTextAlign(12)
    t2d.SetNDC(ROOT.kTRUE)
    t2d.SetTextFont(62)
    t2d.Draw("same")
    pt = drawenergy1D(True,text_="Internal",data=True)
    for ipt in pt: ipt.Draw()
    latex=getLatex()
    c1.Update()
    outputdirnamePDF = 'outPlotDir/'+tag+'/pdf/'
    outputdirnamePNG = 'outPlotDir/'+tag+'/png/'
    # if not os.path.exists(outputdirnamePDF): os.makedirs(outputdirnamePDF)
    # c1.SaveAs(outputdirnamePDF+"/postfit_Summary_"+year+"_"+cat+"_"+cont+".pdf")
    # if not os.path.exists(outputdirnamePNG): os.makedirs(outputdirnamePNG)
    # c1.SaveAs(outputdirnamePNG+"/postfit_Summary_"+year+"_"+cat+"_"+cont+".png")
    if not os.path.exists(outputdirnamePDF): os.makedirs(outputdirnamePDF)
    c1.SaveAs(outputdirnamePDF+"/postfit_Summary_"+cat+"_"+cont+".pdf")
    if not os.path.exists(outputdirnamePNG): os.makedirs(outputdirnamePNG)
    c1.SaveAs(outputdirnamePNG+"/postfit_Summary_"+cat+"_"+cont+".png")
    c1.Draw()
    c1.Close()
