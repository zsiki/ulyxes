#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: freestation
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

#fname = "/home/siki/GeoEasy/data/freestation.geo"
fname = "test.geo"
gama_path = '/home/siki/GeoEasy/gama-local'

class Freestation(object):
    """ Calculate freestation and remove blunders

        :param ifname: input geo/coo or dmp/csv file name
        :param station_id: station id, default first station in observation file
        :param istrument_height: instrument height, default 0
    """

    def __init__(self, fname, gama_path):
        """ initialize
        """
        # create gama interface
        self.g = GamaIface(gama_path, 3, 0.95, 1, 1, 1.5)
        # load observations and coordinates
        fn = fname[:-4] # remove extension
        ext = fname[-4:]
        if ext in ['.geo', '.coo']:
            obs = GeoReader(fname = fn + '.geo')
        else:
            obs = CsvReader(fname = fn + '.dmp')
        # load observations
        no = 0  # number of observations
        ns = 0  # number of stations
        while True:
            w = obs.GetNext()
            if w is None or len(w) == 0:
                break
            if 'station' in w:
                ns += 1
                if ns > 1:
                    break   # only first station is used
                station = w['station']
                self.g.add_observation(w)
            elif 'id' in w and 'hz' in w and 'v' in w and 'distance' in w:
                no += 1 # number of observations
                self.g.add_observation(w)
        if no < 3:
            logging.error("few observations")
        # load coordinates and add to adjustment
        if ext in ['.geo', '.coo']:
            coo = GeoReader(fname = fn + '.coo')
        else:
            coo = CsvReader(fname = fn + '.csv')
        n = 0   # number of points
        st = False  # station found
        while True:
            w = coo.GetNext()
            if w is None or len(w) == 0:
                break
            n += 1
            if 'id' in w:
                if w['id'] == station:
                    self.g.add_point(w, 'ADJ')
                    st = True
                elif 'east' in w and 'north' in w and 'elev' in w:
                    self.g.add_point(w, 'FIX')
                else:
                    logging.warning("point skiped (no 3D coords):" + w['id'])
            else:
                logging.warning("line skiped (no id):" + str(n))
        if n < 3:
            logging.error("not enough points found in coordinate list")
        if not st:
            logging.error("not station found in coordinate list:" + station)

    def Adjustment(self):
        """ adjustment & and blunder removing

            :returns: adjusted coordinates or None
        """
        # adjustment loop
        res = {}
        while True:
            res, blunder = self.g.adjust()
            if res is None or not 'east' in res[0] or not 'north' in res[0] or \
               not 'elev' in res[0]:
                logging.error("adjustment failed")
                break
            elif blunder['std-residual'] < 1.0:
                logging.info("blunders removed")
                break
            else:
                logging.info("%s - %s observation removed" % (blunder['from'], blunder['to']))
                self.g.remove_observation(blunder['from'], blunder['to'])
        return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        if not os.path.isfile(fname):
            print "File not found: " + fname
            exit(-1)
    else:
        print "Usage: freestation.py input_file gama_path station_id station_height"
        exit(-1)
    if not fname[-4:] in ['.geo', '.coo', '.dmp', '.csv']:
        fname += '.geo'
    if len(sys.argv) > 2:
        gama_path = sys.argv[2]
    else:
        gama_path = '/home/siki/GeoEasy/gama-local'
    f = Freestation(fname, gama_path)
    print f.Adjustment()
