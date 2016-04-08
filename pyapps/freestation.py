#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: freestation.py
    :platform: Linux, Windows
    :synopsis: interface modul to GNU Gama

.. moduleauthor::Zoltan Siki <siki@agt.bme.hu>

    calculate 3D coordinates of a station from polar observations as a
    free starion, blunders are eliminated 

    :param argv[1]: input geo/coo or dmp/csv file
    :param argv[2]: gama-local path
"""

import sys
import os
import logging

sys.path.append('../pyapi/')

from georeader import GeoReader
from csvreader import CsvReader
from gamaiface import GamaIface

#logging.getLogger().setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.INFO)

class Freestation(object):
    """ Calculate freestation and remove blunders

        :param obs: list of observations
        :param coords: coordinates of points
        :param gama_path: path to gama-local
        :param dimiension: dimension of adjustment 1/2/3
        :param
    """

    def __init__(self, obs, coords, gama_path, dimension=3, probability=0.95,
                stdev_angle=1, stdev_dist=1, stdev_dist1=1.5):
        """ initialize
        """
        # create gama interface
        self.g = GamaIface(gama_path, dimension, probability, stdev_angle,
                        stdev_dist, stdev_dist1)
        ns = 0    # number of stations
        no = 0    # number of observations
        self.station = None
        for w in obs:
            if 'station' in w:
                ns += 1
                if ns > 1:
                    break    # stop after first station
                self.station = w['station']
                self.g.add_observation(w)
            elif 'id' in w and 'hz' in w and 'v' in w and 'distance' in w:
                no += 1 # number of observations
                self.g.add_observation(w)
        for w in coords:
            if w['id'] == self.station:
                self.g.add_point(w, 'ADJ')
            elif 'east' in w and 'north' in w and 'elev' in w:
                self.g.add_point(w, 'FIX')

    def Adjustment(self):
        """ adjustment & and blunder removing

            :returns: adjusted coordinates or None
        """
        # adjustment loop
        last_res = None
        while True:
            res, blunder = self.g.adjust()
            if res is None or not 'east' in res[0] or not 'north' in res[0] or \
                              not 'elev' in res[0]:
                # adjustment faild or too many blunders
                if not last_res is None:
                    logging.warning("blunders are not fully removed")
                    res = last_res
                else:
                    logging.error("adjustment failed")
                break
            elif blunder['std-residual'] < 1.0:
                logging.info("blunders removed")
                break
            else:
                logging.info("%s - %s observation removed" % (blunder['from'], blunder['to']))
                self.g.remove_observation(blunder['from'], blunder['to'])
                last_res = res
        return res

if __name__ == "__main__":
    #fname = "/home/siki/GeoEasy/data/freestation.geo"
    #fname = "test.geo"
    #gama_path = '/home/siki/GeoEasy/gama-local'

    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if not os.path.isfile(fname):
            print "File not found: " + fname
            sys.exit(-1)
    else:
        print "Usage: freestation.py input_file gama_path station_id station_height"
        sys.exit(-1)
    if not fname[-4:] in ['.geo', '.coo', '.dmp', '.csv']:
        fname += '.geo'
    if len(sys.argv) > 2:
        gama_path = sys.argv[2]
    else:
        gama_path = '/home/siki/GeoEasy/gama-local'

    # load observations and coordinates
    fn = fname[:-4] # remove extension
    ext = fname[-4:]
    if ext in ['.geo', '.coo']:
        obs = GeoReader(fname = fn + '.geo')
    else:
        obs = CsvReader(fname = fn + '.dmp')
    # load observations
    observations = obs.Load()
    # load coordinates and add to adjustment
    if ext in ['.geo', '.coo']:
        coo = GeoReader(fname = fn + '.coo')
    else:
        coo = CsvReader(fname = fn + '.csv')
    n = 0   # number of points
    st = False  # station found
    coords = coo.Load()
    f = Freestation(observations, coords, gama_path)
    print f.Adjustment()
