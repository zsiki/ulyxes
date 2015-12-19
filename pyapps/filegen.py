#!/usr/bin/env python
"""
.. module:: filegen.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input file for robot
Output file uses GeoEasy geo format. The first point in the coordinate list is
the station.

    :param argv[1] output file with observations, geo or dmp file
    :param argv[2] input GeoEasy coo or csv coordinate file
    :param argv[3] station id (default first point in input)
    :param argv[4] instrument height (default 0)
"""

import sys
sys.path.append('../pyapi/')

import math
from angle import Angle
from georeader import GeoReader
from geowriter import GeoWriter
from csvreader import CsvReader
from csvwriter import CsvWriter
from filemaker import modes1

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 2:
        ofname = sys.argv[1]
        ifname = sys.argv[2]
    else:
        print ("Usage: filegen.py output_geo_file input_coo_file [station_id] [instrument_height]")
        #exit(-1)
        ofname = 'xxx.geo'
        ifname = 'test.coo'
    station_id = None
    if len(sys.argv) > 3:
        station_id = sys.argv[3]
    station_ih = 0
    if len(sys.argv) > 4:
        station_ih = float(sys.argv[4])

    if ofname[-4:] == '.geo':
        geo_wrt = GeoWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            filt = ['station', 'id', 'hz', 'v', 'faces', 'ih', 'code'], \
            mode = 'w')
    else:
        geo_wrt = CsvWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            header = True, filt = ['station', 'id', 'hz', 'v', 'faces', 'code'], \
            mode = 'w')
    if ifname[-4:] == '.coo':
        geo_rdr = GeoReader(fname = ifname)
    else:
        geo_rdr = CsvReader(fname = ifname)
    # read coordinates
    coords = []
    while 1:
        w = geo_rdr.GetNext()
        if w is None or len(w) == 0:
            break
        if 'id' in w and 'east' in w and 'north' in w and 'elev' in w:
            # use only 3D points
            coords.append(w)
            print w
    # get station coordinates
    station_east = station_north = station_elev = None
    if station_id is None:
        station_id = coords[0]['id']
        station_east = coords[0]['east']
        station_north = coords[0]['north']
        station_elev = coords[0]['elev']
    else:
        for coo in coords:
            if coo['id'] == station_id:
                station_id = coo['id']
                station_east = coo['east']
                station_north = coo['north']
                station_elev = coo['elev']
                break
    if station_east is None:
        print "station coordinates not found: ", station_id
        exit(-1)
    obs = {}
    obs['station'] = station_id
    obs['ih'] = 0
    geo_wrt.WriteData(obs)
    for coo in coords:
        if station_id == coo['id']:
            #skip station
            continue
        obs = {}
        d_north = coo['north'] - station_north
        d_east = coo['east'] - station_east
        d_elev = coo['elev'] - station_elev - station_ih
        bearing = math.atan2(d_north, d_east)
        dist = math.hypot(d_north, d_east)
        zenith = math.atan(dist / math.fabs(d_elev))
        if d_elev < 0:
            zenith += math.pi / 2.0
        obs['station'] = station_id
        obs['hz'] = Angle(bearing).Positive()
        #obs['hz'].Positive()
        print "hz=" +obs['hz'].GetAngle('DMS')
        obs['v'] = Angle(zenith).Positive()
        #obs['v'].Positive()
        print "v=" + obs['v'].GetAngle('DMS')
        obs['code'] = 'ATR'
        obs['faces'] = 1
        if 'code' in coo and coo['code'] in modes1:
            obs['code'] = coo['code']
        print obs
        geo_wrt.WriteData(obs)
