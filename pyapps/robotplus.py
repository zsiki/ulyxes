#!/usr/bin/env python
"""
.. module:: robot.py

.. moduleauthor:: Zoltan Siki

Sample application for complex monitoring for a station

Parameters are stored in config file using JSON format

    :param station_type: TCRA1103/TPS1200/TCA1800
    :param station_id: pont id for the station
    :param station_height: height above point, optional default 0
    :param fix_list: list of fix points to calculate station coordinates
    :param mon_list: list of monitoring points to measure
    :param port: serial port to use (e.g. COM1 or /dev/ttyS0 or /dev/ttyUSB0)
    :param gama_path: path to GNU Gama executable
    :param coo_rd: URL to get coordinates from (server side script)
    :param coo_wr: URL to send coordinates to
    :param obs_wr: URL to send observations to
    :param met: met sensor name WEBMET/BMP180, optional default None
    :param met_addr: URL to webmet data, optional default None
    :param met_par: parameters to web met service, optional default None
"""

import sys
import re
import logging
import math
import os
import json

sys.path.append('../pyapi/')

from angle import Angle
from httpreader import HttpReader
from httpwriter import HttpWriter
from filegen import ObsGen
from serialiface import SerialIface
from totalstation import TotalStation
from blindorientation import Orientation
from robot import Robot
from freestation import Freestation
from webmetmeasureunit import WebMetMeasureUnit
from webmet import WebMet
from webiface import WebIface
from leicatps1200 import LeicaTPS1200
from leicatcra1100 import LeicaTCRA1100
from leicatca1800 import LeicaTCA1800

logging.getLogger().setLevel(logging.WARNING)

def conf_check(conf):
    """ Check configuration

        :param conf: dict of config parameters
        :returns: True/False
    """
    obligatory = ['station_type', 'station_id', 'mon_list', \
                  'port', 'coo_rd', 'coo_wr']
    for par in obligatory:
        if not par in conf:
            logging.error(par + " not defined in config")
            return False
    if not re.search('120[0-9]$', conf['station_type']) and \
       not re.search('1800$', conf['station_type']) and \
       not re.search('110[0-9]$', conf['station_type']):
        logging.error("Unknown station type:" + conf['station_type'])
        return False
    if not 'station_height' in conf:
        logging.warning("station_height not defined in config, set to 0")
        conf['station_height'] = 0
    if not 'faces' in conf:
        conf['faces'] = 1
    # are thhere fix points?
    if 'fix_list' in conf:
        if not type(conf['fix_list']) == list:
            logging.error("fix_list not a list")
            return False
        elif len(conf['fix_list']) == 0:
            conf['fix_list'] = None
            conf['gama_path'] = None
        elif len(conf['fix_list']) < 3:
            logging.error("fix_list shorter than 3")
            return False
    else:
        conf['fix_list'] = None
        conf['gama_path'] = None
    if not type(conf['mon_list']) == list:
        logging.error("mon_list not a list")
        return False
    if len(conf['mon_list']) < 1:
        logging.error("mon_list is empty")
        return False
    if conf['gama_path'] is not None and \
            not (os.path.isfile(conf['gama_path']) and \
            os.access(conf['gama_path'], os.X_OK)):
        logging.error("GNU Gama not found or not executable:" + conf['gama_path'])
        return False
    if 'met' in conf:
        if not conf['met'].upper() in ['WEBMET', 'BMP180']:
            logging.error("Invalid met sensor:" + conf['met'])
            return False
        if conf['met'].upper() == 'WEBMET':
            if not 'met_addr' in conf:
                logging.error("met_addres not defined")
                return False
            if not 'met_par' in conf:
                logging.error("met_par not defined")
                return False
    else:
        conf['met'] = None
    return True

def conf_load(fname):
    """ Load json config from file

        :param fname: name of the config file
    """
    conf_file = open(fname)    
    c = ""
    for line in conf_file:
        c += line
    conf = json.loads(c)
    return conf

def get_mu(t):
    """ Select measure unit

        :param t: instrument type 1200/1800/1100
        :returns: measure unit or False
    """
    if re.search('120[0-9]$', t):
        return LeicaTPS1200()
    elif re.search('110[0-9]$', t):
        return LeicaTCRA1100()
    elif re.search('180[0-9]$', t):
        return LeicaTCA1800()
    return False

def avg_coo(coords):
    """ Calculate average coordinates

        :param coords: input coordinate list (duplicates)
        :returns: average coordinates no duplicates
    """
    res = []    # output list
    ids = [coo['id'] for coo in coords]
    for i in ids:
        e = [coo['east'] for coo in coords if coo['id'] == i]
        n = [coo['north'] for coo in coords if coo['id'] == i]
        h = [coo['elev'] for coo in coords if coo['id'] == i]
        res.append({'east': sum(e) / len(e), 'north': sum(n) / len(n), 
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
        # get first datetime for k
        dt = [o['datetime'] for o in obs if 'id' in o and o['id'] == k][0]
        # separate face left/right
        hz1 = [o['hz'].GetAngle() for o in obs if o['id'] == k and \
            o['v'].GetAngle() < math.pi]
        hz2 = [o['hz'].GetAngle() for o in obs if o['id'] == k and \
            o['v'].GetAngle() > math.pi]
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
        if hz1[0] > hz2[0]:
            hz2 = [h + math.pi for h in hz2]
        else:
            hz2 = [h - math.pi for h in hz2]
        hz = sum(hz1 + hz2) / (len(hz1) + len(hz2))

        v1 = [o['v'].GetAngle() for o in obs if o['id'] == k and \
            o['v'].GetAngle() < math.pi]
        v2 = [math.pi * 2.0 - o['v'].GetAngle() \
            for o in obs if o['id'] == k and o['v'].GetAngle() > math.pi]
        v = sum(v1 + v2) / (len(v1) + len(v2))
        sd12 = [o['distance'] for o in obs]
        sd = sum(sd12) / len(sd12)
        res.append({'id': k, 'hz': Angle(hz), 'v': Angle(v), 'distance': sd, \
            'datetime': dt})
    return res

if __name__ == "__main__":
    # command line param
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            try:
                conf = conf_load(sys.argv[1])
            except:
                logging.error("Error in config file: ", sys.argv[1])
                sys.exit(-1)
        else:
            logging.error("Config file not found")
    else:
        print "Usage: robotplus.py config_file"
        #sys.exit(-1)
        conf = conf_load('robotplus.json')
    if not conf_check(conf):
        sys.exit(-1)

    # create totalstation
    mu = get_mu(conf['station_type'])
    iface = SerialIface("rs-232", conf['port'])
    ts = TotalStation(conf['station_type'], mu, iface)
    w = ts.GetATR() # wake up instrument
    if 'errorCode' in w:
        time.sleep(15)
    w = ts.GetATR() # wake up instrument
    if 'errorCode' in w or ts.measureIface.GetState():
        logging.error("Instrument wake up failed")
        sys.exit(-1)
    # get meteorology data
    print "Getting met data..."
    if not conf['met'] is None:
        atm = ts.GetAtmCorr()     # get current settings from ts
        if conf['met'].upper() == 'WEBMET':
            wi = WebIface("demo", conf['met_addr'], "json")
            web_mu = WebMetMeasureUnit(msg = conf['met_par'])
            web_met = WebMet('WebMet', web_mu, wi)
            data = web_met.GetPressure()
            pres = data['pressure']
            temp = data['temp']
            humi = data['humidity']
            wet = web_met.GetWetTemp(temp, humi)
        # TODO other met sensors
        ts.SetAtmCorr(float(atm['lambda']), pres, temp, wet)
    # get station coordinates
    print "Loading station coords..."
    rd_st = HttpReader(url=conf['coo_rd'], ptys='STA', \
        filt = ['id', 'east', 'north', 'elev'])
    st_coord = [x for x in rd_st.Load() if x['id'] == conf['station_id']]
    if len(st_coord) == 0:
        logging.error("Station not found: " + conf['station_id'])
        sys.exit(-1)
    # coordinate writer
    wrt = HttpWriter(url = conf['coo_wr'], mode = 'POST')
    # observation writer
    if 'obs_wr' in conf:
        wrt1 = HttpWriter(url = conf['obs_wr'], mode = 'POST')
    else:
        wrt1 = wrt
    if not conf['fix_list'] is None:
    # get fix coordinates from database
        print "Loading fix coords..."
        rd_fix = HttpReader(url=conf['coo_rd'], ptys='FIX', \
            filt = ['id', 'east', 'north', 'elev'])
        # remove other points
        fix_coords = [p for p in rd_fix.Load() if p['id'] in conf['fix_list']]
        # generate observations for fix points, first point is the station
        print "Generating observations for fix..."
        og = ObsGen(st_coord + fix_coords, conf['station_id'], \
            conf['station_height'], conf['faces'])
        observations = og.run()
        # check/find orientation
        print "Orientation..."
        o = Orientation(observations, ts)
        if not o.Search():
            logging.error("Orientation failed %s" % conf['station_id'])
            sys.exit(-1)
        # observation to fix points
        print "Measuring to fix..."
        r = Robot(observations, st_coord, ts)
        obs_out, coo_out = r.run()
        # TODO observations to FIX points to the database????
        # calculate station coordinates as freestation
        print "Freestation..."
        obs_out = avg_obs(obs_out)
        fs = Freestation(obs_out, st_coord + fix_coords, conf['gama_path'])
        w = fs.Adjustment()
        if w is None:
            logging.error("No adjusted coordinates for station %s" % conf['station_id'])
            sys.exit(-1)
        if math.abs(st_coord[0]['east'] - w[0]['east']) > 0.03 or \
           math.abs(st_coord[0]['north'] - w[0]['north']) > 0.03 or \
           math.abs(st_coord[0]['elev'] - w[0]['elev']) > 0.03:
            logging.error("Station moved!!!")
            sys.exit(-1)
        # update station coordinates
        st_coord = w
        # upload station coords to server
        print "Uploading station coords..."
        wrt.WriteData(st_coord[0])
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
        ori_p = [ p for p in fix_coords if p['id'] == back_site ][0]
        bearing = Angle(math.atan2(ori_p['east'] - st_coord[0]['east'], \
                             ori_p['north'] - st_coord[0]['north']))
        # rotate to farest FIX and set orientation
        ts.Move(obs_out[back_indx]['hz'], obs_out[back_indx]['v'], 1)
        ts.SetOri(bearing)
    # get monitoring coordinates from database
    print "Loading mon coords..."
    rd_mon = HttpReader(url=conf['coo_rd'], ptys='MON', \
        filt = ['id', 'east', 'north', 'elev'])
    mon_coords = [p for p in rd_mon.Load() if p['id'] in conf['mon_list']]
    # generate observations for monitoring points, first point is the station
    print "Generating observations for mon..."
    og = ObsGen(st_coord + mon_coords, conf['station_id'], \
        conf['station_height'], conf['faces'])
    observations = og.run()
    # observation to monitoring points
    print "Measuring mon..."
    r = Robot(observations, st_coord, ts)
    obs_out, coo_out = r.run()
    if 'avg_wr' in conf:
        coo_out = avg_coo(coo_out)
        obs_out = avg_obs(obs_out)
    for o in obs_out:
        if 'distance' in o:
            wrt1.WriteData(o)
    for c in coo_out:
        wrt.WriteData(c)
