#!/usr/bin/env python
"""
.. module:: csvwriter.py
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

class CSVWriter(FileWriter):
    """ Class to write observations to csv file

            :param name: name of writer (str)
            :param fname: name of text file to write to (str)
            :param mode: mode of file open (a or w) (str)
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
            :param filt: list of allowed keys (list)
            :param sep: separator character in file (str)
            :param header: add header to file if mode is 'w'
    """
    DEFAULT_FILTER = ['hz', 'v', 'dist']

    def __init__(self, name = 'None', fname = 'ulyxes.txt', mode = 'a',
        angle = 'DMS', dist = '.3f', filt = None, sep = ';', header = None):
        """ Constructor
        """
        super(CSVWriter, self).__init__(name, fname, mode, angle, dist, filt)
        if filt is None:
            self.filt = self.DEFAULT_FILTER
        self.sep = sep
        if header is not None and self.mode == 'w':
            try:
                self.fp.write(self.sep.join(self.filt) + "\n")
            except:
                logging.error(" file write failed")


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
        if data is None:
            logging.warning(" empty data not written")
            return
        linelist = ['' for i in range(len(self.filt))]
        for key, val in data.iteritems():
            if key in self.filt:
                if type(val) is Angle:
                    sval = val.GetAngle(self.angleFormat)
                elif type(val) is float:
                    sval = ("{0:" + self.distFormat + "}").format(val)
                elif type(val) is int:
                    sval = str(val)
                else:
                    sval = val
                index = self.filt.index(key)
                linelist[index] = sval
        try:
            self.fp.write(self.sep.join(linelist) + "\n")
        except:
            logging.error(" file write failed")

if __name__ == "__main__":
    myfile = CSVWriter(header=1)
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    myfile.WriteData(data)
