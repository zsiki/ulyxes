#!/usr/bin/env python
"""
.. module:: robotplus.py

.. moduleauthor:: Zoltan Siki

Sample application to nod by the totalstation

"""

from sys import argv, path, exit
import logging
import os.path

# check PYTHONPATH
if len([p for p in path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from angle import Angle
from leicatca1800 import LeicaTCA1800
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from trimble5500 import Trimble5500
from serialiface import SerialIface
from totalstation import TotalStation
#mu = LeicaTCA1800()
#mu = LeicaTCRA1100()
mu = LeicaTPS1200()
#mu = Trimble5500
si = SerialIface("si", "/dev/ttyUSB0")
if si.state != si.IF_OK:
    exit(1)

ts = TotalStation("yes", mu, si)

logging.getLogger().setLevel(logging.DEBUG)

if len(argv) < 2:
    yes = 1
else:
    yes = int(argv[1])

if yes:
    dhz = Angle(0)
    dv = Angle(30, "DEG")
else:
    dhz = Angle(30, "DEG")
    dv = Angle(0)

shz = Angle(0)
sv = Angle(90, "DEG")
n = 3

try:
    ts.SetATR(0)
except:
    pass
#print(shz.GetAngle('DMS'), sv.GetAngle('DMS'))
ts.Move(shz, sv, 0)

for i in range(n):
    hz1 = shz - dhz
    v1 = sv - dv
    #print(hz1.GetAngle('DMS'), v1.GetAngle('DMS'))
    ts.Move(hz1, v1, 0)
    hz2 = shz + dhz
    v2 = sv + dv
    #print(hz1.GetAngle('DMS'), v1.GetAngle('DMS'))
    ts.Move(hz2, v2, 0)

ts.Move(shz, sv, 0)
