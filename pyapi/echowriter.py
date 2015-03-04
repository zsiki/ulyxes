#!/usr/bin/env python
"""
.. module:: echowriter.py
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
import datetime

class EchoWriter(Writer):
    """ Class to write observations to consol

            :param name: name of writer (str)
            :param filt: list of allowed keys (list)
    """

    def __init__(self, name = 'None', angle = 'GON', dist = '.3f',
                 dt = '%Y-%m-%d %H:%M:%S', filt = None):
        """ Constructor
        """
        super(EchoWriter, self).__init__(name, angle, dist, dt, filt)

    def WriteData(self, data):
        """ Write observation data to consol

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
        print (line + "\n")

if __name__ == "__main__":
    my = EchoWriter()
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    my.WriteData(data)
