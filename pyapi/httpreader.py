#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: httpreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

#import logging
import json
try:
    from urllib.request import urlopen # for python 3
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen        # for python 2

from reader import Reader

class HttpReader(Reader):
    """ Class to read data from web in JSON format
        No filter implemented filter by point name and point type TODO

        :param name: name of reader (str), default None
        :param url: url to read from
        :param pids: point ids to query, list
        :param ptys: point types to query FIX/STA/MON list
    """

    FLOATS = ['east', 'north', 'elev', 'pc']

    def __init__(self, name=None, url=None, pids=None, ptys=None, \
                 filt=None):
        """ Constructor
        """
        super(HttpReader, self).__init__(name, filt)
        self.state = self.RD_OK
        if url[-1] != '?':
            url += '?'
        self.url = url
        self.pids = pids
        self.ptys = ptys
        self.start = 0  # start position in returned JSON array
        self.res = []

    def __del__(self):
        """ Destructor
        """
        pass

    @staticmethod
    def _process(row):
        """ convert numeric fields from text to float

            :param row: dict of data
        """
        for key in row:
            if key in HttpReader.FLOATS:
                row[key] = float(row[key])
        return row

    def GetNext(self):
        """ Get next line from url

            :returns: dictionay with values
        """
        if self.start:
            if len(self.res) > self.start:
                self.start += 1
                return self._process(self.res[self.start - 1])
            return None
        else:
            par = {}
            if self.pids is not None:
                par['pids'] = ','.join(self.pids)
            if self.ptys is not None:
                par['ptys'] = ','.join(self.ptys)
            self.res = json.loads(urlopen(self.url + urlencode(par)).read())
            if len(self.res):
                self.start += 1
                return self._process(self.res[0])
            return None

if __name__ == "__main__":
    # read most recent coordinates of all 3D monitoring points from server
    rd = HttpReader(url='http://localhost/monitoring/query.php', ptys='MON', \
                    filt=['id', 'east', 'north', 'elev'])
    print(rd.Load())
