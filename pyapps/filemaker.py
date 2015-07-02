#!/usr/bin/env python
"""
.. module:: filemaker.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input file for robot
Output file uses GeoEasy geo format

    :param argv[1] output file with observations
    :param argv[2] (sensor): 1100/1800/1200, default 1200
    :param argv[3] (port): serial port, default COM7

For each target point the point id and a type is 
"""
import sys
import re
import logging

sys.path.append('../pyapi/')

from serialiface import SerialIface
from geowriter import GeoWriter
from totalstation import TotalStation

logging.getLogger().setLevel(logging.WARNING)

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 1:
        ofname = sys.argv[1]
    else:
        print ("Usage: filemaker.py output_file [sensor] [serial_port]")
        exit(-1)
    if ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
        ofname = ofname[:-4]
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
    elif re.search('180[0-9]$', stationtype):
        from leicatca1800 import LeicaTCA1800
        mu = LeicaTCA1800()
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
    geo_wrt = GeoWriter(dist = '.4f', fname = ofname + '.geo')
    coo_wrt = GeoWriter(dist = '.4f', fname = ofname + '.coo')
    ts = TotalStation(stationtype, mu, iface)

    # get station data
    coo = {}
    coo['id'] = raw_input("Station id: ")
    coo['east'] = float(raw_input("Station  east: "))
    coo['north'] = float(raw_input("Station north: "))
    coo['elev'] = float(raw_input("Station  elev: "))
    coo_wrt.WriteData(coo)
    geo = {}
    geo['id'] = coo['id']
    geo['ih'] = 0.0
    geo_wrt.WriteData(geo)

    faces = int(raw_input("Number of faces: "))
    while 1:
        t_id = raw_input("Target id: ")
        if len(t_id) == 0:
            break
        t_mode = raw_input("Target mode(ATR/PR/RL/OR): ")
        raw_input("Target on point and press enter")
        angles = ts.GetAngles()
        angles['id'] = t_id
        angles['code'] = t_mode
        angles['faces'] = faces
        geo_wrt.WriteData(angles)
