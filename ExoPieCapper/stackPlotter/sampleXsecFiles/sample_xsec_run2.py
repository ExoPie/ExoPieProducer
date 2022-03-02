import os, sys
#//--------------------------------------------------------------------------------------
def getXsec(samplename, year):
    samplename = str(samplename)
    if 'DYJetsToLL_M-50_HT-100to200'   in samplename: Xsec  =	161
    if 'DYJetsToLL_M-50_HT-1200to2500'   in samplename: Xsec  =	0.1927
    if 'DYJetsToLL_M-50_HT-200to400'   in samplename: Xsec  =	48.58
    if 'DYJetsToLL_M-50_HT-2500toInf'   in samplename: Xsec  =	0.003478
    if 'DYJetsToLL_M-50_HT-400to600'   in samplename: Xsec  =	6.982
    if 'DYJetsToLL_M-50_HT-600to800'   in samplename: Xsec  =	1.747
    if 'DYJetsToLL_M-50_HT-800to1200'   in samplename: Xsec  =	0.8052

    # if 'DYJetsToLL_Pt-0To50'   in samplename: Xsec    = 106300
    # if 'DYJetsToLL_Pt-50To100'   in samplename: Xsec  =408.5
    # if 'DYJetsToLL_Pt-100To250'   in samplename: Xsec  =90.736
    # if 'DYJetsToLL_Pt-250To400'   in samplename: Xsec  =3.772
    # if 'DYJetsToLL_Pt-400To650'   in samplename: Xsec  =0.5156
    # if 'DYJetsToLL_Pt-650ToInf'   in samplename: Xsec  =0.04811

    if 'GJets_HT-100To200'   in samplename: Xsec  =	8622
    if 'GJets_HT-200To400'   in samplename: Xsec  =	2193
    if 'GJets_HT-400To600'   in samplename: Xsec  =	258.5
    if 'GJets_HT-40To100'   in samplename: Xsec  =	18620
    if 'GJets_HT-600ToInf'   in samplename: Xsec  =	85.21
    if 'QCD_HT1000to1500'   in samplename: Xsec  =	1094
    if 'QCD_HT1500to2000'   in samplename: Xsec  =	98.99
    if 'QCD_HT2000toInf'   in samplename: Xsec  =	20.23
    if 'QCD_HT500to700'   in samplename: Xsec  =	29990
    if 'QCD_HT700to1000'   in samplename: Xsec  =	6351

    if 'QCD_HT100to200'   in samplename: Xsec  = 27540000.000000
    if 'QCD_HT200to300'   in samplename: Xsec  = 1735000.000000
    if 'QCD_HT300to500'   in samplename: Xsec  = 366800.000000

    if 'QCD_bEnriched_HT2000toInf' in samplename	:	Xsec = 0.6457
    if 'QCD_bEnriched_HT500to700' in samplename	:	Xsec = 1487.00
    if 'QCD_HT1500to2000_BGenFilter' in	samplename	:	Xsec	=	13.61
    if 'QCD_HT300to500_BGenFilter' in	samplename	:	Xsec	=	27990.00
    if 'QCD_HT100to200_BGenFilter' in	samplename	:	Xsec	=	1278000.00
    if 'QCD_bEnriched_HT100to200' in	samplename	:	Xsec	=	1125000.00
    if 'QCD_bEnriched_HT700to1000' in	samplename	:	Xsec	=	297.40
    if 'QCD_bEnriched_HT1000to1500' in	samplename	:	Xsec	=	46.61
    if 'QCD_HT700to1000_BGenFilter' in	samplename	:	Xsec	=	723.80
    if 'QCD_bEnriched_HT300to500' in	samplename	:	Xsec	=	16680.00
    if 'QCD_bEnriched_HT1500to2000' in	samplename	:	Xsec	=	3.74
    if 'QCD_bEnriched_HT200to300' in	samplename	:	Xsec	=	80200.00

    if 'ST_s-channel_4f_leptonDecays'   in samplename: Xsec  =	10.32
    if 'ST_t-channel_antitop_4f'   in samplename: Xsec  =	80.95
    if 'ST_t-channel_top_4f'   in samplename: Xsec  =	 136.02
    if 'ST_tW_antitop_5f'   in samplename: Xsec  =	38.06
    if 'ST_tW_top_5f'   in samplename: Xsec  =	38.09

    if 'WJetsToLNu_HT-100To200'   in samplename: Xsec  =	1395
    if 'WJetsToLNu_HT-1200To2500'   in samplename: Xsec  =	1.08
    if 'WJetsToLNu_HT-200To400'   in samplename: Xsec  =	409.3
    if 'WJetsToLNu_HT-2500ToInf'   in samplename: Xsec  =	0.008053
    if 'WJetsToLNu_HT-400To600'   in samplename: Xsec  =	57.91
    if 'WJetsToLNu_HT-600To800'   in samplename: Xsec  =	12.93
    if 'WJetsToLNu_HT-800To1200'   in samplename: Xsec  =	5.395
    if 'WW'   in samplename: Xsec  =	75.9
    if 'WZ'   in samplename: Xsec  =	27.57
    if 'ZJetsToNuNu_HT-100To200'   in samplename: Xsec  =	304.5
    if 'ZJetsToNuNu_HT-1200To2500'   in samplename: Xsec  =	0.343
    if 'ZJetsToNuNu_HT-200To400'   in samplename: Xsec  =	91.85
    if 'ZJetsToNuNu_HT-2500ToInf'   in samplename: Xsec  =	0.005146
    if 'ZJetsToNuNu_HT-400To600'   in samplename: Xsec  =	13.11
    if 'ZJetsToNuNu_HT-600To800'   in samplename: Xsec  =	3.257
    if 'ZJetsToNuNu_HT-800To1200'   in samplename: Xsec  =	1.499
    if 'ZZ'   in samplename: Xsec  =	12.14
    if 'ggZH_HToBB_ZToNuNu_M125'  in samplename: Xsec = 0.01222
    if 'ggZH_HToBB_ZToLL_M125'    in samplename: Xsec = 0.006185
    if 'WminusH_HToBB' in samplename: Xsec = 0.3654
    if 'WplusH_HToBB_WToLNu_M125' in samplename: Xsec = 0.2819
    if 'ZH_HToBB_ZToLL_M125'      in samplename and 'ggZH_HToBB_ZToLL_M125' not in samplename:   Xsec = 0.07924
    if 'ZH_HToBB_ZToNuNu_M125'    in samplename and 'ggZH_HToBB_ZToNuNu_M125' not in samplename: Xsec = 0.1565

    if year=='2017':
        # 2017 NLO from monoj
        if 'TTTo2L2Nu'   in samplename: Xsec  =	88.29#687.1*0.105
        if 'TTToHadronic'   in samplename: Xsec  =	377.96#687.1*0.457
        if 'TTToSemiLeptonic'   in samplename: Xsec  =	365.34#687.1*0.438
        if 'DY1JetsToLL_M-50_LHEZpT_150-250' in samplename: Xsec  = 9.5
        if 'DY1JetsToLL_M-50_LHEZpT_250-400' in samplename: Xsec  = 1.097
        if 'DY1JetsToLL_M-50_LHEZpT_400-inf' in samplename: Xsec  = 0.1207
        if 'DY1JetsToLL_M-50_LHEZpT_50-150' in samplename: Xsec  = 315.1
        if 'DY2JetsToLL_M-50_LHEZpT_150-250' in samplename: Xsec  = 15.73
        if 'DY2JetsToLL_M-50_LHEZpT_250-400' in samplename: Xsec  = 2.74
        if 'DY2JetsToLL_M-50_LHEZpT_400-inf' in samplename: Xsec  = 0.4492
        if 'DY2JetsToLL_M-50_LHEZpT_50-150' in samplename: Xsec  = 169

        if 'Z1JetsToNuNu_M-50_LHEZpT_150-250' in samplename: Xsec  = 18.04
        if 'Z1JetsToNuNu_M-50_LHEZpT_250-400' in samplename: Xsec  = 2.051
        if 'Z1JetsToNuNu_M-50_LHEZpT_400-inf' in samplename: Xsec  = 0.2251
        if 'Z1JetsToNuNu_M-50_LHEZpT_50-150' in samplename: Xsec  = 598.9
        if 'Z2JetsToNuNU_M-50_LHEZpT_400-inf' in samplename: Xsec  = 0.8472
        if 'Z2JetsToNuNu_M-50_LHEZpT_150-250' in samplename: Xsec  = 29.6
        if 'Z2JetsToNuNu_M-50_LHEZpT_250-400' in samplename: Xsec  = 5.174
        if 'Z2JetsToNuNu_M-50_LHEZpT_50-150' in samplename: Xsec  = 326.3

        # if 'W1JetsToLNu_LHEWpT_0-50' in samplename: Xsec  =
        if 'W1JetsToLNu_LHEWpT_100-150' in samplename: Xsec  = 284.06
        if 'W1JetsToLNu_LHEWpT_150-250' in samplename: Xsec  = 71.71
        if 'W1JetsToLNu_LHEWpT_250-400' in samplename: Xsec  = 8.06
        if 'W1JetsToLNu_LHEWpT_400-inf' in samplename: Xsec  = 0.89
        # if 'W1JetsToLNu_LHEWpT_50-150' in samplename: Xsec  =
        # if 'W2JetsToLNu_LHEWpT_0-50' in samplename: Xsec  =
        if 'W2JetsToLNu_LHEWpT_100-150' in samplename: Xsec  = 281.63
        if 'W2JetsToLNu_LHEWpT_150-250' in samplename: Xsec  = 108.59
        if 'W2JetsToLNu_LHEWpT_250-400' in samplename: Xsec  = 18.03
        if 'W2JetsToLNu_LHEWpT_400-inf' in samplename: Xsec  = 3
        #if 'W2JetsToLNu_LHEWpT_50-150' in samplename: Xsec  =

    if year=='2016':
        # for 2016 NLO samples
        if 'TTTo2L2Nu'   in samplename: Xsec  =	687.1*0.105
        if 'TTToHadronic'   in samplename: Xsec  =	687.1*0.457
        if 'TTToSemiLeptonic'   in samplename: Xsec  =	687.1*0.438
        if 'DYJetsToLL_Pt-100To250' in samplename: Xsec = 81.42000
        if 'DYJetsToLL_Pt-250To400' in samplename: Xsec = 2.99100
        if 'DYJetsToLL_Pt-400To650' in samplename: Xsec = 0.38820
        if 'DYJetsToLL_Pt-50To100' in samplename: Xsec = 354.90000
        if 'DYJetsToLL_Pt-650ToInf' in samplename: Xsec = 0.03737
        if 'DYJetsToNuNu_PtZ-100To250' in samplename: Xsec = 54.91000
        if 'DYJetsToNuNu_PtZ-250To400' in samplename: Xsec = 2.07300
        if 'DYJetsToNuNu_PtZ-400To650' in samplename: Xsec = 0.27850
        if 'DYJetsToNuNu_PtZ-50To100' in samplename: Xsec = 236.50000
        if 'DYJetsToNuNu_PtZ-650ToInf' in samplename: Xsec = 0.02604
        if 'WJetsToLNu_Wpt-50To100' in samplename: Xsec = 3054.00
        if 'WJetsToLNu_Pt-100To250' in samplename: Xsec = 626.20000
        if 'WJetsToLNu_Pt-250To400' in samplename: Xsec = 21.83000
        if 'WJetsToLNu_Pt-400To600' in samplename: Xsec = 2.63500
        if 'WJetsToLNu_Pt-600ToInf' in samplename: Xsec = 0.41020
        if 'WJetsToLNu_TuneCUETP8M1' in samplename: Xsec = 60380

    if year=='2018':
        #for 2018 NLO samples
        #from https://twiki.cern.ch/twiki/bin/view/CMS/SummaryTable1G25ns#W_jets
        # if 'DYJetsToLL_Pt-100To250' in samplename: Xsec = 83.12
        # if 'DYJetsToLL_Pt-250To400' in samplename: Xsec = 3.047
        # if 'DYJetsToLL_Pt-400To650' in samplename: Xsec = 0.3921
        # if 'DYJetsToLL_Pt-50To100' in samplename: Xsec = 354.90000
        # if 'DYJetsToLL_Pt-650ToInf' in samplename: Xsec = 0.03636
        # #from monoj
        # if 'WJetsToLNu_Pt-100To250' in samplename: Xsec = 769.20000
        # if 'WJetsToLNu_Pt-250To400' in samplename: Xsec = 27.62000
        # if 'WJetsToLNu_Pt-400To600' in samplename: Xsec = 3.59500
        # if 'WJetsToLNu_Pt-600ToInf' in samplename: Xsec = 0.549020
        if 'TTTo2L2Nu'   in samplename: Xsec  =	88.29#687.1*0.105
        if 'TTToHadronic'   in samplename: Xsec  =	377.96#687.1*0.457
        if 'TTToSemiLeptonic'   in samplename: Xsec  =	365.34#687.1*0.438
        #from GenXanalyser
        if 'DYJetsToLL_Pt-0To50'   in samplename: Xsec    = 106200.00
        if 'DYJetsToLL_Pt-50To100'   in samplename: Xsec  =409.80
        if 'DYJetsToLL_Pt-100To250'   in samplename: Xsec  =97.26
        if 'DYJetsToLL_Pt-250To400'   in samplename: Xsec  =3.76
        if 'DYJetsToLL_Pt-400To650'   in samplename: Xsec  =0.52
        if 'DYJetsToLL_Pt-650ToInf'   in samplename: Xsec  =0.05
        if 'WJetsToLNu_Pt-100To250' in samplename: Xsec = 771.20
        if 'WJetsToLNu_Pt-250To400' in samplename: Xsec = 28.06
        if 'WJetsToLNu_Pt-400To600' in samplename: Xsec = 3.59
        if 'WJetsToLNu_Pt-50To100' in samplename: Xsec = 3578.00
        if 'WJetsToLNu_Pt-600ToInf' in samplename: Xsec = 0.55
        if 'Z1JetsToNuNu_M-50_LHEZpT_150-250' in samplename: Xsec = 17.97
        if 'Z1JetsToNuNu_M-50_LHEZpT_250-400' in samplename: Xsec = 2.053
        if 'Z1JetsToNuNu_M-50_LHEZpT_400-inf' in samplename: Xsec = 0.224
        if 'Z1JetsToNuNu_M-50_LHEZpT_50-150' in samplename: Xsec = 598.000
        if 'Z2JetsToNuNu_M-50_LHEZpT_150-250' in samplename: Xsec = 29.660
        if 'Z2JetsToNuNu_M-50_LHEZpT_250-400' in samplename: Xsec = 5.214
        if 'Z2JetsToNuNu_M-50_LHEZpT_50-150' in samplename: Xsec = 326.000

    return Xsec
