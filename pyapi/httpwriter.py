#!/usr/bin/env python
"""
.. module:: httpwriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

import logging
try:
    from urllib.request import urlopen, Request # for python 3
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request        # for python 2
#import urllib
#import urllib2
from angle import Angle
from writer import Writer

class HttpWriter(Writer):
    """ Class to write observations to a web server (HTTP GET/POST)

            :param name: name of writer (str)
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
            :param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
            :param url: url to server side script (str)
            :param mode: GET/POST
    """

    def __init__(self, name=None, angle='GON', dist='.3f',
                 dt='%Y-%m-%d %H:%M:%S', filt=None,
                 url='http://localhost/monitoring/get.php', mode='GET'):
        """ Constructor
        """
        super(HttpWriter, self).__init__(name, angle, dist, dt, filt)
        self.url = url
        self.mode = mode

    def WriteData(self, data):
        """ Write observation data to server

            :param data: dictionary with observation data
            :returns: server answer or None (if error)
        """
        par = {}
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return
        # add datetime and/or id
        data = self.ExtendData(data)
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                par[key] = self.StrVal(val)
        if self.mode == 'GET':
            #res = urlopen(self.url + '?' + urlencode(par)).read()
            print(self.url + '?' + urlencode(par))
            try:
                res = urlopen(self.url + '?' + urlencode(par))
                print(res)
                res = res.read()
                print(res)
            except:
                res = None
        else:
            try:
                d = urlencode(par)
                req = Request(self.url, d)
                print(req)
                res = urlopen(req).read()
                print(res)
            except:
                res = None
        return res

if __name__ == "__main__":
    #myfile = HttpWriter(mode='POST')
    myfile = HttpWriter(mode='GET')
    v = Angle(100.2345, 'GON')
    data = {'id': '1', 'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'distance': 123.6581}
    print(myfile.WriteData(data))
