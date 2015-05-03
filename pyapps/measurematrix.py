#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    module:: measurematrix.py

    moduleauthor:: Jankó József Attila, dr. Takács Bence

    Sample application of Ulyxes PyAPI to measure within a rectangular pyramid
   
   :param argv[1] (angle): horizontal angle start direction, default None
   :param argv[2] (angle): horizontal angle end direction, default None
   :param argv[3] (angle): vertical angle start direction, default None
   :param argv[4] (angle): vertical angle end direction, default None
   :param argv[5] (angle): number of horizontal intervals (between measurements), default 1 (perimeter only)
   :param argv[6] (angle): number of vertical intervals(between measurements), default 1 (perimeter only)
   :param argv[7] (sensor): 1100/1800/1200, default 1100
   :param argv[8] (port): serial port, default COM5
   
    example: python measurematrix.py 120.5 122.75 75.25 76 9 3 1100 COM5
"""
import re
import sys
import datetime
import logging
import math
sys.path.append('../pyapi/')

from angle import Angle
from leicatcra1100 import LeicaTCRA1100
from serialiface import SerialIface
from totalstation import TotalStation
from localiface import LocalIface

from echowriter import EchoWriter
from filewriter import FileWriter

measure_box=[0,1,2,3,4] # set array for measurement pyramid rectangular 'corners' ([0] unused)
for a in range(1, 5): # 1-4 arguments
    if len(sys.argv) > a:
        measure_box[a] = float(sys.argv[a]) # set measurement pyramid rectangular's edge direction
    else:
        print "argument", a, "must be set (numeric)"
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

##mu=LeicaTCRA1100() # test
##iface=SerialIface('test', 'COM6') # test

wrt = FileWriter(angle='DEG', dist = '.3f', fname='measmtrx.txt') # write out measurements # angle='DMS'
##wrt = FileWriter(angle = 'DMS', dist = '.3f', filt = ['id','hz','v','distance','east','north','elev'], fname = 'stdout', mode = 'a', sep = ';') # test from example
ts = TotalStation(stationtype, mu, iface, wrt)
print ts.GetEDMMode() # for testing SetEDMMode effectiveness
ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
##ts.SetEDMMode(5) # reflectorless distance measurement
print ts.GetEDMMode() # for testing SetEDMMode effectiveness
ts.SetRedLaser(1) # turn red laser on
ts.SetATR(0) # turn ATR off
### measurement loops
for i in range(0, dh_nr): # horizontal loop
    measdir = i%2 # check modulo
    for j in range(0, dv_nr): # vertical loop
        if measdir == 0:
            # move downward at odd steps to right
            ts.Move(Angle(measure_box[1]+i*dh, 'DEG'), Angle(measure_box[3]+j*dv, 'DEG'))
#            print "downward", measure_box[1]+i*dh, measure_box[3]+j*dv
        else:
            # move upward at event steps to right
            ts.Move(Angle(measure_box[1]+i*dh, 'DEG'), Angle(measure_box[4]-j*dv, 'DEG'))
#            print "upward", measure_box[1]+i*dh, measure_box[4]-j*dv
        ts.Measure()
        a = ts.GetMeasure()
        ang_hz = a['hz']
        ang_v = a['v']
        dist = a['distance']
        print dist,ang_hz.GetAngle('DMS'),ang_v.GetAngle('DMS')


