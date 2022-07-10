#!/usr/bin/env python
# coding: utf-8
import os
import sys
import ROOT as ROOT
import optparse
from array import array
import datetime

usage = "usage: python crSummary_postfit.py -i <input root file> -d <b or s> -c <1b or 2b> -t <output file tag> -y <year>"
parser = optparse.OptionParser(usage)

parser.add_option("-i", "--indir", type="string",
                  dest="rootFileDir", help="input root file directory")
parser.add_option("-c", "--category", type="string",
                  dest="cat", help="1b or 2b")
parser.add_option("-t", "--tag", type="string",
                  dest="tag", help="output file tag")
parser.add_option("-y", "--year", type="string",
                  dest="year", help="year of histogram")

(options, args) = parser.parse_args()

if options.rootFileDir == None:
    print('Please provide input file name')
    sys.exit()
else:
    in_dir = options.rootFileDir

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
    luminosity_ = '{0:.2f}'.format(137)
else:
    print('Please provide on which year you want to run?')


def SetCanvas():
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 1257, 576)
    c.SetBottomMargin(0.050)
    c.SetRightMargin(0.050)
    c.SetLeftMargin(0.050)
    c.SetTopMargin(0.050)
    return c


def SetCMSAxis(h, xoffset=1., yoffset=1.):
    h.GetXaxis().SetTitleSize(0.047)
    h.GetYaxis().SetTitleSize(0.047)
    if type(h) is ((not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetTitleSize(0.047)

    h.GetXaxis().SetLabelSize(0.047)
    h.GetYaxis().SetLabelSize(0.047)
    if type(h) is ((not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetLabelSize(0.047)

    h.GetXaxis().SetTitleOffset(xoffset)
    h.GetYaxis().SetTitleOffset(yoffset)

    h.GetYaxis().CenterTitle()
    return h


def SetLegend(coordinate_=[.50, .65, .90, .90], ncol=2):
    c_ = coordinate_
    legend = ROOT.TLegend(c_[0], c_[1], c_[2], c_[3])
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
    text = pt.AddText(0.04,0.57,"#font[60]{CMS}")

    #pt1 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1 = ROOT.TPaveText(0.03,0.95,0.9580537,0.96,"brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.215,0.4,text_)
    text1 = pt1.AddText(0.11,0.4,text_)

    #pt2 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2 = ROOT.TPaveText(0.5297181,0.95,0.9580537,0.96,"brNDC")
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

    if data: text3 = pt2.AddText(0.68,0.5,pavetext)
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
        ltx.SetTextFont(42)
        ltx.SetTextSize(0.049)
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


def getHisto(hist, ls, lc, mc, ms):
    gr = hist  # .Clone('gr')
    gr.SetLineStyle(ls)
    gr.SetLineWidth(2)
    gr.SetMarkerStyle(ms)
    gr.SetMarkerSize(1)
    gr.SetLineColor(lc)
    gr.SetMarkerColor(mc)
    return gr


def setRebin(h_temp2, newname, bin):
    h_temp = h_temp2.Rebin(bin)
    h_temp.SetName(newname)
    h_temp.SetTitle(newname)
    return h_temp


def bins_list(n_reg, firstBin, bdiff=[50, 100, 150, 450]):
    bin_list = [firstBin, ]
    bin_val = firstBin
    for i in range(n_reg):
        for j in bdiff:
            bin_val += j
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

if not os.path.exists('outPlotDir'): os.makedirs('outPlotDir')
if cat == '1b':
    region = ['SR', 'ZmumuCR', 'ZeeCR', 'WmunuCR', 'WenuCR']
    varCR = 'Recoil'
    varSR = 'MET'
    bins = bins_list(5, 250, [50, 100, 150, 450])
elif cat == '2b':
    region = ['SR', 'ZmumuCR', 'ZeeCR', 'TopmunuCR', 'TopenuCR']
    varCR = 'ctsValue'
    varSR = 'ctsValue'
    bins = bins_list(5, 0.0, [0.25, 0.25, 0.25, 0.25])
    # varCR = 'Recoil'
    # varSR = 'MET'
    # bins = bins_list(5, 250, [50, 100, 150, 450])


contribution = ['data_obs', 'DIBOSON', 'ZJets', 'GJets', 'QCD', 'SMH', 'STop', 'Top', 'WJets', 'DYJets']
leg_entry = {'DIBOSON': 'WW/WZ/ZZ', 'ZJets': 'Z(#nu#nu)+jets', 'GJets': '#gamma+jets', 'QCD': 'QCD', 'SMH': 'SMH', 'STop': 'Single t', 'Top': 't#bar{t}', 'WJets': 'W(l#nu)+jets', 'DYJets': 'Z(ll)+jets', 'data_obs': 'Data'}

hist_color = {'DIBOSON': ROOT.kBlue+1, 'ZJets': ROOT.kAzure-4, 'GJets': ROOT.kCyan-8, 'QCD': ROOT.kGray+2, 'SMH': ROOT.kRed-1,
              'STop': ROOT.kOrange+2, 'Top': ROOT.kOrange-1, 'WJets': ROOT.kViolet-2, 'DYJets': ROOT.kGreen+1, 'data_obs': ROOT.kBlack}

in_files = {}
for reg in region:
    if 'SR' in reg:
        in_files.update(
            {reg: ROOT.TFile(in_dir+'/h_reg_'+reg+'_'+cat+'_'+varSR+'.root')})
    else:
        if 'Z' in reg:
            cat_ = cat.replace('1b', '2j').replace('2b', '3j')
        else:
            cat_ = cat
        in_files.update(
            {reg: ROOT.TFile(in_dir+'/h_reg_'+reg+'_'+cat_+'_'+varCR+'.root')})

contri = {}
for cont in contribution:
    f_dict = {}
    for reg in region:
      bin_dict = []
      for i in range(1, (in_files[reg].Get(cont)).GetNbinsX()+1):
        bin_dict.append(in_files[reg].Get(cont).GetBinContent(i))
      f_dict.update({reg: bin_dict})
      if not bin_dict:
        f_dict.update({reg: [0 for i in range(4)]})
    contri.update({cont: f_dict})
# print(contri)

contri_err = {}
for cont in contribution:
    f_dict = {}
    for reg in region:
        bin_dict = []
        for i in range(1, (in_files[reg].Get(cont)).GetNbinsX()+1):
            err_up = in_files[reg].Get(cont).GetBinErrorUp(i)
            err_down = in_files[reg].Get(cont).GetBinErrorLow(i)
            bin_dict.append(max(err_up, err_down))
        f_dict.update({reg: bin_dict})
        if not bin_dict:
            f_dict.update({reg: [0 for i in range(4)]})
    contri_err.update({cont: f_dict})
# print(contri_err)


str_bins_ = {'SR': 'SR', 'ZmumuCR': 'Z#mu#mu', 'ZeeCR': 'Zee',
             'TopmunuCR': 't#bar{t}(#mu#nu)', 'TopenuCR': 't#bar{t}(e#nu)', 'WmunuCR': 'W#mu#nu', 'WenuCR': 'We#nu'}
hist_ = {}
for cont in contribution:
    h_temp = ROOT.TH1F(cont+'_temp', 'CRSummaryplot', len(bins)-1, array('d', bins))
    hist_.update({cont: h_temp})
    f_dict = contri[cont]
    f_dict_err = contri_err[cont]
    i = 1
    for key in region:
      for j in range(len(f_dict[key])):
        hist_[cont].SetBinContent(i, f_dict[key][j])
        hist_[cont].SetBinError(i, f_dict_err[key][j])
        if j == 2:
            hist_[cont].GetXaxis().SetBinLabel(i, str_bins_[key])
        i += 1
sig_hist = []
histFile = ROOT.TFile(in_dir+'/h_reg_SR_'+cat+'_'+varSR+'.root')
# if '2016' in year:
#   sig_name = ['Ma10_MChi1_MA600', 'Ma100_MChi1_MA600', 'Ma250_MChi1_MA600', 'Ma500_MChi1_MA600']
# else:
sig_name = ['ma_10_mA_600', 'ma_100_mA_600', 'ma_250_mA_600', 'ma_500_mA_600']
for sig in sig_name:
  sig_hist.append(histFile.Get(sig))
print(sig_hist)
[(sig_hist[i].SetLineStyle(n), sig_hist[i].SetLineWidth(2), sig_hist[i].SetLineColor(n)) for i, n in zip(range(len(sig_hist)), range(2, len(sig_hist)+2))]
[(sig_hist[i].SetMarkerColor(n), sig_hist[i].SetMarkerStyle(n), sig_hist[i].SetMarkerSize(1.1)) for i, n in zip(range(len(sig_hist)), range(2, len(sig_hist)+2))]
sig_leg = SetLegend([.30,.60,.55,.88], ncol=1)
sig_leg.SetTextSize(0.040)
sig_leg.SetTextFont(62)
sig_leg.SetHeader("2HDM+a model")
if '2016' in year:
  [sig_leg.AddEntry(sig_hist[i], "ma = "+filename.split('_')[0].strip('Ma')+" GeV, mA = "+filename.split('_')[-1].strip('MA')+" GeV", "lp") for i, filename in zip(range(len(sig_hist)), sig_name)]
else:
  [sig_leg.AddEntry(sig_hist[i], "ma = "+filename.split('_')[1]+" GeV, mA = "+filename.split('_')
                    [-1]+" GeV", "lp") for i, filename in zip(range(len(sig_hist)), sig_name)]

c1 = SetCanvas()
c1.cd()
##Upper PAD##
c1_1 = ROOT.TPad("c1_1", "c1_1", 0., 0.25, 1., 1.)
c1_1.SetBottomMargin(0.0)
c1_1.SetTopMargin(0.10)
c1_1.SetLeftMargin(0.08)
c1_1.SetRightMargin(0.02)
c1_1.SetLogy(1)
c1_1.SetGridy(0)
c1_1.Draw()
c1_1.cd()
legend = SetLegend([.55,.60,.95,.88],ncol=3)
legend.SetTextSize(0.06)
hs=ROOT.THStack('hs','CR Summary ')
hist_unsorted = {}
for key in hist_:
    hist_unsorted.update({key: hist_[key].Integral()})
hist_sorted = dict(sorted(hist_unsorted.items(), key=lambda item: item[1]))
for key in hist_sorted:
    if not 'data_obs' in key and hist_sorted[key] > 0:
        leg_sty = "f"
        hist_[key].SetFillColor(hist_color[key])
        hist_[key].SetLineWidth(0)
        hs.Add(hist_[key])
        legend.AddEntry(hist_[key], leg_entry[key], leg_sty)
Stackhist = hs.GetStack().Last()
maxi = hs.GetMaximum()*100
hs.SetMaximum(maxi)
hs.SetMinimum(1)
hs.Draw('HIST')
[hist.Draw("same Ehist") for hist in sig_hist]
sig_leg.Draw('same')
##################################
# draw line
l = ROOT.TLine()
l.SetLineStyle(2)
l.SetLineWidth(1)
l.SetLineColor(ROOT.kBlack)
for i in bins[4::4]:
    l.DrawLine(i, 0, i, maxi)
##################################
hs.GetYaxis().SetLabelSize(0.06)
hs.GetYaxis().SetTitleSize(0.08)
hs.GetYaxis().SetTitleOffset(0.45)
c1_1.Modified()
hs.GetYaxis().SetTitle("Events")
h_data = hist_['data_obs']
h_data.Sumw2()
h_data.SetLineColor(1)
h_data.SetLineWidth(2)
h_data.SetMarkerSize(1.2)
h_data.SetMarkerStyle(20)
h_data = SetCMSAxis(h_data)
legend.AddEntry(h_data, leg_entry['data_obs'], 'PEL')
h_data.Draw("same p e1")
h_err = Stackhist.Clone("h_err")
h_err.Sumw2()
h_err.SetFillColor(ROOT.kGray+3)
h_err.SetLineColor(ROOT.kGray+3)
h_err.SetMarkerSize(0)
h_err.SetFillStyle(3013)
h_err.Draw("same E2")
legend.Draw("same")
c1_1.Update()
c1.cd()
##Lower PAD##
c1_2 = ROOT.TPad("c1_2", "c1_2", 0., 0., 1., 0.25)
c1_2.SetLeftMargin(0.08)
c1_2.SetRightMargin(0.02)
c1_2.SetTopMargin(0.00)
c1_2.SetBottomMargin(0.28)
c1_2.SetGridx(0)
c1_2.Draw()
c1_2.cd()
DataMC = h_data.Clone()
DataMC.Add(Stackhist, -1)   # remove for data/mc
DataMC.Divide(Stackhist)
DataMC.GetYaxis().SetTitle("#frac{Data-Pred}{Pred}")
DataMC.GetYaxis().SetTitleSize(0.12)
DataMC.GetYaxis().SetTitleOffset(0.2)
DataMC.GetYaxis().SetTitleFont(42)
DataMC.GetYaxis().SetLabelSize(0.12)
DataMC.GetYaxis().CenterTitle()
DataMC.GetXaxis().SetLabelSize(0.25)
DataMC.GetXaxis().SetTitleSize(0.16)
DataMC.GetXaxis().SetLabelOffset(0.01)
DataMC.GetXaxis().SetTitleFont(42)
DataMC.GetXaxis().SetTickLength(0.07)
DataMC.GetXaxis().SetLabelFont(42)
DataMC.GetYaxis().SetLabelFont(42)
DataMC.GetYaxis().SetNdivisions(505)
DataMC.SetMarkerSize(1.5)
DataMC.SetMarkerStyle(20)
DataMC.SetMarkerColor(1)
DataMC.SetMinimum(-1.1)
DataMC.SetMaximum(1.1)
DataMC.Draw("P e1")
ratioleg = SetLegend([.72, .80, .90, .90], 1)
ratioleg.SetTextSize(0.15)
ratioerr = h_err.Clone("ratioerr")
ratioleg.AddEntry(ratioerr, "stat", "plf")
ratioerr.Sumw2()
ratioerr.SetStats(0)
ratioerr.SetMinimum(0)
ratioerr.SetMarkerSize(0)
ratioerr.SetFillColor(ROOT.kBlack)
ratioerr.SetFillStyle(3013)
for i in range(h_err.GetNbinsX()):
    binerror = 0.0
    ratioerr.SetBinContent(i, 0.0)
    if (h_err.GetBinContent(i) > 1e-6):
        binerror = h_err.GetBinError(i)
        ratioerr.SetBinError(i, binerror/h_err.GetBinContent(i))
    else:
        ratioerr.SetBinError(i, 999.)
ratioerr.Draw("e2 same")
ratioleg.Draw("same")
##################################
# draw line
l1 = ROOT.TLine()
l1.SetLineStyle(2)
l1.SetLineWidth(1)
l1.SetLineColor(ROOT.kBlack)
for i in bins[4::4]:
    l1.DrawLine(i, -1.0, i, 1.0)
##################################
c1_2.Update()
c1.cd()
t2d = ExtraText(str(cat), 0.20, 0.80)
t2d.SetTextSize(0.06)
t2d.SetTextAlign(12)
t2d.SetNDC(ROOT.kTRUE)
t2d.SetTextFont(42)
t2d.Draw("same")
pt = drawenergy1D(True, text_="    Internal", data=True)
for ipt in pt:
    ipt.Draw()
latex = getLatex()
c1.Update()
outputdirname = 'outPlotDir/'+tag+'/'
if not os.path.exists(outputdirname): os.makedirs(outputdirname)
c1.SaveAs(outputdirname+"/prefit_Summary_"+year+"_"+cat+".pdf")
c1.Draw()
