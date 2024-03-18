#!/usr/bin/env python3
"""
.. module:: horizsection.py

.. moduleauthor:: Viktoria Zubaly, Zoltan Siki

Sample application of Ulyxes PyAPI to measure horizontal section(s).

Several parameters can be set from the command line or from a
JSON configuration file.

Parameters are stored in a config file using JSON format::

    log_file: name of log file
    log_level: 10/20/30/40/50
    log_format: format string for log file
    angle_step: angle step in section
    station type: Total station type 1200/1100/5500
    station_east: Station east coordinate
    station_north: Station north coordinate
    station_elev: Station elevation
    port: Communication port
    hz_start: Horizontal start direction bottom
    hz_top: Horizontam start direction top
    max_angle: Max angle from start direction at bottom
    max_top: Max angle from top direction
    tolerance: Height tolerance
    iteration: number of iterations to find section
    height_list: Elevation list for section

Command line parameters::

    -l LOG, --log LOG     Logfile name "stdout" for screen output
    --level LEVEL         Log level
    --format FORMAT       Log format
    --step STEP           Angle step in section
    --type TYPE           Total station type
    --east EAST           Station east
    --north NORTH         Station north
    --elev ELEV           Station elevation
    -p PORT, --port PORT  Communication port
    --start START         Horizontal start direction
    --top TOP             Horizontal start direction at top
    --max MAX             Max angle
    --tmax TMAX           Max angle at top
    --tol TOL             Height tolerance
    --iter ITER           Max iteration to find section
    --heights HEIGHTS     list of elevations for more sections
    --wrt WRT             Output file
"""
import sys
import os.path
import re
import math
import logging
import argparse

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from angle import Angle, PI2
from serialiface import SerialIface
from csvwriter import CsvWriter
from confreader import ConfReader
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from trimble5500 import Trimble5500
from totalstation import TotalStation

class HorizontalSection():
    """ Measure a horizontal section at a given elevation

        :param ts: total station instance
        :param wrt: result writer
        :param hoc: height of collimation
        :param elev: elevation for section
        :param hz_start: start horizontal direction (Angle)
        :param step: horizontal step angle (Angle)
        :param hz_max: end horizontal direction (radians)
        :param maxiter: max iteration to find elevation
        :param tol: tolerance for horizontal angle
        :param levels: more parameters at horizontal cross sections to measure
    """

    def __init__(self, ts, wrt, hoc=0.0, elev=None, hz_start=None,
                 stepinterval=Angle(45, "DEG"), maxa=Angle(PI2), maxiter=10, tol=0.02):
        """ initialize """
        self.ts = ts
        self.wrt = wrt
        self.elev = elev
        self.hz_start = hz_start
        self.stepinterval = stepinterval
        self.maxa = maxa
        self.maxiter = maxiter
        self.tol = tol
        self.hoc = hoc  # height of collimation

    def invalid(self, ans):
        """ check observation results are complete
            use after GetMeasure

            :param ans: result of GetMeasure call
            :returns True/False invalid/valid
            """
        return self.ts.measureIface.state != self.ts.measureIface.IF_OK or \
                'errorCode' in ans or \
                'hz' not in ans or 'v' not in ans or 'distance' not in ans or \
                ans['distance'] < 0.1

    def run(self):
        """ do the observations in horizontal section """
        if self.hz_start is not None:
            # rotate to start position, keeping zenith angle
            a = self.ts.GetAngles()
            self.ts.Move(self.hz_start, a['v'])
        ans = self.ts.Measure()    # initial measurement for startpoint
        if 'errCode' in ans:
            print('FATAL Cannot measure startpoint')
            return 1
        startp0 = None
        startp = self.ts.GetMeasure()
        if self.invalid(startp):
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
        except Exception:
            pass
        act = Angle(0)  # actual angle from startpoint
        while act.GetAngle() < self.maxa.GetAngle(): # go around the whole section
            ans = self.ts.Measure() # measure distance
            if self.ts.measureIface.state != self.ts.measureIface.IF_OK or \
                    'errCode' in ans:
                # skip this and move to next point
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                continue
            nextp = self.ts.GetMeasure()  # get observation data
            if self.invalid(nextp):
                # cannot measure, skip
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                continue
            height = ts.Coords()['elev']
            index = 0
            while abs(height-height0) > self.tol:  # looking for right elevation
                w = True
                zenith = nextp['v'].GetAngle()
                hd = math.sin(zenith) * nextp['distance']
                dz = height0 - self.hoc # height difference from the height of collimation
                alpha = math.atan(abs(dz) / hd)
                zenith1 = math.pi / 2.0 + alpha if dz < 0 else math.pi / 2.0 - alpha
                self.ts.MoveRel(Angle(0), Angle(zenith1-zenith))
                ans = self.ts.Measure()
                if 'errCode' in ans:
                    logging.warning('Cannot measure point, skip')
                    w = False
                    break
                index += 1
                if index > self.maxiter or \
                    self.ts.measureIface.state != self.ts.measureIface.IF_OK:
                    w = False
                    self.ts.measureIface.state = self.ts.measureIface.IF_OK
                    logging.warning('Missing measurement')
                    break
                nextp = self.ts.GetMeasure()
                if self.invalid(nextp):
                    w = False
                    break
                height = ts.Coords()['elev']
            if 'distance' in nextp and startp0 is None:
                startp0 = nextp # store first valid point on section
            if 'distance' in nextp and w:
                coord = self.ts.Coords()
                res = dict(list(nextp.items()) + list(coord.items()))
                self.wrt.WriteData(res)
            self.ts.MoveRel(self.stepinterval, Angle(0))
            act += self.stepinterval
        # rotate back to start
        if startp0 is not None:
            self.ts.Move(startp0['hz'], startp0['v'])
        try:
            self.ts.SetRedLaser(0)       # turn off red laser if possible
        except Exception:
            pass
        return 0

def cmd_params():
    """ process command line parameters
        parameters can be given by switches or in a json file
    """
    # defaults
    def_logfile = 'stdout'
    def_logging = logging.ERROR
    def_format = "%(asctime)s %(levelname)s:%(message)s"
    def_angle = 45.0
    def_east = 0.0
    def_north = 0.0
    def_elev = 0.0
    def_ih = 0.0    # instrument height
    def_port = '/dev/ttyUSB0'
    def_start = None
    def_top = None
    def_max = 359.9
    def_tmax = 359.9
    def_tol = 0.01
    def_iter = 10
    def_hlist = None
    def_wrt = 'stdout'
    hz_start = def_start
    levels = None
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]):
        # process JSON config and drop other switches
        config_pars = {
            'log_file': {'required' : False, 'type': 'logfile', 'default': def_logfile},
            'log_level': {'required' : False, 'type': 'int',
                          'set': [logging.DEBUG, logging.INFO, logging.WARNING,
                                  logging.ERROR, logging.FATAL],
                          'default': def_logging},
            'log_format': {'required': False, 'default': def_format},
            'angle_step' : {'required': False, 'type': "float", 'default': def_angle},

            'station_type': {'required' : True, 'type': 'str', 'set': ['1200', '1100', '5500']},
            'station_east': {'required' : False, 'type': 'float', 'default': def_east},
            'station_north': {'required' : False, 'type': 'float', 'default': def_north},
            'station_elev': {'required' : False, 'type': 'float', 'default': def_elev},
            'station_ih': {'required' : False, 'type': 'float', 'default': def_ih},
            'port': {'required' : False, 'type': 'str', 'default': def_port},
            'hz_start': {"required": False, 'type': "str", 'default': def_start},
            'hz_top': {"required": False, 'type': "str", 'default': def_top},
            'max_angle': {'required': False, 'type': "float", 'default': def_max},
            'max_top': {'required': False, 'type': "float", 'default': def_tmax},
            'tolerance': {'required': False, 'type': "float", 'default': def_tol},
            'iteration': {'required': False, 'type': 'int', 'default': def_iter},
            'height_list': {'required': False, 'type': 'list', 'default': def_hlist},
            'wrt': {'required' : False, 'default': 'stdout'},
            '__comment__': {'required': False, 'type': 'str'}
        }
        cr = ConfReader('HorizontalSection', sys.argv[1], config_pars)
        cr.Load()
        state, msg_lst = cr.Check()
        if state == "FATAL":
            print("Config check failed")
            for msg in msg_lst:
                print(msg)
            sys.exit(-1)

        logging.basicConfig(format=cr.json['log_format'],
                            filename=cr.json['log_file'], filemode='a',
                            level=cr.json['log_level'])
        # deffered config warnings
        if state == "WARNING":
            for msg in msg_lst:
                logging.error(msg)
        if cr.json['hz_start'] is not None:
            hz_start = Angle(float(cr.json['hz_start']), 'DEG')
        if cr.json['hz_top'] is not None:
            hz_top = Angle(float(cr.json['hz_top']), 'DEG')
        else:
            hz_top = hz_start
        stepinterval = Angle(cr.json['angle_step'], 'DEG')
        stationtype = cr.json['station_type']
        east = cr.json['station_east']
        north = cr.json['station_north']
        elev = cr.json['station_elev']
        ih = cr.json['station_ih']
        port = cr.json['port']
        maxa = Angle(cr.json['max_angle'], "DEG")
        if cr.json['max_top'] is not None:
            maxt = Angle(cr.json['max_top'], "DEG")
        else:
            maxt = maxa
        tol = cr.json['tolerance']
        maxiter = cr.json['iteration']
        wrt_file = cr.json['wrt']
        levels = cr.json['height_list']
    else:
        # process command line switches
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--log', type=str, default=def_logfile,
                help=f'Logfile name, default: {def_logfile}, "stdout" for screen output')
        parser.add_argument('--level', type=int, default=def_logging,
                help=f'Log level, default: {def_logging}')
        parser.add_argument('--format', type=str, default=def_format,
                help='Log format, default: time, level, message')
        parser.add_argument('--step', type=float, default=def_angle,
                help=f'Angle step in section [DEG], default: {def_angle}')
        parser.add_argument('--type', type=str, required=True,
                            help='Total station type')
        parser.add_argument('--east', type=float, default=def_east,
                help=f'Station east, default: {def_east}')
        parser.add_argument('--north', type=float, default=def_north,
                help=f'Station north, default: {def_north}')
        parser.add_argument('--elev', type=float, default=def_elev,
                help=f'Station elevation, default: {def_elev}')
        parser.add_argument('--ih', type=float, default=def_ih,
                help=f'Instrument height, default: {def_ih}')
        parser.add_argument('-p', '--port', type=str, default=def_port,
                help=f'Communication port, default: {def_port}')
        parser.add_argument('--start', type=float, default=def_start,
                help='Horizontal start direction, default: actual telescope direction')
        parser.add_argument('--top', type=float, default=def_top,
                help='Horizontal start direction at top, default: same as start')
        parser.add_argument('--max', type=float, default=def_max,
                help='Max angle, default: whole circle')
        parser.add_argument('--tmax', type=float, default=def_tmax,
                help='Max angle at top, default: same as max')
        parser.add_argument('--tol', type=float, default=def_tol,
                help=f'Height tolerance, default: {def_tol}')
        parser.add_argument('--iter', type=int, default=def_iter,
                help='Max iteration to find section, default: {def_iter}')
        parser.add_argument('--heights', type=str, default=def_hlist,
                help='list of elevations for more sections between double quotes, default: single section at the telescope direction')
        parser.add_argument('--wrt', type=str, default=def_wrt,
                help=f'Name of output file, default: {def_wrt}')
        args = parser.parse_args()

        logging.basicConfig(format=args.format, filename=args.log, filemode='a',
                            level=args.level)
        hz_start = None
        if args.start is not None:
            hz_start = Angle(args.start, 'DEG')
        stepinterval = Angle(args.step, 'DEG')
        stationtype = args.type
        east = args.east
        north = args.north
        elev = args.elev
        ih = args.ih
        port = args.port
        maxa = Angle(args.max, "DEG")
        hz_top = None
        if args.top is not None:
            hz_top = Angle(args.top, 'DEG')
        maxt = None
        if args.tmax is not None:
            maxt = Angle(args.tmax, 'DEG')
        tol = args.tol
        maxiter = args.iter
        wrt_file = args.wrt
        try:
            if args.heights is not None:
                levels = [float(l) for l in args.heights.split()]
        except Exception:
            print("parameter error --heights")
            sys.exit(1)

    return {'hz_start': hz_start, 'hz_top': hz_top,
            'stepinterval': stepinterval,
            'stationtype': stationtype,
            'east': east, 'north': north, 'elev': elev, 'ih': ih, 'port': port,
            'max': maxa, 'maxt': maxt,
            'tol': tol, 'iter': maxiter, 'wrt': wrt_file, 'levels': levels}

if __name__ == "__main__":
    # process parameters
    params = cmd_params()
    # writer for instrument
    wrt = CsvWriter(angle='DMS', dist='.3f',
                    filt=['id', 'east', 'north', 'elev', 'hz', 'v', 'distance'],
                    fname=params['wrt'], mode='a', sep=';')
    # iface for instrument
    iface = SerialIface("rs-232", params['port'])
    if iface.state != iface.IF_OK:
        print("serial error")
        sys.exit(1)
    # measure interface for instrument
    if re.search('120[0-9]$', params['stationtype']):
        mu = LeicaTPS1200()
    elif re.search('110[0-9]$', params['stationtype']):
        mu = LeicaTCRA1100()
    elif re.search('550[0-9]$', params['stationtype']):
        mu = Trimble5500()
        iface.eomRead = b'>'
    else:
        print("unsupported instrument type")
        sys.exit(1)
    # create instrument
    ts = TotalStation(params['stationtype'], mu, iface)
    if isinstance(mu, Trimble5500):
        print("Please change to reflectorless EDM mode (MNU 722 from keyboard)")
        print("and turn on red laser (MNU 741 from keyboard) and press enter!")
        input()
    else:
        ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
    # set station coordinates
    ts.SetStation(params['east'], params['north'], params['elev'])
    hoc = params['elev'] + params['ih']
    levels = params['levels']
    if levels is not None and len(levels) > 1:
        if params['hz_start'] is None:
            a = ts.GetAngles()
            params['hz_start'] = a['hz']
        if params['hz_top'] is None:
            params['hz_top'] = params['hz_start']
        dhz = params['hz_top'].GetAngle("DEG") - params['hz_start'].GetAngle("DEG")
        z0 = levels[0]
        z1 = levels[-1]
        dmax = params['maxt'].GetAngle("DEG") - params['max'].GetAngle("DEG")
        for level in levels:
            hz = Angle(params['hz_start'].GetAngle("DEG") + (level - z0) / (z1 - z0) * dhz, "DEG")
            ma = Angle(params['max'].GetAngle("DEG") + (level - z0) / (z1 - z0) * dmax, "DEG")
            h_sec = HorizontalSection(ts, wrt, hoc, level, hz,
                                      params['stepinterval'], ma,
                                      params['iter'], params['tol'])
            h_sec.run()
    else:
        if levels is None or len(levels) == 0:
            h_sec = HorizontalSection(ts, wrt, hoc, None, params['hz_start'],
                                      params['stepinterval'], params['max'],
                                      params['iter'], params['tol'])
        else:
            h_sec = HorizontalSection(ts, wrt, levels[0], params['hz_start'],
                                      params['stepinterval'], params['max'],
                                      params['iter'], params['tol'])
        h_sec.run()
