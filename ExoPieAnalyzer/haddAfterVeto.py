import os, sys
import glob
import optparse

usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)
parser.add_option("-v", "--version", type = "string", dest = "Version")
parser.add_option("-i", "--inputDir1", dest = "inputDir1", default = ".")
parser.add_option("-j", "--inputDir2", dest = "inputDir2", default = ".")
parser.add_option("-y", "--year", dest="year", default="Year")
(options, args) = parser.parse_args()

if options.Version == None:
    print('Please provide which version of histograms are being plotted')
    sys.exit()
else:
    histVersion = options.Version
if options.inputDir1 == None:
    print('Please provide the analysis histogram directory')
    sys.exit()
else:
    inDir1 = options.inputDir1
if options.inputDir2 == None:
    print('Please provide the analysis histogram directory')
    sys.exit()
else:
    inDir2 = options.inputDir2

sampList2018 = {'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8',
                'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8',
                'ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8',
                'ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8',
                'ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8',
                'WZ_TuneCP5_13TeV-pythia8',
                'WW_TuneCP5_13TeV-pythia8',
                'ZZ_TuneCP5_13TeV-pythia8',
                'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
                'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
                'TTToHadronic_TuneCP5_13TeV-powheg-pythia8',
                'WJetsToLNu_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-600To800_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-800To1200_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-1200To2500_TuneCP5_13TeV-madgraphMLM-pythia8',
                'WJetsToLNu_HT-2500ToInf_TuneCP5_13TeV-madgraphMLM-pythia8',
                'ZJetsToNuNu_HT-70To100_13TeV-madgraph',
                'ZJetsToNuNu_HT-100To200_13TeV-madgraph',
                'ZJetsToNuNu_HT-200To400_13TeV-madgraph',
                'ZJetsToNuNu_HT-400To600_13TeV-madgraph',
                'ZJetsToNuNu_HT-600To800_13TeV-madgraph',
                'ZJetsToNuNu_HT-800To1200_13TeV-madgraph',
                'ZJetsToNuNu_HT-1200To2500_13TeV-madgraph',
                'ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph',
                'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8',
                'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8',
                'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8',
                'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8',
                'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8',
                'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8',
                'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8',
                'DYJetsToLL_M-50_HT-70to100_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-100to200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-200to400_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-600to800_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-800to1200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'DYJetsToLL_M-50_HT-2500toInf_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8',
                'QCD_HT50to100_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT100to200_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8',
                'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8',
                'GJets_HT-40To100_TuneCP5_13TeV-madgraphMLM-pythia8',
                'GJets_HT-100To200_TuneCP5_13TeV-madgraphMLM-pythia8',
                'GJets_HT-200To400_TuneCP5_13TeV-madgraphMLM-pythia8',
                'GJets_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8',
                'GJets_HT-600ToInf_TuneCP5_13TeV-madgraphMLM-pythia8',
                'ttHTobb_ttToSemiLep_M125_TuneCP5_13TeV-powheg-pythia8',
                'ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8',
                'DYJetsToLL_Pt-0To50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DYJetsToLL_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DYJetsToLL_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DYJetsToLL_Pt-400To650_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DYJetsToLL_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'DYJetsToLL_Pt-650ToInf_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'WJetsToLNu_Pt-100To250_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'WJetsToLNu_Pt-250To400_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'WJetsToLNu_Pt-400To600_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'WJetsToLNu_Pt-50To100_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'WJetsToLNu_Pt-600ToInf_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                'Z1JetsToNuNu_M-50_LHEZpT_150-250_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z1JetsToNuNu_M-50_LHEZpT_250-400_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z1JetsToNuNu_M-50_LHEZpT_400-inf_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z1JetsToNuNu_M-50_LHEZpT_50-150_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z2JetsToNuNu_M-50_LHEZpT_150-250_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z2JetsToNuNu_M-50_LHEZpT_250-400_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'Z2JetsToNuNu_M-50_LHEZpT_50-150_TuneCP5_13TeV-amcnloFXFX-pythia8',
                'MET-Run2018A-17Sep2018-v1',
                'MET-Run2018B-17Sep2018-v1',
                'MET-Run2018C-17Sep2018-v1',
                'MET-Run2018D-PromptReco-v2',
                'EGamma-Run2018A-17Sep2018-v2',
                'EGamma-Run2018B-17Sep2018-v1',
                'EGamma-Run2018C-17Sep2018-v1',
                'EGamma-Run2018D-22Jan2019-v2',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_1000_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_100_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_100_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_10_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_10_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_150_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_150_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_200_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_200_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_250_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_250_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_300_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_300_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_350_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_350_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_400_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_400_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_450_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_450_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_500_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_500_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_50_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_50_mA_600',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_700_mA_1200',
                'bbDM_2HDMa_LO_5f_TuneCP3_13TeV_madgraph_pythia8_ma_750_mA_1200',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_1000mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_100mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_10mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_150mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_200mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_250mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_300mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_350mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_400mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_450mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_500mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_50mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_700mchi_1',
                'bbDM_DMSimp_pseudo_NLO_TuneCP5_13TeV_amcatnlo_pythia8_mphi_750mchi_1',
                'QCD_bEnriched_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT100to200_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT200to300_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT300to500_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT500to700_TuneCP5_13TeV-madgraph-pythia8',
                'QCD_bEnriched_HT700to1000_TuneCP5_13TeV-madgraph-pythia8',
                }

if options.year == '2016':
    print('code is running for 2016')
    sampList = sampList2016
elif options.year == '2017':
    print('code is running for 2017')
    sampList = sampList2017
elif options.year == '2018':
    print('code is running for 2018')
    sampList = sampList2018
else:
    print('please provide year')
    sys.exit()

outDir = 'analysis_'+histVersion
os.system("mkdir -p "+outDir)
for samp in sampList:
    if not bool(glob.glob(inDir1+'/Output_*'+samp+'*.root')) and not bool(glob.glob(inDir2+'/Output_*'+samp+'*.root')): continue
    os.system('hadd '+outDir+'/'+samp+'.root '+inDir1+'/Output_*'+samp+'*.root '+inDir2+'/Output_*'+samp+'*.root')

print('#$#$##$##$ DONE #$#$##$##$')
