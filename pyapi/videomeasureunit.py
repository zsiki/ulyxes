#!/usr/bin/env python
"""
.. module:: videomeasureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""
from measureunit import MeasureUnit

class VideoMeasureUnit(MeasureUnit):
    """ Video device specific features.

            :param name: name of measure unit (str), default 'webcam'
            :param typ: type of measure unit (str), default 'video'
    """
    def __init__(self, name='webcam', typ='video'):
        """ Constructor
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
    print (mu.GetName())
