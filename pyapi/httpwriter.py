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

from angle import Angle
from writer import Writer
import logging
import urllib
import urllib2

class HttpWriter(Writer):
    """ Class to write observations to a web server (HTTP GET/POST)

            :param name: name of writer (str)
            :param url: url to server side script (str)
            :param mode: GET/POST
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
            :param filt: list of allowed keys (list)
    """

    def __init__(self, name = 'None', url = 'http://localhost/get.php', mode = 'GET',
        angle = 'GON', dist = '.3f', filt = None):
        """ Constructor
        """
        super(HttpWriter, self).__init__(name)
        self.url = url
        self.mode = mode
        self.angleFormat = angle
        self.distFormat = dist
        self.filt = filt

    def WriteData(self, data):
        """ Write observation data to server

            :param data: dictionary with observation data
        """
        line = ""
        par = {}
        if data is None:
            logging.warning(" empty data not written")
            return
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                if type(val) is Angle:
                    sval = str(val.GetAngle(self.angleFormat))
                elif type(val) is float:
                    sval = ("{0:" + self.distFormat + "}").format(val)
                elif type(val) is int:
                    sval = str(val)
                else:
                    sval = val
                if self.mode == 'GET':
                    line += key + "=" + sval + "&"
                else:
                    par[key] = sval
        if self.mode == 'GET':
            res = urllib.urlopen(self.url + '?' + line).read()
        else:
            d = urllib.urlencode(par)
            req = urllib2.Request(self.url, d)
            res = urllib2.urlopen(req).read()
        return res

if __name__ == "__main__":
    myfile = HttpWriter(mode='POST')
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    print (myfile.WriteData(data))
