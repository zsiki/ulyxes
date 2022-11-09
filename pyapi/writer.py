#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: writer.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import datetime
from angle import Angle

class Writer():
    """ Base class for different writers (virtual)

            :param name: name of writer (str), default None
            :param angle: angle unit to use (str), default GON
            :param dist: distance and coordinate format (str), default .3f
            :param dt: date/time format (str), default ansi
            :param filt: list of keys to output (list), default None
    """
    WR_OK = 0
    WR_OPEN = -1
    WR_WRITE = -2

    def __init__(self, name=None, angle='GON', dist='.3f', \
                 dt='%Y-%m-%d %H:%M:%S', filt=None):
        """ Constructor
        """
        self.name = name
        self.angleFormat = angle
        self.distFormat = dist
        self.filt = filt
        self.id = 0  # serial number for records written
        self.dtFormat = dt
        self.state = self.WR_OK

    def GetName(self):
        """ Get the name of the interface being used.

            :returns: name of writer
        """
        return self.name

    def GetState(self):
        """ Get the state of the interface being used.

            :returns: state of writer
        """
        return self.state

    def ClearState(self):
        """ Clear the state of the writer being used.
        """
        self.state = self.WR_OK

    def StrVal(self, val):
        """ Get string representation of value

            :param val: value to convert to string
            :returns: value in string format
        """
        if isinstance(val, Angle):
            sval = str(val.GetAngle(self.angleFormat))
        elif isinstance(val, float):
            sval = ("{0:" + self.distFormat + "}").format(val)
        elif isinstance(val, datetime.datetime):
            sval = val.strftime(self.dtFormat)
        else:
            sval = str(val)
        return sval

    def DropData(self, data):
        """ Decide if data will be output or dropped

            :param data: data to output
            :returns: True if no index in filter is present
        """
        if self.filt is None or sum([1 for i in self.filt if i in data]) > 0:
            return False
        return True

    def ExtendData(self, data):
        """ Add datetime and id to data if neccessary

            :param data: data to extend (dict)
            :returns: extended data (dict)
        """
        # add datetime if not set
        if 'datetime' not in data:
            data['datetime'] = datetime.datetime.now()
        # add record number if not set
        if 'id' not in data:
            data['id'] = self.id
            self.id += 1
        return data
