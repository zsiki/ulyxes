#!/usr/bin/env python
"""
.. module:: geo2sqlite.py

.. moduleauthor:: Zoltan Siki

Sample application to convert robotplus output geo/coo files to sqlite db

    :param argv[1]: input geo/coo file
    :param argv[2]: output database file (tables have to be created)

"""

import sys
import re
import os.path

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from georeader import GeoReader
from sqlitewriter import SqLiteWriter

if len(sys.argv) < 3:
    print("Usage {} file.geo database.sqlite".format(sys.argv[0]))
    exit(0)

fn = sys.argv[1][:-4]
coo_rdr = GeoReader(fname=fn+'.coo')
geo_rdr = GeoReader(fname=fn+'.geo')
coo_wrt = SqLiteWriter(db=sys.argv[2], table='monitoring_coo',
    filt=['id', 'east', 'north', 'elev', 'datetime'])
geo_wrt = SqLiteWriter(db=sys.argv[2], table='monitoring_obs',
    filt=['id', 'hz', 'v', 'distance',
          'crossincline', 'lengthincline', 'datetime'])
buf = coo_rdr.Load()
for b in buf:
    coo_wrt.WriteData(b)

buf = geo_rdr.Load()
for b in buf:
    geo_wrt.WriteData(b)
