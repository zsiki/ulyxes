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

class EchoWriter(Writer):
    """ Class to write observations to consol
    """

    def __init__(self, name = 'None', angle = 'GON', dist = '.3f', filt = None):
        """ Constructor

            :param name: name of writer (str)
            :param angle: angle unit to use (str)
            :param dist: distance and coordinate format (str)
            :param filt: list of allowed keys (list)
        """
        super(EchoWriter, self).__init__(name)
        self.angleFormat = angle
        self.distFormat = dist
        self.filt = filt

    def WriteData(self, data):
        """ Write observation data to consol

            :param data: dictionary with observation data
        """
        line = ""
        if data is None:
            logging.warning(" empty data not written")
            return
        for key, val in data.iteritems():
            if self.filt is None or key in self.filt:
                if type(val) is Angle:
                    sval = str(val.GetAngle(self.angleFormat))
                elif type(val) is float:
                    sval = ("{0:" + self.distFormat + "}").format(val)
                elif type(val) is int:
                    sval = str(val)
                else:
                    sval = val
                line += key + "=" + sval + ";"
        print (line + "\n")

if __name__ == "__main__":
    my = EchoWriter()
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    my.WriteData(data)

