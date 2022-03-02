#!/usr/bin/env python
# coding: utf-8
#coded by P C Tiwari
import os
import sys
import optparse
import numpy as np
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from pdf2image import convert_from_path

##to run
## python CompareImageSideSide.py -f firstDir -s secondDir --f_txt firstDirTxt --s_txt secondDirTxt

usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)
parser.add_option("-f", "--first_dir", dest="FirstDir", default="firstDir")
parser.add_option("-s", "--second_dir", dest="SecondDir", default="secondDir")
parser.add_option("-t", "--third_dir", dest="ThirdDir", default="thirdDir")

parser.add_option("-x", "--f_txt", dest="FirstDirTxt", default="firstDirTxt")
parser.add_option("-y", "--s_txt", dest="SecondDirTxt", default="secondDirTxt")
parser.add_option("-z", "--t_txt", dest="ThirdDirTxt", default="thirdDirTxt")

(options, args) = parser.parse_args()


regions = ['SR_1b', 'SR_2b', 'ZmumuCR_2j', 'ZmumuCR_3j', 'ZeeCR_2j', 'ZeeCR_3j', 'TopenuCR_2b', 'TopmunuCR_2b', 'WmunuCR_1b', 'WenuCR_1b']

list_comp = []
# tobe_comp = ['Recoil_log', 'Jet1Pt_log', 'NTau', 'lep2_pT','_MET']
# tobe_comp = ['Jet1Phi', 'METPhi']
# tobe_comp = ['Recoil']
# tobe_comp = ['cutFlow', 'ctsValue', 'Recoil', 'ctsValue', 'lep1_pT', 'Jet1Phi_log', 'METPhi', 'lep1_Phi' ]
tobe_comp = ['ctsValue_log','cutFlow_log','delta_pfCalo_log','dEtaJet12_log','dPhi_lep1_MET_log','dPhi_lep2_MET_log','dPhiJet12_log','isjet2EtaMatch_log','Jet1CEmEF_log','Jet1CHadEF_log','Jet1CMulti_log','Jet1deepCSV_log','Jet1Eta_log','Jet1NEmEF_log','Jet1NHadEF_log','Jet1NMultiplicity_log','Jet1Phi_log','Jet1Pt_log','Jet2CEmEF_log','Jet2CHadEF_log','Jet2CMulti_log','Jet2deepCSV_log','Jet2Eta_log','Jet2NEmEF_log','Jet2NHadEF_log','Jet2NMultiplicity_log','Jet2Phi_log','Jet2Pt_log','lep1_Phi_log','lep1_pT_log','lep2_pT_log','M_Jet1Jet3_log','MET_log','METPhi_log','min_dPhi_log','NEle_log','nJets_log','NMu_log','nPho_log','nPV','NTau_log','PUnPV','ratioPtJet21_log','rJet1PtMET_log','Zmass','ZpT_log','Recoil']
for reg in regions:
    listfiles_1 = [f for f in os.listdir(options.FirstDir+'/bbDMPng/'+reg)]
    listfiles_2 = [f for f in os.listdir(options.SecondDir+'/bbDMPng/'+reg)]
    list_temp = []
    print([convert_from_path(options.SecondDir+'/bbDMPng/'+i)[0]
          for i in listfiles_2])

    # for i in listfiles_1:
    #     for j in listfiles_2:
    #         if (i == j) and [hist for hist in tobe_comp if(hist in i)]:
    #             im_list = [options.FirstDir+'/bbDMPng/'+reg+'/' +
    #                        i, options.SecondDir+'/bbDMPng/'+reg+'/'+j]
    #             list_temp.append(im_list)
    #         else:
    #             continue
    #     list_comp += list_temp

    for i in listfiles_1:
        print(i)
        if (i in listfiles_1 and i in listfiles_2) and [hist for hist in tobe_comp if(hist in i)]:
            im_list = [options.FirstDir+'/bbDMPng/'+reg+'/' + i, options.SecondDir+'/bbDMPng/'+reg+'/'+convert_from_path(i)]
            list_temp.append(im_list)
        else:
            continue
    list_comp += list_temp

for reg in regions:
    if not os.path.exists('compared_files/bbDMPng/'+reg):
        os.makedirs('compared_files/bbDMPng/'+reg)
    if not os.path.exists('compared_files/bbDMPdf/'+reg):
        os.makedirs('compared_files/bbDMPdf/'+reg)
    if not os.path.exists('compared_files/allFiles'):
        os.makedirs('compared_files/allFiles')

for im in list_comp:
    imgs = [PIL.Image.open(i) for i in im]
    draw = [PIL.ImageDraw.Draw(i) for i in imgs]
    # fonts = PIL.ImageFont.truetype('/Library/Fonts/SourceCodePro-Bold.ttf', 20)
    fonts = PIL.ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 25)
    # draw[0].text((350, 200), options.FirstDirTxt, font=fonts, fill=(0, 0, 0))
    # draw[1].text((300, 200), options.SecondDirTxt, font=fonts, fill=(0, 0, 0))
    color = 'rgb(255, 0, 0)'
    draw[0].text((120, 50), options.FirstDirTxt, font=fonts, fill=color)
    draw[1].text((120, 50), options.SecondDirTxt, font=fonts, fill=color)

    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))

    # save that beautiful picture
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    reg_name = im[1].split('/')[-2]
    image_name = (im[1].split('/')[-1]).split('.')[0]
    print(reg_name, image_name)
    imgs_comb.save('compared_files/bbDMPng/'+reg_name+'/'+image_name+'.png', optimize=True, quality=100)
    imgs_comb.save('compared_files/bbDMPdf/'+reg_name+'/'+image_name+'.pdf', optimize=True, quality=1000)
    imgs_comb.save('compared_files/allFiles/'+image_name+'.png', optimize=True, quality=100)
    imgs_comb.save('compared_files/allFiles/'+image_name+'.pdf', optimize=True, quality=100)
