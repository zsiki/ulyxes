#!/usr/bin/env python3
"""
.. module:: graphplot_demo.py

.. moduleauthor:: Zoltan Siki

demo application for graphplot from spatialite database or 
CSV file generated by video_aruco.py

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
import os.path
import pandas as pd

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

#from csvreader import CsvReader
from sqlitereader import SqLiteReader
from graphplot import GraphPlot, dict2lists

parser = argparse.ArgumentParser()
parser.add_argument('ids', metavar='point_ids', type=str, nargs='+',
                    help='point IDs')
parser.add_argument('-d', '--database', type=str,
                    help='sqlite database')
parser.add_argument('-f', '--file', type=str,
                    help='CSV file')
parser.add_argument('-c', '--coord', type=str, default='elev',
                    help='chart on column east/north/elev, default: elev')
parser.add_argument('-r', '--relative', action="store_true",
                    help='relative to first value')
parser.add_argument('-m', '--mirror', action="store_true",
                    help='mirror graph on horizontal axis')
parser.add_argument('-a', '--scale', type=float, default =1.0,
                    help='scale multiplier to change coordinate to milimetres')
parser.add_argument('-s', '--start', type=str, default=None,
                    help='start date YYYY-MM-DD format')
parser.add_argument('-e', '--end', type=str, default=None,
                    help='end date YYYY-MM-DD format')
parser.add_argument('-o', '--output', type=str, default=None,
                    help='output png file')
args = parser.parse_args()

time_format = '%Y-%m-%d %H:%M:%S'
if not args.coord in ('east', 'north', 'elev'):
    print('Invalid value for coord, east/north/elev are valid')
    sys.exit()
if args.start is None:
    args.start = '1900-01-01 00:00:00'
if args.end is None:
    args.end = datetime.datetime.now().strftime(time_format)
mirror = -1 if args.mirror else 1
scale = float(args.scale)
data = []
if args.database is not None:
    sql_templ = "SELECT obs_date as dt, {} FROM observations WHERE point_id = '{}' and {} is not NULL and obs_date between '{}' and '{}' ORDER BY obs_date"
    for act_id in args.ids:
        sql = sql_templ.format(args.coord, act_id, args.coord,
                               args.start, args.end)
        r1 = SqLiteReader(args.database, sql)
        d1 = r1.Load()
        if len(d1) == 0:
            print(f'No data for point {act_id} in the database')
            continue
        # convert dict to list
        x1, y1s = dict2lists(d1, 'dt', [args.coord], args.relative, mirror, scale)
        data.append([x1, y1s, None, [act_id]])
elif args.file is not None:
    names = ['time', 'east', 'elev', 'width', 'height', 'code']
    tmp_data = pd.read_csv(args.file, sep=';', names=names,
                           parse_dates=['time'])
    start = datetime.datetime.strptime(args.start, time_format)
    end = datetime.datetime.strptime(args.end, time_format)
    for act_id in args.ids:
        int_id = int(act_id)
        tmp = tmp_data.loc[(tmp_data['code'] == int_id) &
                           (tmp_data['time'] >= start) &
                           (tmp_data['time'] <= end)]
        x1 = tmp['time']
        if args.relative:
            y1s = [(tmp[args.coord] - tmp[args.coord].iat[0]) * mirror * scale]
        else:
            y1s = [tmp[args.coord] * mirror * scale]
        data.append([x1, y1s, None, [act_id]])
else:
    print('Missing database or file name')
    sys.exit()
t = args.coord + " relative" if args.relative else args.coord
titles = [t]
units = ["date", "mm"]
g = GraphPlot(titles, units, data)
if g.valid() > 0:
    print("invalid dataset")
    sys.exit()
if args.output is None:
    g.draw()
else:
    g.draw(args.output)
