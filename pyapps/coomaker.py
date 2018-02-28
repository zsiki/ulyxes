#!/usr/bin/env python
"""
.. module:: coomaker.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input coo file for robot/robotplus
Output file uses GeoEasy coo

    :param argv[1]: output file with observations
    :param argv[2] (sensor): 1100/1800/1200, default 1200
    :param argv[3] (port): serial port, default COM1

For each target point the point id and prism constant must be input

"""
import sys
import re

sys.path.append('../pyapi/')

from angle import Angle
from serialiface import SerialIface
from geowriter import GeoWriter
from totalstation import TotalStation

def GetFloat(prompt, errstr="Invalid value!"):

    val = None
    while val is None:
        try:
            val = float(raw_input(prompt))
        except ValueError:
            print errstr
    return val

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 1:
        ofname = sys.argv[1]
    else:
        print "Usage: coomaker.py output_file [sensor] [serial_port]"
        exit(-1)
    if ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
        ofname = ofname[:-4]
        otype = 'geo'
    else:
        print "invalid output type, allowed types: .geo, .coo, .csv, .dmp"
        exit(-1)
    if len(sys.argv) > 2:
        stationtype = sys.argv[2]
    else:
        stationtype = '1800'
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
        port = '/dev/ttyUSB0'

    iface = SerialIface("rs-232", port)
    geo_wrt = GeoWriter(dist='.4f', angle='RAD', fname=ofname+'.geo', mode='w')
    coo_wrt = GeoWriter(dist='.4f', angle='RAD', fname=ofname + '.coo', mode='w')
    ts = TotalStation(stationtype, mu, iface)

    # get station data
    coo = {}
    coo['id'] = raw_input("Station id: ")
    coo['east'] = GetFloat("Station  east: ")
    coo['north'] = GetFloat("Station north: ")
    coo['elev'] = GetFloat("Station  elev: ")
    ih = GetFloat("Instrument height: ")
    coo_wrt.WriteData(coo)
    # upload station coordinates and instrument height to the instrument
    ts.SetStation(coo['east'], coo['north'], coo['elev'], ih)
    print ts.GetStation()
    geo = {}
    if otype == 'geo':
        geo['station'] = coo['id']
        geo['ih'] = ih
        geo_wrt.WriteData(geo)

    ts.SetATR(1)
    ts.SetEDMMode('STANDARD')
    while 1:
        t_id = raw_input("Target id: ")
        if len(t_id) == 0:
            break
        pc = float(raw_input("Prism constant [mm]: ")) / 1000.0
        raw_input("Target on prism and press enter")
        ts.SetPc(pc)
        res = ts.MoveRel(Angle(0), Angle(0), 1)
        if 'errorCode' in res or ts.measureIface.state != ts.measureIface.IF_OK:
            print "Cannot target on prism"
            ts.measureIface.state = ts.measureIface.IF_OK
            continue
        res = ts.Measure()
        obs = ts.GetMeasure()
        obs['id'] = t_id
        geo_wrt.WriteData(obs)
        coo = ts.Coords()
        coo['id'] = t_id
        coo['pc'] = pc
        coo_wrt.WriteData(coo)
