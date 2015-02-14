#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: gnss.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>
"""
from instrument import Instrument

class Gnss(Instrument):
    """ GNSS receiver sending NMEA messages

            :param name: name of gnss instrument
            :param measureUnit: reference to measure unit
            :param measureIface: reference to measure interface
    """
    def __init__(self, name, measureUnit, measureIface, writerUnit = None):
        """ constructor for gnss
        """
        super(Gnss, self).__init__(name, measureUnit, measureIface, writerUnit)

    def _process(self, msg):
        """ Get a line from measure unit and process answer

            :param msg: empty string, not used
            :returns: parsed answer (dictionary)
        """
        ans = self.measureIface.GetLine()
        if self.measureIface.state != self.measureIface.IF_OK:
            return ''
        res = self.measureUnit.Result(msg, ans)
        if self.writerUnit is not None and res is not None and len(res) > 0:
            self.writerUnit.WriteData(res)
        return res

    def Measure(self):
        """ Get position from nmea stream
        """
        ret = None
        while ret is None:
            if self.measureIface.state != self.measureIface.IF_OK:
                break
            msg = self.measureUnit.MeasureMsg()
            ret = self._process(msg)
        return ret


if __name__ == '__main__':
    #from echowriter import EchoWriter
    #from serialiface import SerialIface
    from httpwriter import HttpWriter
    from localiface import LocalIface
    from nmeagnssunit import NmeaGnssUnit
    #import logging
    #iface = SerialIface("", "COM5")
    iface = LocalIface('test', '/home/siki/meresfeldolgozas/nmea1.txt')
    mu = NmeaGnssUnit()
    wrt = HttpWriter(url='http://localhost/get.php', angle='DEG')
    g = Gnss('', mu, iface, wrt)
    #logging.getLogger().setLevel(logging.DEBUG)
    for i in range(10):
        g.Measure()
