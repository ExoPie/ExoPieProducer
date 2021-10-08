from uncert_binwise_v17_07_04_00 import syst_dict
import os
import sys
import datetime
import sys
import optparse
import ROOT as ROOT
import array
import string
import math


ROOT.gROOT.SetBatch(1)
#command  python StackPlotter_syst.py -d <DATASET_NAME> -m -y <Year> -D <histo_DIR> -S <signal_Dir>
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)

parser.add_option("-d", "--data", dest="datasetname")
parser.add_option("-D", "--pDir", type="string", dest="rootFileDir", help="histogram dir")
parser.add_option("-S", "--sigDir", type="string", dest="SIGrootFileDir", help="signal histogram")
parser.add_option("-v", "--version", type="string",dest="Version", help="version of histograms")
parser.add_option("-s", "--sr", action="store_true", dest="plotSIGNAL")
parser.add_option("-m", "--mu", action="store_true", dest="plotMuChannels")
parser.add_option("-e", "--ele", action="store_true", dest="plotEleChannels")
parser.add_option("-p", "--pho", action="store_true", dest="plotPhoChannels")
parser.add_option("-q", "--qcd", action="store_true", dest="plotQCDChannels")
parser.add_option("-y", "--year", dest="year", default="Year")

(options, args) = parser.parse_args()

if options.plotSIGNAL == None:
    makeSIGplots = False
else:
    makeSIGplots = options.plotSIGNAL

if options.plotMuChannels == None:
    makeMuCHplots = False
else:
    makeMuCHplots = options.plotMuChannels

if options.plotEleChannels == None:
    makeEleCHplots = False
else:
    makeEleCHplots = options.plotEleChannels

if options.plotPhoChannels == None:
    makePhoCRplots = False
else:
    makePhoCRplots = options.plotPhoChannels

if options.plotQCDChannels == None:
    makeQCDCRplots = False
else:
    makeQCDCRplots = options.plotQCDChannels

if options.datasetname.upper() == "SE":
    dtset = "SE"
elif options.datasetname.upper() == "SP":
    dtset = "SP"
elif options.datasetname.upper() == "SM":
    dtset = "SM"
else:
    dtset = "MET"

print("Using dataset "+dtset)

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
    # import sample_xsec_2016 as sample_xsec
    # import sample_xsec_2016_GenXSecAnalyser as sample_xsec
    import sig_sample_xsec_2016 as sig_sample_xsec
    #checking 2017 crossection for 2016
    import sample_xsec_2017_GenXSecAnalyser as sample_xsec
    from uncert_v16_12_00_02 import syst_dict
    luminosity = 35.82 * 1000
    luminosity_ = '{0:.2f}'.format(35.82)
elif runOn2017:
    #import sample_xsec_2017 as sample_xsec
    import sample_xsec_2017_GenXSecAnalyser as sample_xsec
    import sig_sample_xsec_2017 as sig_sample_xsec
    from uncert_v17_12_00_02 import syst_dict
    luminosity = 41.5 * 1000
    luminosity_ = '{0:.2f}'.format(41.50)
elif runOn2018:
    import sample_xsec_2018 as sample_xsec
    import sig_sample_xsec_2018 as sig_sample_xsec
    from uncert_v18_12_00_02 import syst_dict
    luminosity = 59.64 * 1000
    luminosity_ = '{0:.2f}'.format(59.64)


datestr = str(datetime.date.today().strftime("%d%m%Y"))

if options.Version == None:
    print('Please provide which version of histograms are being plotted')
    sys.exit()
else:
    histVersion = options.Version

if options.rootFileDir == None:
    print('Please provide histogram directory name')
    sys.exit()
else:
    path = options.rootFileDir

sig_path = options.SIGrootFileDir

print("sig_path sig_path sig_path", sig_path)
if makeMuCHplots:
    yield_outfile_binwise = open('YieldsFiles/'+histVersion+'_Muon_binwise.txt','w')
    yield_outfile = open('YieldsFiles/'+histVersion+'_Muon.txt','w')
if makeEleCHplots:
    yield_outfile_binwise = open('YieldsFiles/'+histVersion+'_Electron_binwise.txt','w')
    yield_outfile = open('YieldsFiles/'+histVersion+'_Electron.txt', 'w')

alpha_list = list(string.ascii_uppercase)

syst_sources = ['CMSyear_eff_b', 'CMSyear_fake_b', 'EWK', 'CMSyear_Top', 'CMSyear_trig_met', 'CMSyear_trig_ele', 'CMSyear_EleID', 'CMSyear_EleRECO', 'CMSyear_MuID', 'CMSyear_MuISO', 'CMSyear_MuTRK',
                'CMSyear_PU', 'JECAbsolute', 'JECAbsolute_year', 'JECBBEC1', 'JECBBEC1_year', 'JECEC2', 'JECEC2_year', 'JECFlavorQCD', 'JECHF', 'JECHF_year', 'JECRelativeBal', 'JECRelativeSample_year', 'En']

def set_overflow(hist):
    bin_num = hist.GetXaxis().GetNbins()
    #print (bin_num)
    hist.SetBinContent(bin_num, hist.GetBinContent(
        bin_num+1)+hist.GetBinContent(bin_num))  # Add overflow bin content to last bin
    hist.SetBinContent(bin_num+1, 0.)
    return hist

def setVarBin(h_temp1, hist):
    #bins_ = [250,280,340,460,1000]
    # bins_ = [250,270,320,400,1000]
    # bins_ = [250,275,325,400,1000]
    # bins_ = [250,265,325,425,1000]
    # bins_ = [250, 300, 325, 375, 1000]
    # bins_ = [250, 300, 312, 325, 1000]
    bins_ = [250,260,300,350,1000]
    if 'MET' in hist and 'SR' in hist:
        h_temp = h_temp1.Rebin(len(bins_)-1, 'h_temp', array.array('d', bins_))
    elif 'Recoil' in hist and 'CR' in hist:
        h_temp = h_temp1.Rebin(len(bins_)-1, 'h_temp', array.array('d', bins_))
    else:
        h_temp = h_temp1
    return h_temp

def setHistStyle(h_temp2, hist, rebin):
    bins = h_temp2.GetNbinsX()
    if rebin > 1:
        if bins%rebin == 0:
            h_temp_ = h_temp2.Rebin(rebin)
        elif bins%(rebin+1) == 0:
            h_temp_ = h_temp2.Rebin(rebin+1)
        elif bins%(rebin-1) == 0:
            h_temp_ = h_temp2.Rebin(rebin-1)
    else:
        h_temp_ = h_temp2
    return h_temp_


def SetCMSAxis(h, xoffset=1., yoffset=1.):
    h.GetXaxis().SetTitleSize(0.047)
    h.GetYaxis().SetTitleSize(0.047)

    print(type(h))
    if type(h) is ((not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetTitleSize(0.047)

    h.GetXaxis().SetLabelSize(0.047)
    h.GetYaxis().SetLabelSize(0.047)
    if type(h) is ((not ROOT.TGraphAsymmErrors) or (not ROOT.TGraph)):
        h.GetZaxis().SetLabelSize(0.047)

    h.GetXaxis().SetTitleOffset(xoffset)
    h.GetYaxis().SetTitleOffset(yoffset)
    return h


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


def myCanvas1D():
    c = ROOT.TCanvas("myCanvasName", "The Canvas Title", 650, 600)
    c.SetBottomMargin(0.050)
    c.SetRightMargin(0.050)
    c.SetLeftMargin(0.050)
    c.SetTopMargin(0.050)
    return c

#def SetLegend(coordinate_=[.38,.7,.890,.87],ncol=2):


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
    legend.SetTextSize(0.045)
    return legend


def drawenergy1D(is2017, text_="Work in progress 2018", data=True):
    #pt = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt = ROOT.TPaveText(0.0877181, 0.95, 0.9580537, 0.96, "brNDC")
    pt.SetBorderSize(0)
    pt.SetTextAlign(12)
    pt.SetFillStyle(0)
    pt.SetTextFont(52)

    cmstextSize = 0.07
    preliminarytextfize = cmstextSize * 0.7
    lumitextsize = cmstextSize * 0.7
    pt.SetTextSize(cmstextSize)
    text = pt.AddText(0.03, 0.57, "#font[61]{CMS}")

    #pt1 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt1 = ROOT.TPaveText(0.0877181, 0.95, 0.9580537, 0.96, "brNDC")
    pt1.SetBorderSize(0)
    pt1.SetTextAlign(12)
    pt1.SetFillStyle(0)
    pt1.SetTextFont(52)

    pt1.SetTextSize(preliminarytextfize)
    #text1 = pt1.AddText(0.215,0.4,text_)
    text1 = pt1.AddText(0.15, 0.4, text_)

    #pt2 = ROOT.TPaveText(0.0877181,0.9,0.9580537,0.96,"brNDC")
    pt2 = ROOT.TPaveText(0.0877181, 0.95, 0.9580537, 0.96, "brNDC")
    pt2.SetBorderSize(0)
    pt2.SetTextAlign(12)
    pt2.SetFillStyle(0)
    pt2.SetTextFont(52)
    pt2.SetTextFont(42)
    pt2.SetTextSize(lumitextsize)

    pavetext = ''
    if is2017 and data:
        pavetext = str(luminosity_)+' fb^{-1}'+" (13 TeV)"
    if (not is2017) and data:
        pavetext = str(luminosity_)+' fb^{-1}'+"(13 TeV)"

    if is2017 and not data:
        pavetext = "13 TeV"
    if (not is2017) and not data:
        pavetext = "13 TeV"

    if data:
        text3 = pt2.AddText(0.68, 0.5, pavetext)
    if not data:
        text3 = pt2.AddText(0.68, 0.5, pavetext)

    return [pt, pt1, pt2]

def makeplot(loc, hist, titleX, XMIN, XMAX, Rebin, ISLOG, NORATIOPLOT, reg, varBin, row=2):
    # try:

    print('plotting histogram:   ', hist)
    isrebin = True  # bool(varBin)
    if runOn2016:
        files = open("samplelist_2016.txt", "r")
        # files = open("test_2016.txt", "r")
    elif runOn2017:
        files = open("samplelist_2017.txt", "r")
        # files = open("test_2017.txt", "r")
    elif runOn2018:
        files = open("samplelist_2018.txt", "r")

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetFrameLineWidth(3)
    #gStyle->SetErrorX(0)
    ROOT.gStyle.SetLineWidth(1)

    if 'preselR' in hist:
        histolabel = "Pre Selection"
    elif '_SR_1b' in hist:
        histolabel = "SR(1b)"
    elif '_SR_2b' in hist:
        histolabel = "SR(2b)"
    elif 'ZmumuCR_1b' in hist:
        histolabel = "Z(#mu#mu)+1b CR"
    elif 'ZeeCR_1b' in hist:
        histolabel = "Z(ee)+1b CR"
    elif 'WmunuCR_1b' in hist:
        histolabel = "W(#mu#nu)+1b CR"
    elif 'WenuCR_1b' in hist:
        histolabel = "W(e#nu)+1b CR"
    elif 'TopmunuCR_1b' in hist:
        histolabel = "t#bar{t}(#mu#nu)+1b CR"
    elif 'TopenuCR_1b' in hist:
        histolabel = "t#bar{t}(e#nu)+1b CR"
    elif 'ZmumuCR_2b' in hist:
        histolabel = "Z(#mu#mu)+2b CR"
    elif 'ZeeCR_2b' in hist:
        histolabel = "Z(ee)+2b CR"
    elif 'WmunuCR_2b' in hist:
        histolabel = "W(#mu#nu)+2b CR"
    elif 'WenuCR_2b' in hist:
        histolabel = "W(e#nu)+2b CR"
    elif 'TopmunuCR_2b' in hist:
        histolabel = "t#bar{t}(#mu#nu)+2b CR"
    elif 'TopenuCR_2b' in hist:
        histolabel = "t#bar{t}(e#nu)+2b CR"
    elif '_QCDbCR_1b' in hist:
        histolabel = "QCD(1b)"
    elif '_QCDbCR_2b' in hist:
        histolabel = "QCD(2b)"
    else:
        histolabel = "testing"

    xsec = 1.0
    norm = 1.0
    BLINDFACTOR = 1.0
    r_fold = 'rootFiles/'
    DIBOSON = ROOT.TH1F()
    Top = ROOT.TH1F()
    WJets = ROOT.TH1F()
    DYJets = ROOT.TH1F()
    ZJets = ROOT.TH1F()
    STop = ROOT.TH1F()
    GJets = ROOT.TH1F()
    QCD = ROOT.TH1F()
    SMH = ROOT.TH1F()

    DYJets_Hits = []
    ZJets_Hits = []
    WJets_Hists = []
    GJets_Hists = []
    DIBOSON_Hists = []
    STop_Hists = []
    Top_Hists = []
    QCD_Hists = []
    SMH_Hists = []
    MET_Hist = []
    SE_Hist = []

    count = 0
    for file in files.readlines()[:]:
        myFile = path+'/'+file.rstrip()
        Str = str(count)
        exec("f"+Str+"=ROOT.TFile(myFile,'READ')", locals(), globals())
        exec("h_temp=f"+Str+".Get("+"\'"+str(hist)+"\'"+")", locals(), globals())
        exec("h_total_weight=f"+Str+".Get('h_total_mcweight')", locals(), globals())
        total_events = h_total_weight.Integral()
        if 'WJetsToLNu_HT' in file:
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                WJets_Hists.append(h_temp2)
            else:
                WJets_Hists.append(h_temp1)

        elif 'DYJetsToLL_M-50' in file:
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                DYJets_Hits.append(h_temp2)
            else:
                DYJets_Hits.append(h_temp1)

        elif 'ZJetsToNuNu' in file:
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                ZJets_Hits.append(h_temp2)
            else:
                ZJets_Hits.append(h_temp1)

        elif 'GJets_HT' in file:
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*xsec)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                GJets_Hists.append(h_temp2)
            else:
                GJets_Hists.append(h_temp1)

        elif ('WWTo' in file) or ('WZTo' in file) or ('ZZTo' in file) or ('WW_' in file) or ('ZZ_' in file) or ('WZ_' in file):
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                DIBOSON_Hists.append(h_temp2)
            else:
                DIBOSON_Hists.append(h_temp1)

        elif ('ST_t' in file) or ('ST_s' in file):
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                STop_Hists.append(h_temp2)
            else:
                STop_Hists.append(h_temp1)

        elif ('TTTo' in file) or ('TT_TuneCUETP8M2T4' in file):
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                Top_Hists.append(h_temp2)
            else:
                Top_Hists.append(h_temp1)

        elif ('QCD_HT' in file) or ('QCD_bEnriched_HT' in file):
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                QCD_Hists.append(h_temp2)
            else:
                QCD_Hists.append(h_temp1)

        elif 'HToBB' in file:
            xsec = sample_xsec.getXsec(file)
            # print ('file', file ,'xsec', xsec,'\n')
            if (total_events > 0):
                normlisation = (xsec*luminosity)/(total_events)
            else:
                normlisation = 0
            h_temp.Scale(normlisation)
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                SMH_Hists.append(h_temp2)
            else:
                SMH_Hists.append(h_temp1)

        elif 'combined_data_MET' in file:
            h_temp1 = setVarBin(h_temp,hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                MET_Hist.append(h_temp2)
            else:
                MET_Hist.append(h_temp1)

        elif 'combined_data_SE' in file:
            h_temp1 = setVarBin(h_temp, hist)
            if isrebin:
                h_temp2 = setHistStyle(h_temp1, hist, Rebin)
                SE_Hist.append(h_temp2)
            else:
                SE_Hist.append(h_temp1)

        count += 1

###==========================================================add all the histograms regional based ======================================

    for i in range(len(WJets_Hists)):
        if i == 0:
            WJets = WJets_Hists[i]
        else:
            WJets.Add(WJets_Hists[i])
    WJets.Sumw2()

    for i in range(len(DYJets_Hits)):
        if i == 0:
            DYJets = DYJets_Hits[i]
        else:
            DYJets.Add(DYJets_Hits[i])
    DYJets.Sumw2()

    for i in range(len(ZJets_Hits)):
        if i == 0:
            ZJets = ZJets_Hits[i]
        else:
            ZJets.Add(ZJets_Hits[i])
    ZJets.Sumw2()

    for i in range(len(GJets_Hists)):
        if i == 0:
            GJets = GJets_Hists[i]
        else:
            GJets.Add(GJets_Hists[i])
    GJets.Sumw2()

    for i in range(len(DIBOSON_Hists)):
        if i == 0:
            DIBOSON = DIBOSON_Hists[i]
        else:
            DIBOSON.Add(DIBOSON_Hists[i])
    DIBOSON.Sumw2()

    for i in range(len(STop_Hists)):
        if i == 0:
            STop = STop_Hists[i]
        else:
            STop.Add(STop_Hists[i])
    STop.Sumw2()

    for i in range(len(Top_Hists)):
        if i == 0:
            Top = Top_Hists[i]
        else:
            Top.Add(Top_Hists[i])
    Top.Sumw2()

    for i in range(len(QCD_Hists)):
        if i == 0:
            QCD = QCD_Hists[i]
        else:
            QCD.Add(QCD_Hists[i])
    QCD.Sumw2()

    for i in range(len(SMH_Hists)):
        if i == 0:
            SMH = SMH_Hists[i]
        else:
            SMH.Add(SMH_Hists[i])
    SMH.Sumw2()

##=================================================================

    ZJetsCount = ZJets.Integral()
    DYJetsCount = DYJets.Integral()
    WJetsCount = WJets.Integral()
    STopCount = STop.Integral()
    GJetsCount = GJets.Integral()
    TTCount = Top.Integral()
    VVCount = DIBOSON.Integral()
    QCDCount = QCD.Integral()
    SMHCount = SMH.Integral()

    mcsum = ZJetsCount + DYJetsCount + WJetsCount + STopCount + GJetsCount + TTCount + VVCount + QCDCount
    print('mcsum', mcsum)
    total_hists = WJets_Hists + DYJets_Hits + ZJets_Hits + GJets_Hists + DIBOSON_Hists + STop_Hists + Top_Hists + QCD_Hists

    if '_cutFlow' not in str(hist):
        for histo in total_hists:
            histo = set_overflow(histo)

    ROOT.gStyle.SetHistTopMargin(0.1)

#============== CANVAS DECLARATION ===================
    #c12 = ROOT.TCanvas("Hist", "Hist", 0,0,1000,1000)
    c12 = myCanvas1D()

#==================Stack==============================
    hs = ROOT.THStack("hs", " ")

#============Colors for Histos
    DYJets.SetFillColor(ROOT.kGreen+1)
    DYJets.SetLineWidth(0)
    ZJets.SetFillColor(ROOT.kAzure-4)
    ZJets.SetLineWidth(0)
    DIBOSON.SetFillColor(ROOT.kBlue+1)
    DIBOSON.SetLineWidth(0)
    Top.SetFillColor(ROOT.kOrange-1)
    Top.SetLineWidth(0)
    WJets.SetFillColor(ROOT.kViolet-2)
    WJets.SetLineWidth(0)
    STop.SetFillColor(ROOT.kOrange+2)
    STop.SetLineWidth(0)
    GJets.SetFillColor(ROOT.kCyan-8)
    GJets.SetLineWidth(0)
    QCD.SetFillColor(ROOT.kGray+2)
    QCD.SetLineWidth(0)
    SMH.SetFillColor(ROOT.kRed-1)
    SMH.SetLineWidth(0)

#=====================Stack all the histogram =========================

    ZJetsCount = ZJets.Integral()
    DYJetsCount = DYJets.Integral()
    WJetsCount = WJets.Integral()
    STopCount = STop.Integral()
    GJetsCount = GJets.Integral()
    TTCount = Top.Integral()
    VVCount = DIBOSON.Integral()
    QCDCount = QCD.Integral()
    SMHCount = SMH.Integral()
    counts_ = {ZJetsCount:ZJets, DYJetsCount:DYJets, WJetsCount:WJets, STopCount:STop, GJetsCount:GJets, TTCount:Top, VVCount:DIBOSON, QCDCount:QCD, SMHCount:SMH}
    counts_sort = { key:counts_[key] for key in sorted(counts_)}
    for key in counts_sort:
        if key > 0:
            hs.Add(counts_sort[key],"hist")


    hasNoEvents = False
    # if '_MET' in hist:
    #     bins_MET = [200, 250, 350, 500, 1000]
    #     hs = hs.Rebin(len(bins_MET)-1, "hs", array('d', bins_MET))

    Stackhist = hs.GetStack().Last()
    maxi = Stackhist.GetMaximum()
    Stackhist.SetLineWidth(2)
    if (Stackhist.Integral() == 0):
        hasNoEvents = True
        print('No events found! for '+hist+'\n')

# =====================histogram for systematic/ statistical uncertainty ========================
    h_stat_err = Stackhist.Clone("h_stat_err")
    h_stat_err.Sumw2()
    h_stat_err.SetFillColor(ROOT.kGray+3)
    h_stat_err.SetLineColor(ROOT.kGray+3)
    h_stat_err.SetMarkerSize(0)
    h_stat_err.SetFillStyle(3013)
    h_stat_syst_err = h_stat_err.Clone("h_stat_syst_err")

# =============================================

    if(NORATIOPLOT):
        c1_2 = ROOT.TPad("c1_2", "newpad", 0, 0.05, 1, 1)  # 0.993)
        c1_2.SetRightMargin(0.06)
    else:
        c1_2 = ROOT.TPad("c1_2", "newpad", 0, 0.20, 1, 1)
    c1_2.SetBottomMargin(0.09)
    c1_2.SetTopMargin(0.08)
    c1_2.SetLeftMargin(0.12)
    c1_2.SetRightMargin(0.06)
    c1_2.SetLogy(ISLOG)
    c1_2.Draw()
    c1_2.cd()
    for h in hs:
        h = SetCMSAxis(h)
    hs.Draw()
    if makeMuCHplots:
        # if makeSIGplots:
        #     noYieldHisto = bool(('weight' in hist) or ('_up' in hist)
        #                         or ('_down' in hist) or or ('dPhiTrk' in hist) or ('dPhiCalo' in hist) or ('rJet1Pt' in hist))
        # else:
        noYieldHisto = bool(('weight' in hist) or ('_up' in hist)
                                or ('_down' in hist) or ('dPhiTrk' in hist) or ('dPhiCalo' in hist) or ('rJet1Pt' in hist))
    elif makeEleCHplots:
        noYieldHisto = bool(('weight' in hist) or ('_up' in hist)
                            or ('_down' in hist))
    if makeSIGplots:
        if ('MET' in hist) and ('SR' in hist) and not noYieldHisto:
        # if ('MET' in hist) and ('SR' in hist):
        # if ('nJets' in hist) and ('SR' in hist):
            # how many signal points you want to include
            #ma_points = [10,50,100, 150, 200, 250,300, 350, 400, 500, 700, 750,1000]
            ma_points = [150,500]
            sig_leg = SetLegend([.45, .32, .70, .58], ncol=1)
            # sig_leg.SetTextSize(0.030)
            sig_leg.SetHeader("2HDM+a model")
            if runOn2016:
                signal_files_name = [name for name in os.listdir(sig_path) for mapoint in ma_points if 'Ma'+str(mapoint)+'_' in name]
                signal_files_name = sorted(signal_files_name, key=lambda item: (int(item.split('_')[4].strip('Ma')) if item.split('_')[4].strip('Ma').isdigit() else float('inf'), item))
                signal_files = {}
                for name in signal_files_name:
                    signal_files.update({name:ROOT.TFile(sig_path+'/'+name, 'READ')})
                total = {}
                sig_hist = {}
                sig_hist_list = []
                for key in signal_files:
                    total.update({key:signal_files[key].Get('h_total_mcweight')})
                    sig_hist.update({key: signal_files[key].Get(hist)})
                    sig_hist[key].Scale(luminosity*sig_sample_xsec.getSigXsec(key)/total[key].Integral())
            if runOn2017 or runOn2018:
                signal_files_name = [name for name in os.listdir(sig_path) for mapoint in ma_points if 'ma_'+str(mapoint)+'_' in name]
                signal_files_name = sorted(signal_files_name, key=lambda item: (int(item.split('_')[-3]) if item.split('_')[-3].isdigit() else float('inf'), item))
                signal_files = {}
                for name in signal_files_name:
                    signal_files.update({name:ROOT.TFile(sig_path+'/'+name, 'READ')})
                total = {}
                sig_hist = {}
                sig_hist_list = []
                for key in signal_files:
                    total.update({key:signal_files[key].Get('h_total_mcweight')})
                    sig_hist.update({key: signal_files[key].Get(hist)})
                    sig_hist_list.append(sig_hist[key].Scale(luminosity*sig_sample_xsec.getSigXsec_official(key)/total[key].Integral()))

            LineStyling = [(sig_hist[i].SetLineStyle(n), sig_hist[i].SetLineWidth(
                3), sig_hist[i].SetLineColor(n)) for i, n in zip(sig_hist, range(2, len(sig_hist)+2))]
            MarkerStyling = [(sig_hist[i].SetMarkerColor(n), sig_hist[i].SetMarkerStyle(n), sig_hist[i].SetMarkerSize(1.1)) for i, n in zip(sig_hist, range(2, len(sig_hist)+2))]
            if runOn2016:
                sig_leg_list = [sig_leg.AddEntry(sig_hist[his_list], "ma = "+filename.split('_')[4].strip('Ma')+" GeV, mA = "+filename.split('_')[6].strip('MA')+" GeV", "lp") for his_list, filename in zip(sig_hist, signal_files_name)]
            if runOn2017 or runOn2018:
                sig_leg_list = [sig_leg.AddEntry(sig_hist[his_list], "ma = "+filename.split('_')[-3]+" GeV, mA = "+filename.split('_')[-1].strip('.root')+" GeV", "lp") for his_list, filename in zip(sig_hist, signal_files_name)]

            draw_hist = [sig_hist[i].Draw(
                " same Ehist") for i in sig_hist]
            sig_leg.Draw('same')
#####================================= data section =========================
    if 'SR' in reg:
        h_data = hs.GetStack().Last()
    else:
        if dtset == "SE":
            h_data = SE_Hist[0]
        elif dtset == "MET":
            h_data = MET_Hist[0]
    # h_data = hs.GetStack().Last()
    h_data.Sumw2()
    h_data.SetLineColor(1)
    h_data.SetLineWidth(2)
    h_data.SetMarkerSize(1.3)
    h_data.SetMarkerStyle(20)
    h_data = SetCMSAxis(h_data)
    if '_cutFlow' not in str(hist):
        h_data = set_overflow(h_data)
    if(not NORATIOPLOT):
        h_data.Draw("same p e1")
    if (ISLOG):
        if '_cutFlow' in str(hist):
            hs.SetMaximum(1000000000)
            hs.SetMinimum(100)
        else:
            hs.SetMaximum(maxi * 50)
            hs.SetMinimum(1)
    else:
        hs.SetMaximum(maxi * 1.35)
        hs.SetMinimum(0)
    #print ('Data Integral',h_data.Integral())
##=============================== hs setting section =====================
#
    if (not hasNoEvents):
        hs.GetXaxis().SetNdivisions(508)
        if(NORATIOPLOT):
            hs.GetXaxis().SetTitleOffset(1.05)
            hs.GetXaxis().SetTitleFont(42)
            hs.GetXaxis().SetLabelFont(42)
            hs.GetXaxis().SetLabelSize(.03)
            hs.GetXaxis().SetTitle(str(titleX))
            hs.GetXaxis().SetTitleFont(42)
            hs.GetXaxis().SetLabelOffset(.01)
            hs.GetYaxis().SetTitleOffset(0.7)
            hs.GetYaxis().SetTitle("Events/bin")
            hs.GetYaxis().SetTitleSize(0.08)
            hs.GetYaxis().SetTitleFont(42)
            hs.GetYaxis().SetLabelFont(42)
            hs.GetYaxis().SetLabelSize(.04)
        else:
            hs.GetXaxis().SetTitle(str(titleX))
            hs.GetXaxis().SetTitleOffset(0.00)
            hs.GetXaxis().SetTitleFont(42)
            hs.GetXaxis().SetTitleSize(0.05)
            hs.GetXaxis().SetLabelFont(42)
            hs.GetXaxis().SetLabelOffset(.01)
            hs.GetXaxis().SetLabelSize(0.04)
            hs.GetYaxis().SetTitle("Events/bin")
            hs.GetYaxis().SetTitleSize(0.08)
            hs.GetYaxis().SetTitleOffset(0.7)
            hs.GetYaxis().SetTitleFont(42)
            hs.GetYaxis().SetLabelFont(42)
            hs.GetYaxis().SetLabelSize(.05)

        # if not isrebin:
        if True:
            hs.GetXaxis().SetRangeUser(XMIN, XMAX)
        hs.GetXaxis().SetNdivisions(508)

#=============================  legend section =========================================
    DYLegend = "Z(ll)+jets "
    WLegend = "W(l#nu)+jets "
    GLegend = "#gamma+jets "
    ZLegend = "Z(#nu#nu)+jets "
    STLegend = "Single t "
    TTLegend = "t#bar{t} "
    VVLegend = "WW/WZ/ZZ "
    QCDLegend = "QCD "
    SMHLegend = "SMH "

    legend = SetLegend([.50, .58, .93, .92], ncol=2)

    if(not NORATIOPLOT):
        if 'SR' in reg:
            legend.AddEntry(h_data, "bkgSum", "PEL")
        else:
            legend.AddEntry(h_data, "Data", "PEL")
    legend.AddEntry(Top, TTLegend, "f")
    legend.AddEntry(STop, STLegend, "f")
    legend.AddEntry(WJets, WLegend, "f")
    legend.AddEntry(DIBOSON, VVLegend, "f")
    if GJetsCount > 0:
        legend.AddEntry(GJets, GLegend, "f")
    if ZJetsCount > 0:
        legend.AddEntry(ZJets, ZLegend, "f")
    legend.AddEntry(DYJets, DYLegend, "f")
    legend.AddEntry(QCD, QCDLegend, "f")
    legend.AddEntry(SMH, SMHLegend, "f")

    legend.Draw('same')

#=================================================latex section =====================
    t2d = ExtraText(str(histolabel), 0.20, 0.80)
    t2d.SetTextSize(0.06)

    t2d.SetTextAlign(12)
    t2d.SetNDC(ROOT.kTRUE)
    t2d.SetTextFont(42)
    t2d.Draw("same")

    pt = drawenergy1D(True, text_="Internal", data=True)
    for ipt in pt:
        ipt.Draw()
#======================================== ratio log ================

    ratioleg = SetLegend([.72, .80, .90, .90], 1)
    ratioleg.SetTextSize(0.15)

#============================================= statistical error section ======================

    ratiostaterr = h_stat_err.Clone("ratiostaterr")
    ratiostaterr.Sumw2()
    ratiostaterr.SetStats(0)
    ratiostaterr.SetMinimum(0)
    ratiostaterr.SetMarkerSize()
    ratiostaterr.SetFillColor(ROOT.kBlack)
    ratiostaterr.SetFillStyle(3013)
    for i in range(h_stat_err.GetNbinsX()+2):
        ratiostaterr.SetBinContent(i, 0.0)
        if (h_stat_err.GetBinContent(i) > 1e-6):

            binerror = h_stat_err.GetBinError(i)/h_stat_err.GetBinContent(i)
            ratiostaterr.SetBinError(i, binerror)
            # h_stat_err.SetBinError(i, binerror)
        else:
            ratiostaterr.SetBinError(i, 999.)
            # h_stat_err.SetBinError(i, 999.)
#============================================= systematic error section ======================
    if 'MET' in hist or 'Recoil' in hist:
        ratiosysterr = h_stat_err.Clone("ratiosysterr")
        ratiosysterr.Sumw2()
        ratiosysterr.SetStats(0)
        ratiosysterr.SetMinimum(0)
        ratiosysterr.SetMarkerSize(0)
        ratiosysterr.SetFillColor(ROOT.kBlack)
        ratiosysterr.SetFillStyle(3013)
        if 'SR' in reg and '_MET' in hist:
            main_var = '_MET'
            for i in range(h_stat_err.GetNbinsX()):
                binerror2 = 0.0
                ratiosysterr.SetBinContent(i, 0.0)
                if (h_stat_err.GetBinContent(i) > 1e-6):
                    # binerror2 = (pow(h_stat_err.GetBinError(i), 2) +
                    #             pow(syst_dict['CMSyear_fake_b_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_eff_b_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_trig_met_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_Top_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_PU_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECAbsolute_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECAbsolute_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECBBEC1_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECBBEC1_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECEC2_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECEC2_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECFlavorQCD_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECHF_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECHF_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECRelativeBal_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECRelativeSample_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             # pow(syst_dict['Res_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['En_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2)
                    #             )
                    binerror = math.sqrt(binerror2)
                    ratiosysterr.SetBinError(
                        i, binerror/h_stat_err.GetBinContent(i))
                    h_stat_syst_err.SetBinError(
                        i, binerror/h_stat_err.GetBinContent(i))
                else:
                    ratiosysterr.SetBinError(i, 999.)
                    h_stat_syst_err.SetBinError(i, 999.)
        elif 'CR' in reg and '_Recoil' in hist:
            main_var = '_Recoil'
            for i in range(1, h_stat_err.GetNbinsX()+1):
                binerror2 = 0.0
                ratiosysterr.SetBinContent(i, 0.0)
                if (h_stat_err.GetBinContent(i) > 1e-6):
                    # binerror2 = (pow(h_stat_err.GetBinError(i), 2) +
                    #             pow(syst_dict['CMSyear_fake_b_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_eff_b_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_Top_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_trig_met_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_PU_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECAbsolute_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECAbsolute_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECBBEC1_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECBBEC1_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECEC2_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECEC2_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECFlavorQCD_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECHF_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECHF_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECRelativeBal_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['JECRelativeSample_year_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             # pow(syst_dict['Res_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['En_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_trig_ele_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_EleID_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_EleRECO_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_MuID_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_MuISO_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2) +
                    #             pow(syst_dict['CMSyear_MuTRK_syst_'+reg+main_var][i-1]*h_stat_err.GetBinContent(i), 2)
                    #             )
                    binerror = math.sqrt(binerror2)
                    ratiosysterr.SetBinError(i, binerror/h_stat_err.GetBinContent(i))
                    h_stat_syst_err.SetBinError(i, binerror/h_stat_err.GetBinContent(i))
                else:
                    ratiosysterr.SetBinError(i, 999.)
                    h_stat_syst_err.SetBinError(i, 999.)
    if 'MET' in hist or 'Recoil' in hist :
        # ratioleg.AddEntry(ratiosysterr, "stat + syst", "f")
        ratioleg.AddEntry(ratiosysterr, "stat", "f")
    else:
        ratioleg.AddEntry(ratiostaterr, "stat", "f")

    if(not NORATIOPLOT):
        if 'MET' in hist or 'Recoil' in hist :
            h_stat_err.Draw("same E2")
        else:
            h_stat_syst_err.Draw("same E2")

#============================================= Lower Tpad Decalaration ====================================
    if(not NORATIOPLOT):
        c12.cd()
        DataMC = h_data.Clone()
        DataMC.Add(Stackhist, -1)   # remove for data/mc
        #DataMCPre = h_data.Clone()
        DataMC.Divide(Stackhist)
        DataMC.GetYaxis().SetTitle("#frac{Data-Pred}{Pred}")
        DataMC.GetYaxis().SetTitleSize(0.12)
        DataMC.GetYaxis().SetTitleOffset(0.42)
        DataMC.GetYaxis().SetTitleFont(42)
        DataMC.GetYaxis().SetLabelSize(0.12)
        DataMC.GetYaxis().CenterTitle()
        DataMC.GetXaxis().SetTitle(str(titleX))
        DataMC.GetXaxis().SetLabelSize(0.14)
        DataMC.GetXaxis().SetTitleSize(0.16)
        DataMC.GetXaxis().SetTitleOffset(1)
        DataMC.GetXaxis().SetTitleFont(42)
        DataMC.GetXaxis().SetTickLength(0.07)
        DataMC.GetXaxis().SetLabelFont(42)
        DataMC.GetYaxis().SetLabelFont(42)

    c1_1 = ROOT.TPad("c1_1", "newpad", 0, 0.00, 1, 0.3)
    if (not NORATIOPLOT):
        c1_1.Draw()
    c1_1.cd()
    c1_1.Range(-7.862408, -629.6193, 53.07125, 486.5489)
    c1_1.SetFillColor(0)
    c1_1.SetTicky(1)
    c1_1.SetLeftMargin(0.12)
    c1_1.SetRightMargin(0.06)
    c1_1.SetTopMargin(0.00)
    c1_1.SetBottomMargin(0.42)
    c1_1.SetFrameFillStyle(0)
    c1_1.SetFrameBorderMode(0)
    c1_1.SetFrameFillStyle(0)
    c1_1.SetFrameBorderMode(0)
    c1_1.SetLogy(0)

    if(not NORATIOPLOT):
        if (0):  # if(VARIABLEBINS)
            c1_1.SetLogx(0)
            DataMC.GetXaxis().SetMoreLogLabels()
            DataMC.GetXaxis().SetNoExponent()
            DataMC.GetXaxis().SetNdivisions(508)
        # if not isrebin:
        if True:
            DataMC.GetXaxis().SetRangeUser(XMIN, XMAX)
        DataMC.SetMarkerSize(1.5)
        DataMC.SetMarkerStyle(20)
        DataMC.SetMarkerColor(1)
        DataMC.SetMinimum(-1.08)
        DataMC.SetMaximum(1.08)
        DataMC.GetXaxis().SetNdivisions(508)
        DataMC.GetYaxis().SetNdivisions(505)
        DataMC.Draw("P e1")
        if 'MET' in hist or 'Recoil' in hist:
            ratiosysterr.Draw("e2 same")
        else:
            ratiostaterr.Draw("e2 same")
        DataMC.Draw("P e1 same")
        # line1 = ROOT.TLine(XMIN, 0.2, XMAX, 0.2)
        # line2 = ROOT.TLine(XMIN, -0.2, XMAX, -0.2)
        # line1.SetLineStyle(2)
        # line1.SetLineColor(2)
        # line1.SetLineWidth(2)
        # line2.SetLineStyle(2)
        # line2.SetLineColor(2)
        # line2.SetLineWidth(2)
        # line1.Draw("same")
        # line2.Draw("same")
        ratioleg.Draw("same")
    c12.Draw()
    plot = str(hist)
    noPdfPng = True
    if ('Up' in str(hist) or 'Down' in str(hist) or 'CMSyear' in str(hist)):
        noPdfPng = False
    if not os.path.exists('plots_norm/'+histVersion+'/bbDMPng/'+reg):
        os.makedirs('plots_norm/'+histVersion+'/bbDMPng/'+reg)
    if not os.path.exists('plots_norm/'+histVersion+'/bbDMPdf/'+reg):
        os.makedirs('plots_norm/'+histVersion+'/bbDMPdf/'+reg)
    if not os.path.exists('plots_norm/'+histVersion+'/bbDMRoot/'):
        os.makedirs('plots_norm/'+histVersion+'/bbDMRoot/')
    if (ISLOG == 0) and noPdfPng:
        c12.SaveAs('plots_norm/'+histVersion+'/bbDMPdf/'+reg+'/'+plot+'.pdf')
        c12.SaveAs('plots_norm/'+histVersion+'/bbDMPng/'+reg+'/'+plot+'.png')
        print("Saved. \n")
    if (ISLOG == 1) and noPdfPng:
        c12.SaveAs('plots_norm/'+histVersion+'/bbDMPdf/'+reg+'/'+plot+'_log.pdf')
        c12.SaveAs('plots_norm/'+histVersion+'/bbDMPng/'+reg+'/'+plot+'_log.png')
    fshape = ROOT.TFile('plots_norm/'+histVersion+'/bbDMRoot/'+plot+'.root', "RECREATE")
    fshape.cd()
    Stackhist.SetNameTitle("bkgSum", "bkgSum")
    Stackhist.Write()
    DIBOSON.SetNameTitle("DIBOSON", "DIBOSON")
    DIBOSON.Write()
    ZJets.SetNameTitle("ZJets", "ZJets")
    ZJets.Write()
    GJets.SetNameTitle("GJets", "GJets")
    GJets.Write()
    QCD.SetNameTitle("QCD", "QCD")
    QCD.Write()
    SMH.SetNameTitle("SMH", "SMH")
    SMH.Write()
    STop.SetNameTitle("STop", "STop")
    STop.Write()
    Top.SetNameTitle("Top", "Top")
    Top.Write()
    WJets.SetNameTitle("WJets", "WJets")
    WJets.Write()
    DYJets.SetNameTitle("DYJets", "DYJets")
    DYJets.Write()
    data_obs = h_data
    data_obs.SetNameTitle("data_obs", "data_obs")
    data_obs.Write()
    if makeSIGplots and ('MET' in hist) and ('SR' in hist) and not noYieldHisto and ('SR_1b' in reg or 'SR_2b' in reg):
    # if makeSIGplots and ('MET' in hist) and ('SR' in hist) and ('SR_1b' in reg or 'SR_2b' in reg):
    # if makeSIGplots and ('nJets' in hist) and ('SR' in hist) and ('SR_1b' in reg or 'SR_2b' in reg):
        if runOn2016: [sig_hist[h_key].SetNameTitle(h_key.split('5f_')[-1].split('_tanb35_')[0], h_key.split('5f_')[-1].split('_tanb35_')[0]) for h_key in  sig_hist]
        else: [sig_hist[h_key].SetNameTitle(h_key.partition('_pythia8_')[-1].partition('.root')[0], h_key.partition('_pythia8_')[-1].partition('.root')[0]) for h_key in  sig_hist]
        [sig_hist[h_key].Write() for h_key in sig_hist]
    fshape.Write()
    fshape.Close()
    c12.Close()
    print('\n')
    syst_Unc = ('Up' not in hist) or ('Down' not in hist)
    if (('MET' in hist and 'SR' in hist) or ('Recoil' in hist)) and syst_Unc and not noYieldHisto:
        bkg_list = { 'Top': Top, 'STop': STop, 'WJets': WJets, 'DIBOSON': DIBOSON, 'GJets': GJets, 'ZJets': ZJets, 'DYJets': DYJets, 'QCD': QCD, 'SMH': SMH,'Total_Bkg': Stackhist,'data_obs': h_data}
        bkg_list_name = { 'Top': "$t\\bar{t}$", 'STop': "Single$t$", 'WJets': "W(l$\\nu$)+jets", 'DIBOSON':"WW/WZ/ZZ", 'GJets': "$\\gamma$+jets", 'ZJets': "Z($\\nu\\nu$)+jets", 'DYJets': "Z(ll)+jets", 'QCD': "QCD", 'SMH': "SMH" ,'Total_Bkg': "Total_Bkg",'data_obs': "data_obs",}
        if 'SR_1b' in str(hist): reg_name = 'SR-(1b)'
        elif 'SR_2b' in str(hist): reg_name = 'SR-(2b)'
        elif 'ZmumuCR_1b' in str(hist): reg_name = 'Z$\\mu\\mu$-CR-(1b)'
        elif 'ZmumuCR_2b' in str(hist): reg_name = 'Z$\\mu\\mu$-CR-(2b)'
        elif 'TopmunuCR_1b' in str(hist): reg_name = 't$\\bar{t}(\\mu)$-CR-(1b)'
        elif 'TopmunuCR_2b' in str(hist): reg_name = 't$\\bar{t}(\\mu)$-CR-(2b)'
        elif 'WmunuCR_1b' in str(hist): reg_name =  'W-$(\\mu\\nu)$-CR-(1b)'
        elif 'WmunuCR_2b' in str(hist): reg_name = 'W-$(\\mu\\nu)$-CR-(2b)'
        elif 'ZeeCR_1b' in str(hist): reg_name = 'Zee-CR-(1b)'
        elif 'ZeeCR_2b' in str(hist): reg_name = 'Zee-CR-(2b)'
        elif 'TopenuCR_1b' in str(hist): reg_name = 't$\\bar{t}(e)$-CR-(1b)'
        elif 'TopenuCR_2b' in str(hist): reg_name = 't$\\bar{t}(e)$-CR-(2b)'
        elif 'WenuCR_1b' in str(hist): reg_name = 'W-$(e\\nu)$-CR-(1b)'
        elif 'WenuCR_2b' in str(hist): reg_name = 'W-$(e\\nu)$-CR-(2b)'
        yield_outfile.write('region '+str(reg_name)+'\n')
        yield_outfile_binwise.write('region '+str(hist)+'\n')
        if makeSIGplots and ('MET' in hist) and ('SR' in hist) and not noYieldHisto and ('SR_1b' in reg or 'SR_2b' in reg):
            for h_key in sig_hist:
                bkg_list.update({h_key.split('5f_')[-1].split('_tanb35_')[0]: sig_hist[h_key]})
                bkg_list_name.update({h_key.split('5f_')[-1].split('_tanb35_')[0]: h_key.split('5f_')[-1].split('_tanb35_')[0]})
        yield_outfile_binwise.write('       Bin1   Bin2   Bin3   Bin4\n')
        for key in bkg_list:
            bin_cont = [bkg_list[key].GetBinContent(i)>0 for i in range(1,5)]
            if any(bin_cont):
                yield_outfile_binwise.write(str(bkg_list_name[key])+'   '+str.format('{0:.3f}', bkg_list[key].GetBinContent(1))+'\xb1'+str.format('{0:.3f}', bkg_list[key].GetBinError(1))+'   '+str.format('{0:.3f}', bkg_list[key].GetBinContent(2))+'\xb1'+str.format('{0:.3f}', bkg_list[key].GetBinError(2))+'   '+str.format('{0:.3f}', bkg_list[key].GetBinContent(3))+'\xb1'+str.format('{0:.3f}', bkg_list[key].GetBinError(3))+'   '+str.format('{0:.3f}', bkg_list[key].GetBinContent(4))+'\xb1'+str.format('{0:.3f}', bkg_list[key].GetBinError(4))+'\n')
        for key in bkg_list:
            binerror = 0.00
            bkg_list[key].Rebin(bkg_list[key].GetNbinsX())
            binerror = (bkg_list[key].GetBinError(1))
            # if bkg_list[key].GetBinContent(1) > 0.0:
            yield_outfile.write(str(bkg_list_name[key])+' '+str.format('{0:.3f}', bkg_list[key].GetBinContent(1))+'\xb1'+str.format('{0:.3f}', bkg_list[key].GetBinError(1))+'\n')
        yield_outfile_binwise.write('\n')
        yield_outfile.write('\n')

 #=======================================================================


######################################################################

regions = []
PUreg = []
if makeMuCHplots:
    regions += ['preselR', 'SR_1b', 'SR_2b','ZmumuCR_1b', 'ZmumuCR_2b',
                'TopmunuCR_1b', 'TopmunuCR_2b', 'WmunuCR_1b', 'WmunuCR_2b', 'QCDbCR_1b', 'QCDbCR_2b']
if makeEleCHplots:
    regions += ['ZeeCR_1b', 'ZeeCR_2b', 'TopenuCR_1b',
                'TopenuCR_2b', 'WenuCR_1b', 'WenuCR_2b']
# makeplot("reg_SR_2b_MET",'h_reg_SR_2b_MET','p_{T}^{miss} (GeV)',250.,1000.,1,1,0,'SR_2b',varBin=False)
for reg in regions:
    if '_2b' in reg:
        rebin = 1
    else:
        rebin = 1
    if 'SR_' in reg or 'preselR' in reg or 'QCDCR' in reg:
        makeplot('reg_'+reg+'_cutFlow', 'h_reg_'+reg+'_cutFlow',
                 'CutFlow', 0, 8, 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET', 'h_reg_'+reg+'_MET',
                 ' p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_METPhi', 'h_reg_'+reg+'_METPhi',
                 ' p_{T}^{miss} #phi', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhiTrk_pfMET', 'h_reg_'+reg+'_dPhiTrk_pfMET',
                 '#Delta#phi (Trkp_{T}^{miss} - p_{T}^{miss})', -3.2, 3.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhiCalo_pfMET', 'h_reg_'+reg+'_dPhiCalo_pfMET',
                 '#Delta#phi(Calop_{T}^{miss} - pfp_{T}^{miss})', -3.2, 3.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_eff_bUp', 'h_reg_'+reg+'_MET_CMSyear_eff_bUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_eff_bDown', 'h_reg_'+reg+'_MET_CMSyear_eff_bDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_fake_bUp', 'h_reg_'+reg+'_MET_CMSyear_fake_bUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_fake_bDown', 'h_reg_'+reg+'_MET_CMSyear_fake_bDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_EWKUp', 'h_reg_'+reg+'_MET_EWKUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_EWKDown', 'h_reg_'+reg+'_MET_EWKDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_TopUp', 'h_reg_'+reg+'_MET_CMSyear_TopUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_TopDown', 'h_reg_'+reg+'_MET_CMSyear_TopDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_trig_metUp', 'h_reg_'+reg+'_MET_CMSyear_trig_metUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_trig_metDown', 'h_reg_'+reg+'_MET_CMSyear_trig_metDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_PUUp', 'h_reg_'+reg+'_MET_CMSyear_PUUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_PUDown', 'h_reg_'+reg+'_MET_CMSyear_PUDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_MET_JECUp', 'h_reg_'+reg+'_MET_JECUp',
        #          'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_MET_JECDown', 'h_reg_'+reg+'_MET_JECDown',
        #          'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECAbsoluteUp', 'h_reg_'+reg+'_MET_JECAbsoluteUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECAbsolute_yearUp', 'h_reg_'+reg +
                 '_MET_JECAbsolute_yearUp', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECBBEC1Up', 'h_reg_'+reg+'_MET_JECBBEC1Up',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECBBEC1_yearUp', 'h_reg_'+reg+'_MET_JECBBEC1_yearUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECEC2Up', 'h_reg_'+reg+'_MET_JECEC2Up',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECEC2_yearUp', 'h_reg_'+reg+'_MET_JECEC2_yearUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECFlavorQCDUp', 'h_reg_'+reg+'_MET_JECFlavorQCDUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECHFUp', 'h_reg_'+reg+'_MET_JECHFUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECHF_yearUp', 'h_reg_'+reg+'_MET_JECHF_yearUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECRelativeBalUp', 'h_reg_'+reg+'_MET_JECRelativeBalUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECRelativeSample_yearUp', 'h_reg_'+reg +
                 '_MET_JECRelativeSample_yearUp', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECAbsoluteDown', 'h_reg_'+reg+'_MET_JECAbsoluteDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECAbsolute_yearDown', 'h_reg_'+reg +
                 '_MET_JECAbsolute_yearDown', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECBBEC1Down', 'h_reg_'+reg+'_MET_JECBBEC1Down',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECBBEC1_yearDown', 'h_reg_'+reg +
                 '_MET_JECBBEC1_yearDown', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECEC2Down', 'h_reg_'+reg+'_MET_JECEC2Down',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECEC2_yearDown', 'h_reg_'+reg+'_MET_JECEC2_yearDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECFlavorQCDDown', 'h_reg_'+reg+'_MET_JECFlavorQCDDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECHFDown', 'h_reg_'+reg+'_MET_JECHFDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECHF_yearDown', 'h_reg_'+reg+'_MET_JECHF_yearDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECRelativeBalDown', 'h_reg_'+reg +
                 '_MET_JECRelativeBalDown', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_JECRelativeSample_yearDown', 'h_reg_'+reg +
                 '_MET_JECRelativeSample_yearDown', 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_MET_ResUp', 'h_reg_'+reg+'_MET_ResUp',
        #          'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_MET_ResDown', 'h_reg_'+reg+'_MET_ResDown',
        #          'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_EnUp', 'h_reg_'+reg+'_MET_EnUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_EnDown', 'h_reg_'+reg+'_MET_EnDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_mu_scaleUp', 'h_reg_'+reg+'_MET_CMSyear_mu_scaleUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_mu_scaleDown', 'h_reg_'+reg+'_MET_CMSyear_mu_scaleDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_pdfUp', 'h_reg_'+reg+'_MET_CMSyear_pdfUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_pdfDown', 'h_reg_'+reg+'_MET_CMSyear_pdfDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_prefireUp', 'h_reg_'+reg+'_MET_CMSyear_prefireUp',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET_CMSyear_prefireDown', 'h_reg_'+reg+'_MET_CMSyear_prefireDown',
                 'p_{T}^{miss} (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        if ('QCDCR' in reg):
            makeplot('reg_'+reg+'_min_dPhi', 'h_reg_'+reg+'_min_dPhi',
                     'min_dPhi', 0, 0.6, rebin, 1, 0, reg, varBin=False)
        else:
            makeplot('reg_'+reg+'_min_dPhi', 'h_reg_'+reg+'_min_dPhi',
                     'min_dPhi', 0, 4, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Pt', 'h_reg_'+reg+'_Jet1Pt',
                 'JET1 p_{T} (GeV)', 30., 800., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_delta_pfCalo', 'h_reg_'+reg+'_delta_pfCalo',
                 'PFp_{T}^{miss}-Calop_{T}^{miss}/Recoil', 0., 1.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Eta', 'h_reg_'+reg+'_Jet1Eta',
                 'JET1 #eta', -2.5, 2.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Phi', 'h_reg_'+reg+'_Jet1Phi',
                 'JET1 #phi', -3.14, 3.14, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1deepCSV', 'h_reg_'+reg+'_Jet1deepCSV',
                 'JET1 deepCSV', 0, 1.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NHadEF', 'h_reg_'+reg+'_Jet1NHadEF',
                 'Jet1NHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CHadEF', 'h_reg_'+reg+'_Jet1CHadEF',
                 'Jet1CHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CEmEF', 'h_reg_'+reg+'_Jet1CEmEF',
                 'Jet1CEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NEmEF', 'h_reg_'+reg+'_Jet1NEmEF',
                 'Jet1NEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CMulti', 'h_reg_'+reg+'_Jet1CMulti',
                 'Jet1CMulti', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NMultiplicity', 'h_reg_'+reg+'_Jet1NMultiplicity',
                 'Jet1NMultiplicity', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2Pt', 'h_reg_'+reg+'_Jet2Pt',
                 'JET2 p_{T} (GeV)', 30., 800., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2Eta', 'h_reg_'+reg+'_Jet2Eta',
                 'JET2 #eta', -2.5, 2.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2Phi', 'h_reg_'+reg+'_Jet2Phi',
                 'JET2 #phi', -3.14, 3.14, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2deepCSV', 'h_reg_'+reg+'_Jet2deepCSV',
                 'JET2 deepCSV', 0, 1.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2NHadEF', 'h_reg_'+reg+'_Jet2NHadEF',
                 'Jet2NHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2CHadEF', 'h_reg_'+reg+'_Jet2CHadEF',
                 'Jet2CHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2CEmEF', 'h_reg_'+reg+'_Jet2CEmEF',
                 'Jet2CEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2NEmEF', 'h_reg_'+reg+'_Jet2NEmEF',
                 'Jet2NEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2CMulti', 'h_reg_'+reg+'_Jet2CMulti',
                 'Jet2CMulti', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet2NMultiplicity', 'h_reg_'+reg+'_Jet2NMultiplicity',
                 'Jet2NMultiplicity', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_nJets', 'h_reg_'+reg+'_nJets',
                 'nJets', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NEle', 'h_reg_'+reg+'_NEle',
                 'NEle', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NMu', 'h_reg_'+reg+'_NMu', 'NMu',
                 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_nPho', 'h_reg_'+reg+'_nPho',
                 'nPho', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NTau', 'h_reg_'+reg+'_NTau',
                 'NTau', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_ratioPtJet21', 'h_reg_'+reg+'_ratioPtJet21',
                 'JET2 p_{T}/JET1 p_{T} ', 0., 1.0, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhiJet12', 'h_reg_'+reg+'_dPhiJet12',
                 'JET1#phi - JET2#phi', -7.5, 7.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dEtaJet12', 'h_reg_'+reg+'_dEtaJet12',
                 'JET1#eta - JET2#eta', -7.5, 7.5, rebin, 1, 0, reg, varBin=False)
        if ('SR_1b' in reg):
            makeplot('reg_'+reg+'_isjet1EtaMatch', 'h_reg_'+reg+'_isjet1EtaMatch',
                     'JET1#eta X JET2#eta', 0, 1, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet2', 'h_reg_'+reg+'_M_Jet1Jet2',
                     'Inv Mass(Jet1, Jet2)', 0, 2000, 5, 1, 0, reg, varBin=False)
        elif ('SR_2b' in reg):
            makeplot('reg_'+reg+'_isjet2EtaMatch', 'h_reg_'+reg+'_isjet2EtaMatch',
                     'JET1#eta X JET3#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet3', 'h_reg_'+reg+'_M_Jet1Jet3',
                     'Inv Mass(Jet1, Jet3)', 0, 2000, 10, 1, 0, reg, varBin=False)
            # makeplot('reg_'+reg+'_M_Jet1Jet2', 'h_reg_'+reg+'_M_Jet1Jet2',
            #          'Inv Mass(Jet1, Jet2)', 0, 2000, 5, 1, 0, reg, varBin=False)
        elif ('preselR' in reg):
            makeplot('reg_'+reg+'_isjet1EtaMatch', 'h_reg_'+reg+'_isjet1EtaMatch',
                     'JET1#eta X JET3#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet3', 'h_reg_'+reg+'_M_Jet1Jet3',
                     'Inv Mass(Jet1, Jet2)', 0, 2000, 5, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_isjet2EtaMatch', 'h_reg_'+reg+'_isjet2EtaMatch',
                     'JET1#eta X JET3#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet3', 'h_reg_'+reg+'_M_Jet1Jet3',
                     'Inv Mass(Jet1, Jet3)', 0, 2000, 5, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_rJet1PtMET', 'h_reg_'+reg+'_rJet1PtMET',
                 'Jet1 p_{T}/MET', 0, 20, 5, 1, 0, reg, varBin=False)
    else:
        makeplot('reg_'+reg+'_cutFlow', 'h_reg_'+reg+'_cutFlow',
                 'CutFlow', 0, 12, 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_MET', 'h_reg_'+reg+'_MET',
                 'Real p_{T}^{miss} (GeV)', 0., 700., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_METPhi', 'h_reg_'+reg+'_METPhi',
                 ' p_{T}^{miss} #phi', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhiTrk_pfMET', 'h_reg_'+reg+'_dPhiTrk_pfMET',
                 '#Delta#phi (Trkp_{T}^{miss} - p_{T}^{miss})', -3.2, 3.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhiCalo_pfMET', 'h_reg_'+reg+'_dPhiCalo_pfMET',
                 '#Delta#phi(Calop_{T}^{miss} - pfp_{T}^{miss})', -3.2, 3.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil', 'h_reg_'+reg+'_Recoil',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_eff_bUp', 'h_reg_'+reg+'_Recoil_CMSyear_eff_bUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_eff_bDown', 'h_reg_'+reg+'_Recoil_CMSyear_eff_bDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_fake_bUp', 'h_reg_'+reg+'_Recoil_CMSyear_fake_bUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_fake_bDown', 'h_reg_'+reg+'_Recoil_CMSyear_fake_bDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_EWKUp', 'h_reg_'+reg+'_Recoil_EWKUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_EWKDown', 'h_reg_'+reg+'_Recoil_EWKDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_TopUp', 'h_reg_'+reg+'_Recoil_CMSyear_TopUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_TopDown', 'h_reg_'+reg+'_Recoil_CMSyear_TopDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_trig_metUp', 'h_reg_'+reg +
                 '_Recoil_CMSyear_trig_metUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_trig_metDown', 'h_reg_'+reg +
                 '_Recoil_CMSyear_trig_metDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_PUUp', 'h_reg_'+reg+'_Recoil_CMSyear_PUUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_PUDown', 'h_reg_'+reg+'_Recoil_CMSyear_PUDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_Recoil_JECUp', 'h_reg_'+reg+'_Recoil_JECUp',
        #          'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_Recoil_JECDown', 'h_reg_'+reg+'_Recoil_JECDown',
        #          'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECAbsoluteUp', 'h_reg_'+reg +
                 '_Recoil_JECAbsoluteUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECAbsolute_yearUp', 'h_reg_'+reg +
                 '_Recoil_JECAbsolute_yearUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECBBEC1Up', 'h_reg_'+reg +
                 '_Recoil_JECBBEC1Up', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECBBEC1_yearUp', 'h_reg_'+reg +
                 '_Recoil_JECBBEC1_yearUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECEC2Up', 'h_reg_'+reg +
                 '_Recoil_JECEC2Up', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECEC2_yearUp', 'h_reg_'+reg +
                 '_Recoil_JECEC2_yearUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECFlavorQCDUp', 'h_reg_'+reg +
                 '_Recoil_JECFlavorQCDUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECHFUp', 'h_reg_'+reg+'_Recoil_JECHFUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECHF_yearUp', 'h_reg_'+reg +
                 '_Recoil_JECHF_yearUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECRelativeBalUp', 'h_reg_'+reg +
                 '_Recoil_JECRelativeBalUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECRelativeSample_yearUp', 'h_reg_'+reg +
                 '_Recoil_JECRelativeSample_yearUp', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECAbsoluteDown', 'h_reg_'+reg +
                 '_Recoil_JECAbsoluteDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECAbsolute_yearDown', 'h_reg_'+reg +
                 '_Recoil_JECAbsolute_yearDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECBBEC1Down', 'h_reg_'+reg +
                 '_Recoil_JECBBEC1Down', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECBBEC1_yearDown', 'h_reg_'+reg +
                 '_Recoil_JECBBEC1_yearDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECEC2Down', 'h_reg_'+reg +
                 '_Recoil_JECEC2Down', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECEC2_yearDown', 'h_reg_'+reg +
                 '_Recoil_JECEC2_yearDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECFlavorQCDDown', 'h_reg_'+reg +
                 '_Recoil_JECFlavorQCDDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECHFDown', 'h_reg_'+reg +
                 '_Recoil_JECHFDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECHF_yearDown', 'h_reg_'+reg +
                 '_Recoil_JECHF_yearDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECRelativeBalDown', 'h_reg_'+reg +
                 '_Recoil_JECRelativeBalDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_JECRelativeSample_yearDown', 'h_reg_'+reg +
                 '_Recoil_JECRelativeSample_yearDown', 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_Recoil_ResUp', 'h_reg_'+reg+'_Recoil_ResUp',
        #          'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        # makeplot('reg_'+reg+'_Recoil_ResDown', 'h_reg_'+reg+'_Recoil_ResDown',
        #          'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_EnUp', 'h_reg_'+reg+'_Recoil_EnUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_EnDown', 'h_reg_'+reg+'_Recoil_EnDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_mu_scaleUp', 'h_reg_'+reg+'_Recoil_CMSyear_mu_scaleUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_mu_scaleDown', 'h_reg_'+reg+'_Recoil_CMSyear_mu_scaleDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_pdfUp', 'h_reg_'+reg+'_Recoil_CMSyear_pdfUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_pdfDown', 'h_reg_'+reg+'_Recoil_CMSyear_pdfDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_prefireUp', 'h_reg_'+reg+'_Recoil_CMSyear_prefireUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_prefireDown', 'h_reg_'+reg+'_Recoil_CMSyear_prefireDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_trig_eleUp', 'h_reg_'+reg+'_Recoil_CMSyear_trig_eleUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_trig_eleDown', 'h_reg_'+reg+'_Recoil_CMSyear_trig_eleDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_EleIDUp', 'h_reg_'+reg+'_Recoil_CMSyear_EleIDUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_EleIDDown', 'h_reg_'+reg+'_Recoil_CMSyear_EleIDDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_EleRECOUp', 'h_reg_'+reg+'_Recoil_CMSyear_EleRECOUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_EleRECODown', 'h_reg_'+reg+'_Recoil_CMSyear_EleRECODown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuIDUp', 'h_reg_'+reg+'_Recoil_CMSyear_MuIDUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuIDDown', 'h_reg_'+reg+'_Recoil_CMSyear_MuIDDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuISOUp', 'h_reg_'+reg+'_Recoil_CMSyear_MuISOUp',
                    'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuISODown', 'h_reg_'+reg+'_Recoil_CMSyear_MuISODown',
                    'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuTRKUp', 'h_reg_'+reg+'_Recoil_CMSyear_MuTRKUp',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Recoil_CMSyear_MuTRKDown', 'h_reg_'+reg+'_Recoil_CMSyear_MuTRKDown',
                 'Recoil (GeV)', 250., 1000., 1, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_min_dPhi', 'h_reg_'+reg+'_min_dPhi',
                 'min_dPhi', 0, 4, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Pt', 'h_reg_'+reg+'_Jet1Pt',
                 'JET1 p_{T} (GeV)', 30., 800., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_delta_pfCalo', 'h_reg_'+reg+'_delta_pfCalo',
                 'PFp_{T}^{miss}-Calop_{T}^{miss}/Recoil', 0., 1.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Eta', 'h_reg_'+reg+'_Jet1Eta',
                 'JET1 #eta', -2.5, 2.5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_dPhi_lep1_MET', 'h_reg_'+reg+'_dPhi_lep1_MET',
                 '#Delta(lepton1,p_{T}^{Miss})', 0, 5, rebin, 1, 0, reg, varBin=False)
        if '2b' in reg and 'Z' in reg:
            makeplot('reg_'+reg+'_dPhi_lep2_MET', 'h_reg_'+reg+'_dPhi_lep2_MET',
                     '#Delta(lepton2,p_{T}^{Miss})', 0, 5, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1Phi', 'h_reg_'+reg+'_Jet1Phi',
                 'JET1 #phi', -3.14, 3.14, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1deepCSV', 'h_reg_'+reg+'_Jet1deepCSV',
                 'JET1 deepCSV', 0, 1.2, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NHadEF', 'h_reg_'+reg+'_Jet1NHadEF',
                 'Jet1NHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CHadEF', 'h_reg_'+reg+'_Jet1CHadEF',
                 'Jet1CHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CEmEF', 'h_reg_'+reg+'_Jet1CEmEF',
                 'Jet1CEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NEmEF', 'h_reg_'+reg+'_Jet1NEmEF',
                 'Jet1NEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1CMulti', 'h_reg_'+reg+'_Jet1CMulti',
                 'Jet1CMulti', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_Jet1NMultiplicity', 'h_reg_'+reg+'_Jet1NMultiplicity',
                 'Jet1NMultiplicity', 0, 50, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_lep1_pT', 'h_reg_'+reg+'_lep1_pT',
                 'lepton1 p_{T}', 0, 500, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_lep1_Phi', 'h_reg_'+reg+'_lep1_Phi',
                 'lepton1 #phi', -3.14, 3.14, rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_nJets', 'h_reg_'+reg+'_nJets',
                 'nJets', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NEle', 'h_reg_'+reg+'_NEle',
                 'NEle', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NMu', 'h_reg_'+reg+'_NMu', 'NMu',
                 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_nPho', 'h_reg_'+reg+'_nPho',
                 'nPho', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_NTau', 'h_reg_'+reg+'_NTau',
                 'NTau', 0., 10., rebin, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_nPV', 'h_reg_'+reg+'_nPV',
                 'Before PU reweighting', 0., 70., 2, 0, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_PUnPV', 'h_reg_'+reg+'_PUnPV',
                 'After PU reweighting', 0., 70., 2, 0, 0, reg, varBin=False)
        if ('W' in reg) or ('Top' in reg):
            makeplot('reg_'+reg+'_Wmass', 'h_reg_'+reg+'_Wmass',
                     'W candidate mass (GeV)', 0., 165., rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_WpT', 'h_reg_'+reg+'_WpT',
                     'W candidate p_{T} (GeV)', 0., 700., rebin, 1, 0, reg, varBin=False)
        if ('Z' in reg):
            makeplot('reg_'+reg+'_Zmass', 'h_reg_'+reg+'_Zmass',
                     'Z candidate mass (GeV)', 70., 110., 1, 0, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_ZpT', 'h_reg_'+reg+'_ZpT',
                     'Z candidate p_{T} (GeV)', 0., 700., rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_lep2_pT', 'h_reg_'+reg+'_lep2_pT',
                     'lepton2 p_{T}', 0, 200, 2, 1, 0, reg, varBin=False)
        if ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            makeplot('reg_'+reg+'_Jet2Pt', 'h_reg_'+reg+'_Jet2Pt',
                     'JET2 p_{T} (GeV)', 30., 800., rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2Eta', 'h_reg_'+reg+'_Jet2Eta',
                     'JET2 #eta', -2.5, 2.5, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2Phi', 'h_reg_'+reg+'_Jet2Phi',
                     'JET2 #phi', -3.14, 3.14, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2deepCSV', 'h_reg_'+reg+'_Jet2deepCSV',
                     'JET2 deepCSV', 0, 1.2, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2NHadEF', 'h_reg_'+reg+'_Jet2NHadEF',
                     'Jet2NHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2CHadEF', 'h_reg_'+reg+'_Jet2CHadEF',
                     'Jet2CHadEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2CEmEF', 'h_reg_'+reg+'_Jet2CEmEF',
                     'Jet2CEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2NEmEF', 'h_reg_'+reg+'_Jet2NEmEF',
                     'Jet2NEmEF', 0, 1.1, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2CMulti', 'h_reg_'+reg+'_Jet2CMulti',
                     'Jet2CMulti', 0, 50, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_Jet2NMultiplicity', 'h_reg_'+reg+'_Jet2NMultiplicity',
                     'Jet2NMultiplicity', 0, 50, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_ratioPtJet21', 'h_reg_'+reg+'_ratioPtJet21',
                     'JET2 p_{T}/JET1 p_{T} ', 0., 1.0, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_dPhiJet12', 'h_reg_'+reg+'_dPhiJet12',
                     'JET1#phi - JET2#phi', -7.5, 7.5, rebin, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_dEtaJet12', 'h_reg_'+reg+'_dEtaJet12',
                     'JET1#eta - JET2#eta', -7.5, 7.5, rebin, 1, 0, reg, varBin=False)
        if ('1b' in reg) and ('WmunuCR_1b' not in reg) and ('WenuCR_1b' not in reg):
            makeplot('reg_'+reg+'_isjet1EtaMatch', 'h_reg_'+reg+'_isjet1EtaMatch',
                     'JET1#eta X JET2#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet2', 'h_reg_'+reg+'_M_Jet1Jet2',
                     'Inv Mass(Jet1, Jet2)', 0, 2000, rebin, 1, 0, reg, varBin=False)
        elif ('WmunuCR_2b' in reg or 'WenuCR_2b' in reg):
            makeplot('reg_'+reg+'_isjet1EtaMatch', 'h_reg_'+reg+'_isjet1EtaMatch',
                     'JET1#eta X JET2#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet2', 'h_reg_'+reg+'_M_Jet1Jet2',
                     'Inv Mass(Jet1, Jet2)', 0, 2000, 5, 1, 0, reg, varBin=False)
        elif ('2b' in reg):
            makeplot('reg_'+reg+'_isjet2EtaMatch', 'h_reg_'+reg+'_isjet2EtaMatch',
                     'JET1#eta X JET3#eta', -1, 1, 1, 1, 0, reg, varBin=False)
            makeplot('reg_'+reg+'_M_Jet1Jet3', 'h_reg_'+reg+'_M_Jet1Jet3',
                     'Inv Mass(Jet1, Jet3)', 0, 2000, 5, 1, 0, reg, varBin=False)
        makeplot('reg_'+reg+'_rJet1PtMET', 'h_reg_'+reg+'_rJet1PtMET',
                 'Jet1 p_{T}/MET', 0, 10, 1, 1, 0, reg, varBin=False)
yield_outfile.close()
yield_outfile_binwise.close()
