import os
import sys
sys.path.append('../../ExoPieUtils/commonutils/')

import MathUtils as mathutil
from MathUtils import *

def getJECSourceUnc(njets,jetSourceUnc,index=False):
    JECSource_up   ={"Absolute":1.0, "Absolute_year":1.0, "BBEC1":1.0, "BBEC1_year":1.0, "EC2":1.0, "EC2_year":1.0,"FlavorQCD":1.0, "HF":1.0, "HF_year":1.0, "RelativeBal":1.0, "RelativeSample_year":1.0}

    JECSource_down ={"Absolute":1.0, "Absolute_year":1.0, "BBEC1":1.0, "BBEC1_year":1.0, "EC2":1.0, "EC2_year":1.0,"FlavorQCD":1.0, "HF":1.0, "HF_year":1.0, "RelativeBal":1.0, "RelativeSample_year":1.0}

    if index:runOn=njets
    else:runOn=range(njets)
    for i in runOn:
        JECSources = jetSourceUnc[i]

        JECSource_up["Absolute"] *= (1+JECSources[0])
        JECSource_down["Absolute"] *= (1-JECSources[0])

        JECSource_up["Absolute_year"] *= (1+JECSources[1])
        JECSource_down["Absolute_year"] *= (1-JECSources[1])

        JECSource_up["BBEC1"] *= (1+JECSources[2])
        JECSource_down["BBEC1"] *= (1-JECSources[2])

        JECSource_up["BBEC1_year"] *= (1+JECSources[3])
        JECSource_down["BBEC1_year"] *= (1-JECSources[3])

        JECSource_up["EC2"] *= (1+JECSources[4])
        JECSource_down["EC2"] *= (1-JECSources[4])

        JECSource_up["EC2_year"] *= (1+JECSources[5])
        JECSource_down["EC2_year"] *= (1-JECSources[5])

        JECSource_up["FlavorQCD"] *= (1+JECSources[6])
        JECSource_down["FlavorQCD"] *= (1-JECSources[6])

        JECSource_up["HF"] *= (1+JECSources[7])
        JECSource_down["HF"] *= (1-JECSources[7])

        JECSource_up["HF_year"] *= (1+JECSources[8])
        JECSource_down["HF_year"] *= (1-JECSources[8])

        JECSource_up["RelativeBal"] *= (1+JECSources[9])
        JECSource_down["RelativeBal"] *= (1-JECSources[9])

        JECSource_up["RelativeSample_year"] *= (1+JECSources[10])
        JECSource_down["RelativeSample_year"] *= (1-JECSources[10])

    return JECSource_up, JECSource_down