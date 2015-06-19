#!/usr/bin/env python
"""
.. module:: wificollector

:platform: Unix, Windows
:synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2015 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>
"""

import wifi
from instrument import Instrument

class WifiCollector(Instrument):
    """ Wifi collector collects information about available wifi networks
        This modul depends on https://github.com/rockymeza/wifi

            :param name: name of instrument
            :param measureUnit: measure unit part of instrument 
            :param measureIface: interface to measure unit, default None
            :param writerUnit: store data, default None
    """

    def __init__(self, name, measureUnit, measureIface = None, writerUnit = None):
        """ Constructor
        """
        # call super class init
        super(WifiCollector, self).__init__(name, measureUnit, measureIface, writerUnit)

    def GetWifis(self):
        """ Get all available wifis

            :returns: list of available wifis
        """
        wlist = wifi.Cell.all(self.measureUnit.wlan)
        res = []
        for w in wlist:
            r = {'ssid': w.ssid, 'address': w.address, 
                'quality': eval(w.quality + '.0'), 'signal': w.signal}
            if len(r):
                if self.writerUnit is not None:
                    self.writerUnit.WriteData(r) 
                res.append(r)
        return res

if __name__ == '__main__':
    from wifiunit import WifiUnit
    from csvwriter import CsvWriter

    wu = WifiUnit()
    wr = CsvWriter(fname = 'wifitest.csv', mode = 'w',
        filt = ['ssid', 'address', 'quality', 'signal', 'datetime'])
    wc = WifiCollector('wc', wu, None, wr)
    while 1:
        wc.GetWifis()
