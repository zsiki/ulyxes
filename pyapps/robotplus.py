#!/usr/bin/env python
"""
.. module:: robotplus.py

.. moduleauthor:: Zoltan Siki

Sample application for complex monitoring for a station
Different prism constants can be set with code 20/pc in input

Parameters are stored in config file using JSON format::

    log_file: path to log file, file must exist!
    log_level: 10/20/30/40/50 for DEBUG/INFO/WARNING/ERROR/FATAL
    log_format: format string for log (default: "%(asctime)s %(levelname)s:%(message)s"), optional
    station_type: 1100/1200/1800
    station_id: pont id for the station
    station_height: instrument height above point, optional (default: 0)
    station_coo_limit: limitation for station coordinate change from free station (default 0.01), optional
    orientation_limit: distance limit for orientation to identify a target (default 0.1)
    faces: number of faces to measure (first face left for all pointt then face right) (default 1)
    face_coo_limit: maximum difference for face left and face right coords (m) (default: 0.01)
    face_dir_limit: maximum difference for face left and face right angle (rad) (default 0.0029 60")
    face_dist_limit: maximum difference for face left and face right dist (m) (default 0.01)
    directfaces: number of faces to measure (face left and right are measured directly) (default 1)
    fix_list: list of fix points to calculate station coordinates, optional (default: empty)
    mon_list: list of monitoring points to measure, optional (default: empty)
    max_try: maximum trying to measure a point, optional (default: 3)
    delay_try: delay between tries, optional (default: 0)
    dir_limit: angle limit for false direction in radians (default 0.015. 5')
    port: serial port to use (e.g. COM1 or /dev/ttyS0 or /dev/ttyUSB0)
    coo_rd: source to get coordinates from
    coo_wr: target to send coordinates to
    obs_wr: target to send observations to
    met_wr: target to send meteorological observations to, optional (default: no output)
    inf_wr: target to send general information to
    avg_wr: calculate averages from more faces if value 1, no average calculation if value is zero, optional (default: 1) DEPRICATED average always calculated
    decimals: number of decimals in output, optional (default: 4)
    gama_path: path to GNU Gama executable, optional (default: empty, no adjustment)
    stdev_angle: standard deviation of angle measurement (arc seconds), optional (default: 1)
    stdev_dist: additive tag for standard deviation of distance measurement (mm), optional (default: 1)
    stdev_dist1: multiplicative tag for standard deviation of distance measurement (mm), optional (default: 1.5)
    dimension: dimension of stored points (1D/2D/3D), optional (default: 3)
    probability: probability for data snooping, optional (default: 0.95)
    blunders: data snooping on/off 1/0, optional (default: 1)
    met: met sensor name WEBMET/BMP180/SENSEHAT, optional default None
    met_addr: URL to webmet data, optional (default: empty)
    met_par: parameters to web met service, optional (default: empty)
"""

import sys
import re
import logging
import math
import os
import time
import datetime

sys.path.append('../pyapi/')

from angle import Angle
from httpreader import HttpReader
from httpwriter import HttpWriter
from georeader import GeoReader
from geowriter import GeoWriter
from csvwriter import CsvWriter
from sqlitewriter import SqLiteWriter
from confreader import ConfReader
from filegen import ObsGen
from serialiface import SerialIface
from totalstation import TotalStation
from blindorientation import Orientation
from robot import Robot
from freestation import Freestation
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from leicatca1800 import LeicaTCA1800
from localiface import LocalIface

def get_mu(t):
    """ Select measure unit

        :param t: instrument type 1200/1800/1100/local
        :returns: measure unit or False
    """
    if re.search('120[0-9]$', t):
        return LeicaTPS1200()
    elif re.search('110[0-9]$', t):
        return LeicaTCRA1100()
    elif re.search('180[0-9]$', t):
        return LeicaTCA1800()
    elif re.search('^local', t):
        return LeicaTPS1200()
    return False

def avg_coo(coords, face_coo_limit=0.01):
    """ Calculate average coordinates

        :param coords: input coordinate list (duplicates)
        :params face_coo_limit: difference limit from average coords (m)
        :returns: average coordinates no duplicates
    """
    res = []    # output list
    ids = list(set([coo['id'] for coo in coords]))
    for i in ids:
        e = [coo['east'] for coo in coords if coo['id'] == i]
        n = [coo['north'] for coo in coords if coo['id'] == i]
        h = [coo['elev'] for coo in coords if coo['id'] == i]
        avg_e = sum(e) / len(e)
        avg_n = sum(n) / len(n)
        avg_h = sum(h) / len(h)
        # check before store average
        if [x for x in e if abs(x - avg_e) > face_coo_limit] or \
           [y for y in n if abs(y - avg_n) > face_coo_limit] or \
           [z for z in h if abs(z - avg_h) > face_coo_limit]:
            logging.error("Large coordinate difference from faces: %.3f %.3f %.3f", e, n, h)
            continue    # skip point
        res.append({'id': i, 'east': avg_e, 'north': avg_n, 'elev': avg_h})
    return res

def avg_obs(obs, face_dir_limit=0.0029, face_dist_limit=0.01):
    """ Calculate average observations in faces

        :param obs: list of observations
        :params face_dir_limit: difference limit from average angles (rad)
        :params face_dist_limit: difference limit from average distance (m)
        :returns: average observations
    """
    res = []    # output list
    # copy station record to output
    if 'station' in obs[0]:
        res.append(obs[0])
    # get unique point ids
    ids = list(set([o['id'] for o in obs if 'id' in o]))
    for k in ids:
        # separate face left/right
        hz1 = [o['hz'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi]
        hz2 = [o['hz'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() > math.pi]
        if len(hz1) != len(hz2):
            logging.warning('Different number of observations in two faces %s FL: %d FR: %d', k, len(hz1), len(hz2))
        # check angles around 0/360 degree
        for i in range(1, len(hz1)):
            if hz1[i] - hz1[0] > math.pi:
                hz1[i] -= math.pi * 2.0
            elif hz1[0] - hz1[i] > math.pi:
                hz1[i] += math.pi * 2.0
        for i in range(1, len(hz2)):
            if hz2[i] - hz2[0] > math.pi:
                hz2[i] -= math.pi * 2.0
            elif hz2[0] - hz2[i] > math.pi:
                hz2[i] += math.pi * 2.0
        # rotate face right by 180 degree
        if hz2 and hz1:
            if hz1[0] > hz2[0]:
                hz2 = [h + math.pi for h in hz2]
            else:
                hz2 = [h - math.pi for h in hz2]
            kol = (sum(hz2) / len(hz2) - sum(hz1) / len(hz1)) / 2.0
            logging.info('Collimation error [GON]: %.4f %s',
                         Angle(kol).GetAngle('GON'), k)
        elif hz2:
            if hz2[0] > math.pi:
                hz2 = [h - math.pi for h in hz2]
            else:
                hz2 = [h + math.pi for h in hz2]
        hz = sum(hz1 + hz2) / (len(hz1) + len(hz2))
        # check before store average
        str_hz = [Angle(abs(x - hz)).GetAngle('GON')
                  for x in hz1 + hz2 if abs(x - hz) > face_dir_limit]
        if str_hz:
            logging.error('Large Hz difference from faces [GON]: %.4f %s',
                          max(str_hz), k)
            continue    # skip point
        v1 = [o['v'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi]
        v2 = [math.pi * 2.0 - o['v'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() > math.pi]
        if v1 and v2:
            ind = (sum(v2) / len(v2) - sum(v1) / len(v1)) / 2.0
            logging.info('Index error [GON]: %.4f %s',
                         Angle(ind).GetAngle('GON'), k)
        v = sum(v1 + v2) / (len(v1) + len(v2))
        # check before store average
        str_v = [Angle(abs(x-v)).GetAngle('GON')
                 for x in v1 + v2  if abs(x - v) > face_dir_limit]
        if str_v:
            logging.error('Large V difference from faces: %.4f at point %s',
                          max(str_v), k)
            continue    # skip point
        res_obs = {'id': k, 'hz': Angle(hz), 'v': Angle(v)}
        sd12 = [o['distance'] for o in obs \
            if 'id' in o and o['id'] == k and 'distance' in o]
        if sd12:
            sd = sum(sd12) / len(sd12)
            # check before store average
            str_d = [abs(x - sd) for x in sd12 if abs(x - sd) > face_dist_limit]
            if str_d:
                logging.error('Large dist difference from faces: %.4f at point %s', max(str_d), k)
                continue    # skip point
            res_obs['distance'] = sd
        # cross & lengthincline from face left
        cross = [o['crossincline'] for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi and \
            'crossincline' in o]
        if cross:
            res_obs['crossincline'] = cross[0]
        length = [o['lengthincline'] for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi and \
            'lengthincline' in o]
        if length:
            res_obs['lengthincline'] = length[0]
        res.append(res_obs)
    return res

if __name__ == "__main__":
    config_pars = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
                      'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.FATAL]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'station_type': {'required' : True, 'type': 'str', 'set': ['1200', '1800', '1100']},
        'station_id': {'required' : True, 'type': 'str'},
        'station_height': {'required': False, 'default': 0, 'type': 'float'},
        'station_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'orientation_limit': {'required': False, 'default': 0.1, 'type': 'float'},
        'faces': {'required': False, 'default': 1, 'type': 'int'},
        'face_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'face_dir_limit': {'required': False, 'default': 0.0029, 'type': 'float'},
        'face_dist_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'directfaces': {'required': False, 'default': 1, 'type': 'int'},
        'fix_list': {'required': False, 'type': 'list'},
        'mon_list': {'required': False, 'type': 'list'},
        'max_try': {'required': False, 'type': 'int', 'default': 3},
        'delay_try': {'required': False, 'type': 'float', 'default': 0},
        'dir_limit': {'required': False, 'type': 'float', 'default': 0.015},
        'port': {'required' : True, 'type': 'str'},
        'coo_rd': {'required' : True},
        'coo_wr': {'required' : True},
        'obs_wr': {'required': True},
        'met_wr': {'required': False},
        'inf_wr': {'required': False},
        'decimals': {'required': False, 'type': 'int', 'default': 4},
        'gama_path': {'required': False, 'type': 'file'},
        'stdev_angle': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist1': {'required': False, 'type': 'float', 'default': 1.5},
        'dimension': {'required': False, 'type': 'int', 'default': 3},
        'probability': {'required': False, 'type': 'float', 'default': 0.95},
        'blunders': {'required': False, 'type': 'int', 'default': 1},
        'ts_off': {'required': False, 'type': 'int', 'default': 0},
        'met': {'required': False, 'set': ['WEBMET', 'BMP180', 'SENSEHAT']},
        'met_addr': {'required': False},
        'met_par': {'required': False},
        '__comment__': {'required': False, 'type': 'str'}
    }
    # check command line param
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            try:
                cr = ConfReader('robotplus', sys.argv[1], None, config_pars)
                cr.Load()
            except:
                print("Error in config file: {0}".format(sys.argv[1]))
                sys.exit(-1)
            if not cr.Check():
                print("Config check failed")
                sys.exit(-1)
        else:
            print("Config file not found %s" % sys.argv[1])
            logging.fatal("Config file not found %s", sys.argv[1])
            sys.exit(-1)
    else:
        print("Missing parameter")
        print("Usage: robotplus.py config_file")
        sys.exit(-1)
    # logging
    logging.basicConfig(format=cr.json['log_format'], filename=cr.json['log_file'], \
         filemode='a', level=cr.json['log_level'])
    # create totalstation
    mu = get_mu(cr.json['station_type'])
    if not mu:
        logging.fatal('Invalid instrument type')
        sys.exit(-1)
    if cr.json['station_type'] == 'local':
        iface = LocalIface('test', 'test_iface.txt', 'rand')
    else:
        iface = SerialIface("rs-232", cr.json['port'])
    if iface.GetState():
        logging.fatal("Serial interface error")
        sys.exit(-1)
    ts = TotalStation(cr.json['station_type'], mu, iface)
    for i in range(10):
        w = ts.GetATR() # wake up instrument
        if 'errorCode' in w or ts.measureIface.GetState():
            ts.measureIface.ClearState()
            time.sleep(10)
        else:
            break
    if 'errorCode' in w or ts.measureIface.GetState():
        logging.fatal("Instrument wake up failed")
        sys.exit(-1)
    # get meteorology data
    print("Getting met data...")
    if 'met' in cr.json and cr.json['met'] is not None:
        atm = ts.GetAtmCorr()     # get current settings from ts
        if cr.json['met'].upper() == 'WEBMET':
            from webmetmeasureunit import WebMetMeasureUnit
            from webmet import WebMet
            from webiface import WebIface
            wi = WebIface("demo", cr.json['met_addr'], "json")
            web_mu = WebMetMeasureUnit(msg=cr.json['met_par'])
            web_met = WebMet('WebMet', web_mu, wi)
            data = web_met.GetPressure()
            pres = temp = humi = wet = None
            if data is not None:
                if 'pressure' in data:
                    pres = data['pressure']
                if 'temp' in data:
                    temp = data['temp']
                if 'humidity' in data:
                    humi = data['humidity']
                if 'temp' in data and 'humidity' in data:
                    wet = web_met.GetWetTemp(temp, humi)
        elif cr.json['met'].upper() == 'BMP180':
            from bmp180measureunit import BMP180MeasureUnit
            from i2ciface import I2CIface
            from bmp180 import BMP180
            bmp_mu = BMP180MeasureUnit()
            i2c = I2CIface(None, 0x77)
            try:
                bmp = BMP180('BMP180', bmp_mu, i2c)
            except IOError:
                logging.fatal("BMP180 sensor not found")
                sys.exit(1)
            pres = float(bmp.GetPressure()['pressure'])
            temp = float(bmp.GetTemp()['temp'])
            wet = None    # wet temperature unknown
        elif cr.json['met'].upper() == 'SENSEHAT':
            from sense_hat import SenseHat
            from webmet import WebMet
            sense = SenseHat()
            pres = sense.get_pressure()
            temp = sense.get_temperature()
            humi = sense.get_humidity()
            wet = WebMet.GetWetTemp(temp, humi)
        if pres is not None and temp is not None:
            ts.SetAtmCorr(float(atm['lambda']), pres, temp, wet)
        else:
            logging.warning("meteorological data not available")
        if 'met_wr' in cr.json:
            if re.search('^http[s]?://', cr.json['met_wr']):
                wrtm = HttpWriter(
                    name='met', url=cr.json['met_wr'], mode='POST',
                    filt=['id', 'temp', 'pressure', 'humidity', 'wettemp',
                          'datetime'])
            elif re.search('^sqlite:', cr.json['met_wr']):
                wrtm = SqLiteWriter(db=cr.json['met_wr'][7:],
                                    table='monitoring_met',
                                    filt=['id', 'pressure', 'temp', 'humidity',
                                          'wettemp', 'datetime'])
            else:
                wrtm = CsvWriter(name='met', fname=cr.json['met_wr'],
                                 filt=['id', 'temp', 'pressure', 'humidity',
                                       'wettemp', 'datetime'], mode='a')
            data = {'id': cr.json['station_id'], 'temp': temp,
                    'pressure': pres, 'humidity': humi, 'wettemp': wet}
            if wrtm.WriteData(data) == -1:
                logging.error('Met data write failed')
    # get station coordinates
    print("Loading station coords...")
    if re.search('^http[s]?://', cr.json['coo_rd']):
        rd_st = HttpReader(url=cr.json['coo_rd'], ptys=['STA'], \
                           filt=['id', 'east', 'north', 'elev'])
    else:
        rd_st = GeoReader(fname=cr.json['coo_rd'], \
                          filt=['id', 'east', 'north', 'elev'])
    w = rd_st.Load()
    st_coord = [x for x in w if x['id'] == cr.json['station_id']]
    if not st_coord:
        logging.fatal("Station not found: %s", cr.json['station_id'])
        sys.exit(-1)
    # coordinate writer
    fmt = '.%df' % cr.json['decimals']
    if re.search('^http[s]?://', cr.json['coo_wr']):
        wrt = HttpWriter(url=cr.json['coo_wr'], mode='POST', dist=fmt)
    elif re.search('^sqlite:', cr.json['coo_wr']):
        wrt = SqLiteWriter(db=cr.json['coo_wr'][7:], dist=fmt,
                           table='monitoring_coo',
                           filt=['id', 'east', 'north', 'elev', 'datetime'])
    else:
        wrt = GeoWriter(fname=cr.json['coo_wr'], mode='a', dist=fmt)
    # observation writer
    if re.search('^http[s]?://', cr.json['obs_wr']):
        wrt1 = HttpWriter(url=cr.json['obs_wr'], mode='POST', dist=fmt)
    elif re.search('^sqlite:', cr.json['obs_wr']):
        wrt1 = SqLiteWriter(db=cr.json['obs_wr'][7:], dist=fmt,
                            table='monitoring_obs',
                            filt=['id', 'hz', 'v', 'distance',
                                  'crossincline', 'lengthincline', 'datetime'])
    else:
        wrt1 = GeoWriter(fname=cr.json['obs_wr'], mode='a', dist=fmt)
    # information writer
    if 'inf_wr' in cr.json:
        if re.search('^http[s]?://', cr.json['inf_wr']):
            wrt2 = HttpWriter(url=cr.json['inf_wr'], mode='POST', dist=fmt)
        elif re.search('^sqlite:', cr.json['inf_wr']):
            wrt2 = SqLiteWriter(db=cr.json['inf_wr'][7:], dist=fmt,
                                table='monitoring_inf',
                                filt=['datetime', 'nref', 'nrefobs', 'nmon',
                                      'nmonobs', 'maxincl', 'std_east',
                                      'std_north', 'std_elev', 'std_ori'])
        else:
            wrt2 = GeoWriter(fname=cr.json['inf_wr'], mode='a', dist=fmt)
    if 'fix_list' in cr.json and cr.json['fix_list'] is not None:
        # get fix coordinates from database
        print("Loading fix coords...")
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_fix = HttpReader(url=cr.json['coo_rd'], ptys=['FIX'], \
                                filt=['id', 'east', 'north', 'elev'])
        else:
            rd_fix = GeoReader(fname=cr.json['coo_rd'], \
                               filt=['id', 'east', 'north', 'elev'])
        # remove other points
        fix_coords = [p for p in rd_fix.Load() if p['id'] in cr.json['fix_list']]
        if len(cr.json['fix_list']) != len(fix_coords):
            logging.error("Not all fix points found in database")
    else:
        fix_coords = []

    if 'mon_list' in cr.json and cr.json['mon_list'] is not None:
        # get monitoring coordinates from database
        print("Loading mon coords...")
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_mon = HttpReader(url=cr.json['coo_rd'], ptys=['MON'], \
                                filt=['id', 'east', 'north', 'elev'])
        else:
            rd_mon = GeoReader(fname=cr.json['coo_rd'], \
                               filt=['id', 'east', 'north', 'elev'])
        mon_coords = [p for p in rd_mon.Load() if p['id'] in cr.json['mon_list']]
        if len(cr.json['mon_list']) != len(mon_coords):
            logging.error("Not all mon points found in database")
    else:
        mon_coords = []
    # check orientation including FIX and MON points
    # generate observations for all target points, first point is the station
    print("Generating observations for targets...")
    og = ObsGen(st_coord + fix_coords + mon_coords, cr.json['station_id'], \
        cr.json['station_height'], cr.json['faces'], cr.json['directfaces'])
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
    # check/find orientation
    print("Orientation...")
    o = Orientation(observations, ts, cr.json['orientation_limit'])
    ans = o.Search()
    if 'errCode' in ans and cr.json['station_type'] != 'local':
        logging.fatal("Orientation failed %d", ans['errCode'])
        sys.exit(-1)

    if 'fix_list' in cr.json and cr.json['fix_list'] is not None and \
        len(fix_coords) < 2:
        logging.warning('No enough fix points for freestation')
    elif 'fix_list' in cr.json and cr.json['fix_list'] is not None and \
        len(fix_coords) > 1:
        # generate observations for fix points, first point is the station
        print("Generating observations for fix...")
        og = ObsGen(st_coord + fix_coords, cr.json['station_id'], \
            cr.json['station_height'], cr.json['faces'], cr.json['directfaces'])
        observations = og.run()
        # observation to fix points
        print("Measuring fix...")
        act_date = datetime.datetime.now()  # start of observations
        r = Robot(observations, st_coord, ts, cr.json['max_try'],
                  cr.json['delay_try'], cr.json['dir_limit'])
        obs_out, coo_out = r.run()
        # calculate station coordinates as freestation if gama_path set
        if 'gama_path' in cr.json and cr.json['gama_path'] is not None:
            print("Freestation...")
            if cr.json['faces'] > 1 or cr.json['directfaces'] > 1:
                obs_out = avg_obs(obs_out, cr.json['face_dir_limit'],
                                  cr.json['face_dist_limit'])
            # store observations to FIX points
            for o in obs_out:
                o['datetime'] = act_date
                if 'distance' in o:
                    if wrt1.WriteData(o) == -1:
                        logging.error('Observation data write failed %s',
                                      o['id'])
                    logging.info('inclination [GON]: %.4f %.4f %s',
                                 o['crossincline'].GetAngle('GON'),
                                 o['lengthincline'].GetAngle('GON'), o['id'])
            fs = Freestation(obs_out, st_coord + fix_coords,
                             cr.json['gama_path'], cr.json['dimension'],
                             cr.json['probability'], cr.json['stdev_angle'],
                             cr.json['stdev_dist'], cr.json['stdev_dist1'],
                             cr.json['blunders'])
            w = fs.Adjustment()
            if w is None or 'east' not in w or 'north' not in w:
                logging.fatal("No adjusted coordinates for station %s",
                              cr.json['station_id'])
                sys.exit(-1)
            if abs(st_coord[0]['east'] - w[0]['east']) > cr.json['station_coo_limit'] or \
               abs(st_coord[0]['north'] - w[0]['north']) > cr.json['station_coo_limit'] or \
               abs(st_coord[0]['elev'] - w[0]['elev']) > cr.json['station_coo_limit']:
                logging.fatal("Station moved!!! %s", w[0]['id'])
                sys.exit(-1)
            # update station coordinates
            st_coord = w
            # upload station coords to server
            print("Uploading station coords...")
            st_coord[0]['datetime'] = act_date
            logging.info("station stddevs[mm/cc]: %.1f %.1f %.1f %.1f",
                         st_coord[0]['std_east'], st_coord[0]['std_north'],
                         st_coord[0]['std_elev'], st_coord[0]['std_ori'])
            if wrt.WriteData(st_coord[0]) == -1:
                logging.error('Station coords write failed')
            if 'inf_wr' in cr.json:
                maxincl = max([max(abs(o['crossincline'].GetAngle('GON')),
                                   abs(o['lengthincline'].GetAngle('GON')))
                               for o in obs_out if 'crossincline' in o])
                inf = {'datetime': act_date, 'nref': len(fix_coords),
                       'nrefobs': len(obs_out)-1, 'maxincl': maxincl,
                       'std_east': st_coord[0]['std_east'],
                       'std_north': st_coord[0]['std_north'],
                       'std_elev': st_coord[0]['std_elev'],
                       'std_ori': st_coord[0]['std_ori']}
                if wrt2.WriteData(inf) == -1:
                    logging.error('Station inf write failed')
            if 'ori' in st_coord[0]:
                # rotate to Hz 0
                ts.Move(Angle(0.0), Angle(90, 'DEG'), 0)
                # set direction to orientation angle
                ans = ts.SetOri(Angle(st_coord[0]['ori'], 'GON'))
                #print(Angle(st_coord[0]['ori'], 'GON').GetAngle('DMS'))
                if 'errCode' in ans:
                    logging.fatal("Cannot upload orientation to instrument")
                    sys.exit(-1)
            else:
                # update orientation using farest FIX
                max_dist = 0
                back_site = None
                i = 0
                for o in obs_out:
                    if 'distance' in o and o['distance'] > max_dist:
                        max_dist = o['distance']
                        back_site = o['id']
                        back_indx = i
                    i += 1
                if back_site is None:
                    logging.fatal("Backsite trouble")
                    sys.exit(1)
                ori_p = [p for p in fix_coords if p['id'] == back_site][0]
                bearing = Angle(math.atan2(ori_p['east'] - st_coord[0]['east'], \
                                     ori_p['north'] - st_coord[0]['north']))
                # rotate to farest FIX and set orientation
                ts.Move(obs_out[back_indx]['hz'], obs_out[back_indx]['v'], 1)
                ans = ts.SetOri(bearing)
                if 'errCode' in ans:
                    logging.fatal("Cannot upload orientation to instrument")
                    sys.exit(-1)
    if 'mon_list' in cr.json and cr.json['mon_list'] is not None:
        # generate observations for monitoring points, first point is the station
        print("Generating observations for mon...")
        og = ObsGen(st_coord + mon_coords, cr.json['station_id'], \
            cr.json['station_height'], cr.json['faces'], cr.json['directfaces'])
        observations = og.run()
        # observation to monitoring points
        print("Measuring mon...")
        act_date = datetime.datetime.now()  # start of observations
        r = Robot(observations, st_coord, ts, cr.json['max_try'],
                  cr.json['delay_try'], cr.json['dir_limit'])
        obs_out, coo_out = r.run()
        # calculate average for observations
        if cr.json['faces'] > 1 or cr.json['directfaces'] > 1:
            obs_out = avg_obs(obs_out, cd.json['face_dir_limit'],
                              cd.json['face_dist_limit'])
        for o in obs_out:
            o['datetime'] = act_date
            if 'distance' in o:
                if wrt1.WriteData(o) == -1:
                    logging.error('Observation data write failed')
        # calculate coordinate average
        coo_out = avg_coo(coo_out, cr.json['face_coo_limit'])
        for c in coo_out:
            # add datetime to coords (same as obs)
            c['datetime'] = act_date
            if wrt.WriteData(c) == -1:
                logging.error('Coord data write failed')
        if 'inf_wr' in cr.json:
            maxi = [max(abs(o['crossincline'].GetAngle('GON')),
                        abs(o['lengthincline'].GetAngle('GON')))
                    for o in obs_out if 'crossincline' in o]
            if maxi:
                maxincl = max(maxi)
            else:
                maxincl = -99
            inf = {'datetime': act_date, 'nmon': len(mon_coords),
                   'nmonobs': len(obs_out)-1, 'maxincl': maxincl}
            if wrt2.WriteData(inf) == -1:
                logging.error('Station inf write failed')
    # move telescope to safe position
    ans = ts.Move(Angle(0), Angle(180, "DEG")) # no ATR
    #if cr.json['ts_off']:
    #    ts.SwitchOff(1)
