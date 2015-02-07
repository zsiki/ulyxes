#!/usr/bin/env python
"""
.. module:: leicatca1800.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results. GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>

"""

from leicameasureunit import LeicaMeasureUnit

class LeicaTCA1800(LeicaMeasureUnit):
    """ This class contains the Leica TCA1800 robotic total station specific
        functions

            :param name: name of ts (str), default=TCA1800
            :param type: type od ts (str), default=TPS
    """

    def __init__(self, name = 'Leica TCA1800', typ = 'TPS'):
        """ Constructor to leica generic ts
        """
        # call super class init
        super(LeicaTCA1800, self).__init__(name, typ)

    @staticmethod
    def GetCapabilities():
        """ Get instrument specialities

            :returns: List of specialities
        """
        return ['ROBOT', 'ANGLE', 'EDM', 'ATR', 'LOCK', 'POSITION']

if __name__ == "__main__":
    print LeicaTCA1800.GetCapabilities()
    tca = LeicaTCA1800()
    print tca.GetCapabilities()
