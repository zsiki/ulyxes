#!/usr/bin/env python
"""
.. module:: coord_plot.py

.. moduleauthor:: Bence Takacs

Plot coordinate changes from monitoring coordinate file

Parameters are stored in config file using JSON format::

    log_file: path to log file, file must exist!
    log_level: 10/20/30/40/50 for DEBUG/INFO/WARNING/ERROR/FATAL
    log_format: format string for log (default: "%(asctime)s %(levelname)s:%(message)s"), optional
    point_list: list of points to plot
    ref_line_points: two point ids to transform coordinates into the reference line defined by these two points
    coo_rd: database to get coordinates from
    coo_ref: reference of coordinates to et changes from
    range: range of plots, optional (default: 50 mm)
    date_from: date to plot coordinates from, optional (default: first date in the database/file)
    date_until: date to plot coordinates until (default: last date in the database/file)
    plot_folder: path of folder where to put plots (default: current folder)

"""

import sys
import re
import logging
import os
#https://sourceforge.net/projects/pygnuplot/
import pyGnuplot
import math

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from httpreader import HttpReader
from sqlitereader import SqLiteReader
from confreader import ConfReader
from georeader import GeoReader

if __name__ == "__main__":
    config_pars = {
        'log_file': {'required' : True, 'type': 'file'},
        'log_level': {'required' : True, 'type': 'int',
            'set': [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]},
        'log_format': {'required': False, 'default': "%(asctime)s %(levelname)s:%(message)s"},
        'point_list': {'required': True, 'type': 'list'},
        'ref_line_points': {'required': False, 'type': 'list'},
        'coo_ref': {'required': True, 'type': 'file'},
        'coo_rd': {'required' : True},
        'range': {'required': False, 'type': 'float', 'default': 50},
        'date_from': {'required': True, 'type': 'date', 'default': ""},
        'date_until': {'required': True, 'type': 'date', 'default': ""},
        'plot_folder': {'required' : False, 'type': 'str', 'default': "."},
        '__comment__': {'required': False, 'type': 'str'}
    }
    # check command line param
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            try:
                cr = ConfReader('coords', sys.argv[1], config_pars)
                cr.Load()
            except:
                logging.fatal("Error in config file: " + sys.argv[1])
                sys.exit(-1)
            if not cr.Check():
                logging.fatal("Config check failed")
                sys.exit(-1)
        else:
            print("Config file not found " + sys.argv[1])
            logging.fatal("Config file not found " + sys.argv[1])
            sys.exit(-1)
    else:
        print("Usage: coord_plot.py config_file")
        sys.exit(-1)

    # logging
    #TODO if the log file does not exist, it causes an error message
    logging.basicConfig(format=cr.json['log_format'], filename=cr.json['log_file'], \
         filemode='w', level=cr.json['log_level'])

    # load reference coordinates of points
    if re.search('^http[s]?://', cr.json['coo_ref']):
        rd_st = HttpReader(url=cr.json['coo_ref'], ptys=['STA'], \
                           filt=['id', 'east', 'north', 'elev'])
    elif re.search('^sqlite:', cr.json['coo_ref']):
        rd_st = SqLiteReader(db=cr.json['coo_ref'][7:], \
                             filt=['id', 'east', 'north', 'elev'])
    else:
        rd_st = GeoReader(fname=cr.json['coo_ref'], \
                          filt=['id', 'east', 'north', 'elev'])
    w = rd_st.Load()
    logging.info('%d rows read from %s' % (len(w), cr.json['coo_ref']))

    #transform into system of reference line
    if len(cr.json['ref_line_points']) == 2:
        logging.info('ref line points: %s, %s' % (cr.json['ref_line_points'][0], cr.json['ref_line_points'][1]))
        # A point coordinates in reference line
        try:
            iA = filter(lambda pp: pp['id'] == cr.json['ref_line_points'][0], w)[0]
        except IndexError:
            iA = None
            logging.error('No A point of reference line found: %s ' % cr.json['ref_line_points'][0])
        # B point coordinates in reference line
        try:
            iB = filter(lambda pp: pp['id'] == cr.json['ref_line_points'][1], w)[0]
        except IndexError:
            iB = None
            logging.error('No B point of reference line found: %s ' % cr.json['ref_line_points'][1])
        #TODO: tavolsag, iranyszog fuggveny nincs?
        if (iA and iB):
            dAB = math.hypot(iB['east'] - iA['east'], iB['north'] - iA['north'])
            sinAB = (iB['east'] - iA['east']) / dAB
            cosAB = (iB['north'] - iA['north']) / dAB
            y0 = iA['east']
            x0 = iA['north']
        else:
            y0 = 0
            x0 = 0
            sinAB = 0
            cosAB = 1
        logging.info('parameters of transformation into reference line: %.4f, %.4f, %.6f, %.6f' % (y0, x0, sinAB, cosAB))

    #plot each points
    for p in cr.json['point_list']:
        logging.info('Plotting point: %s' % p)

        # load coordinates recorded by robotplus of selected points
        if re.search('^sqlite:', cr.json['coo_rd']):
            sql = "SELECT * FROM monitoring_coo WHERE id='%s'" % p
            if cr.json['date_from']:
                sql = sql + " and datetime > '" + cr.json['date_from'] + "'"
            if cr.json['date_until']:
                sql = sql + " and datetime < '" + cr.json['date_until'] + "'"
            rd_coo = SqLiteReader(db=cr.json['coo_rd'][7:], sql=sql)
        else:
            logging.fatal('sorry, get coordinates only from sqlite database')
            sys.exit(-1)
        coo = rd_coo.Load()
        logging.info('%d rows read from %s' % (len(coo), cr.json['coo_rd']))
        if len(coo) < 5:
            logging.error('less then 5 points are in the db for %s' % p)
            continue

        # reference coordinates
        try:
            i0 = filter(lambda pp: pp['id'] == p, w)[0]
            logging.info('reference coordinates %.4f, %.4f, %.4f' % (i0['east'], i0['north'], i0['elev']))
        except IndexError:
            logging.error('no reference coordinates in file %s for point %s' % (cr.json['coo_ref'], p))
            continue

        #transform reference coordinates into reference line system
        a0 = (i0['east'] - y0) * sinAB + (i0['north'] - x0) * cosAB
        b0 =-(i0['east'] - y0) * cosAB + (i0['north'] - x0) * sinAB
        logging.info('reference coordinates: %.4f, %.4f' % (a0, b0))

        #transform coordinates into reference line system
        #a is in the reference line, b is perpendicular to the reference line
        a = [ (c['east'] - y0) * sinAB + (c['north'] - x0) * cosAB for c in coo]
        b = [-(c['east'] - y0) * cosAB + (c['north'] - x0) * sinAB for c in coo]

        # subtract reference coordinates
        a[:] = [1000 * (x - a0) for x in a]
        b[:] = [1000 * (x - b0) for x in b]
        z = [1000 * (c['elev'] - i0['elev']) for c in coo]
        t = [c['datetime'] for c in coo]

        # plot coordinate changes in elevation
        g = pyGnuplot.gnuplot(debug=False)
        g('set title "point: ' + p.replace("_", "-") + ' change in elevation "')
        g('set xdata time')
        g('set timefmt "%Y-%d-%m %H:%M:%S"')
        g('set format x "%m/%d"')
        g('set yrange [' + str(-cr.json['range']) + ":" + str(cr.json['range']) + "]")
        g('set grid lt 0')
        g('set xlabel "date [mm/dd]"')
        g('set ylabel "coordinate change [mm]"')
        ps = g.style(style="point", ps=1, pt=1, lc="orange") #point style
        plt = g.plot(z, xvals=t, u="1:3", style="point", ls=ps)
        if not os.path.exists(cr.json['plot_folder']):
            os.makedirs(cr.json['plot_folder'])
        g.hardcopy(plt, file=cr.json['plot_folder'] + '/' + p + 'elev.png', terminal='png')

        # plot coordinate changes in a
        g('set title "point: ' + p.replace("_", "-") + ' change in reference line"')
        ps = g.style(style="point", ps=1, pt=1, lc="blue") #point style
        plt = g.plot(a, xvals=t, u="1:3", style="point", ls=ps)
        if not os.path.exists(cr.json['plot_folder']):
            os.makedirs(cr.json['plot_folder'])
        g.hardcopy(plt, file=cr.json['plot_folder'] + '/' + p + 'x.png', terminal='png')

        # plot coordinate changes in b
        g('set title "point: ' + p.replace("_", "-") + ' change in perpendicular to reference line"')
        ps = g.style(style="point", ps=1, pt=1, lc="red") #point style
        plt = g.plot(b, xvals=t, u="1:3", style="point", ls=ps)
        if not os.path.exists(cr.json['plot_folder']):
            os.makedirs(cr.json['plot_folder'])
        g.hardcopy(plt, file=cr.json['plot_folder'] + '/' + p + 'y.png', terminal='png')
