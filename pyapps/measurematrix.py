#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
.. module:: measurematrix.py

.. moduleauthor:: Jozsef Attila Janko, Bence Takacs, Zoltan Siki (code optimalization)

Sample application of Ulyxes PyAPI to measure within a rectangular area
   
   :param argv[1] (int): number of horizontal intervals (between measurements), default 1 (perimeter only)
   :param argv[2] (int): number of vertical intervals(between measurements), default 1 (perimeter only)
   :param argv[3] (sensor): 1100/1800/1200, default 1100
   :param argv[4] (port): serial port, default COM5
   :param argv[5]: output file, default stdout
   
usage: python measurematrix.py 9 3 1100 COM5
"""
import re
import sys
sys.path.append('../pyapi/')

from angle import Angle
from serialiface import SerialIface
from totalstation import TotalStation
from filewriter import FileWriter

if __name__ == "__main__":
    # set horizontal stepping interval dh_nr
    dh_nr = 1
    if len(sys.argv) > 1:
        try:
            dh_nr = int(sys.argv[1])
        except ValueError:
            print "invalid numeric value " + sys.argv[1]
            #sys.exit(1)
    # set vertical stepping interval dv_nr
    dv_nr = 1
    if len(sys.argv) > 2:
        try:
            dv_nr = int(sys.argv[2])
        except ValueError:
            print "invalid numeric value " + sys.argv[2]
            #sys.exit(1)
    # set instrument
    stationtype = '1100'
    if len(sys.argv) > 3:
        stationtype = sys.argv[3]
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
        #sys.exit(1)
    # set port
    port = 'COM5'
    if len(sys.argv) > 4:
        port = sys.argv[4]
    iface = SerialIface("test", port)
    # set output file name
    fn = 'measmtrx.txt'
    if len(sys.argv) > 5:
        fn = sys.argv[5]
    # write out measurements
    wrt = FileWriter(angle='DEG', dist = '.3f', fname=fn)
    # TODO error handling wrt
    ts = TotalStation(stationtype, mu, iface, wrt)
    ts.SetATR(0) # turn ATR off
    ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
    ts.SetRedLaser(1) # turn red laser on

    w = raw_input("Target on lower left corner and press Enter")
    w1 = ts.GetAngles()
    w = raw_input("Target on upper right corner and press Enter")
    w2 = ts.GetAngles()

    dh = (w2['hz'].GetAngle() - w1['hz'].GetAngle()) / dh_nr
    dv = (w2['v'].GetAngle() - w1['v'].GetAngle()) / dv_nr
    # measurement loops
    for i in range(dh_nr+1): # horizontal loop
        measdir = i % 2 # check modulo
        hz = Angle(w1['hz'].GetAngle() + i * dh, 'RAD')
        for j in range(dv_nr+1): # vertical loop
            if measdir == 0:
                # move downward at odd steps to right
                ts.Move(hz, Angle(w1['v'].GetAngle() + j * dv, 'RAD'))
            else:
                # move upward at event steps to right
                ts.Move(hz, Angle(w2['v'].GetAngle() - j * dv, 'RAD'))
            ts.Measure()
            ts.GetMeasure()
