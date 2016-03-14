#!/usr/bin/env python
"""
.. module:: filemaker.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input file for robot
Output file uses GeoEasy geo format or simple csv

    :param argv[1] output file with observations
    :param argv[2] (sensor): 1100/1800/1200, default 1200
    :param argv[3] (port): serial port, default COM1

For each target point the point id and a type is 
A mode have to be defined for each point
ATRn - use automatic targeting, n is prism type id (1/2/3/...)
PRn - prism with manual targeting, n is prism type id (1/2/3/...)
RL - reflectorless distance with manual targeting
RLA - automatic reflectorless distance measurement
OR - orientation direction, manual targeting, no distance

"""
import sys
import re
import logging

sys.path.append('../pyapi/')

from serialiface import SerialIface
from geowriter import GeoWriter
from csvwriter import CsvWriter
from totalstation import TotalStation

logging.getLogger().setLevel(logging.WARNING)
modes = ['ATR', 'PR', 'RL', 'RLA', 'OR']
modes1 = ['ATR', 'ATR0', 'ATR1', 'ATR2', 'ATR3', 'ATR4', 'ATR5', 'ATR6', 'ATR7', 'PR', 'PR0', 'PR1', 'PR2', 'PR3', 'PR4', 'PR5', 'PR6', 'PR7', 'RL', 'RLA', 'OR']
modes_str = '/'.join(modes)

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 1:
        ofname = sys.argv[1]
    else:
        print ("Usage: filemaker.py output_file [sensor] [serial_port]")
        exit(-1)
    if ofname[-4:] == '.csv' or ofname[-4:] == '.dmp':
        ofname = ofname[:-4]
        otype = 'csv'
    elif ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
        ofname = ofname[:-4]
        otype = 'geo'
    else:
        print "invalid output type, allowed types: .geo, .coo, .csv, .dmp"
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
        port = 'COM1'

    iface = SerialIface("rs-232", port)
    if otype == 'geo':
        geo_wrt = GeoWriter(dist = '.4f', angle = 'RAD', fname = ofname + '.geo', mode = 'w')
        coo_wrt = GeoWriter(dist = '.4f', angle = 'RAD', fname = ofname + '.coo', mode = 'w')
    else:
        geo_wrt = CsvWriter(dist = '.4f', fname = ofname + '.dmp', \
            header = True, filt = ['station', 'id', 'hz', 'v', 'faces'])
        coo_wrt = CsvWriter(dist = '.4f', fname = ofname + '.csv', \
            header = True, filt = ['id', 'east', 'north', 'elev'])
    ts = TotalStation(stationtype, mu, iface)

    # get station data
    coo = {}
    coo['id'] = raw_input("Station id: ")
    coo['east'] = float(raw_input("Station  east: "))
    coo['north'] = float(raw_input("Station north: "))
    coo['elev'] = float(raw_input("Station  elev: "))
    coo_wrt.WriteData(coo)
    ih = float(raw_input("Instrument height: "))
    geo = {}
    if otype == 'geo':
        geo['station'] = coo['id']
        geo['ih'] = ih
        geo_wrt.WriteData(geo)

    faces = int(raw_input("Number of faces: "))
    while 1:
        t_id = raw_input("Target id: ")
        if len(t_id) == 0:
            break
        t_mode = ""
        while not t_mode in modes1:
            t_mode = raw_input("Target mode(" + modes_str + "): ").upper()
        raw_input("Target on point and press enter")
        angles = ts.GetAngles()
        if 'errorCode' in angles or ts.measureIface.state != ts.measureIface.IF.OK:
            print "Cannot get angles from instrument"
            ts.measureIface.state = ts.measureIface.IF.OK
            continue
        if otype == 'csv':
            angles['station'] = coo['id']
        angles['id'] = t_id
        angles['code'] = t_mode
        angles['faces'] = faces
        geo_wrt.WriteData(angles)
