#!/usr/bin/env python
"""
.. module:: robotplus.py

.. moduleauthor:: Zoltan Siki

Sample application for complex monitoring for a station

Parameters are stored in config file using JSON format::

    log_file: path to log file, file must exist!
    log_level: 10/20/30/40/50 for DEBUG/INFO/WARNING/ERROR/FATAL
    log_format: format string for log (default: "%(asctime)s %(levelname)s:%(message)s"), optional
    station_type: 1100/1200/1800
    station_id: pont id for the station
    station_height: instrument height above point, optional (default: 0)
    station_coo_limit: limitation for station coordinate change from free station (default 0.01), optional
    fix_list: list of fix points to calculate station coordinates, optional (default: empty)
    mon_list: list of monitoring points to measure, optional (default: empty)
    max_try: maximum trying to measure a point, optional (default: 3)
    delay_try: delay between tries, optional (default: 0)
    port: serial port to use (e.g. COM1 or /dev/ttyS0 or /dev/ttyUSB0)
    coo_rd: URL or local file to get coordinates from
    coo_wr: URL or local file to send coordinates to
    obs_wr: URL or local file to send observations to, oprional (default: no output)
    met_wr: URL or local file to send meteorological observations to, optional (default: no output)
    avg_wr: calculate averages from more faces if value 1, no average calculation if value is zero, optional (default: 1)
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

sys.path.append('../pyapi/')

from angle import Angle
from httpreader import HttpReader
from httpwriter import HttpWriter
from georeader import GeoReader
from geowriter import GeoWriter
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

def avg_coo(coords):
    """ Calculate average coordinates

        :param coords: input coordinate list (duplicates)
        :returns: average coordinates no duplicates
    """
    res = []    # output list
    ids = list(set([coo['id'] for coo in coords]))
    for i in ids:
        e = [coo['east'] for coo in coords if coo['id'] == i]
        n = [coo['north'] for coo in coords if coo['id'] == i]
        h = [coo['elev'] for coo in coords if coo['id'] == i]
        res.append({'id': i, 'east': sum(e) / len(e), 'north': sum(n) / len(n),
                    'elev': sum(h) / len(h)})
    return res

def avg_obs(obs):
    """ Calculate average observations in faces

        :param obs: list of observations
        :returns: average observations
    """
    res = []    # output list
    # copy station record to output
    if 'station' in obs[0]:
        res.append(obs[0])
    ids = list(set([o['id'] for o in obs if 'id' in o]))
    for k in ids:
        # separate face left/right
        hz1 = [o['hz'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi]
        hz2 = [o['hz'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() > math.pi]
        if len(hz1) != len(hz2):
            logging.warning("differenctnumber of observations in two face at point: " + k)
        
        # check angles around 0
        for i in range(len(hz1)):
            if hz1[i] - hz1[0] > math.pi:
                hz1[i] -= math.pi * 2.0
            if hz1[i] - hz1[0] < math.pi:
                hz1[i] += math.pi * 2.0
        for i in range(len(hz2)):
            if hz2[i] - hz2[0] > math.pi:
                hz2[i] -= math.pi * 2.0
            if hz2[i] - hz2[0] < math.pi:
                hz2[i] += math.pi * 2.0
        if len(hz2):
            if hz2[0] < math.pi:
                hz2 = [h + math.pi for h in hz2]
            else:
                hz2 = [h - math.pi for h in hz2]
        hz = sum(hz1 + hz2) / (len(hz1) + len(hz2))

        v1 = [o['v'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() < math.pi]
        v2 = [math.pi * 2.0 - o['v'].GetAngle() for o in obs \
            if 'id' in o and o['id'] == k and o['v'].GetAngle() > math.pi]
        v = sum(v1 + v2) / (len(v1) + len(v2))
        sd12 = [o['distance'] for o in obs \
            if 'id' in o and o['id'] == k]
        sd = sum(sd12) / len(sd12)
        # TODO cross & lengthincline?
        res.append({'id': k, 'hz': Angle(hz), 'v': Angle(v), 'distance': sd,
                    'face': 2})
    return res

if __name__ == "__main__":
    config_pars = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
            'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'station_type': {'required' : True, 'type': 'str', 'set': ['1200', '1800', '1100']},
        'station_id': {'required' : True, 'type': 'str'},
        'station_height': {'required': False, 'default': 0, 'type': 'float'},
        'station_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'orientation_limit': {'required': False, 'default': 0.1, 'type': 'float'},
        'faces': {'required': False, 'default': 1, 'type': 'int'},
        'fix_list': {'required': False, 'type': 'list'},
        'mon_list': {'required': False, 'type': 'list'},
        'max_try': {'required': False, 'type': 'int', 'default': 3},
        'delay_try': {'required': False, 'type': 'float', 'default': 0},
        'port': {'required' : True, 'type': 'str'},
        'coo_rd': {'required' : True},
        'coo_wr': {'required' : True},
        'obs_wr': {'required': False},
        'met_wr': {'required': False},
        'avg_wr': {'required': False, 'type': 'int', 'default': 1},
        'decimals': {'required': False, 'type': 'int', 'default': 4},
        'gama_path': {'required': False, 'type': 'file'},
        'stdev_angle': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist1': {'required': False, 'type': 'float', 'default': 1.5},
        'dimension': {'required': False, 'type': 'int', 'default': 3},
        'probability': {'required': False, 'type': 'float', 'default': 0.95},
        'blunders': {'required': False, 'type': 'int', 'default': 1},
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
                logging.error("Error in config file: " + sys.argv[1])
                sys.exit(-1)
            if not cr.Check():
                sys.exit(-1)
        else:
            print "Config file not found" + sys.argv[1]
            logging.error("Config file not found" + sys.argv[1])
    else:
        print "Usage: robotplus.py config_file"
        #cr = ConfReader('robotplus', 'robotplus.json', None, config_pars)
        #cr.Load()
        #if not cr.Check():
        #    sys.exit(-1)
        sys.exit(-1)
    # logging
    logging.basicConfig(format=cr.json['log_format'], filename=cr.json['log_file'], \
         filemode='a', level=cr.json['log_level'])
    # create totalstation
    mu = get_mu(cr.json['station_type'])
    if not mu:
        logging.error('Invalid instrument type')
        sys.exit(-1)
    if cr.json['station_type'] == 'local':
        iface = LocalIface('test', 'test_iface.txt', 'rand')
    else:
        iface = SerialIface("rs-232", cr.json['port'])
    if iface.GetState():
        logging.error("Serial interface error")
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
        logging.error("Instrument wake up failed")
        sys.exit(-1)
    # get meteorology data
    print "Getting met data..."
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
                if 'huminidity' in data:
                    humi = data['humidity']
                if 'temp' in data and 'huminidity' in data:
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
                logging.error("BMP180 sensor not found")
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
                    filt=['id', 'temp', 'pressure', 'huminidity', 'wettemp',
                          'datetime'])
            else:
                wrtm = CsvWriter(name='met', fname=cr.json['met_wr'],
                    filt=['id', 'temp', 'pressure', 'huminidity',
                    'wettemp', 'datetime'], mode='a')
            data = {'id': cr.json['station_id'], 'temp': temp,
                'pressure': pres, 'huminidity': humi, 'wettemp': wet}
            wrtm.WriteData(data)
            # TODO check result of write
    # get station coordinates
    print "Loading station coords..."
    if re.search('^http[s]?://', cr.json['coo_rd']):
        rd_st = HttpReader(url=cr.json['coo_rd'], ptys=['STA'], \
                           filt=['id', 'east', 'north', 'elev'])
        # TODO read from local file if HttpReader failed
        # other file reader from config coo_rd_loc (optional)
    else:
        rd_st = GeoReader(fname=cr.json['coo_rd'], \
                          filt=['id', 'east', 'north', 'elev'])
    w = rd_st.Load()
    st_coord = [x for x in w if x['id'] == cr.json['station_id']]
    if len(st_coord) == 0:
        logging.error("Station not found: " + cr.json['station_id'])
        sys.exit(-1)
    # coordinate writer & observation writer
    fmt = '.%df' % cr.json['decimals']
    if re.search('^http[s]?://', cr.json['coo_wr']):
        wrt = HttpWriter(url=cr.json['coo_wr'], mode='POST', dist=fmt)
        # observation writer
        if 'obs_wr' in cr.json:
            wrt1 = HttpWriter(url=cr.json['obs_wr'], mode='POST', dist=fmt)
        else:
            wrt1 = wrt
        # TODO write to local file if HttpWriter failed
    else:
        wrt = GeoWriter(fname=cr.json['coo_wr'], mode='a', dist=fmt)
        if 'obs_wr' in cr.json:
            wrt1 = GeoWriter(fname=cr.json['obs_wr'], mode='a', dist=fmt)
    if 'fix_list' in cr.json and cr.json['fix_list'] is not None:
        # get fix coordinates from database
        print "Loading fix coords..."
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_fix = HttpReader(url=cr.json['coo_rd'], ptys=['FIX'], \
                                filt=['id', 'east', 'north', 'elev'])
            # TODO read from local file if HttpReader failed
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
        print "Loading mon coords..."
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_mon = HttpReader(url=cr.json['coo_rd'], ptys=['MON'], \
                                filt=['id', 'east', 'north', 'elev'])
            # TODO read from local file if HttpReader failed
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
    print "Generating observations for targets..."
    og = ObsGen(st_coord + fix_coords + mon_coords, cr.json['station_id'], \
        cr.json['station_height'], cr.json['faces'])
    observations = og.run()
    # change to face left
    if ts.GetFace()['face'] == ts.FACE_RIGHT:
        a = ts.GetAngles()
        a['hz'] = (a['hz'] + Angle(180, 'DEG')).Normalize()
        a['v'] = (Angle(360, 'DEG') - a['v']).Normalize()
        ans = ts.Move(a['hz'], a['v'], 0) # no ATR
        if 'errCode' in ans:
            logging.error("Rotation to face left failed %d" % ans['errCode'])
            sys.exit(-1)
    # check/find orientation
    print "Orientation..."
    o = Orientation(observations, ts, cr.json['orientation_limit'])
    ans = o.Search()
    if 'errCode' in ans and cr.json['station_type'] != 'local':
        logging.error("Orientation failed %d" % ans['errCode'])
        sys.exit(-1)

    if 'fix_list' in cr.json and cr.json['fix_list'] is not None:
        # generate observations for fix points, first point is the station
        print "Generating observations for fix..."
        og = ObsGen(st_coord + fix_coords, cr.json['station_id'], \
            cr.json['station_height'], cr.json['faces'])
        observations = og.run()
        # observation to fix points
        print "Measuring fix..."
        r = Robot(observations, st_coord, ts, cr.json['max_try'], cr.json['delay_try'])
        obs_out, coo_out = r.run()
        # calculate station coordinates as freestation if gama_path set
        if 'gama_path' in cr.json and cr.json['gama_path'] is not None:
            print "Freestation..."
            if cr.json['faces'] > 1:
                obs_avg = avg_obs(obs_out)
            else:
                obs_avg = obs_out
            if cr.json['faces'] > 1 and 'avg_wr' in cr.json and cr.json['avg_wr']:
                obs_out = obs_avg
            # store observations to FIX points into the database
            for o in obs_out:
                if 'distance' in o:
                    wrt1.WriteData(o)
                    # TODO check result of write
            fs = Freestation(obs_avg, st_coord + fix_coords,
                             cr.json['gama_path'], cr.json['dimension'],
                             cr.json['probability'], cr.json['stdev_angle'],
                             cr.json['stdev_dist'], cr.json['stdev_dist1'],
                             cr.json['blunders'])
            w = fs.Adjustment()
            if w is None:
                logging.error("No adjusted coordinates for station %s" % cr.json['station_id'])
                sys.exit(-1)
            if abs(st_coord[0]['east'] - w[0]['east']) > cr.json['station_coo_limit'] or \
               abs(st_coord[0]['north'] - w[0]['north']) > cr.json['station_coo_limit'] or \
               abs(st_coord[0]['elev'] - w[0]['elev']) > cr.json['station_coo_limit']:
                logging.error("Station moved!!!" + str(w))
                sys.exit(-1)
            # update station coordinates
            st_coord = w
            # upload station coords to server
            print "Uploading station coords..."
            wrt.WriteData(st_coord[0])
            # TODO check write result
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
                logging.error("Backsite trouble")
                sys.exit(1)
            ori_p = [p for p in fix_coords if p['id'] == back_site][0]
            bearing = Angle(math.atan2(ori_p['east'] - st_coord[0]['east'], \
                                 ori_p['north'] - st_coord[0]['north']))
            # rotate to farest FIX and set orientation
            ts.Move(obs_out[back_indx]['hz'], obs_out[back_indx]['v'], 1)
            ans = ts.SetOri(bearing)
            if 'errCode' in ans:
                logging.error("Cannot upload orientation to instrument")
                sys.exit(-1)
    if 'mon_list' in cr.json and cr.json['mon_list'] is not None:
        # generate observations for monitoring points, first point is the station
        print "Generating observations for mon..."
        og = ObsGen(st_coord + mon_coords, cr.json['station_id'], \
            cr.json['station_height'], cr.json['faces'])
        observations = og.run()
        # observation to monitoring points
        print "Measuring mon..."
        r = Robot(observations, st_coord, ts)
        obs_out, coo_out = r.run()
        # calculate average for observations
        if cr.json['faces'] > 1 and 'avg_wr' in cr.json and cr.json['avg_wr']:
            obs_out = avg_obs(obs_out)
        for o in obs_out:
            if 'distance' in o:
                wrt1.WriteData(o)
                # TODO check result of write
                #print o['id'] + ' ' + o['hz'].GetAngle('DMS') + ' ' + \
                #    o['v'].GetAngle('DMS') + ' ' + str(o['distance'])
        # always calculate coordinate average
        coo_out = avg_coo(coo_out)
        for c in coo_out:
            wrt.WriteData(c)
            # TODO check result of write
            #print c['id'] + ' ' + str(c['east']) + ' ' + str(c['north']) + ' ' + str(c['elev'])
    # move telescope to safe position
    ans = ts.Move(Angle(0), Angle(180, "DEG")) # no ATR
