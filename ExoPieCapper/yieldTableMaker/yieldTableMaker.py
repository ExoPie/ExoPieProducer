
import os
import pandas as pd
import datetime


datestr = str(datetime.date.today().strftime("%d%m%Y"))
version = '12-02-01_cl68pdf'

dfEle2016 = pd.read_csv('inYieldDir/v'+version+'/v16_'+version+'_Electron.txt',header=None,sep=" ",names=['reg', 'yield'])
dfEle2017 = pd.read_csv('inYieldDir/v'+version+'/v17_'+version+'_Electron.txt',header=None,sep=" ",names=['reg', 'yield'])
dfEle2018 = pd.read_csv('inYieldDir/v'+version+'/v18_'+version+'_Electron.txt',header=None,sep=" ",names=['reg', 'yield'])

dfMu2016 = pd.read_csv('inYieldDir/v'+version+'/v16_'+version+'_Muon.txt',header=None,sep=" ",names=['reg', 'yield'])
dfMu2017 = pd.read_csv('inYieldDir/v'+version+'/v17_'+version+'_Muon.txt',header=None,sep=" ",names=['reg', 'yield'])
dfMu2018 = pd.read_csv('inYieldDir/v'+version+'/v18_'+version+'_Muon.txt',header=None,sep=" ",names=['reg', 'yield'])


if not os.path.exists('outYieldDir/texTableDir/v'+version):
    os.makedirs('outYieldDir/texTableDir/v'+version)
print(dfMu2016)


yT = open('outYieldDir/texTableDir/texTableFiles/texTable_v'+version+'.tex','w')
txt_1 = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage[width=29.70cm, height=42.00cm, left=1cm, right=1.0cm, top=1.00cm, bottom=2.00cm]{geometry}
\title{testing}
\author{Praveen Chandra Tiwari}
\date{February 2020}
\usepackage{natbib}
\usepackage{graphicx}
\begin{document}

"""
txt_2 = r"""\begin{table}[]
\centering
\caption{Background yield for REGION}
\label{tab:LABEL}
\resizebox{0.8\textwidth}{!}{
\begin{tabular}{|l|l|l|l|}
\hline
\multicolumn{1}{|c|}{\textbf{}} & \multicolumn{1}{c|}{\textbf{2016}} & \multicolumn{1}{c|}{\textbf{2017}} & \multicolumn{1}{c|}{\textbf{2018}} \\ \hline
"""

txt_3 = r"""
\end{tabular}
}
\end{table}

"""

txt_4 = r"""
\end{document}
"""


yT.write(txt_1)
for (index16, row16),(index17,row17),(index18,row18) in zip(dfMu2016.iterrows(),dfMu2017.iterrows(),dfMu2018.iterrows()):
    if 'region' in row16["reg"] and 'region' in row17["reg"] and 'region' in row18["reg"]:
        print(row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')',''))
        # tex_filename = row16["yield"].split('_')[2]+'_'+row16["yield"].split('_')[3]
        tex_filename = row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')','')
        tex_table = open('outYieldDir/texTableDir/v'+version+'/'+tex_filename+'.tex','w')
        if index16 != 0:
            yT.write(txt_3)
        # txt_2_apply= txt_2.replace("REGION",str(row16["yield"]).split('_')[2]+'\_'+str(row16["yield"]).split('_')[3]).replace("LABEL",str(row16["yield"]).split('_')[2]+str(row16["yield"]).split('_')[3])
        txt_2_apply= txt_2.replace("REGION",str(row16["yield"]).replace('-',' ')).replace("LABEL",str(row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')','')))
#         if 'SR_2b' in row16["reg"] and 'SR_2b' in row17["reg"] and 'SR_2b' in row18["reg"]:
#             txt_2_apply = txt_2_apply.replace('SR_2b','SR_1p5b')
        yT.write(txt_2_apply)
        tex_table.write(txt_2_apply)
    else:
        yT.write(row16["reg"].replace('_','\_').replace('-',' ')+' & '+str(row16["yield"]).replace('±', '$\pm$')+' & '+str(row17["yield"]).replace('±', '$\pm$')+' & '+str(row18["yield"]).replace('±', '$\pm$')+r' \\ \hline'+'\n')
        tex_table.write(row16["reg"].replace('_','\_').replace('-',' ')+' & '+str(row16["yield"]).replace('±', '$\pm$')+' & '+str(row17["yield"]).replace('±', '$\pm$')+' & '+str(row18["yield"]).replace('±', '$\pm$')+r' \\ \hline'+'\n')
    if index16 == len(dfMu2016)-1:
        yT.write(txt_3)
        tex_table.close()




for (index16, row16),(index17,row17),(index18,row18) in zip(dfEle2016.iterrows(),dfEle2017.iterrows(),dfEle2018.iterrows()):
    if 'region' in row16["reg"] and 'region' in row17["reg"] and 'region' in row18["reg"]:
        print(row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')',''))
        # tex_filename = row16["yield"].split('_')[2]+'_'+row16["yield"].split('_')[3]
        tex_filename = row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')','')
        tex_table = open('outYieldDir/texTableDir/v'+version+'/'+tex_filename+'.tex','w')
        if index16 != 0:
            yT.write(txt_3)
        # txt_2_apply= txt_2.replace("REGION",str(row16["yield"]).split('_')[2]+'\_'+str(row16["yield"]).split('_')[3]).replace("LABEL",str(row16["yield"]).split('_')[2]+str(row16["yield"]).split('_')[3])
        txt_2_apply= txt_2.replace("REGION",str(row16["yield"]).replace('-',' ')).replace("LABEL",str(row16["yield"].replace('-','').replace('$','').replace('\\','').replace('(','').replace('bar{','').replace('}','').replace(')','')))
        yT.write(txt_2_apply)
        tex_table.write(txt_2_apply)
    else:
        yT.write(row16["reg"].replace('_','\_').replace('-',' ')+' & '+str(row16["yield"]).replace('±', '$\pm$')+' & '+str(row17["yield"]).replace('±', '$\pm$')+' & '+str(row18["yield"]).replace('±', '$\pm$')+r' \\ \hline'+'\n')
        tex_table.write(row16["reg"].replace('_','\_').replace('-',' ')+' & '+str(row16["yield"]).replace('±', '$\pm$')+' & '+str(row17["yield"]).replace('±', '$\pm$')+' & '+str(row18["yield"]).replace('±', '$\pm$')+r' \\ \hline'+'\n')
    if index16 == len(dfEle2016)-1:
        yT.write(txt_3)
        tex_table.close()
yT.write(txt_4)
yT.close()


for files in os.listdir('outYieldDir/texTableDir/v'+version):
    # print (files)
    if files.endswith(".tex"):
        fin = open('outYieldDir/texTableDir/v'+version+'/'+files,'a')
        fin.write(txt_3)
        # os.system('cat outYieldDir/texTableDir/'+datestr+'/'+files)
        fin.close()





