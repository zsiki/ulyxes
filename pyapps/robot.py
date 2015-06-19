#!/usr/bin/env python
"""
.. module:: robot.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to measure a series of points

    :param argv[1] input file with directions
    :param argv[2] output file with observations, default stdout
    :param argv[3] (sensor): 1100/1800/1200, default 1200
    :param argv[4] (port): serial port, default COM7

Input file is a GeoEasy geo file (can be created by filemaker.py).
Sample::

    {2 S2} {3 0.0}                                    # station id & istrumnt h.
    {5 2} {7 6.283145} {8 1.120836} {4 PR0} {112 2}  # target id, hz, v, code,
    {5 T1} {7 2.022707} {8 1.542995} {4 RL} {112 2} # number of faces
    {5 3} {7 3.001701} {8 1.611722} {4 OR} {112 2}
    {5 T2} {7 3.006678} {8 1.550763} {4 ATRn} {112 2}
    {5 4} {7 3.145645} {8 1.610680} {4 PR2} {112 2}
    {5 1} {7 6.002123} {8 1.172376} {4 PR} {112 2}

Codes describe target type::

    ATRn - prism and automatic targeting, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
    PRn - prism, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
    RL - refrectorless observation
    OR - do not measure distance (orientation)

    In case of PR/RL/OR the program stops and the user have to aim at the target
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

if __name__ == "__main__":
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
    coo_wrt = CsvWriter(dist = '.4f', \
        filt = ['id', 'east', 'north', 'elev', 'datetime'], \
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

    maxtry = 3 # number of retry if failed
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
                while j < maxtry:
                    if directions[i]['code'][0:3] == 'ATR':
                        ts.SetATR(1)
                        ts.SetEDMMode('STANDARD')
                        if len(directions[i]['code']) > 3:
                            ts.SetPrismType(int(directions[i]['code'][3:]))
                        ts.Move(Angle(hz), Angle(v), 1)
                        ts.Measure()
                    elif directions[i]['code'][0:2] == 'PR':
                        # prism type: 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
                        ts.SetATR(0)
                        ts.SetEDMMode('STANDARD')
                        if len(directions[i]['code']) > 2:
                            ts.SetPrismType(int(directions[i]['code'][2:]))
                        ts.Move(Angle(hz), Angle(v), 0)
                        # wait for user to target on point
                        raw_input("Target on %s point(%s) in face %d and press enter" % (pn, directions[i]['code'], n % 2 + 1))
                        ts.Measure()
                    elif directions[i]['code'] == 'RL':
                        ts.SetATR(0)
                        ts.SetEDMMode('RLSTANDARD')
                        ts.Move(Angle(hz), Angle(v), 0)
                        # wait for user to target on point
                        raw_input("Target on %s point(%s) in face %d and press enter" % (pn, directions[i]['code'], n % 2 + 1))
                        ts.Measure()
                    elif directions[i]['code'] == 'OR':
                        ts.Move(Angle(hz), Angle(v), 0)
                        # wait for user to target on point
                        raw_input("Target on %s point(%s) in face %d and press enter" % (pn, directions[i]['code'], n % 2 + 1))
                    else:
                        print ("Unknow code")
                        j = maxtry
                        break
                    if directions[i]['code'] == 'OR':
                        obs = ts.GetAngles()
                    else:
                        obs = ts.GetMeasure()
                    if ts.measureIface.state != ts.measureIface.IF_OK or \
                        'errorCode' in obs:
                        ts.measureIface.state = ts.measureIface.IF_OK
                        j = j + 1
                        continue
                    else:
                        break   # observation OK
                if j >= maxtry:
                    print "Cannot measure point %s" % pn
                    continue
                obs['id'] = pn
                obs['station'] = directions[0]['station']
                dmp_wrt.WriteData(obs)
                if directions[i]['code'] != 'OR':
                    coo = {}
                    coo['id'] = pn
                    coo['east'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * \
                        math.sin(obs['hz'].GetAngle())
                    coo['north'] = obs['distance'] * math.sin(obs['v'].GetAngle()) * \
                        math.cos(obs['hz'].GetAngle())
                    coo['elev'] = obs['distance'] * math.cos(obs['v'].GetAngle())
                    coo_wrt.WriteData(coo)
        n = n + 1
    # rotate back to first point
    ts.Move(directions[1]['hz'], directions[1]['v'], 0)
