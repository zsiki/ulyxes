#!/usr/bin/env python
"""
.. module:: geowriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from angle import Angle
from filewriter import FileWriter
import logging

class GeoWriter(FileWriter):
    """ Class to write observations to csv file
            :param name: name of writer (str), default None
            :param angle: angle unit to use (str), default GON
            :param dist: distance and coordinate format (str), default .3f
            :param dt: date/time format (str), default ansi
            :param filt: list of keys to output (list), default None (use all)
            :param fname: name of text file to write to (str)
            :param mode: mode of file open (a or w) (str)
    """

    # ulyxes to GeoEasy code translator
    codes = { 'station': 2, 'ih': 3, 'id': 5, 'th': 6,
        'hz': 7, 'v': 8, 'distance': 9, 'hd': 11, 'faces': 112,
        'datetime': 4}
    def __init__(self, name = 'None', angle = 'DMS', dist = '.3f',
                dt = '%Y-%m-%d %H:%M:%S', filt = None,
                fname = None, mode = 'a'):
        """ Constructor
        """
        super(GeoWriter, self).__init__(name, angle, dist, dt, filt, fname, mode)

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def WriteData(self, data):
        """ Write observation data to csv file

            :param data: dictionary with observation data
        """
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return
        # add datetime and/or id
        data = self.ExtendData(data)
        # remove point id if station given
        if 'station' in data and 'id' in data:
            del data['id']
        line = ''
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                line = line + '{' + str(self.codes[key]) + ' ' + \
                    self.StrVal(val) + '} '
        try:
            self.fp.write(line + "\n")
            self.fp.flush()
        except:
            logging.error(" file write failed")

if __name__ == "__main__":
    myfile = GeoWriter()
    data = {'station': 111, 'ih': 1.234}
    myfile.WriteData(data)
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'distance': 123.6581}
    myfile.WriteData(data)
