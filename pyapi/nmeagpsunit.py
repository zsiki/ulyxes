#!/usr/bin/env python
"""
.. module:: nmeagpsunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>
"""

from measureunit import MeasureUnit

class NmeaGpsUnit(MeasureUnit):
    """ NMEA measure unit
    """
    def __init__(self, name = 'Nmea Gps', type = '-'):
        """ constructor for nmea measure unit

            :param name: name of nmea unit
            :param type: type of nmea unit
        """
        # call super class init
        super(NmeaGpsUnit, self).__init__(name, type)

    def Result(self, msg, ans):
        pass

    def MeasureMsg(self):
        return None

if __name__ == '__main__':
    main()
