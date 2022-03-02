import sys
from ROOT import TFile, TObject
file=sys.argv[1]
tfile = TFile.Open(str(file))
tfile.cd()

histo_list = []
for h in tfile.GetListOfKeys():
    h = h.ReadObj()
    if 'QCDCR' not in h.GetName():
      histo_list.append(h)
    else:
      newname = h.GetName().replace('QCDCR', 'QCDbCR')
      h.SetName(newname)
      histo_list.append(h)
newFile = TFile(str(file).split('/')[-1], "RECREATE")
newFile.cd()
for hist in histo_list:
  hist.Write()
newFile.Close()
print('Done')
