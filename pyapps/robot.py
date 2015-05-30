#!/usr/bin/env python
"""
.. module:: robot.py

.. moduleauthor:: Zoltan Siki

    Sample application of Ulyxes PyAPI to measure a series of points

    :param argv[1] input file with directions
    :param argv[2] output file with observations, default stdout
    :param argv[3] (sensor): 1100/1800/1200, default 1200
    :param argv[4] (port): serial port, default COM7
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
    ifname = sys.argv[1]
else:
    print ("Usage: robot.py input_file [output_file] [sensor] [serial_port]")
    exit(-1)
    #ifname = 'robot.geo'
if len(sys.argv) > 2:
    ofname = sys.argv[2]
else:
    ofname = 'stdout'
if len(sys.argv) > 3:
    stationtype = sys.argv[3]
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
if len(sys.argv) > 4:
    port = sys.argv[4]
else:
    port = 'COM7'

iface = SerialIface("rs-232", port)
dmp_wrt = CsvWriter(angle = 'DMS', dist = '.4f', \
    filt = ['station', 'id','hz','v','distance', 'datetime'], \
    fname = ofname + '.dmp', mode = 'a', sep = ';')
coo_wrt = CsvWriter(dist = '.4f', filt = ['id','east','north','elev', 'datetime'], \
    fname = ofname + '.csv', mode = 'a', sep = ';')
ts = TotalStation(stationtype, mu, iface)

# load input data set
g = GeoReader(fname = ifname)
directions = []
max_faces = 0
while 1:
    w = g.GetNext()
    if w is None or len(w) == 0:
        break
    directions.append(w)
    if 'faces' in w and max_faces < w['faces']:
        max_faces = w['faces']

n = 0  # number of faces measured fo far
while n < max_faces:
    if n % 2 == 0:   # face left
        i1 = 1
        i2 = len(directions)
        step = 1
    else:            # face right
        i1 = len(directions) - 1
        i2 = 0
        step = -1

    for i in range(i1, i2, step):
        if directions[i]['faces'] > n:
            pn = directions[i]['pid']
            hz = directions[i]['hz'].GetAngle()
            v = directions[i]['v'].GetAngle()
            if step < 0:
                # change angles to face right
                hz = hz - math.pi if hz > math.pi else hz + math.pi 
                v = PI2 - v
            j = 0   # try count
            if directions[i]['code'] == 'ATR':
                ts.SetATR(1)
                ts.SetEDMMode('STANDARD')
                ts.Move(Angle(hz), Angle(v), 1)
                ts.Measure()
            elif directions[i]['code'] == 'PRISM':
                ts.SetATR(0)
                ts.SetEDMMode('STANDARD')
                ts.Move(Angle(hz), Angle(v), 0)
                # wait for user to target on point
                raw_input("Target on %d point and press enter" % (pn))
                ts.Measure()
            elif directions[i]['code'] == 'RL':
                ts.SetATR(0)
                ts.SetEDMMode('RLSTANDARD')
                ts.Move(Angle(hz), Angle(v), 0)
                # wait for user to target on point
                raw_input("Target on %s point in face %d and press enter" % (pn, n % 2 + 1))
                ts.Measure()
            else:
                print ("Unknow code")
                continue
            obs = ts.GetMeasure()
            if ts.measureIface.state != ts.measureIface.IF_OK or \
                'errorCode' in obs:
                ts.measureIface.state = ts.measureIface.IF_OK
                print "Cannot measure point %s" % pn
                continue
            obs['id'] = pn
            obs['station'] = directions[0]['station']
            coo = {}
            coo['id'] = pn
            coo['east'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * \
                math.sin(obs['hz'].GetAngle())
            coo['north'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * \
                math.cos(obs['hz'].GetAngle())
            coo['elev'] = obs['distance'] * math.cos(obs['v'].GetAngle())
            dmp_wrt.WriteData(obs)
            coo_wrt.WriteData(coo)
    n = n + 1
# rotate back to first point
ts.Move(directions[1]['hz'], directions[1]['v'], 0)