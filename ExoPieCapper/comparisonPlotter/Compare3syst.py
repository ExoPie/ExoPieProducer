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
# tobe_comp = ['ctsValue_log','Recoil']
# tobe_comp = ['ctsValue_log','cutFlow_log','delta_pfCalo_log','dEtaJet12_log','dPhi_lep1_MET_log','dPhi_lep2_MET_log','dPhiJet12_log','isjet2EtaMatch_log','Jet1CEmEF_log','Jet1CHadEF_log','Jet1CMulti_log','Jet1deepCSV_log','Jet1Eta_log','Jet1NEmEF_log','Jet1NHadEF_log','Jet1NMultiplicity_log','Jet1Phi_log','Jet1Pt_log','Jet2CEmEF_log','Jet2CHadEF_log','Jet2CMulti_log','Jet2deepCSV_log','Jet2Eta_log','Jet2NEmEF_log','Jet2NHadEF_log','Jet2NMultiplicity_log','Jet2Phi_log','Jet2Pt_log','lep1_Phi_log','lep1_pT_log','lep2_pT_log','M_Jet1Jet3_log','MET_log','METPhi_log','min_dPhi_log','NEle_log','nJets_log','NMu_log','nPho_log','nPV','NTau_log','PUnPV','ratioPtJet21_log','rJet1PtMET_log','Zmass','ZpT_log','Recoil']
tobe_comp = ['bkgSum_CMSyear_eff_b','bkgSum_CMSyear_EleID ','bkgSum_CMSyear_EleRECO ','bkgSum_CMSyear_fake_b ','bkgSum_CMSyear_mu_scale ','bkgSum_CMSyear_MuID ','bkgSum_CMSyear_MuISO ','bkgSum_CMSyear_MuTRK ','bkgSum_CMSyear_pdf ','bkgSum_CMSyear_PU ','bkgSum_CMSyear_trig_ele ','bkgSum_CMSyear_trig_met ','bkgSum_JECAbsolute ','bkgSum_JECAbsolute_year ','bkgSum_JECBBEC1','bkgSum_JECBBEC1_year','bkgSum_JECEC2','bkgSum_JECEC2_year','bkgSum_JECFlavorQCD ','bkgSum_JECHF ','bkgSum_JECHF_year ','bkgSum_JECRelativeBal ','bkgSum_JECRelativeSample_year ','DIBOSON_CMSyear_eff_b ','DIBOSON_CMSyear_EleID ','DIBOSON_CMSyear_EleRECO ','DIBOSON_CMSyear_fake_b ','DIBOSON_CMSyear_mu_scale ','DIBOSON_CMSyear_MuID ','DIBOSON_CMSyear_MuISO ','DIBOSON_CMSyear_MuTRK ','DIBOSON_CMSyear_pdf ','DIBOSON_CMSyear_PU ','DIBOSON_CMSyear_trig_ele ','DIBOSON_CMSyear_trig_met ','DIBOSON_JECAbsolute ','DIBOSON_JECAbsolute_year ','DIBOSON_JECBBEC1','DIBOSON_JECBBEC1_year','DIBOSON_JECEC2','DIBOSON_JECEC2_year','DIBOSON_JECFlavorQCD ','DIBOSON_JECHF ','DIBOSON_JECHF_year ','DIBOSON_JECRelativeBal ','DIBOSON_JECRelativeSample_year ','DYJets_CMSyear_eff_b ','DYJets_CMSyear_EleID ','DYJets_CMSyear_EleRECO ','DYJets_CMSyear_fake_b ','DYJets_CMSyear_mu_scale ','DYJets_CMSyear_MuID ','DYJets_CMSyear_MuISO ','DYJets_CMSyear_MuTRK ','DYJets_CMSyear_pdf ','DYJets_CMSyear_PU ','DYJets_CMSyear_trig_ele ','DYJets_CMSyear_trig_met ','DYJets_JECAbsolute ','DYJets_JECAbsolute_year ','DYJets_JECBBEC1','DYJets_JECBBEC1_year','DYJets_JECEC2','DYJets_JECEC2_year','DYJets_JECFlavorQCD ','DYJets_JECHF ','DYJets_JECHF_year ','DYJets_JECRelativeBal ','DYJets_JECRelativeSample_year ','GJets_CMSyear_eff_b ','GJets_CMSyear_EleID ','GJets_CMSyear_EleRECO ','GJets_CMSyear_fake_b ','GJets_CMSyear_mu_scale ','GJets_CMSyear_MuID ','GJets_CMSyear_MuISO ','GJets_CMSyear_MuTRK ','GJets_CMSyear_pdf ','GJets_CMSyear_PU ','GJets_CMSyear_trig_ele ','GJets_CMSyear_trig_met ','GJets_JECAbsolute ','GJets_JECAbsolute_year ','GJets_JECBBEC1','GJets_JECBBEC1_year','GJets_JECEC2','GJets_JECEC2_year','GJets_JECFlavorQCD ','GJets_JECHF ','GJets_JECHF_year ','GJets_JECRelativeBal ','GJets_JECRelativeSample_year ','QCD_CMSyear_eff_b ','QCD_CMSyear_EleID ','QCD_CMSyear_EleRECO ','QCD_CMSyear_fake_b ','QCD_CMSyear_mu_scale ','QCD_CMSyear_MuID ','QCD_CMSyear_MuISO ','QCD_CMSyear_MuTRK ','QCD_CMSyear_pdf ','QCD_CMSyear_PU ','QCD_CMSyear_trig_ele ','QCD_CMSyear_trig_met ','QCD_JECAbsolute ','QCD_JECAbsolute_year ','QCD_JECBBEC1','QCD_JECBBEC1_year','QCD_JECEC2','QCD_JECEC2_year','QCD_JECFlavorQCD ','QCD_JECHF ','QCD_JECHF_year ','QCD_JECRelativeBal ','QCD_JECRelativeSample_year ','SMH_CMSyear_eff_b ','SMH_CMSyear_EleID ','SMH_CMSyear_EleRECO ','SMH_CMSyear_fake_b ','SMH_CMSyear_mu_scale ','SMH_CMSyear_MuID ','SMH_CMSyear_MuISO ','SMH_CMSyear_MuTRK ','SMH_CMSyear_pdf ','SMH_CMSyear_PU ','SMH_CMSyear_trig_ele ','SMH_CMSyear_trig_met ','SMH_JECAbsolute ','SMH_JECAbsolute_year ','SMH_JECBBEC1','SMH_JECBBEC1_year','SMH_JECEC2','SMH_JECEC2_year','SMH_JECFlavorQCD ','SMH_JECHF ','SMH_JECHF_year ','SMH_JECRelativeBal ','SMH_JECRelativeSample_year ','STop_CMSyear_eff_b ','STop_CMSyear_EleID ','STop_CMSyear_EleRECO ','STop_CMSyear_fake_b ','STop_CMSyear_mu_scale ','STop_CMSyear_MuID ','STop_CMSyear_MuISO ','STop_CMSyear_MuTRK ','STop_CMSyear_pdf ','STop_CMSyear_PU ','STop_CMSyear_trig_ele ','STop_CMSyear_trig_met ','STop_JECAbsolute ','STop_JECAbsolute_year ','STop_JECBBEC1','STop_JECBBEC1_year','STop_JECEC2','STop_JECEC2_year','STop_JECFlavorQCD ','STop_JECHF ','STop_JECHF_year ','STop_JECRelativeBal ','STop_JECRelativeSample_year ','Top_CMSyear_eff_b ','Top_CMSyear_EleID ','Top_CMSyear_EleRECO ','Top_CMSyear_fake_b ','Top_CMSyear_mu_scale ','Top_CMSyear_MuID ','Top_CMSyear_MuISO ','Top_CMSyear_MuTRK ','Top_CMSyear_pdf ','Top_CMSyear_PU ','Top_CMSyear_trig_ele ','Top_CMSyear_trig_met ','Top_JECAbsolute ','Top_JECAbsolute_year ','Top_JECBBEC1','Top_JECBBEC1_year','Top_JECEC2','Top_JECEC2_year','Top_JECFlavorQCD ','Top_JECHF ','Top_JECHF_year ','Top_JECRelativeBal ','Top_JECRelativeSample_year ','WJets_CMSyear_eff_b ','WJets_CMSyear_EleID ','WJets_CMSyear_EleRECO ','WJets_CMSyear_fake_b ','WJets_CMSyear_mu_scale ','WJets_CMSyear_MuID ','WJets_CMSyear_MuISO ','WJets_CMSyear_MuTRK ','WJets_CMSyear_pdf ','WJets_CMSyear_PU ','WJets_CMSyear_trig_ele ','WJets_CMSyear_trig_met ','WJets_JECAbsolute ','WJets_JECAbsolute_year ','WJets_JECBBEC1','WJets_JECBBEC1_year','WJets_JECEC2','WJets_JECEC2_year','WJets_JECFlavorQCD ','WJets_JECHF ','WJets_JECHF_year ','WJets_JECRelativeBal ','WJets_JECRelativeSample_year ','ZJets_CMSyear_eff_b ','ZJets_CMSyear_EleID ','ZJets_CMSyear_EleRECO ','ZJets_CMSyear_fake_b ','ZJets_CMSyear_mu_scale ','ZJets_CMSyear_MuID ','ZJets_CMSyear_MuISO ','ZJets_CMSyear_MuTRK ','ZJets_CMSyear_pdf ','ZJets_CMSyear_PU ','ZJets_CMSyear_trig_ele ','ZJets_CMSyear_trig_met ','ZJets_JECAbsolute ','ZJets_JECAbsolute_year ','ZJets_JECBBEC1','ZJets_JECBBEC1_year','ZJets_JECEC2','ZJets_JECEC2_year','ZJets_JECFlavorQCD ','ZJets_JECHF ','ZJets_JECHF_year ','ZJets_JECRelativeBal ','ZJets_JECRelativeSample_year']
# tobe_comp = ['Jet1Phi', 'METPhi']
# tobe_comp = ['Recoil']
# tobe_comp = ['NTau']
for reg in regions:
    listfiles_1 = [f for f in os.listdir(options.FirstDir+'/bbDMPng/'+reg)]
    listfiles_2 = [f for f in os.listdir(options.SecondDir+'/bbDMPng/'+reg)]
    listfiles_3 = [f for f in os.listdir(options.ThirdDir+'/bbDMPng/'+reg)]
    # print(listfiles_1,listfiles_2,listfiles_3)
    list_temp = []
    # for i in listfiles_1:
    #     for j in listfiles_2:
    #         if (i == j) and [hist for hist in tobe_comp if(hist in i)]:
    #             im_list = [options.FirstDir+'/bbDMPng/'+reg+'/' +
    #                        i, options.SecondDir+'/bbDMPng/'+reg+'/'+j]
    #             list_temp.append(im_list)
    #         else:
    #             continue
    #     list_comp += list_temp

    for i,j,k in zip(listfiles_1,listfiles_2,listfiles_3):
        if i==j and i==k:
          im_list = [options.FirstDir+'/bbDMPng/'+reg+'/' +i, options.SecondDir+'/bbDMPng/'+reg+'/'+j, options.ThirdDir+'/bbDMPng/'+reg+'/'+k]
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
    fonts = PIL.ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 25)
    # draw[0].text((350, 200), options.FirstDirTxt, font=fonts, fill=(0, 0, 0))
    # draw[1].text((300, 200), options.SecondDirTxt, font=fonts, fill=(0, 0, 0))
    color = 'rgb(255, 0, 0)'
    draw[0].text((110, 120), options.FirstDirTxt, font=fonts, fill=color)
    draw[1].text((110, 120), options.SecondDirTxt, font=fonts, fill=color)
    draw[2].text((110, 120), options.ThirdDirTxt, font=fonts, fill=color)

    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))

    # save that beautiful picture
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    reg_name = im[1].split('/')[-2]
    image_name = (im[1].split('/')[-1]).split('.')[0]
    print(reg_name, image_name)
    imgs_comb.save('compared_files/bbDMPng/'+reg_name+'/'+image_name+'.png', optimize=True, quality=100)
    imgs_comb.save('compared_files/bbDMPdf/'+reg_name+'/'+image_name+'.pdf', optimize=True, quality=100)
    imgs_comb.save('compared_files/allFiles/'+image_name+'.png', optimize=True, quality=20)
