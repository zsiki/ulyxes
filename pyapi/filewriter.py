#!/usr/bin/env python
"""
.. module:: filewriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>
"""

from angle import Angle
from writer import Writer
import logging

class FileWriter(Writer):
    """ Class to write observations to file
    """

    def __init__(self, name = 'None', fname = 'ulyxes.txt', mode = 'a', angle = 'DMS', dist = '.3f', filt = None):
        """ Constructor

            :param name: name of writer (str)
            :param fname: name of text file to write to (str)
            :param mode: mode of file open (a or w) (str)
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
            :param filt: list of allowed keys (list)
        """
        super(FileWriter, self).__init__(name)
        self.fname = fname
        self.mode = mode
        self.angleFormat = angle
        self.distFormat = dist
        self.filt = filt
        self.state = self.WR_OK
        try:
            self.fp = open(fname, mode)
        except:
            self.state = self.WR_OPEN
            logging.error(" cannot open file %s", self.fname)

    def __del__(self):
        """ Destructor
        """
        try:
            self.fp.close()
        except:
            pass

    def WriteData(self, data):
        """ Write observation data to file

            :param data: dictionary with observation data
        """
        line = ""
        if data is None:
            logging.warning(" empty data not written")
            return
        for key, val in data.iteritems():
            if self.filt is None or key in selt.filt:
                if type(val) is Angle:
                    sval = val.GetAngle(self.angleFormat)
                elif type(val) is float:
                    sval = ("{0:" + self.distFormat + "}").format(val)
                elif type(val) is int:
                    sval = str(val)
                else:
                    sval = val
                line += key + "=" + sval + ";"
        try:
            self.fp.write(line + "\n")
        except:
            logging.error(" file write failed")

if __name__ == "__main__":
   myfile = FileWriter()
   data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
   myfile.WriteData(data)

