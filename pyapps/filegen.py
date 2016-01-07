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

        :param ifname: input coordinate file
        :param station_id: id of the station point, default first point from input
        :param instrument_height: height of instrument, default: 0
    """

    def __init__(self, ifname, station_id = None, instrument_height = 0):
        """ Initialize
        """
        self.station_id = station_id
        self.station_ih = instrument_height
        self.station_east = None
        self.station_north = None
        self.station_elev = None
        self.coords = self.Load(ifname)

    def Load(self, ifn):
        """ load coordinate data from file

            :param ifn: name of input file
            :returns: coordinate list
        """
        # load input data set
        if ifn[-4:] == '.coo':
            g = GeoReader(fname = ifn)
        else:
            g = CsvReader(fname = ifn)
        data = []
        while 1:
            w = g.GetNext()
            if w is None or len(w) == 0:
                break
            if 'id' in w and 'east' in w and 'north' in w and 'elev' in w:
                data.append(w)
                if self.station_id is None:
                    # first point is the station if not defined
                    self.station_id = w['id']
                if w['id'] == self.station_id:
                    self.station_east = w['east']
                    self.station_north = w['north']
                    self.station_elev = w['elev']
        return data

    def run(self):
        """ generate observetion list

            :returns: list of observation dicts
        """
        observations = []
        obs = {}
        obs['station'] = self.station_id
        obs['ih'] = self.station_ih
        observations.append(obs)
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
            zenith = math.atan(dist / math.fabs(d_elev))
            if d_elev < 0:
                zenith = math.pi - zenith
            obs['id'] = coo['id']
            obs['ih'] = self.station_ih
            obs['hz'] = Angle(bearing).Positive()
            obs['v'] = Angle(zenith).Positive()
            obs['code'] = 'ATR'
            obs['faces'] = 1
            if 'code' in coo and coo['code'] in modes1:
                obs['code'] = coo['code']
            observations.append(obs)
        return observations

if __name__ == "__main__":
    # process commandline parameters
    if len(sys.argv) > 1:
        ifname = sys.argv[1]
    else:
        print ("Usage: filegen.py input_coo_file output_geo_file [station_id] [instrument_height]")
        #exit(-1)
        ifname = "otthon.coo"
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

    if ofname[-4:] == '.geo':
        geo_wrt = GeoWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            filt = ['station', 'id', 'hz', 'v', 'faces', 'ih', 'code'], \
            mode = 'w')
    else:
        geo_wrt = CsvWriter(dist = '.4f', angle = 'RAD', fname = ofname, \
            header = True, mode = 'w', \
            filt = ['station', 'id', 'hz', 'v', 'faces', 'ih', 'code'])
    og = ObsGen(ifname, station_id, station_ih)
    if og.station_east is None or og.station_north is None or og.station_elev is None:
        print "station coordinates not found: ", station_id
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
