#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
.. module:: nmea_demo.py
  :platform: Unix, Windows

.. moduleauthor:: dr. Zoltan Siki <siki.zoltan@epito.bme.hu>

GNSS demo collects data from the NMEA GNSS receiver or reads data from file,
sends data to a remote url to store/process them.

Usage: 

* python nmea_demo.py COM1
* python nmea_demo.py /dev/sttyUSB0 
* python nmea_demo.py demo.nmea
* python nmea_demo.py COM1 http://enfo.hu/gnss_demo/get.php
* python nmea_demo.py /dev/sttyUSB0 http://enfo.hu/gnss_demo/get.php
"""
import sys
import os
import re
import argparse
import logging

# check PYTHONPATH
if len([p for p in sys.path if 'pyapi' in p]) == 0:
    if os.path.isdir('../pyapi/'):
        sys.path.append('../pyapi/')
    else:
        print("pyapi not found")
        print("Add pyapi directory to the Python path or start your application from ulyxes/pyapps folder")
        sys.exit(1)

from localiface import LocalIface
from serialiface import SerialIface
from bluetoothiface import BluetoothIface
from nmeagnssunit import NmeaGnssUnit
from httpwriter import HttpWriter
from echowriter import EchoWriter
from csvwriter import CsvWriter
from gnss import Gnss

# topcon hiper II bluetooth: 00:07:80:57:3b:6e
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', type=str,
        help='interface e.g. COM1: /dev/ttyUSB0 of file name', default = '/dev/ttyUSB0')
    parser.add_argument('-s', '--speed', type=int,
        help='communication speed e.g. 9600', default = 9600)
    parser.add_argument('-o', '--output', type=str,
        help='output, default stdout')
    parser.add_argument('-d', '--debug', action="store_true",
        help='detailed log output to stdout')
    # get file from command line params
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    # NMEA input interface
    if re.search('^COM[0-9][0-9]?$', args.interface) or \
        re.search('^/dev/ttyUSB[0-9]$', args.interface) or \
        re.search('^/dev/ttyS[0-9]*', args.interface):
        # serial
        li = SerialIface('test', args.interface, args.speed)
    elif re.search('^([0-9a-fA-F]{2}:){5}[0-9A-f-F]{2}$', args.interface):
        # bluetooth
        li = BluetoothIface('test', args.interface, 1)
    elif os.path.exists(args.interface) and os.path.isfile(args.interface):
        # input from file
        li = LocalIface('test', args.interface)
    else:
        print('invalid interface given')
        sys.exit(1)

    if li.state != li.IF_OK:
        sys.exit(1)

    # output
    filt = ['id', 'latitude', 'longitude', 'altitude', 'datetime', 'quality',
            'nsat']
    if args.output is None:
        wrt = EchoWriter('', 'DEG', '.3f', '%Y-%m-%d %H:%M:%S', filt)
    elif re.search('^https?://', args.output):
        wrt = HttpWriter(angle='DEG', url=args.output, filt=filt)
    elif re.search('\.csv$', args.output):
        wrt = CsvWriter('', 'DEG', '.3f', '%Y-%m-%d %H:%M:%S', filt, args.output)
    else:
        print('invalid output given')
        sys.exit(2)

    # nmea data OK?
    if li.state != li.IF_OK:
        print("input file/device?")
        exit(1)

    # nmea processing unit
    mu = NmeaGnssUnit(['GNS', 'GGA', 'ZDA'])
    # instrument
    g = Gnss('test', mu, li, wrt)
    while g.measureIface.state == g.measureIface.IF_OK:
        g.Measure()
