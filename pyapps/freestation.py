#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: freestation
    :platform: Linux, Windows
    :synopsis: interface modul to GNU Gama

.. moduleauthor::Zoltan Siki <siki@agt.bme.hu>

    calculate 3D coordinates of a station from polar observations
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

logging.getLogger().setLevel(logging.WARNING)

fname = "/home/siki/GeoEasy/data/freestation.geo"
gama_path = '/home/siki/GeoEasy/gama-local'

if len(sys.argv) > 1:
    fname = sys.argv[1]
if not fname[-4:] in ['.geo', '.coo', '.dmp', '.csv']:
    fname += '.geo'
if not os.path.isfile(fname):
    print "File not found: " + fname
    exit(-1)
fn = fname[:-4] # remove extension
ext = fname[-4:]
g = GamaIface(gama_path, 3, 0.95, 1, 1, 1.5)
if ext in ['.geo', '.coo']:
    obs = GeoReader(fname = fn + '.geo')
else:
    obs = CsvReader(fname = fn + '.dmp')
# load observations
no = 0
ns = 0
while True:
    w = obs.GetNext()
    if w is None or len(w) == 0:
        break
    if 'station' in w:
        ns += 1
        if ns > 1:
            break   # only first station is used
        station = w['station']
        g.add_observation(w)
    elif 'id' in w and 'hz' in w and 'v' in w and 'distance' in w:
        no += 1 # number of observations
        g.add_observation(w)
# load coordinates
if ext in ['.geo', '.coo']:
    coo = GeoReader(fname = fn + '.coo')
else:
    coo = CsvReader(fname = fn + '.csv')
n = 0
while True:
    w = coo.GetNext()
    if w is None or len(w) == 0:
        break
    if 'id' in w:
        if w['id'] == station:
            g.add_point(w, 'ADJ')
        else:
            g.add_point(w, 'FIX')
# adjustment loop
res = {}
while True:
    last_res = res
    res, blunder = g.adjust()
    print res[0]
    print blunder
    if not 'east' in res[0] or not 'north' in res[0] or not 'elev' in res[0]:
        print "adjustment failed"
        break
    elif blunder['std-residual'] < 1.0:
        print "blunders removed"
        break
    else:
        print "%s - %s observation removed" % (blunder['from'], blunder['to'])
        g.remove_observation(blunder['from'], blunder['to'])
