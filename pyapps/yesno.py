#!/usr/bin/env python
"""
.. module:: robotplus.py

.. moduleauthor:: Zoltan Siki

Sample application to nod by the totalstation

"""

from sys import argv, path

path.append('../pyapi/')

from angle import Angle
from leicatca1800 import LeicaTCA1800
from serialiface import SerialIface
from totalstation import TotalStation

mu = LeicaTCA1800()
si = SerialIface("si", "/dev/ttyUSB0")
ts = TotalStation("yes", mu, si)

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


for i in range(n):
    ts.Move(shz - dhz, sv - dv)
    ts.Move(shz + dhz, sv + dv)

ts.Move(shz,sv)
