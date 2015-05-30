#!/usr/bin/env python
"""
.. module:: filemaker.py

.. moduleauthor:: Zoltan Siki

    Sample application of Ulyxes PyAPI to create input file for robot

    :param argv[1] output file with observations, default stdout
    :param argv[2] (sensor): 1100/1800/1200, default 1200
    :param argv[3] (port): serial port, default COM7
"""
import sys
import re
import math
import logging

sys.path.append('../pyapi/')

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from georeader import GeoReader
from totalstation import TotalStation

logging.getLogger().setLevel(logging.WARNING)
# process commandline parameters
if len(sys.argv) > 1:
    ofname = sys.argv[1]
else:
    print ("Usage: filemaker.py output_file [sensor] [serial_port]")
    exit(-1)
if len(sys.argv) > 2:
    stationtype = sys.argv[2]
else:
    stationtype = '1200'
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
if len(sys.argv) > 3:
    port = sys.argv[3]
else:
    port = 'COM7'

iface = SerialIface("rs-232", port)
fgeo = open(ofname + '.geo', 'w')
coo_wrt = CsvWriter(dist = '.3f', filt = ['id','east','north','elev'], \
    fname = ofname + '.csv', mode = 'a', sep = ';')
ts = TotalStation(stationtype, mu, iface)

# get station data
coo = {}
coo['id'] = raw_input("Station id: ")
fgeo.write("{2 %s} {3 0.0}\n" % coo['id'])
coo['east'] = float(raw_input("Station  east: "))
coo['north'] = float(raw_input("Station north: "))
coo['elev'] = float(raw_input("Station  elev: "))
coo_wrt.WriteData(coo)

faces = int(raw_input("Number of faces: "))
while 1:
    t_id = raw_input("Target id: ")
    if len(t_id) == 0:
        break
    t_mode = raw_input("Target mode(ATR/PR/RL): ")
    raw_input("Target on point and press enter")
    angles = ts.GetAngles()
    fgeo.write("{5 %s} {7 %.6f} {8 %.6f} {4 %s} {112 %d}\n" % \
        (t_id, angles['hz'].GetAngle(), angles['v'].GetAngle(), \
         t_mode, faces))
fgeo.close()
