#!/usr/bin/env python
"""
.. module:: filewriter.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from angle import Angle
from echowriter import EchoWriter
import logging

class FileWriter(EchoWriter):
    """ Class to write observations to file

            :param name: name of writer (str)
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
			:param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
            :param fname: name of text file to write to (str)
            :param mode: mode of file open (a or w) (str)
    """

    def __init__(self, name = 'None', angle = 'GON', dist = '.3f',
                dt = '%Y-%m-%d %H:%M:%S', filt = None, fname = 'ulyxes.txt',
                mode = 'a'):
        """ Constructor
        """
        super(FileWriter, self).__init__(name, angle, dist, dt, filt)
        self.fname = fname
        self.mode = mode
        self.fp = None
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
        if data is None or self.DropData(data):
            logging.warning(" empty or inappropiate data not written")
            return
        # add datetime and/or id
        data = self.ExtendData(data)
        for key, val in data.items():
            if self.filt is None or key in self.filt:
                line += key + "=" + self.StrVal(val) + ";"
        try:
            self.fp.write(line + "\n")
        except:
            logging.error(" file write failed")

if __name__ == "__main__":
    myfile = FileWriter()
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    myfile.WriteData(data)

