#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
.. module:: nmea_demo.py
  :platform: Unix, Windows

.. moduleauthor:: dr. Zoltan Siki <siki@agt.bme.hu>

GNSS demo collects data from the NMEA GNSS receiver or reads data from file,
sends data to a remote url to store/process them.

Usage: 

* python nmea_demo.py COM1
* python nmea_demo.py /dev/sttyUSB0 
* python nmea_demo.py COM1 http://enfo.hu/gnss_demo/get.php
* python nmea_demo.py /dev/sttyUSB0 http://enfo.hu/gnss_demo/get.php
"""
import sys
import os

sys.path.append('../pyapi')

if __name__ == "__main__":
    # get file from command line params
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    else:
        fn = 'test.log'
    if len(sys.argv) > 2:
        web = sys.argv[2]
    else:
        web = 'http://enfo.hu/gnss_demo/get.php'
    # file or on-line?
    if os.path.exists(fn) and os.path.isfile(fn):
        # input from file
        from localiface import LocalIface
        li = LocalIface('test', fn)
    else:
        # input from gnss receiver
        from serialiface import SerialIface
        li = SerialIface('test', fn)

    from nmeagnssunit import NmeaGnssUnit
    from httpwriter import HttpWriter
    from gnss import Gnss

    # nmea data OK?
    if li.state != li.IF_OK:
        print("input file/device?")
        exit(1)

    # nmea processing unit
    mu = NmeaGnssUnit()
    # processed data to web
    #wrt = HttpWriter(angle='DEG', url='http://localhost/gnss/get.php',
    #    filt=['longitude', 'latitude', 'altitude', 'datetime'])
    wrt = HttpWriter(angle='DEG', url='http://enfo.hu/gnss_demo/get.php',
        filt=['longitude', 'latitude', 'altitude', 'datetime'])
    # instrument
    g = Gnss('test', mu, li, wrt)
    while g.measureIface.state == g.measureIface.IF_OK:
        g.Measure()
