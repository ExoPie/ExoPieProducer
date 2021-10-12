import os, sys

def getSigXsec(sig_name):
    if 'Ma1000_MChi1_MA1200' in sig_name: Xsec = 0.004647
    if 'Ma100_MChi1_MA600' in sig_name: Xsec = 14.850000
    if 'Ma10_MChi1_MA1200' in sig_name: Xsec = 431.400000
    if 'Ma10_MChi1_MA600' in sig_name: Xsec = 433.400000
    if 'Ma150_MChi1_MA1200' in sig_name: Xsec = 5.738000
    if 'Ma150_MChi1_MA600' in sig_name: Xsec = 5.746000
    if 'Ma200_MChi1_MA1200' in sig_name: Xsec = 2.595000
    if 'Ma200_MChi1_MA600' in sig_name: Xsec = 2.639000
    if 'Ma250_MChi1_MA1200' in sig_name: Xsec = 1.314000
    if 'Ma250_MChi1_MA600' in sig_name: Xsec = 1.345000
    if 'Ma300_MChi1_MA600' in sig_name: Xsec = 0.747900
    if 'Ma350_MChi1_MA1200' in sig_name: Xsec = 0.415900
    if 'Ma350_MChi1_MA600' in sig_name: Xsec = 0.448900
    if 'Ma400_MChi1_MA1200' in sig_name: Xsec = 0.251900
    if 'Ma400_MChi1_MA600' in sig_name: Xsec = 0.289900
    if 'Ma450_MChi1_MA1200' in sig_name: Xsec = 0.159000
    if 'Ma450_MChi1_MA600' in sig_name: Xsec = 0.198300
    if 'Ma500_MChi1_MA1200' in sig_name: Xsec = 0.103100
    if 'Ma500_MChi1_MA600' in sig_name: Xsec = 0.139400
    if 'Ma50_MChi1_MA1200' in sig_name: Xsec = 55.390000
    if 'Ma50_MChi1_MA600' in sig_name: Xsec = 55.710000
    if 'Ma700_MChi1_MA1200' in sig_name: Xsec = 0.023600
    if 'Ma750_MChi1_MA1200' in sig_name: Xsec = 0.017120
    return Xsec

def getSigXsec_official(sig_name):
    if 'ma_10_mA_1200'in sig_name: Xsec =0.9018
    if 'ma_50_mA_1200'in sig_name: Xsec =0.6207
    if 'ma_100_mA_1200'in sig_name: Xsec =0.4139
    if 'ma_150_mA_1200'in sig_name: Xsec =0.2674
    if 'ma_200_mA_1200'in sig_name: Xsec =0.1739
    if 'ma_250_mA_1200'in sig_name: Xsec =0.1159
    if 'ma_300_mA_1200'in sig_name: Xsec =0.07691
    if 'ma_350_mA_1200'in sig_name: Xsec =0.05272
    if 'ma_400_mA_1200'in sig_name: Xsec =0.03691
    if 'ma_450_mA_1200'in sig_name: Xsec =0.02631
    if 'ma_500_mA_1200'in sig_name: Xsec =0.01894
    if 'ma_700_mA_1200'in sig_name: Xsec =0.005757
    if 'ma_750_mA_1200'in sig_name: Xsec =0.004415
    if 'ma_1000_mA_1200'in sig_name: Xsec =0.001411
    if 'ma_10_mA_600'in sig_name: Xsec =0.9124
    if 'ma_50_mA_600'in sig_name: Xsec =0.6275
    if 'ma_100_mA_600'in sig_name: Xsec =0.421
    if 'ma_150_mA_600'in sig_name: Xsec =0.2869
    if 'ma_200_mA_600'in sig_name: Xsec =0.1886
    if 'ma_250_mA_600'in sig_name: Xsec =0.1266
    if 'ma_300_mA_600'in sig_name: Xsec =0.08627
    if 'ma_350_mA_600'in sig_name: Xsec =0.06118
    if 'ma_400_mA_600'in sig_name: Xsec =0.04518
    if 'ma_450_mA_600'in sig_name: Xsec =0.03419
    if 'ma_500_mA_600'in sig_name: Xsec =0.02596
    if 'mphi_10_mchi_1' in sig_name: Xsec = 0.01208000
    if 'mphi_50_mchi_1' in sig_name: Xsec = 0.00710200
    if 'mphi_100_mchi_1' in sig_name: Xsec = 0.00446900
    if 'mphi_150_mchi_1' in sig_name: Xsec = 0.00298100
    if 'mphi_200_mchi_1' in sig_name: Xsec = 0.00186400
    if 'mphi_250_mchi_1' in sig_name: Xsec = 0.00113800
    if 'mphi_300_mchi_1' in sig_name: Xsec = 0.00079840
    if 'mphi_350_mchi_1' in sig_name: Xsec = 0.00039440
    if 'mphi_400_mchi_1' in sig_name: Xsec = 0.00019620
    if 'mphi_450_mchi_1' in sig_name: Xsec = 0.00011120
    if 'mphi_500_mchi_1' in sig_name: Xsec = 0.00008467
    if 'mphi_700_mchi_1' in sig_name: Xsec = 0.00002900
    if 'mphi_750_mchi_1' in sig_name: Xsec = 0.00002412
    if 'mphi_1000_mchi_1' in sig_name: Xsec = 0.00000660
    return Xsec