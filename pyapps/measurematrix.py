#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    module:: measurematrix.py

    moduleauthor:: Janko Jozsef Attila, dr. Takacs Bence

    Sample application of Ulyxes PyAPI to measure within a rectangular pyramid
   
   :param argv[1] (degree): horizontal angle start direction
   :param argv[2] (degree): horizontal angle end direction
   :param argv[3] (degree): vertical angle start direction
   :param argv[4] (degree): vertical angle end direction
   :param argv[5] (int): number of horizontal intervals (between measurements), default 1 (perimeter only)
   :param argv[6] (int): number of vertical intervals(between measurements), default 1 (perimeter only)
   :param argv[7] (sensor): 1100/1800/1200, default 1100
   :param argv[8] (port): serial port, default COM5
   
    example: python measurematrix.py 120.5 122.75 75.25 76 9 3 1100 COM5
"""
import re
import sys
sys.path.append('../pyapi/')

from angle import Angle
from serialiface import SerialIface
from totalstation import TotalStation
from filewriter import FileWriter

# set array for measurement pyramid rectangular 'corners' ([0] unused)
measure_box = [0,1,2,3,4]
for a in range(1, 5): # 1-4 arguments
    if len(sys.argv) > a:
        # set measurement pyramid rectangular edge direction
        measure_box[a] = float(sys.argv[a])
    else:
        print "missing argument ", a, " (numeric)"
        exit(1)

## set delta horizontal dh
## set horizontal stepping interval dh_nr
## assuming sys.argv[5] is nonzero integer
if len(sys.argv) > 5:
    dh_nr = int(sys.argv[5])
    dh = (measure_box[2]-measure_box[1])/dh_nr
    dh_nr = dh_nr+1 # for 0-dh_nr range at measurement loops
else:
    dh = measure_box[2]-measure_box[1]
    dh_nr = 2 # 2 steps, 1 interval (measure left/right boundaries only)
## set delta vertical dv
## set vertical stepping interval dv_nr
## assuming sys.argv[6] is nonzero integer
if len(sys.argv) > 6:
    dv_nr = int(sys.argv[6])
    dv = (measure_box[4]-measure_box[3])/dv_nr
    dv_nr = dv_nr+1 # for 0-dv_nr range at measurement loops
else:
    dv = measure_box[4]-measure_box[3]
    dv_nr = 2 # 2 steps, 1 interval (measure top/buttom boundaries only)
### set instrument
if len(sys.argv) > 7:
    stationtype = sys.argv[7]
else:
    stationtype = '1100'
if re.search('120[0-9]$', stationtype):
    from leicatps1200 import LeicaTPS1200
    mu = LeicaTPS1200()
elif re.search('110[0-9]$', stationtype):
    from leicatcra1100 import LeicaTCRA1100
    mu = LeicaTCRA1100()
elif re.search('550[0-9]$', stationtype):
    from trimble5500 import Trimble5500
    mu = Trimble5500()
else:
    print "unsupported instrument type"
    exit(1)
### set port
if len(sys.argv) > 8:
    port = sys.argv[8]
else:
    port = 'COM5'
iface = SerialIface("test", port)

# write out measurements # angle='DMS'
wrt = FileWriter(angle='DEG', dist = '.3f', fname='measmtrx.txt')
ts = TotalStation(stationtype, mu, iface, wrt)
ts.SetATR(0) # turn ATR off
ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
ts.SetRedLaser(1) # turn red laser on
### measurement loops
for i in range(0, dh_nr): # horizontal loop
    measdir = i % 2 # check modulo
    for j in range(0, dv_nr): # vertical loop
        if measdir == 0:
            # move downward at odd steps to right
            ts.Move(Angle(measure_box[1]+i*dh, 'DEG'), \
                Angle(measure_box[3]+j*dv, 'DEG'))
        else:
            # move upward at event steps to right
            ts.Move(Angle(measure_box[1]+i*dh, 'DEG'), \
                Angle(measure_box[4]-j*dv, 'DEG'))
        ts.Measure()
        a = ts.GetMeasure()
