#!/usr/bin/env python
# coding: utf-8

##Usage: python crSummary_postfit_run2comb.py -i inputRootFile/fitDiagnostics_C_161718_fit_CRonly_result_checkscombo161718.root -d b -c 1b -t fitDiagnostics_C_161718_fit_CRonly_result_checkscombo161718 -y 2017
import os
import sys
import ROOT as ROOT
import optparse
from array import array
import datetime

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
    luminosity_ = '{0:.1f}'.format(35.9)
elif year == '2017':
    luminosity_ = '{0:.1f}'.format(41.5)
elif year == '2018':
    luminosity_ = '{0:.1f}'.format(59.6)
elif year == 'run2':
    luminosity_ = '{0:.0f}'.format(138)
else:
    print('Please provide on which year you want to run?')



def SetCanvas():
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 1257, 576)
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

    if data: text3 = pt2.AddText(0.72,0.5,pavetext)
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
    region = ['SR', 'ZMUMU', 'ZEE', 'WMU', 'WE']
elif cat == '2b':
    region = ['SR', 'ZMUMU', 'ZEE', 'TOPMU', 'TOPE']

# rtFile = ROOT.TFile('outPlotDir/postfit_Summary_test.root', 'RECREATE')

rtFile = ROOT.TFile('outPlotDir/'+str(tag)+'/postfit_Summary_'+year+'_'+cat+'.root', 'RECREATE')

contribution =  ['data','qcd','diboson','singlet','smh','tt','wjets','zjets','dyjets','prefit','postfit']

leg_entry = {'diboson':'WW/WZ/ZZ','zjets':'Z(#nu#nu)+jets','gjets':'#gamma+jets','qcd':'QCD','smh':'SMH','singlet':'Single t','tt':'t#bar{t}','wjets':'W(l#nu)+jets','dyjets':'Z(ll)+jets','data':'Data','prefit':'Prefit','postfit':'Postfit'}

hist_color = {'diboson':ROOT.kBlue+1,'zjets':ROOT.kAzure-4,'GJets':ROOT.kCyan-8,'qcd':ROOT.kGray+2,'smh':ROOT.kYellow-6,'singlet':ROOT.kOrange+2,'tt':ROOT.kOrange-1,'wjets':ROOT.kViolet-2,'dyjets':ROOT.kGreen+1,'data':ROOT.kBlack,'prefit':ROOT.kRed+2,'postfit':ROOT.kBlack}

if year=='run2':
  yr_list = ['2016','2017','2018']
else:
  yr_list = [year]

yr_dict = {}
yr_dict_err = {}
for yr in yr_list:
  contri={}
  contri_err={}
  for cont in contribution:
    f_dict = {}
    f_dict_err = {}
    for reg in region:
        # reg = 'cat_'+cat+'_'+reg
        # reg = 'd'+yr+'_'+reg
        reg = 'd'+yr+'_'+'cat_'+cat+'_'+reg
        bin_dict = []
        bin_dict_err = []
        if 'data' in cont:
            # to remove data from sr
            if 'SR' in reg:
                for i in range(4):
                  bin_dict.append(0)
                  bin_dict_err.append(0)
            else:
                print(fit_dir+'/'+reg+'/'+cont)
                for i in range(in_file.Get(fit_dir+'/'+reg+'/'+cont).GetN()):
                    bin_dict.append(in_file.Get(fit_dir+'/'+reg+'/'+cont).GetY()[i])
                    err_up = in_file.Get(fit_dir+'/'+reg+'/'+cont).GetErrorYhigh(i)
                    err_down = in_file.Get(fit_dir+'/'+reg+'/'+cont).GetErrorYlow(i)
                    bin_dict_err.append(max(err_up,err_down))
        elif 'prefit' in cont:
            for i in range(1,(in_file.Get('shapes_prefit/'+reg+'/total_background').GetNbinsX()+1)):
                bin_dict.append(in_file.Get('shapes_prefit/'+reg+'/total_background').GetBinContent(i))
                err_up = in_file.Get('shapes_prefit/'+reg+'/total_background').GetBinErrorUp(i)
                err_down = in_file.Get('shapes_prefit/'+reg+'/total_background').GetBinErrorLow(i)
                bin_dict_err.append(max(err_up,err_down))
        elif 'postfit' in cont:
            for i in range(1,(in_file.Get(fit_dir+'/'+reg+'/total_background').GetNbinsX()+1)):
                bin_dict.append(in_file.Get(fit_dir+'/'+reg+'/total_background').GetBinContent(i))
                err_up = in_file.Get(fit_dir+'/'+reg+'/total_background').GetBinErrorUp(i)
                err_down = in_file.Get(fit_dir+'/'+reg+'/total_background').GetBinErrorLow(i)
                bin_dict_err.append(max(err_up,err_down))
        else:
            if bool(in_file.Get(fit_dir+'/'+reg+'/'+cont)):
                for i in range(1,(in_file.Get(fit_dir+'/'+reg+'/'+cont)).GetNbinsX()+1):
                    bin_dict.append(in_file.Get(fit_dir+'/'+reg+'/'+cont).GetBinContent(i))
                    err_up = in_file.Get(fit_dir+'/'+reg+'/'+cont).GetBinErrorUp(i)
                    err_down = in_file.Get(fit_dir+'/'+reg+'/'+cont).GetBinErrorLow(i)
                    bin_dict_err.append(max(err_up,err_down))
        f_dict.update({reg:bin_dict})
        if not bin_dict:
          f_dict.update({reg:[0 for i in range(4)]})
        f_dict_err.update({reg:bin_dict_err})
        if not bin_dict_err:
          f_dict_err.update({reg:[0 for i in range(4)]})
    contri.update({cont:f_dict})
    contri_err.update({cont:f_dict_err})
  yr_dict.update({yr: contri})
  yr_dict_err.update({yr: contri_err})


str_bins_ = {'SR':'SR','ZMUMU':'Z#mu#mu','ZEE':'Zee','TOPMU':'t#bar{t}(#mu#nu)','TOPE':'t#bar{t}(e#nu)','WMU':'W#mu#nu','WE':'We#nu'}
hist_ = {}
if year=='run2':
    for cont in contribution:
        if '1b' in cat:
            bins = bins_list(5, 250, [50, 100, 150, 450])
            h_temp = ROOT.TH1F(cont+'_temp','CRSummaryplot',len(bins)-1,array('d', bins))
        elif '2b' in cat:
            bins = bins_list(5, 0.0, [0.25, 0.25, 0.25, 0.25])
            h_temp = ROOT.TH1F(cont+'_temp','CRSummaryplot',len(bins)-1,array('d', bins))
        hist_.update({cont:h_temp})
        f_dict16= yr_dict['2016'][cont]
        f_dict_err16 = yr_dict_err['2016'][cont]
        f_dict17= yr_dict['2017'][cont]
        f_dict_err17 = yr_dict_err['2017'][cont]
        f_dict18= yr_dict['2018'][cont]
        f_dict_err18 = yr_dict_err['2018'][cont]
        i=1
        for key in region:
            for j in range(len(f_dict16['d2016'+'_'+'cat_'+cat+'_'+key])):
                hist_[cont].SetBinContent(i, f_dict16['d2016'+'_'+'cat_'+cat+'_'+key][j]+f_dict17['d2017'+'_'+'cat_'+cat+'_'+key][j]+f_dict18['d2018'+'_'+'cat_'+cat+'_'+key][j])
                hist_[cont].SetBinError(i, f_dict_err16['d2016'+'_'+'cat_'+cat+'_'+key][j]+f_dict_err17['d2017'+'_'+'cat_'+cat+'_'+key][j]+f_dict_err18['d2018'+'_'+'cat_'+cat+'_'+key][j])
                if j==2:
                    # hist_[cont].GetXaxis().SetBinLabel(i,str_bins_[key.strip('cat_'+cat+'_')])
                    hist_[cont].GetXaxis().SetBinLabel(i,str_bins_[key.strip('d2016_'+'_'+'cat_'+cat+'_')])
                i+=1
else:
    for cont in contribution:
        if '1b' in cat:
            bins = bins_list(5, 250, [50, 100, 150, 450])
            h_temp = ROOT.TH1F(cont+'_temp','CRSummaryplot',len(bins)-1,array('d', bins))
        elif '2b' in cat:
            bins = bins_list(5, 0.0, [0.25, 0.25, 0.25, 0.25])
            h_temp = ROOT.TH1F(cont+'_temp','CRSummaryplot',len(bins)-1,array('d', bins))
        hist_.update({cont:h_temp})
        f_dict= contri[cont]
        f_dict_err = contri_err[cont]
        i=1
        for key in region:
            # key = 'cat_'+cat+'_'+key
            # key = 'd'+year+'_'+key
            key = 'd'+year+'_'+'cat_'+cat+'_'+key
            for j in range(len(f_dict[key])):
                hist_[cont].SetBinContent(i, f_dict[key][j])
                hist_[cont].SetBinError(i, f_dict_err[key][j])
                if j==2:
                    # hist_[cont].GetXaxis().SetBinLabel(i,str_bins_[key.strip('cat_'+cat+'_')])
                    # hist_[cont].GetXaxis().SetBinLabel(i,str_bins_[key.strip('d'+year+'_')])
                    hist_[cont].GetXaxis().SetBinLabel(i,str_bins_[key.strip('d'+year+'_cat_'+cat+'_')])
                i+=1

c1 = SetCanvas()
c1.cd()
##Upper PAD##
c1_1 = ROOT.TPad("c1_1", "c1_1", 0., 0.25, 1., 1.)
c1_1.SetBottomMargin(0.0)
c1_1.SetTopMargin(0.10)
c1_1.SetLeftMargin(0.08)
c1_1.SetRightMargin(0.02)
c1_1.SetLogy(1)
c1_1.SetGridx(0)
c1_1.Draw()
c1_1.cd()
legend = SetLegend([.55,.60,.95,.88],ncol=3)
legend.SetTextSize(0.06)
hs=ROOT.THStack('hs','CR Summary ')
hist_unsorted = {}
for key in hist_:
    hist_unsorted.update({key:hist_[key].Integral()})
hist_sorted = dict(sorted(hist_unsorted.items(), key=lambda item: item[1]))
for key in hist_sorted:
    if 'data' not in key and 'prefit' not in key and 'postfit' not in key and hist_sorted[key]>0:
        leg_sty = "f"
        hist_[key].SetFillColor(hist_color[key])
        hist_[key].SetLineWidth(0)
        hs.Add(hist_[key])
        legend.AddEntry(hist_[key],leg_entry[key],leg_sty)
maxi = hs.GetMaximum()*50
hs.SetMaximum(maxi)
# hs.SetMinimum(0.001)
hs.Draw('HIST')
##################################
# draw line
l=ROOT.TLine()
l.SetLineStyle(2)
l.SetLineWidth(1)
l.SetLineColor(ROOT.kGray+2)
for i in bins[4::4]:
    l.DrawLine(i, 0, i, maxi)
##################################
hs.GetYaxis().SetLabelSize(0.06)
hs.GetYaxis().SetTitleSize(0.08)
hs.GetYaxis().SetTitleOffset(0.45)
c1_1.Modified()
hs.GetYaxis().SetTitle("Events")
h_prefit = hist_['prefit']
h_prefit.Sumw2()
h_prefit.SetLineColor(hist_color['prefit'])
h_prefit.SetLineWidth(1)
h_prefit.SetMarkerSize(1.5)
h_prefit.SetMarkerColor(hist_color['prefit'])
h_prefit.SetMarkerStyle(29)
h_prefit = SetCMSAxis(h_prefit)
legend.AddEntry(h_prefit,leg_entry['prefit'],'PEL')
h_prefit.Draw("histsame el")
h_data = hist_['data']
h_data.Sumw2()
h_data.SetLineColor(hist_color['data'])
h_data.SetLineWidth(1)
h_data.SetMarkerSize(1.2)
h_data.SetMarkerStyle(20)
h_data = SetCMSAxis(h_data)
legend.AddEntry(h_data,leg_entry['data'],'PEL')
h_err = hist_['postfit'].Clone("h_err")
h_err.Sumw2()
h_err.SetFillColor(ROOT.kGray+2)
h_err.SetLineColor(ROOT.kGray+2)
h_err.SetMarkerSize(0)
h_err.SetFillStyle(3001)
h_err.Draw("same E2")
h_data.Draw("same p e1")
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
ratioleg = SetLegend([.62, .82, .95, .90], ncol=3)
ratioleg.SetTextSize(0.18)
ratioerr = h_err.Clone("ratioerr")
ratioerr.Sumw2()
ratioerr.SetStats(0)
ratioerr.GetYaxis().SetTitle("#frac{Data-Pred}{Pred}")
ratioerr.GetYaxis().SetTitleSize(0.18)
ratioerr.GetYaxis().SetTitleOffset(0.2)
ratioerr.GetYaxis().SetTitleFont(42)
ratioerr.GetYaxis().SetLabelSize(0.16)
ratioerr.GetYaxis().CenterTitle()
ratioerr.GetXaxis().SetLabelSize(0.25)
ratioerr.GetXaxis().SetTitleSize(0.16)
ratioerr.GetXaxis().SetLabelOffset(0.04)
ratioerr.GetXaxis().SetTitleFont(42)
ratioerr.GetXaxis().SetTickLength(0.07)
ratioerr.GetXaxis().SetLabelFont(42)
ratioerr.GetYaxis().SetLabelFont(42)
ratioerr.GetYaxis().SetNdivisions(505)
ratioerr.SetMarkerSize(0)
ratioerr.SetFillColor(ROOT.kGray+1)
ratioerr.SetFillStyle(3001)
ratioerr.SetMinimum(-0.57)
ratioerr.SetMaximum(0.57)
ratioleg.AddEntry(ratioerr, "stats","f")
for i in range(1,h_err.GetNbinsX()+1):
    binerror = 0.0
    ratioerr.SetBinContent(i, 0.0)
    if (h_err.GetBinContent(i) > 1e-6):
        binerror = h_err.GetBinError(i)
        ratioerr.SetBinError(i, binerror/h_err.GetBinContent(i))
    else:
        ratioerr.SetBinError(i, 999.)
ratioerr.Draw("e2 same")
DataMC = h_data.Clone()
DataMC.Add(hist_['postfit'], -1)   # remove for data/mc
DataMC.Divide(hist_['postfit'])
DataMC.SetMarkerSize(1.2)
DataMC.SetMarkerStyle(20)
DataMC.SetMarkerColor(1)
DataMC.SetLineWidth(1)
ratioleg.AddEntry(DataMC, "Postfit",'PEL')
DataMC.Draw("P e1 same")
prefitMC = h_data.Clone()
prefitMC.Add(h_prefit, -1)
prefitMC.Divide(h_prefit)
prefitMC.SetLineColor(hist_color['prefit'])
prefitMC.SetMarkerStyle(29)
prefitMC.SetLineWidth(1)
prefitMC.SetMarkerSize(1.5)
prefitMC.SetMarkerColor(hist_color['prefit'])
ratioleg.AddEntry(prefitMC, "Prefit","PEL")
prefitMC.Draw("same")
ratioleg.Draw("e2 same")
##################################
# draw line
l1=ROOT.TLine()
l1.SetLineStyle(2)
l1.SetLineWidth(1)
l1.SetLineColor(ROOT.kGray+2)
for i in bins[4::4]:
    l1.DrawLine(i,-1.0, i, 1.0)
##################################
c1_2.Update()
c1.cd()
t2d = ExtraText(str(cat), 0.20, 0.80)
t2d.SetTextSize(0.06)
t2d.SetTextAlign(12)
t2d.SetNDC(ROOT.kTRUE)
t2d.SetTextFont(42)
t2d.Draw("same")
pt = drawenergy1D(True,text_="    Internal",data=True)
for ipt in pt: ipt.Draw()
latex=getLatex()
c1.Update()
outputdirname = 'outPlotDir/'+tag+'/'
if not os.path.exists(outputdirname): os.makedirs(outputdirname)
c1.SaveAs(outputdirname+"/postfit_Summary_"+year+"_"+cat+".pdf")
c1.Draw()
rtFile.cd()
for h in hs:
    h.Write()
h_prefit.Write()
h_data.Write()
rtFile.Close()