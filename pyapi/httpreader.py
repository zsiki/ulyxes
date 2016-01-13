#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: csvreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

#import logging
import urllib
import json

from reader import Reader

# TODO extend float for all possible fields
FLOATS = ['east', 'north', 'elev']

class HttpReader(Reader):
    """ Class to read data from web in JSON format
        No filter implemented filter by point name and point type TODO

        :param name: name of reader (str), default None
        :param url: url to read from
        :param pids: point ids to query, list
        :param ptys: point types to query FIX/STA/MON list
    """

    def __init__(self, name = None, url = None, pids = None, ptys = None):
        """ Constructor
        """
        super(HttpReader, self).__init__(name)
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
            if key in FLOATS:
                row[key] = float(row[key])
        return row

    def GetNext(self):
        """ Get next line from url
        """
        if self.start:
            if len(self.res) > self.start:
                self.start += 1
                return self._process(self.res[self.start - 1])
            return None
        else:
            par = {}
            if not self.pids is None:
                par['pids'] = ','.join(self.pids)
            if not self.ptys is None:
                par['ptys'] = ','.join(self.ptys)
            self.res = json.loads(urllib.urlopen(self.url + urllib.urlencode(par)).read())
            self.start += 1
            return self._process(self.res[0])

if __name__ == "__main__":
    # read most recent coordinates of all monitoring points from server
    rd = HttpReader(url='http://localhost/monitoring/query.php', ptys='MON')
    while True:
        r = rd.GetNext()
        if r:
            print r
        else:
            break
