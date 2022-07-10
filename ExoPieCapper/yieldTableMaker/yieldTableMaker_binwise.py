#!/usr/bin/env python
# coding: utf-8

# In[1]:
import os
import pandas as pd
import datetime
# In[2]:

datestr = str(datetime.date.today().strftime("%d%m%Y"))

dfEle2016 = pd.read_csv('inYieldDir/v16_12-00-02_Electron_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])

dfEle2016['yield'] = dfEle2016[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfEle2016 = dfEle2016.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

dfEle2017 = pd.read_csv('inYieldDir/v17_12-00-02_Electron_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])
dfEle2017['yield'] = dfEle2017[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfEle2017 = dfEle2017.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

dfEle2018 = pd.read_csv('inYieldDir/v18_12-00-02_Electron_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])
dfEle2018['yield'] = dfEle2018[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfEle2018 = dfEle2018.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

dfMu2016 = pd.read_csv('inYieldDir/v16_12-00-02_Muon_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])
dfMu2016['yield'] = dfMu2016[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfMu2016 = dfMu2016.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

dfMu2017 = pd.read_csv('inYieldDir/v17_12-00-02_Muon_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])
dfMu2017['yield'] = dfMu2017[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfMu2017 = dfMu2017.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

dfMu2018 = pd.read_csv('inYieldDir/v18_12-00-02_Muon_binwise.txt',
                        header=None, sep="   ", names=['reg', 'bin1', 'bin2', 'bin3', 'bin4'])
dfMu2018['yield'] = dfMu2018[['bin1', 'bin2', 'bin3', 'bin4']].values.tolist()
dfMu2018 = dfMu2018.drop(['bin1', 'bin2', 'bin3', 'bin4'], axis=1)

# In[3]:


if not os.path.exists('outYieldDir/texTableDir/'+datestr):
    os.makedirs('outYieldDir/texTableDir/'+datestr)


# In[4]:


yT = open('outYieldDir/texTableDir/texTableFiles/texTable_'+datestr+'_binwise.tex', 'w')
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
\begin{tabular}{|l|l|l|l|l|l|l|l|l|l|l|l|l|}
\hline
\multicolumn{1}{|c|}{\textbf{}} & \multicolumn{4}{c|}{\textbf{2016}} & \multicolumn{4}{c|}{\textbf{2017}} & \multicolumn{4}{c|}{\textbf{2018}} \\ \hline
& Bin1 & Bin2 & Bin3 & Bin4 & Bin1 & Bin2 & Bin3 & Bin4 & Bin1 & Bin2 & Bin3 & Bin4 \\ \hline

"""

txt_3 = r"""
\end{tabular}
}
\end{table}

"""

txt_4 = r"""
\end{document}
"""


# In[5]:

yT.write(txt_1)
for (index16, row16), (index17, row17), (index18, row18) in zip(dfMu2016.iterrows(), dfMu2017.iterrows(), dfMu2018.iterrows()):
    if 'region' in row16["reg"] and 'region' in row17["reg"] and 'region' in row18["reg"]:
        tex_filename = row16["reg"].partition(
            ' ')[-1].split('_')[2]+'_'+row16["reg"].partition(' ')[-1].split('_')[3]+'_binwise'
        tex_table = open('outYieldDir/texTableDir/'+datestr +'/'+tex_filename+'.tex', 'w')
        if index16 != 0:
            yT.write(txt_3)
        txt_2_apply = txt_2.replace("REGION", str(row16["reg"].partition(' ')[-1]).split('_')[2]+'\_'+str(row16["reg"].partition(' ')[-1]).split(
            '_')[3]).replace("LABEL", str(row16["reg"].partition(' ')[-1]).split('_')[2]+str(row16["reg"].partition(' ')[-1]).split('_')[3])
        yT.write(txt_2_apply)
        tex_table.write(txt_2_apply)
    elif 'Bin1' in row16["reg"] and 'Bin1' in row17["reg"] and 'Bin1' in row18["reg"]:
        continue
    else:
        yT.write(row16["reg"].replace('_', '\_')+' & ')
        tex_table.write(row16["reg"].replace('_', '\_')+' & ')
        for yd16, yd17, yd18 in zip(row16["yield"], row17["yield"], row18["yield"]):
            yT.write(str(yd16).replace('±', '$\pm$')+' & '+str(
                yd17).replace('±', '$\pm$')+' & '+str(yd18).replace('±', '$\pm$'))
            tex_table.write(str(yd16).replace('±', '$\pm$')+' & '+str(
                yd17).replace('±', '$\pm$')+' & '+str(yd18).replace('±', '$\pm$'))
        yT.write(r' \\ \hline'+'\n')
        tex_table.write(r' \\ \hline'+'\n')
    if index16 == len(dfMu2016)-1:
        yT.write(txt_3)
        tex_table.close()


# In[ ]:


for (index16, row16), (index17, row17), (index18, row18) in zip(dfEle2016.iterrows(), dfEle2017.iterrows(), dfEle2018.iterrows()):
    if 'region' in row16["reg"] and 'region' in row17["reg"] and 'region' in row18["reg"]:
        tex_filename = row16["reg"].partition(
            ' ')[-1].split('_')[2]+'_'+row16["reg"].partition(' ')[-1].split('_')[3]+'_binwise'
        tex_table = open('outYieldDir/texTableDir/'+datestr +
                        '/'+tex_filename+'.tex', 'w')
        if index16 != 0:
            yT.write(txt_3)
        txt_2_apply = txt_2.replace("REGION", str(row16["reg"].partition(' ')[-1]).split('_')[2]+'\_'+str(row16["reg"].partition(' ')[-1]).split(
            '_')[3]).replace("LABEL", str(row16["reg"].partition(' ')[-1]).split('_')[2]+str(row16["reg"].partition(' ')[-1]).split('_')[3])
        yT.write(txt_2_apply)
        tex_table.write(txt_2_apply)
    elif 'Bin1' in row16["reg"] and 'Bin1' in row17["reg"] and 'Bin1' in row18["reg"]:
        continue
    else:
        yT.write(row16["reg"].replace('_', '\_')+' & ')
        tex_table.write(row16["reg"].replace('_', '\_')+' & ')
        for yd16 in row16["yield"]:
            yT.write(str(yd16).replace('±', '$\pm$')+' & ')
            tex_table.write(str(yd16).replace('±', '$\pm$')+' & ')
        for yd17 in row17["yield"]:
            yT.write(str(yd17).replace('±', '$\pm$')+' & ')
            tex_table.write(str(yd17).replace('±', '$\pm$')+' & ')
        for yd18 in row18["yield"]:
            yT.write(str(yd18).replace('±', '$\pm$'))
            tex_table.write(str(yd18).replace('±', '$\pm$'))
        yT.write(r' \\ \hline'+'\n')
        tex_table.write(r' \\ \hline'+'\n')
    if index16 == len(dfEle2016)-1:
        yT.write(txt_3)
        tex_table.close()
yT.write(txt_4)
yT.close()


# In[ ]:


for files in os.listdir('outYieldDir/texTableDir/'+datestr):
    if files.endswith('.tex'):
        print(files)
        fin = open('outYieldDir/texTableDir/'+datestr+'/'+files, 'a')
        fin.write(txt_3)
        # os.system('cat '+files)
    fin.close()


# In[ ]:


# In[ ]:
