#!/usr/bin/env python
"""
.. module:: horizsection.py
.. moduleauthor:: Viktoria Zubaly, Zoltan Siki
Sample application of Ulyxes PyAPI to measure a horizontal section(s)
target on the first point of the first section and start this app
coordinates and observations are written to csv file
    :param argv[1] (angle step): angle step between points in DEG, default 45
    :param argv[2] (sensor): 1100/1200/5500, default 1200
    :param argv[3] (port): serial port, default /dev/ttyUSB0
    :param argv[4] (max angle): stop at this direction, default 360 degree
    :param argv[5] (tolerance): acceptable tolerance (meter) from the horizontal plane, default 0.01
    :param argv[6] (iteration): max iteration number for a point, default 10
    :param argv[7].. (elevations): elevations for horizontal sections
"""
import sys
import time
import re
import math
import logging

sys.path.append('../pyapi/')

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from confreader import ConfReader
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from trimble5500 import Trimble5500
from totalstation import TotalStation

class HorizontalSection(object):
    """ Measure a horizontal section at a given elevation
        :param ts: total station instance
        :param elev: elevation for section
        :param hz_start: start horizontal direction (Angle)
        :param step: horizontal step angle (Angle)
        :param hz_max: end horizontal direction (radians)
        :param maxiter: max iteration to find elevation
        :param tol: tolerance for horizontal angle
    """

    def __init__(self, ts, wrt, elev=None, hz_start=None,
                 stepinterval=Angle(45, "DEG"), maxa=PI2, maxiter=10, tol=0.02):
        """ initialize """
        self.ts = ts
        self.wrt = wrt
        self.elev = elev
        self.hz_start = hz_start
        self.stepinterval = stepinterval
        self.maxa = maxa
        self.maxiter = maxiter
        self.tol = tol

    def run(self):
        """ do the observations in horizontal section """
        self.ts.Measure()    # initial measurement for startpoint
        if self.hz_start is not None:
            # rotate to start position, keeping zenith angle
            a = self.ts.GetAngles()
            self.ts.Move(self.hz_start, a['v'])
        startp = self.ts.GetMeasure()
        startp0 = None
        if self.ts.measureIface.state != self.ts.measureIface.IF_OK or 'errorCode' in startp:
            print('FATAL Cannot measure startpoint')
            return 1

        # height of startpoint above the horizontal axis
        if self.elev is None:
            height0 = ts.Coords()['elev']
        else:
            height0 = self.elev
        w = True
        try:
            self.ts.SetRedLaser(1)       # turn on red laser if possible
        except:
            pass
        act = Angle(0)  # actual angle from startpoint
        while act.GetAngle() < self.maxa: # go around the whole circle
            self.ts.Measure() # measure distance0
            if self.ts.measureIface.state != self.ts.measureIface.IF_OK:
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                continue
            nextp = self.ts.GetMeasure()  # get observation data
            if self.ts.measureIface.state != self.ts.measureIface.IF_OK:
                # cannot measure, skip
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                continue

            if 'v' not in nextp or 'distance' not in nextp or 'hz' not in nextp:
                self.ts.MoveRel(self.stepinterval, Angle(0))
                continue
            height = ts.Coords()['elev']
            index = 0
            while abs(height-height0) > self.tol:  # looking for right elevation
                w = True
                zenith = nextp['v'].GetAngle()
                height_rel = nextp['distance'] * math.cos(zenith)
                hd = math.sin(zenith) * nextp['distance']
                zenith1 = math.atan(hd / (height_rel + height0 - height))
                self.ts.MoveRel(Angle(0), Angle(zenith1-zenith))
                ans = self.ts.Measure()
                if 'errCode' in ans:
                    print ('Cannot measure point')
                    break
                index += 1
                if index > self.maxiter or \
                    self.ts.measureIface.state != self.ts.measureIface.IF_OK:
                    w = False
                    self.ts.measureIface.state = self.ts.measureIface.IF_OK
                    logging.warning('Missing measurement')
                    break
                nextp = self.ts.GetMeasure()
                if 'v' not in nextp or 'distance' not in nextp:
                    break
                height = ts.Coords()['elev']
            if 'distance' in nextp and startp0 is None:
                startp0 = nextp # store first valid point on section
            if 'distance' in nextp and w:
                coord = self.ts.Coords()
                res = dict(nextp.items() + coord.items())
                self.wrt.WriteData(res)
            self.ts.MoveRel(self.stepinterval, Angle(0))
            act += self.stepinterval
        # rotate back to start
        self.ts.Move(startp0['hz'], startp0['v'])
        return 0

if __name__ == "__main__":
    if sys.version_info[0] > 2:  # Python 3 compatibility
        raw_input = input

    config_pars = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
            'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'angle_step' : {'required': False, 'type': "float", 'default': 45.0},

        'station_type': {'required' : True, 'type': 'str', 'set': ['1200', '1100', '5500']},
        'port': {'required' : True, 'type': 'str', 'default': '/dev/ttyUSB0'},
        'hz_start': {"required": False, 'type': "str", 'default': None},
        'max_angle': {'required': False, 'type': "float", 'default': 360.0},
        'tolerance': {'required': False, 'type': "float", 'default': 0.01},
        'iteration': {'required': False, 'type': 'int', 'default': 10},
        'height_list': {'required': False, 'type': 'list'},
        'wrt': {'required' : False, 'default': 'stdout'},
        '__comment__': {'required': False, 'type': 'str'}
    }
    logging.getLogger().setLevel(logging.DEBUG)
    # process commandline parameters
    pat = re.compile(r'\.json$')
    #sys.argv.append('horiz.json')
    if len(sys.argv) == 2 and pat.search(sys.argv[1]):
        # load json config
        cr = ConfReader('HorizontalSection', sys.argv[1], None, config_pars)
        cr.Load()
        if not cr.Check():
            print("Config check failed")
            sys.exit(-1)
        logging.basicConfig(format=cr.json['log_format'],
            filename=cr.json['log_file'], filemode='a',
            level=cr.json['log_level'])
        hz_start = None
        if cr.json['hz_start'] is not None:
            hz_start = Angle(float(cr.json['hz_start']), 'DEG')
        stepinterval = Angle(cr.json['angle_step'], 'DEG')
        stationtype = cr.json['station_type']
        port = cr.json['port']
        maxa = cr.json['max_angle'] / 180.0 * math.pi
        tol = cr.json['tolerance']
        maxiter = cr.json['iteration']
        wrt = CsvWriter(angle='DMS', dist='.3f',
            filt=['id', 'east', 'north', 'elev', 'hz', 'v', 'distance'],
            fname=cr.json['wrt'], mode='a', sep=';')
        levels = cr.json['height_list']
    else:
        if len(sys.argv) > 1:
            stepinterval = Angle(float(sys.argv[1]), 'DEG')
        else:
            stepinterval = Angle(45, 'DEG')
        if len(sys.argv) > 2:
            stationtype = sys.argv[2]
        else:
            stationtype = '1200'
        if len(sys.argv) > 3:
            port = sys.argv[3]
        else:
            port = '/dev/ttyUSB0'
        hz_start = None
        if len(sys.argv) > 4:
            maxa = float(sys.argv[4]) / 180.0 * math.pi
        else:
            maxa = PI2
        tol = 0.01
        if len(sys.argv) > 5:
            tol = float(sys.argv[5])
        maxiter = 10    # number of iterations to find point on horizontal plan
        if len(sys.argv) > 6:
            maxiter = int(sys.argv[6])
        wrt = CsvWriter(angle='DMS', dist='.3f',
            filt=['id', 'east', 'north', 'elev', 'hz', 'v', 'distance'],
            fname='stdout', mode='a', sep=';')
        if len(sys.argv) > 7:
            levels = [float(a) for a in sys.argv[7:]]
        else:
            levels = None
    iface = SerialIface("rs-232", port)
    if iface.state != iface.IF_OK:
        print("serial error")
        exit(1)
    if re.search('120[0-9]$', stationtype):
        mu = LeicaTPS1200()
    elif re.search('110[0-9]$', stationtype):
        mu = LeicaTCRA1100()
    elif re.search('550[0-9]$', stationtype):
        mu = Trimble5500()
        iface.eomRead = b'>'
    else:
        print("unsupported instrument type")
        exit(1)

    ts = TotalStation(stationtype, mu, iface)
    if isinstance(mu, Trimble5500):
        print("Please change to reflectorless EDM mode (MNU 722 from keyboard)")
        print("and turn on red laser (MNU 741 from keyboard) and press enter!")
        raw_input()
    else:
        ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
    if levels is not None and len(levels) > 0:
        for i in levels:
            h_sec = HorizontalSection(ts, wrt, i, hz_start, stepinterval, maxa,
                                      maxiter, tol)
            h_sec.run()
    else:
        h_sec = HorizontalSection(ts, wrt, hz_start=hz_start,stepinterval=stepinterval, 
                                  maxa=maxa, maxiter=maxiter, tol=tol)
        h_sec.run()
