#!/usr/bin/env python
"""
.. module:: coords.py

.. moduleauthor:: Zoltan Siki

Coordinate calculation from monitoring observation file

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
    coo_rd: URL or local file to get coordinates from
    coo_wr: URL or local file to send coordinates to
    obs_wr: URL or local file to send observations to, oprional (default: no output)
    obs_wr_sql: SQL select command to execute
    strict: 1/0 free station calculated if only all fix points observed in reound
    mon_only: 1/0 calculate polars if only monitoring point in observations/do not calculate polar
    st_only: 1/0 calculate monitoring point only in the same round with freestation
    avg_wr: calculate averages from more faces if value 1, no average calculation if value is zero, optional (default: 1) OBSOLATE
    decimals: number of decimals in output, optional (default: 4)
    gama_path: path to GNU Gama executable, optional (default: empty, no adjustment)
    stdev_angle: standard deviation of angle measurement (arc seconds), optional (default: 1)
    stdev_dist: additive tag for standard deviation of distance measurement (mm), optional (default: 1)
    stdev_dist1: multiplicative tag for standard deviation of distance measurement (mm), optional (default: 1.5)
    dimension: dimension of stored points (1D/2D/3D), optional (default: 3)
    probability: probability for data snooping, optional (default: 0.95)
    blunders: data snooping on/off 1/0, optional (default: 1)
"""

import sys
import re
import logging
import math
import os
import datetime

sys.path.append('../pyapi/')

from angle import Angle
from httpreader import HttpReader
from httpwriter import HttpWriter
from georeader import GeoReader
from geowriter import GeoWriter
from sqlitereader import SqLiteReader
from sqlitewriter import SqLiteWriter
from confreader import ConfReader
from freestation import Freestation

if __name__ == "__main__":
    config_pars = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
            'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'station_id': {'required' : True, 'type': 'str'},
        'station_height': {'required': False, 'default': 0, 'type': 'float'},
        'station_coo_limit': {'required': False, 'default': 0.01, 'type': 'float'},
        'orientation_limit': {'required': False, 'default': 0.1, 'type': 'float'},
        'fix_list': {'required': False, 'type': 'list'},
        'mon_list': {'required': False, 'type': 'list'},
        'coo_rd': {'required' : True},
        'coo_wr': {'required' : True},
        'obs_rd': {'required': False},
        'obs_rd_sql': {'required': False},
        'strict':{'required': False, 'type': 'int', 'default': 1},
        'mon_only':{'required': False, 'type': 'int', 'default': 1},
        'st_only':{'required': False, 'type': 'int', 'default': 0},
        'obs_wr': {'required': False},
        'decimals': {'required': False, 'type': 'int', 'default': 4},
        'gama_path': {'required': False, 'type': 'file'},
        'stdev_angle': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist': {'required': False, 'type': 'float', 'default': 1},
        'stdev_dist1': {'required': False, 'type': 'float', 'default': 1.5},
        'dimension': {'required': False, 'type': 'int', 'default': 3},
        'probability': {'required': False, 'type': 'float', 'default': 0.95},
        'blunders': {'required': False, 'type': 'int', 'default': 1},
        '__comment__': {'required': False, 'type': 'str'}
    }
    # check command line param
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            try:
                cr = ConfReader('coords', sys.argv[1], None, config_pars)
                cr.Load()
            except:
                logging.fatal("Error in config file: " + sys.argv[1])
                sys.exit(-1)
            if not cr.Check():
                logging.fatal("Config check failed")
                sys.exit(-1)
        else:
            print "Config file not found " + sys.argv[1]
            logging.fatal("Config file not found " + sys.argv[1])
            sys.exit(-1)
    else:
        print "Usage: coords.py config_file"
        cr = ConfReader('coords', '/home/siki/tanszek/szelkapu/szk1/szk1_all.json', None, config_pars)
        cr.Load()
        if not cr.Check():
            logging.fatal("Config check failed")
        logging.fatal("Invalid parameters")
        #sys.exit(-1)
    # logging
    logging.basicConfig(format=cr.json['log_format'], filename=cr.json['log_file'], \
         filemode='a', level=cr.json['log_level'])
    # get station coordinates
    #print "Loading station coords..."
    if re.search('^http[s]?://', cr.json['coo_rd']):
        rd_st = HttpReader(url=cr.json['coo_rd'], ptys=['STA'], \
                           filt=['id', 'east', 'north', 'elev'])
    elif re.search('^sqlite:', cr.json['coo_rd']):
        rd_st = SqLiteReader(db=cr.json['coo_rd'][7:], \
                             filt=['id', 'east', 'north', 'elev'])
    else:
        rd_st = GeoReader(fname=cr.json['coo_rd'], \
                          filt=['id', 'east', 'north', 'elev'])
    w = rd_st.Load()
    st_coord = [x for x in w if x['id'] == cr.json['station_id']]
    if len(st_coord) == 0:
        logging.fatal("Station not found: " + cr.json['station_id'])
        sys.exit(-1)
    # coordinate writer
    fmt = '.%df' % cr.json['decimals']
    if re.search('^http[s]?://', cr.json['coo_wr']):
        wrt = HttpWriter(url=cr.json['coo_wr'], mode='POST', dist=fmt)
    elif re.search('^sqlite:', cr.json['coo_wr']):
        wrt = SqLiteWriter(db=cr.json['coo_wr'][7:], dist=fmt,
                           table='monitring_coo',
                           filt=['id', 'east', 'north', 'elev', 'datetime', 'n', 'ori', 'std_east', 'std_north', 'std_elev', 'std_ori'])
    else:
        wrt = GeoWriter(fname=cr.json['coo_wr'], mode='a', dist=fmt)
    if 'fix_list' in cr.json and cr.json['fix_list'] is not None:
        # get fix coordinates from database
        #print "Loading fix coords..."
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_fix = HttpReader(url=cr.json['coo_rd'], ptys=['FIX'], \
                                filt=['id', 'east', 'north', 'elev'])
        elif re.search('^sqlite:', cr.json['coo_rd']):
            rd_fix = SqLiteReader(db=cr.json['coo_wr'][7:])
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
        #print "Loading mon coords..."
        if re.search('^http[s]?://', cr.json['coo_rd']):
            rd_mon = HttpReader(url=cr.json['coo_rd'], ptys=['MON'], \
                                filt=['id', 'east', 'north', 'elev'])
        else:
            rd_mon = GeoReader(fname=cr.json['coo_rd'], \
                               filt=['id', 'east', 'north', 'elev'])
        mon_coords = [p for p in rd_mon.Load() if p['id'] in cr.json['mon_list']]
        if len(cr.json['mon_list']) != len(mon_coords):
            logging.error("Not all mon points found in database")
            #print mon_coords
    else:
        mon_coords = []
    if re.search('^http[s]?://', cr.json['coo_wr']):
        wrt = HttpWriter(url=cr.json['coo_wr'], mode='POST', dist=fmt)
    # observation writer
    if 'obs_wr' in cr.json:
        if re.search('^http[s]?://', cr.json['obs_wr']):
            wrt1 = HttpWriter(url=cr.json['obs_wr'], mode='POST', dist=fmt)
        elif re.search('^sqlite:', cr.json['obs_wr']):
            wrt1 = SqLiteWriter(db=cr.json['obs_wr'][7:], dist=fmt,
                                table='monitoring_obs',
                                filt=['id', 'hz', 'v', 'distance',
                                'crossincline', 'lengthincline', 'datetime'])
        else:
            wrt1 = GeoWriter(fname=cr.json['obs_wr'], mode='a', dist=fmt)
    # load observations recorded by robotplus
    if re.search('^sqlite:', cr.json['obs_rd']):
        rd_obs = SqLiteReader(db=cr.json['obs_rd'][7:], \
            sql=cr.json['obs_rd_sql'])
    else:
        obs_rd = GeoReader(fname=cr.json['obs_rd'])
    obs = rd_obs.Load()
    n = len(obs)
    # change data types
    for o in obs:
        o['hz'] = Angle(o['hz'], 'GON')
        o['v'] = Angle(o['v'], 'GON')
        o['datetime'] = datetime.datetime.strptime(o['datetime'], '%Y-%m-%d %H:%M:%S')
    i = 0
    delta = datetime.timedelta(seconds=20)
    while i < n:
        # collect observations with  timestamp
        d = obs[i]['datetime']
        j = i
        while j < n and obs[j]['datetime'] - d <= delta:
            # correct time
            obs[j]['datetime'] = d
            j += 1
        #obs_avg = avg_obs(obs[i:j])
        obs_avg = obs[i:j]
        fix_obs = []
        if 'fix_list' in cr.json and cr.json['fix_list'] is not None:
            fix_obs = [o for o in obs_avg if o['id'] in cr.json['fix_list']]
        mon_obs = []
        if 'mon_list' in cr.json and cr.json['mon_list'] is not None:
            mon_obs = [o for o in obs_avg if o['id'] in cr.json['mon_list']]
        print "obs fix:%d all:%d" % (len(fix_obs), len(obs_avg))
        # process observations i..j-1
        n_fix = len(fix_obs)
        n_all = len(obs_avg)
        n_mon = len(mon_obs)
        station = False
        if n_fix > 1 and (cr.json['strict'] == 0 or \
            (cr.json['strict'] == 1 and n_fix == n_all)):
            # calculate station coordinates as freestation if gama_path set
            if 'gama_path' in cr.json and cr.json['gama_path'] is not None:
                #print "Freestation..."
                obs1 = [{'station': cr.json['station_id']}] + fix_obs
                fs = Freestation(obs1, st_coord + fix_coords,
                                 cr.json['gama_path'], cr.json['dimension'],
                                 cr.json['probability'], cr.json['stdev_angle'],
                                 cr.json['stdev_dist'], cr.json['stdev_dist1'],
                                 cr.json['blunders'])
                w = fs.Adjustment()
                if w is None:
                    logging.fatal("No adjusted coordinates for station %s" % cr.json['station_id'])
                    sys.exit(-1)
                # update station coordinates
                st_coord = w
                # upload station coords to server
                #print "Uploading station coords..."
                # datetime from observations
                st_coord[0]['datetime'] = fix_obs[0]['datetime']
                # add number of known points
                st_coord[0]['n'] = len(fix_obs)
                # save observations with corrected time
                if wrt.WriteData(st_coord[0]) <> 0:
                    logging.fatal("Cannot write station coordinates")
                for o in fix_obs:
                    if wrt1.WriteData(o) <> 0:
                        logging.fatal("Cannot write observations")
                station = True
        #print "Saving calculated coords..."
        # TODO orientation????
        if n_mon > 0 and \
            (cr.json['st_only'] == 0 or station) and \
            (cr.json['mon_only'] == 0 or \
            cr.json['mon_only'] == 1 and n_all == n_mon):
            for o in mon_obs:       # process monitoring points
                v = o['v'].GetAngle()
                hd = o['distance'] * math.sin(v)
                a = (o['hz']).GetAngle()
                east = st_coord[0]['east'] + math.sin(a) * hd
                north = st_coord[0]['north'] + math.cos(a) * hd
                elev = st_coord[0]['elev'] + hd / math.tan(v)
                c = {'id': o['id'], 'east': east, 'north': north, \
                     'elev': elev, 'datetime': o['datetime']}
                if wrt.WriteData(c) <> 0:
                    logging.fatal("Cannot write mon coordinates")
                if wrt1.WriteData(o) <> 0:
                    logging.fatal("Cannot write mon observations")
        i = j
