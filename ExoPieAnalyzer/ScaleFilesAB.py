from ROOT import TFile

import os,traceback
import sys, optparse,argparse
import glob

usage = "python DataframeToHist.py -F -inDir directoryName -D outputDir "
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-i", "--inputfile",  dest="inputfile",default="myfiles.root")
parser.add_argument("-F", "--farmout", action="store_true",  dest="farmout")
parser.add_argument("-inDir", "--inputDir",  dest="inputDir",default=".")
parser.add_argument("-D", "--outputdir", dest="outputdir",default=".")
parser.add_argument("-c", "--isCondor", action="store_true", dest="isCondor")

args = parser.parse_args()

if args.farmout==None:
    isfarmout = False
else:
    isfarmout = args.farmout

if args.inputDir and isfarmout:
    inDir=args.inputDir

if args.isCondor == None:
  isCondor = False
else:
  isCondor = args.isCondor

outputdir = '.'
if args.outputdir:
    outputdir = str(args.outputdir)

if isCondor:
  with open(args.inputfile) as f:
    content_list = f.readlines()
  content_list = [x.strip() for x in content_list]
  infile = content_list[0]
else:
  infile = args.inputfile

A=13.9
B=7.04
C=6.87
D=31.5
lumiAB = (A+B)/(A+B+C+D)

def scaleHists(infilename,outDir):
    isDatafile = False
    rootFile   = infilename.split('/')[-1]
    if 'MET' in rootFile or 'EGamma' in rootFile:isDatafile=True
    print ('isDatafile',isDatafile)

    f = TFile.Open(infilename, "READ")

    h_total_mcweight = f.Get("h_total_mcweight")
    totalEvents = h_total_mcweight.Integral()
    Keys = f.GetListOfKeys()

    if outDir == '.':outfilename = 'Scaled_'+rootFile.replace(".root","_norm.root")

    else:outfilename = outDir+'/'+rootFile
    print ('outfilename',outfilename)
    fout = TFile.Open(outfilename,"RECREATE")

    dirs = {}
    td = None

    for key in Keys:
      if key.GetClassName() == 'TDirectory':
        td = key.ReadObj()
        dirName = td.GetName()
        print ("found directory", dirName)
        dirs[dirName] = td

      elif key.GetClassName() == 'TH1F':
        hist = key.ReadObj()
        histName = hist.GetName()
        if 'h_total_mcweight' in histName:
            print(hist.Integral())
        if not isDatafile:hist.Scale(lumiAB)
        if 'h_total_mcweight' in histName:
            print(lumiAB, hist.Integral())
        fout.cd()
        hist.Write()
        fout.Write()
      else:continue


if isfarmout:
  path=inDir
  files=glob.glob(path+'/'+'*.root')
  for inputFile in files:
    print ('running code for file:  ',inputFile)
    scaleHists(inputFile,outputdir)

if not isfarmout:
  inputFile=infile
  print ('running code for file:  ',inputFile)
  scaleHists(inputFile,outputdir)
