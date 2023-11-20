#!/usr/bin/env python
"""
.. module:: httpwriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import logging
try:
    from urllib.request import urlopen, Request # for python 3
    from urllib.parse import urlencode
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request        # for python 2
    from urllib2 import HTTPError
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
        super().__init__(name, angle, dist, dt, filt)
        self.url = url
        self.mode = mode

    def WriteData(self, data):
        """ Write observation data to server

            :param data: dictionary with observation data
            :returns: server answer or negative error code
        """
        par = {}
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return -1
        # add datetime and/or id
        data = self.ExtendData(data)
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                par[key] = self.StrVal(val)
        if self.mode == 'GET':
            try:
                res = urlopen(self.url + '?' + urlencode(par)).read()
                if len(res.strip()) == 0:
                    res = 0
                else:
                    res = int(res)
            except HTTPError as err:
                logging.error("http error %d %s ", err.code, err.msg)
                res = -err.code
            except URLError:
                logging.error("URL error")
                res = -2
        else:
            try:
                d = urlencode(par).encode('ascii')
                req = Request(self.url, d)
                res = urlopen(req).read()
                if len(res.strip()) == 0:
                    res = 0
                else:
                    res = int(res)
            except HTTPError as err:
                logging.error("http error %d %s ", err.code, err.msg)
                res = -err.code
            except URLError:
                logging.error("URL error")
                res = -2
        return res

if __name__ == "__main__":
    myfile = HttpWriter(mode='GET', url="http://localhos/get.php")
    dd = {'id': '111', 'east': 123, 'north': 543, 'datetime': '2023-11-20 17:00:03'}
    print(myfile.WriteData(dd))
