#!/usr/bin/env python3
"""
.. module:: robotplus.py

.. moduleauthor:: Zoltan Siki

demo application for graphplot from spatialite database

command line parameters::

    --database sqlite database with an observations table and obs_date, east, north, elev columns
    --coord east/north/elev coodinate for the graphicon
    --relative display relative values from the first data
    --start date start date in 2021-01-01 format
    --end date stop date
    -- output file output to png file if not given graph is shown on display
"""
import sys
import argparse
import datetime

sys.path.append('../pyapi/')
#from csvreader import CsvReader
from sqlitereader import SqLiteReader
from graphplot import GraphPlot, dict2lists

parser = argparse.ArgumentParser()
parser.add_argument('ids', metavar='point_ids', type=str, nargs='+',
                    help='point IDs')
parser.add_argument('-d', '--database', type=str,
                    help='sqlite database')
parser.add_argument('-c', '--coord', type=str, default='elev',
                    help='chart on column east/north/elev, default: elev')
parser.add_argument('-r', '--relative', action="store_true",
                    help='relative to first value')
parser.add_argument('-s', '--start', type=str, default=None,
                    help='start date YYYY-MM-DD format')
parser.add_argument('-e', '--end', type=str, default=None,
                    help='end date YYYY-MM-DD format')
parser.add_argument('-o', '--output', type=str, default=None,
                    help='output png file')
args = parser.parse_args()

if not args.coord in ('east', 'north', 'elev'):
    print('Invalid value for coord, east/north/elev are valid')
    sys.exit()
if args.database is None:
    print('Missing database name')
    sys.exit()
if args.start is None:
    args.start = '1900-01-01'
if args.end is None:
    args.end = datetime.date.today().strftime('%Y-%m-%d')
sql_templ = "SELECT obs_date as dt, {} FROM observations WHERE point_id = '{}' and {} is not NULL and obs_date between '{}' and '{}' ORDER BY obs_date"
data = []
for act_id in args.ids:
    sql = sql_templ.format(args.coord, act_id, args.coord, args.start, args.end)
    r1 = SqLiteReader(args.database, sql)
    d1 = r1.Load()
    # convert dict to list
    x1, y1s = dict2lists(d1, 'dt', [args.coord], args.relative)
    data.append([x1, y1s, None, [act_id]])

t = args.coord + " relative" if args.relative else args.coord
titles = [t]
units = ["date", "m"]
g = GraphPlot(titles, units, data)
if g.valid() > 0:
    print("invalid dataset")
    sys.exit()
if args.output is None:
    g.draw()
else:
    g.draw(args.output)
