#!/usr/bin/env python
"""
.. module:: videomeasureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>.
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""
from measureunit import MeasureUnit

class VideoMeasureUnit(MeasureUnit):
    """ Video device specific features.
    """
    def __init__(self, name = 'webcam', typ = 'video'):
        """ Constructor

            :param name: name of measure unit
            :param typ: type of measure unit
            :param source: id of device or file name
        """
        super(VideoMeasureUnit, self).__init__(name, typ)

    @staticmethod
    def GetCapabilities():
        """ Get instrument specialities

            :returns: list of capabilities
        """
        return ['IMAGE']

if __name__ == "__main__":
    mu = VideoMeasureUnit()
    print mu.GetName()
