#!/usr/bin/env python
"""
.. module:: csvwriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import logging
from angle import Angle
from filewriter import FileWriter

class CsvWriter(FileWriter):
    """ Class to write observations to csv file
            :param name: name of writer (str), default None
            :param angle: angle unit to use (str), default GON
            :param dist: distance and coordinate format (str), default .3f
            :param dt: date/time format (str), default ansi
            :param filt: list of keys to output (list), default None
            :param fname: name of text file to write to (str)
            :param mode: mode of file open (a or w) (str)
            :param sep: separator character in file (str)
            :param header: add header to file if true and mode is 'w'
    """

    def __init__(self, name='None', angle='GON', dist='.3f',
                 dt='%Y-%m-%d %H:%M:%S', filt=None,
                 fname=None, mode='a', sep=';', header=None):
        """ Constructor
        """
        if filt is None or len(filt) == 0:
            raise NameError('Filter is empty -- CSV writer')
        super().__init__(name, angle, dist, dt, filt, fname, mode)
        self.sep = sep
        if header and self.mode == 'w':
            try:
                self.fp.write(self.sep.join(self.filt) + "\n")
            except Exception:
                logging.error(" file write failed")


    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except Exception:
            pass

    def WriteData(self, data):
        """ Write observation data to csv file

            :param data: dictionary with observation data
            :returns: 0/-1/-2 OK/write error/empty not written
        """
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return -2
        # add datetime and/or id
        data = self.ExtendData(data)
        linelist = ['' for i in range(len(self.filt))]
        for key, val in data.items():
            if key in self.filt:
                index = self.filt.index(key)
                linelist[index] = self.StrVal(val)
        try:
            self.fp.write(self.sep.join(linelist) + "\n")
            self.fp.flush()
        except Exception:
            logging.error(" file write failed")
            return -1
        return 0

if __name__ == "__main__":
    myfile = CsvWriter(header=True)
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    myfile.WriteData(data)
