#!/usr/bin/env python
"""
.. module:: horizsection.py

.. moduleauthor:: Viktoria Zubaly, Zoltan Siki

    Sample application of Ulyxes PyAPI to measure a horizontal section

	:param argv[1] (angle step): angle step between point in DEG, default 45
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
from totalstation import TotalStation

logging.getLogger().setLevel(logging.WARNING)
if len(sys.argv) > 1:
    stepinterval = Angle(float(sys.argv[1]), 'DEG')
else:
    stepinterval = Angle(45, 'DEG')
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
MAXITER = 10
iface = SerialIface("rs-232", port)
wrt = CsvWriter(angle = 'DMS', dist = '.3f', filt = ['id','hz','v','distance','east','north','elev'], fname = 'stdout', mode = 'a', sep = ';')
ts = TotalStation(stationtype, mu, iface)
ts.SetEDMMode('RLSTANDARD')
ts.Measure()
startp = ts.GetMeasure()
if ts.measureIface.state != ts.measureIface.IF_OK or 'errorCode' in startp:
    print 'Start again!'
    exit(1)

act = Angle(0)
height0 = math.cos(startp['v'].GetAngle()) * startp['distance']
w = True
while act.GetAngle() < PI2:
   ts.Measure()
   if ts.measureIface.state != ts.measureIface.IF_OK:
       ts.measureIface.state = ts.measureIface.IF_OK
       ts.MoveRel(stepinterval, Angle(0))
       continue
   nextp = ts.GetMeasure()
   if ts.measureIface.state != ts.measureIface.IF_OK:
       ts.measureIface.state = ts.measureIface.IF_OK
       ts.MoveRel(stepinterval, Angle(0))
       continue

   height = math.cos(nextp['v'].GetAngle()) * nextp['distance']
   index = 0
   while abs(height-height0) > 0.01:
       w = True
       zenith = nextp['v'].GetAngle()
       zenith1 = math.acos(height0 / nextp['distance'])	
       ts.MoveRel(Angle(0), Angle(zenith1-zenith))	   
       ts.Measure()
       index += 1
       if index > MAXITER or ts.measureIface.state != ts.measureIface.IF_OK:
           w = False
           ts.measureIface.state = ts.measureIface.IF_OK
           logging.warning('Missing measurement')
           break
       nextp = ts.GetMeasure()
       if not 'v' in nextp or not 'distance' in nextp:
           break
       height = math.cos(nextp['v'].GetAngle()) * nextp['distance']
   if 'distance' in nextp and w:
       coord = ts.Coords()
       res = dict(nextp.items()+coord.items())
       wrt.WriteData(res)
   ts.MoveRel(stepinterval, Angle(0))
   act += stepinterval
