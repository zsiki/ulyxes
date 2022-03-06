#!/usr/bin/env python3
"""
.. module:: dna_demo.py
    :platform: Unix, Windows

.. moduleauthor:: dr. Siki Zoltan <siki.zoltan@emk.bme.hu>

Leica DNA03 continuous observation to a single target

Usage:

* dna_demo.py /dev/sttyUSB0 csv_file
"""
import sys

sys.path.append('../pyapi')

from leicadnaunit import LeicaDnaUnit
from serialiface import SerialIface
from csvwriter import CsvWriter
from digitallevel import DigitalLevel

n = len(sys.argv)
ser = '/dev/ttyUSB0'
out = 'dna_demo.csv'
if n > 1:
    ser = sys.argv[1]
if n > 2:
    out = sys.arv[2]

mu = LeicaDnaUnit()
iface = SerialIface('x', '/dev/ttyUSB0')
wrt = CsvWriter(angle='DMS', dist='.5f',
                filt=['id', 'distance', 'staff', 'datetime'],
                fname='stdout', mode='a', sep=';')
dna = DigitalLevel('DNA03', mu, iface, wrt)
dna.SetAutoOff(0)
#print (dna.Temperature())
while iface.state == iface.IF_OK:
    dna.Measure()
