#!/usr/bin/env python
"""
.. module:: measuretoprism.py

.. moduleauthor:: dr. Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>

   Sample application of Ulyxes PyAPI to measure to a moving prism
   
   :param argv[1] (sensor): 110n/180n/120n, default 1200
   :param argv[2] (mode): 0/1/2/3/4 without ATR/with ATR/with ATR no distance/lock single distance/lock with distance, default 1
   :param argv[3] (edm): edm mode STANDARD/FAST, default STANDARD
   :param argv[4] (port): serial port, use a filename for local iface, default COM4
   :param argv[5] (file): output file, default None
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

print len(sys.argv)
print sys.argv[0]
logging.getLogger().setLevel(logging.DEBUG)

if len(sys.argv) > 1:
    if re.search('110[0-9]$', sys.argv[1]):
        from leicatcra1100 import LeicaTCRA1100
        mu = LeicaTCRA1100()
    elif re.search('180[0-9]$' , sys.argv[1]):
        from leicatca1800 import LeicaTCA1800
        mu = LeicaTCA1800()
    elif re.search('120[0-9]$', sys.argv[1]):
        from leicatps1200 import LeicaTPS1200
        mu = LeicaTPS1200()
else:
    # default TPS 1200
    from leicatps1200 import LeicaTPS1200
    mu = LeicaTPS1200()
# measure mode
mode = 1
if len(sys.argv) > 2:
    mode = int(sys.argv[2])
# EDM mode
edm = 0
if len(sys.argv) > 3:
    edm = sys.argv[3]
# serial port
com = 'COM4'
if len(sys.argv) > 4:
    com = sys.argv[4]
if re.search('^COM[0-9]+', com) or re.search('^/dev/.*tty', com):
    iface = SerialIface("rs-232", com)
else:
    iface = LocalIface("testIface", com) # Local iface for testing the module

if len(sys.argv) > 5:
    from csvwriter import CsvWriter
    wrt = CsvWriter(fname = sys.argv[5])
else:
    from echowriter import EchoWriter
    wrt = EchoWriter()

ts = TotalStation("Leica", mu, iface, wrt)

ts.SetEDMMode(edm)
if mode > 0:
    ts.SetLock(0)
    ts.SetATR(1)
    ts.SetEDMMode(4) #TCA 1800 EDM mode for tracking the target TODO
    ts.MoveRel(Angle(0), Angle(0), 1)
    ts.Measure()
    ts.GetMeasure()
    if mode in (3, 4):
        ts.SetLock(1)
        ts.LockIn()
else:
    ts.SetATR(0)

while ts.measureIface.state == ts.measureIface.IF_OK:
    if mode == 0:
        ts.Measure() # distance measurement
        measurement = ts.GetMeasure()
    elif mode == 1:
        ts.MoveRel(Angle(0), Angle(0), 1)  # aim on target with ATR
        ts.Measure()
        measurement = ts.GetMeasure()
    elif mode == 2:
        ts.MoveRel(Angle(0), Angle(0), 1) # aim on target with ATR
        measurement = ts.GetAngles()
    elif mode == 3:
        measurement = ts.GetAngles() # get angles only
    elif mode == 4:
        ts.Measure()
        measurement = ts.GetMeasure()

    #  Get each measurement data
    if 'distance' in measurement:  # Check existence of 'distance' key
        slopeDist = measurement['distance']
    if 'hz' in measurement:  # Check existence of 'hz' key
        hz = measurement['hz']
    if 'v' in measurement:  # Check existence of 'v' key
        v = measurement['v']

    # Compute relative coordinates
    #if('distance' in measurement and 'hz' in measurement and 'v' in measurement):
    try:
        dx = slopeDist * math.sin(v.GetAngle()) * math.sin(hz.GetAngle())
        dy = slopeDist * math.sin(v.GetAngle()) * math.sin(v.GetAngle())
        # Print results for testing purpose
        print "dx  " + str(dx)
        print "dy  " + str(dy)
    except ValueError:
        print "Some measurement data(s) are missing..."


