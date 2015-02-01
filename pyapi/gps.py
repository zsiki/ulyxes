#!/usr/bin/env python
"""
.. module:: gps.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>.
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>
"""
from instrument import Instrument

class GPS(Instrument):
    def __init__(self, name, measureUnit, measureInterf, writerUnit = None):
        """ constructor for gps

            :param name: name of gps instrument
            :param measureUnit: reference to measure unit
            :param measureInterf: reference to measure interface
        """
        super(GPS, self).__init__(name, measureUnit, measureInterf, writerUnit)

    def _process(self, msg):
        """ Get a line from measure unit and process answer

            :param msg: empty string, not used
            :returns: parsed answer (dictionary)
        """
        ans = self.measureInterf.GetLine()
        if self.measureInterf.state != self.measureInterf.IF_OK:
            return {'error': self.measureInterf.state}   # TODO logical???
        res = self.measureUnit.Result(msg, ans)
        if res is not None and len(res) > 0:
            self.writerUnit.WriteData(res)
        return res

    def Measure(self):
        """ Get position from nmea stream
        """
        ret = None
        while ret is None:
            if self.measureInterf.state != IF_OK:
                break
            ret = _process(ans)
        return ret


if __name__ == '__main__':
    pass
