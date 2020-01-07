#!/usr/bin/env python
"""
.. module:: coomaker.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input coo file for robot/robotplus
Output file uses GeoEasy coo

    :param argv[1]: output file with observations
    :param argv[2] (sensor): 1100/1800/1200/5500, default 1200
    :param argv[3] (port): serial port, default COM1

For each target point the point id and prism constant must be input

"""
import sys
import re
import logging

sys.path.append('../pyapi/')

from angle import Angle
from serialiface import SerialIface
from geowriter import GeoWriter
from totalstation import TotalStation
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from leicatca1800 import LeicaTCA1800
from trimble5500 import Trimble5500

def GetFloat(prompt, default=0.0, errstr="Invalid value!"):
    """ read a float value with error control & default
        :param prompt: message to write out to the user
        :param default: default value
        :param errstr: error message if input not float
        :returns: value entered or none
    """
    val = None
    while val is None:
        ans = raw_input((prompt + "[{:.1f}]: ").format(default))
        if len(ans):
            try:
                val = float(ans)
            except ValueError:
                print(errstr)
        else:
            val = default
    return val

def GetInt(prompt, default=0.0, errstr="Invalid value!"):
    """ read an int value with error control & default
        :param prompt: message to write out to the user
        :param default: default value
        :param errstr: error message if input not float
        :returns: value entered or none
    """
    val = None
    while val is None:
        ans = raw_input((prompt + "[{:d}]: ").format(default))
        if len(ans):
            try:
                val = int(ans)
            except ValueError:
                print(errstr)
        else:
            val = default
    return val

if __name__ == "__main__":
    if sys.version_info[0] > 2:  # Python 3 compatibility
        raw_input = input
    # process commandline parameters
    if len(sys.argv) > 1:
        ofname = sys.argv[1]
    else:
        print("Usage: coomaker.py output_file [sensor] [serial_port]")
        exit(-1)
    if ofname[-4:] == '.geo' or ofname[-4:] == '.coo':
        ofname = ofname[:-4]
        otype = 'geo'
    else:
        print("invalid output type, allowed types: .geo, .coo")
        exit(-1)
    if len(sys.argv) > 2:
        stationtype = sys.argv[2]
    else:
        stationtype = '1200'
    if re.search('120[0-9]$', stationtype):
        mu = LeicaTPS1200()
    elif re.search('110[0-9]$', stationtype):
        mu = LeicaTCRA1100()
    elif re.search('180[0-9]$', stationtype):
        mu = LeicaTCA1800()
    elif re.search('550[0-9]$', stationtype):
        mu = Trimble5500()
    else:
        print("unsupported instrument type")
        exit(1)
    if len(sys.argv) > 3:
        port = sys.argv[3]
    else:
        port = '/dev/ttyUSB0'

    #logging.getLogger().setLevel(logging.DEBUG)
    iface = SerialIface("rs-232", port)
    geo_wrt = GeoWriter(dist='.4f', angle='RAD', fname=ofname+'.geo', mode='w')
    coo_wrt = GeoWriter(dist='.4f', angle='RAD', fname=ofname + '.coo', mode='w')
    ts = TotalStation(stationtype, mu, iface)

    # get station data
    coo = {}
    coo['id'] = raw_input("Station id: ")
    coo['east'] = GetFloat("Station  east ")
    coo['north'] = GetFloat("Station north ")
    coo['elev'] = GetFloat("Station  elev ")
    ih = GetFloat("Instrument height ")
    coo_wrt.WriteData(coo)
    # upload station coordinates and instrument height to the instrument
    res = {'errorCode': 0}
    i = 1
    while 'errorCode' in res and i < 3:
        res = ts.SetStation(coo['east'], coo['north'], coo['elev'], ih)
        i += 1
    if 'errorCode' in res:
        print("Failed to upload station coordinates code: {:d}".format(res['errorCode']))
        exit()
    geo = {}
    if otype == 'geo':
        geo['station'] = coo['id']
        geo['ih'] = ih
        geo_wrt.WriteData(geo)
    atr = 1
    ts.SetEDMMode('STANDARD')
    pc = 0.0
    p = 0
    if isinstance(ts.GetMeasureUnit(), LeicaTPS1200):
        print("Prism types:")
        for i in range(20):
            res = ts.SetPrismType(i)
            if 'errorCode' in res:
                continue
            res = ts.GetPc()
            if 'errorCode' in res:
                continue
            if 'pc' in res:
                print(i, res['pc'] * 1000, " mm")
    while 1:
        t_id = raw_input("Target id: ")
        if len(t_id) == 0:
            break
        if isinstance(ts.GetMeasureUnit(), LeicaTPS1200):
            p = GetInt("Prism number (-1 for none) ", p)
            if p >= 0:
                ts.SetPrismType(p)
            else:
                pc = -99
            atr = 0 if p == 2 else 1
        else:
            pc = GetFloat("Prism constant [mm] (-99 for none) ", pc * 1000) / 1000.0
            if pc > -99:
                ts.SetPc(pc)
                #pc = -99
            atr = 0 if pc == 0.00344 else 1
        print(ts.GetPc())
        ts.SetATR(atr)
        raw_input("Target on prism and press enter")
        if atr:
            res = ts.MoveRel(Angle(0), Angle(0), atr)
            if 'errorCode' in res or ts.measureIface.state != ts.measureIface.IF_OK:
                print("Cannot target on prism")
                ts.measureIface.state = ts.measureIface.IF_OK
                continue
        res = ts.Measure()
        obs = ts.GetMeasure()
        obs['id'] = t_id
        geo_wrt.WriteData(obs)
        coo = ts.Coords()
        coo['id'] = t_id
        if pc > -99:
            coo['pc'] = pc
        elif 'pc' in coo:
            del coo['pc']
        coo_wrt.WriteData(coo)
