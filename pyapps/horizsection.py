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
    --pid ID              Start of point IDs, default 0
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
from georeader import GeoReader
from csvreader import CsvReader
from csvwriter import CsvWriter
from confreader import ConfReader
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from axis10 import Axis10
from trimble5500 import Trimble5500
from totalstation import TotalStation
from blindorientation import Orientation
from filegen import ObsGen
from robot import Robot
from freestation import Freestation
from anystation import AnyStation

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
        :param pid: start point id
    """

    def __init__(self, ts, wrt, st_east=None, st_north=None, hoc=None, elev=None,
                 hz_start=None, stepinterval=Angle(45, "DEG"), maxa=Angle(PI2),
                 maxiter=10, tol=0.02):
        """ initialize """
        self.ts = ts
        self.wrt = wrt
        self.st_east = st_east
        self.st_north = st_north
        self.hoc = hoc  # height of collimation
        self.elev = elev
        self.hz_start = hz_start
        self.stepinterval = stepinterval
        self.maxa = maxa
        self.maxiter = maxiter
        self.tol = tol

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

    def Coords(self, measure):
        """ calculate target coordinates

            :param measure: disctionary of observations
            :returns: dictionary of coords
        """
        hd = measure['distance'] * math.sin(measure['v'].GetAngle())
        east = self.st_east + hd * math.sin(measure['hz'].GetAngle())
        north = self.st_north + hd * math.cos(measure['hz'].GetAngle())
        elev = self.hoc +  measure['distance'] * math.cos(measure['v'].GetAngle())
        return {'east': east, 'north': north, 'elev': elev}

    def run(self):
        """ do the observations in horizontal section """
        if self.hz_start is not None:
            # rotate to start position, keeping zenith angle
            a = self.ts.GetAngles()
            self.ts.Move(self.hz_start, a['v'])
        startp0 = None

        if self.elev is None:
            ans = self.ts.Measure()    # initial measurement for startpoint
            if 'errCode' in ans:
                print('FATAL Cannot measure startpoint')
                return 1
            startp = self.ts.GetMeasure()
            if self.invalid(startp):
                print('FATAL Cannot measure startpoint')
                return 1
            # coords of startpoint
            coords = self.Coords(startp)
            height0 = coords['elev']
        else:
            height0 = self.elev
        w = True
        act = Angle(0)  # actual angle from startpoint
        while act.GetAngle() < self.maxa.GetAngle(): # go around the whole section
            ans = self.ts.Measure() # measure distance
            if self.ts.measureIface.state != self.ts.measureIface.IF_OK or \
                    'errCode' in ans:
                # skip this and move to next point
                logging.warning('Cannot measure point, skip')
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                act += self.stepinterval
                continue
            nextp = self.ts.GetMeasure()  # get observation data
            if self.invalid(nextp):
                # cannot measure, skip
                logging.warning('Cannot measure point, skip')
                self.ts.measureIface.state = self.ts.measureIface.IF_OK
                self.ts.MoveRel(self.stepinterval, Angle(0))
                act += self.stepinterval
                continue
            coords = self.Coords(nextp)
            height = coords['elev']
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
                coords = self.Coords(nextp)
                height = coords['elev']
            if 'distance' in nextp and startp0 is None:
                startp0 = nextp # store first valid point on section
            if 'distance' in nextp and w:
                #coord = self.Coords(nextp)
                res = dict(list(nextp.items()) + list(coords.items()))
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
    def_type = "1200"
    def_angle = 45.0
    def_east = None
    def_north = None
    def_elev = None
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
    def_coords = None   # coordinates of reference points for blind orientation
    def_pid = 0
    hz_start = def_start
    levels = None
    def_gama = 'gama-local'
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

            'station_type': {'required' : False, 'type': 'str', 'set': ['1200', '1100', '5500', 'axis10'], 'default': def_type},
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
            'wrt': {'required': False, 'default': 'stdout'},
            'coords': {'required': False, 'default': def_coords},
            'pid': {'required' : False, 'type': 'int', 'default': def_pid},
            'center_east': {'required' : False, 'type': 'float', 'default': None},
            'center_north': {'required' : False, 'type': 'float', 'default': None},
            'radius': {'required' : False, 'type': 'float', 'default': None},
            'gama': {'required' : False, 'type': 'str', 'default': None},
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

        if cr.json['log_file'] == 'stdout':
            logging.basicConfig(format=cr.json['log_format'],
                                level=cr.json['log_level'])
        else:
            logging.basicConfig(format=cr.json['log_format'],
                                filename=cr.json['log_file'], filemode='a',
                                level=cr.json['log_level'])
        # deffered config warnings
        if state == "WARNING":
            for msg in msg_lst:
                logging.warning(msg)
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
        coords = cr.json['coords']
        levels = cr.json['height_list']
        pid = cr.json['pid']
        center_east = cr.json['center_east']
        center_north = cr.json['center_north']
        radius = cr.json['radius']
        gama = cr.json['gama']
    else:
        # process command line switches
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--log', type=str, default=def_logfile,
                help=f'Logfile name, default: {def_logfile}, "stdout" for screen output')
        parser.add_argument('--log_level', type=int, default=def_logging,
                help=f'Log level, default: {def_logging}')
        parser.add_argument('--log_format', type=str, default=def_format,
                help='Log format, default: time, level, message')
        parser.add_argument('--step', type=float, default=def_angle,
                help=f'Angle step in section [DEG], default: {def_angle}')
        parser.add_argument('--type', type=str, required=False, default=def_type,
                help=f'Total station type, default: {def_type}')
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
                help=f'Max iteration to find section, default: {def_iter}')
        parser.add_argument('--heights', type=str, default=def_hlist,
                help='list of elevations for more sections between double quotes, default: single section at the telescope direction')
        parser.add_argument('--wrt', type=str, default=def_wrt,
                help=f'Name of output file, default: {def_wrt}')
        parser.add_argument('--coords', type=str, default=def_coords,
                help=f'Name of coordinate file, default: {def_coords}')
        parser.add_argument('--pid', type=int, default=def_pid,
                help=f'Starting point ID, default: {def_pid}')
        parser.add_argument('--center_east', type=float, default=None,
                            help='Center point east of section, default: None')
        parser.add_argument('--center_north', type=float, default=None,
                            help='Center point north of section, default: None')
        parser.add_argument('--radius', type=float, default=None,
                            help='Radius of section, default: None')
        parser.add_argument('--gama', type=str, default=def_gama,
                            help=f'Path to gama-local, default: {def_gama}')
        args = parser.parse_args()

        if args.log == "stdout":
            logging.basicConfig(format=args.format, filemode='a',
                                level=args.level)
        else:
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
        coords = args.coords
        try:
            if args.heights is not None:
                levels = [float(l) for l in args.heights.split()]
        except Exception:
            print("parameter error --heights")
            sys.exit(1)
        pid = args.pid
        center_east = args.center_east
        center_north = args.center_north
        radius = args.radius
        gama = args.gama

    return {'hz_start': hz_start, 'hz_top': hz_top,
            'stepinterval': stepinterval,
            'stationtype': stationtype,
            'east': east, 'north': north, 'elev': elev, 'ih': ih, 'port': port,
            'max': maxa, 'maxt': maxt,
            'tol': tol, 'iter': maxiter, 'wrt': wrt_file, 'coords': coords,
            'levels': levels, 'pid': pid,
            'center_east': center_east, 'center_north': center_north,
            'radius': radius, 'gama': gama}

if __name__ == "__main__":
    # process parameters
    params = cmd_params()
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
    elif params['stationtype'].lower() == "axis10":
        mu = Axis10()
    else:
        print("unsupported instrument type")
        sys.exit(1)
    # create instrument
    ts = TotalStation(params['stationtype'], mu, iface)
    coords = None
    ts.SetEDMMode('STANDARD')
    orig_dir = ts.GetAngles()   # save original direction
    # orientation
    if params['coords']:    # use coords for blind orientation
        if re.search(r'\.txt$', params['coords']) or re.search(r'\.csv$', params['coords']):
            rd = CsvReader(fname=params['coords'], \
                           filt=['id', 'east', 'north', 'elev'])
        else:
            rd = GeoReader(fname=params['coords'], \
                           filt=['id', 'east', 'north', 'elev'])
        coords = rd.Load()  # load coordinates of reference points
        if 'east' in params and 'north' in params and 'elev' in params and \
                params['east'] is not None and params['north'] is not None and params['elev'] is not None:
            # know station coords
            st_coord = [{'id': 'STATION', 'east': params['east'],
                        'north': params['north'], 'elev': params['elev']}]
            og = ObsGen(st_coord + coords, 'STATION', params['ih'])
            observations = og.run()
            # change to face left
            if ts.GetFace()['face'] == ts.FACE_RIGHT:
                a = ts.GetAngles()
                a['hz'] = (a['hz'] + Angle(180, 'DEG')).Normalize()
                a['v'] = (Angle(360, 'DEG') - a['v']).Normalize() 
                ans = ts.Move(a['hz'], a['v'], 0) # no ATR
                if 'errCode' in ans:
                    logging.fatal("Rotation to face left failed %d", ans['errCode'])
                    sys.exit(-1)
            o = Orientation(observations, ts)   # TODO orientation limit????
            ans = o.Search()
            if 'errCode' in ans:
                logging.fatal("Orientation failed %d", ans['errCode'])
                sys.exit(-1)
            # freestation
            r = Robot(observations, st_coord, ts)
            obs_out, coo_out = r.run()
            fs = Freestation(obs_out, st_coord + coords,
                     '/usr/local/bin/gama-local', 3)    # TODO gama path, stddev
            st_coord = fs.Adjustment()
        else:
            # no station coordinates
            a_s = AnyStation(coords, ts, 'gama-local', params['ih'])
            st_coord = a_s.run()
        ts.SetStation(st_coord[0]['east'], st_coord[0]['north'],
                      st_coord[0]['elev'], params['ih'])
        # set exact orientation on instrument
        ts.Move(Angle(0.0), Angle(math.pi/2), 0)
        ts.SetOri(Angle(st_coord[0]['ori'], 'GON'))
        hoc = st_coord[0]['elev'] + params['ih']
        params['east'] = st_coord[0]['east']
        params['north'] = st_coord[0]['north']
        params['elev'] = st_coord[0]['elev']
    else:
        # set station coordinates
        ts.SetStation(params['east'], params['north'],
                      params['elev'], params['ih'])
        hoc = params['elev'] + params['ih']
    # writer for coordinates and observations
    wrt = CsvWriter(angle='DMS', dist='.3f',
                    filt=['id', 'east', 'north', 'elev', 'hz', 'v', 'distance'],
                    fname=params['wrt'], mode='a', sep=';', pid=params['pid'])
    if isinstance(mu, Trimble5500):
        print("Please change to reflectorless EDM mode (MNU 722 from keyboard)")
        print("and turn on red laser (MNU 741 from keyboard) and press enter!")
        input()
    else:
        ts.SetEDMMode('RLSTANDARD') # reflectorless distance measurement
        try:
            ts.SetRedLaser(1)       # turn on red laser if possible
        except Exception:
            pass
    if params['center_east'] is not None and params['center_north'] is not None and params['radius'] is not None:
        center_dir = math.atan2(params['center_north']-params['north'],
                                params['center_east']-params['east'])
        center_dist = math.hypot(params['center_north']-params['north'],
                                 params['center_east']-params['east'])
        alpha = math.atan(params['radius'] / center_dist)
        params['hz_start'] = Angle(center_dir-alpha)
        params['max'] = Angle(alpha * 2)
        params['hz_top'] = None
        params['tmax'] = None
    else:
    # turn instrument back to original direction
        ts.Move(orig_dir["hz"].GetAngle(), orig_dir["v"].GetAngle(), 0)
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
            h_sec = HorizontalSection(ts, wrt, params['east'], params['north'],
                                      hoc, level, hz,
                                      params['stepinterval'], ma,
                                      params['iter'], params['tol'])
            h_sec.run()
    else:
        if levels is None or len(levels) == 0:
            h_sec = HorizontalSection(ts, wrt, params['east'], params['north'],
                                      hoc, None, params['hz_start'],
                                      params['stepinterval'], params['max'],
                                      params['iter'], params['tol'])
        else:
            h_sec = HorizontalSection(ts, wrt, params['east'], params['north'],
                                      hoc, levels[0], params['hz_start'],
                                      params['stepinterval'], params['max'],
                                      params['iter'], params['tol'])
        h_sec.run()
