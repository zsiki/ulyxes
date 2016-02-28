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
from filewriter import FileWriter
import logging
import datetime

class EchoWriter(FileWriter):
    """ Class to write observations to consol

            :param name: name of writer (str)
            :param angle: angle unit to use (str), default GON
            :param dist: distance and coordinate format (str), default 3 decimals
            :param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
    """

    def __init__(self, name = 'None', angle = 'GON', dist = '.3f',
                 dt = '%Y-%m-%d %H:%M:%S', filt = None):
        """ Constructor
        """
        super(EchoWriter, self).__init__(name, angle, dist, dt, filt, None, 'w')

if __name__ == "__main__":
    my = EchoWriter()
    data = {'hz': Angle(0.12345), 'v': Angle(100.2365, 'GON'), 'dist': 123.6581}
    my.WriteData(data)
