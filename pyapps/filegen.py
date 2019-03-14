#!/usr/bin/env python
"""
.. module:: filegen.py

.. moduleauthor:: Zoltan Siki

Sample application of Ulyxes PyAPI to create input file for robot
Output file uses GeoEasy geo format. The first point in the coordinate list is
the station if no station id given.

    :param argv[1] input GeoEasy coo or csv coordinate file
    :param argv[2] output file with observations, geo or dmp file (default stdout)
    :param argv[3] station id (default first point in input)
    :param argv[4] instrument height (default 0)
"""

import sys
import math

sys.path.append('../pyapi/')

from angle import Angle
from georeader import GeoReader
from geowriter import GeoWriter
from csvreader import CsvReader
from csvwriter import CsvWriter
from filemaker import modes1

class ObsGen(object):
    """ Generate observations from coordinates (bearings and zenith angles

        :param ifname: input coordinate file or list of coordinates
        :param station_id: id of the station point, default first point from input
        :param instrument_height: height of instrument, default: 0
        :param faces: default number of faces to measure
    """

    def __init__(self, coords, station_id = None, instrument_height = 0, \
                faces =1):
        """ Initialize
        """
        self.station_id = station_id
        self.station_ih = instrument_height
        self.faces = faces
        self.station_east = None
        self.station_north = None
        self.station_elev = None
        self.coords = coords
        for w in self.coords:
            if self.station_id is None:
                # first point is the station if not defined
                self.station_id = w['id']
            if w['id'] == self.station_id:
                self.station_east = w['east']
                self.station_north = w['north']
                self.station_elev = w['elev']

    def run(self):
        """ generate observation list

            :returns: list of observation dicts ordered by hz
        """
        observations = []
        for coo in self.coords:
            if self.station_id == coo['id']:
                #skip station
                continue
            obs = {}
            d_north = coo['north'] - self.station_north
            d_east = coo['east'] - self.station_east
            d_elev = coo['elev'] - self.station_elev - self.station_ih
            bearing = math.atan2(d_east, d_north)
            dist = math.hypot(d_east, d_north)
            zenith = math.atan2(dist, d_elev)
            obs['id'] = coo['id']
            obs['ih'] = self.station_ih
            obs['hz'] = Angle(bearing).Positive()
            obs['v'] = Angle(zenith).Positive()
            obs['distance'] = math.hypot(dist, d_elev)
            if 'code' in coo:
                obs['code'] = coo['code']
            else:
                obs['code'] = 'ATR'
            obs['faces'] = self.faces
            if 'pc' in coo:
                obs['pc'] = coo['pc']
            #else:                  # let pc set on instrument
            #    obs['pc'] = 0
            if 'code' in coo and coo['code'] in modes1:
                obs['code'] = coo['code']
            observations.append(obs)
        observations = sorted(observations, key = lambda a: a['hz'].GetAngle())
        obs = {}
        obs['station'] = self.station_id
        obs['ih'] = self.station_ih
        observations.insert(0, obs)
        return observations

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 1:
        ifname = sys.argv[1]
    else:
        print ("Usage: filegen.py input_coo_file output_geo_file [station_id] [instrument_height]")
        exit(-1)
        #ifname = "test.coo"
    if len(sys.argv) > 2:
        ofname = sys.argv[2]
    else:
        ofname = 'stdout'
    station_id = None
    if len(sys.argv) > 3:
        station_id = sys.argv[3]
    station_ih = 0
    if len(sys.argv) > 4:
        station_ih = float(sys.argv[4])

    # load input data set
    if ifname[-4:] == '.coo':
        g = GeoReader(fname = ifname, filt = ['id', 'east', 'north', 'elev'])
    else:
        g = CsvReader(fname = ifname, filt = ['id', 'east', 'north', 'elev'])
    data = g.Load()
    if ofname[-4:] == '.geo':
        geo_wrt = GeoWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            filt = ['station', 'id', 'hz', 'v', 'distance', 'faces', 'ih', \
                    'code'], mode = 'w')
    else:
        geo_wrt = CsvWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            header = True, mode = 'w', \
            filt = ['station', 'id', 'hz', 'v', 'distance', 'faces', 'ih', \
                    'code'])
    og = ObsGen(data, station_id, station_ih)
    if og.station_east is None or og.station_north is None or og.station_elev is None:
        print("station coordinates not found: ", station_id)
        exit(-1)
    observations = og.run()

    for obs in observations:
        # heck for dmp output
        if ofname[-4:] != '.geo':
            if 'station' in obs:
                station = obs['station']
                continue
            else:
                obs['station'] = station
        geo_wrt.WriteData(obs)
