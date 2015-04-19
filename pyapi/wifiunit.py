#!/usr/bin/env python
"""
.. module:: wifiunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
        publish observation results.  GPL v2.0 license Copyright (C)
        2010-2015 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

from measureunit import MeasureUnit

class WifiUnit(MeasureUnit):
    """ Collect wifi information 

        :param name: name of nmea unit (str), default 'Nmea Gnss'
        :param typ: type of nmea unit (str), default None
        :param wlan: wifi interface, default wlan0
    """

    def __init__(self, name = 'wlan', typ = 'wifi', wlan = 'wlan0'):
        """ constructor for wifi measure unit
        """
        # call super class init
        super(WifiUnit, self).__init__(name, typ)
        self.wlan = wlan

    @staticmethod
    def GetCapabilities():
        """ Get instrument specific functions

            :returns: list of capabilities
        """
        return ['WLAN']
