#!/usr/bin/env python
"""
.. module:: nmeagnssunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
        publish observation results.  GPL v2.0 license Copyright (C)
        2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>
"""

import re
import logging
from angle import Angle
from measureunit import MeasureUnit

class NmeaGnssUnit(MeasureUnit):
    """ NMEA measure unit

            :param name: name of nmea unit (str), default 'Nmea Gnss'
            :param type: type of nmea unit (str), default None
    """
    def __init__(self, name = 'Nmea Gnss', typ = None):
        """ constructor for nmea measure unit
        """
        # call super class init
        super(NmeaGnssUnit, self).__init__(name, typ)

    @staticmethod
    def GetCapabilities():
        """ Get instrument specific functions

            :returns: list of capabilities
        """
        return ['POSITION']

    def Result(self, msg, ans):
        """ process the answer from GNSS

            :param msg: MNEA message to get
            :param ans: NMEA message from GNSS unit
            :returns: processed message or None if msg and ans do not match
        """
        res = {}
        if ans[1:len(msg)+1] != msg:
            return None
        # check checksum 
        data, cksum = re.split('\*', ans)
        cksum1 = 0
        for s in data[1:]:
            cksum1 ^= ord(s)
        if ('0x' + cksum).lower() != hex(cksum1).lower():
            logging.error(' Checksum error')
            return None
        anslist = ans.split(',')
        if msg == 'GPGGA':
            # no fix
            if anslist[4] == 0:
                return None
            res['latitude'] = Angle(float(anslist[2]), 'NMEA')
            res['longitude'] = Angle(float(anslist[4]), 'NMEA')
            res['hdop'] = float(anslist[8])
            res['altitude'] = float(anslist[9])
        return res

    def MeasureMsg(self):
        """ NMEA sentence type for lat,lon

            :returns: GPGGA
        """
        return "GPGGA"

if __name__ == '__main__':
    ans = "$GPGGA,183730,3907.356,N,12102.482,W,1,05,1.6,646.4,M,-24.1,M,,*75"
    nmeaunit = NmeaGnssUnit()
    print (nmeaunit.Result("GPGGA", ans))
