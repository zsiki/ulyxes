#!/usr/bin/env python3
"""
.. module:: dna_demo.py
    :platform: Unix, Windows

.. moduleauthor:: dr. Siki Zoltan <siki.zoltan@emk.bme.hu>

Leica DNA03 continuous observation to a single target

Usage:

* dna_demo.py [serial_port] [csv_file] [number_of_readings]
"""
import sys
import signal
import os.path

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from leicadnaunit import LeicaDnaUnit
from serialiface import SerialIface
from csvwriter import CsvWriter
from digitallevel import DigitalLevel

def handler(signum, frame):
    """ catch ctrl/C from keyboard """
    sys.exit()

n = len(sys.argv)
# default parameters
ser = '/dev/ttyUSB0'
out = 'stdout'
k = -1                  # infinite readings
if n > 1:
    ser = sys.argv[1]
if n > 2:
    out = sys.argv[2]
if n > 3:
    k = int(sys.argv[3])
mu = LeicaDnaUnit()
iface = SerialIface('x', ser)
wrt = CsvWriter(angle='DMS', dist='.5f',
                filt=['id', 'distance', 'staff', 'datetime'],
                fname=out, mode='a', sep=';')
dna = DigitalLevel('DNA03', mu, iface, wrt)
dna.SetAutoOff(0)
#print (dna.Temperature())

signal.signal(signal.SIGINT, handler)   # catch ctrl/C
i = 0
while iface.state == iface.IF_OK and i != k:
    dna.Measure()
    i += 1
