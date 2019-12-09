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
from datetime import datetime, date
from angle import Angle
from measureunit import MeasureUnit

class NmeaGnssUnit(MeasureUnit):
    """ NMEA measure unit

            :param name: name of nmea unit (str), default 'Nmea Gnss'
            :param typ: type of nmea unit (str), default None
    """
    def __init__(self, name='Nmea Gnss', typ=None):
        """ constructor for nmea measure unit
        """
        # call super class init
        super(NmeaGnssUnit, self).__init__(name, typ)
        self.date_time = None

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
        if ans[3:len(msg)+3] != msg:
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
        if msg == 'GGA':
            # no fix
            if int(anslist[6]) == 0:
                return None
            try:
                hour = int(anslist[1][0:2])
                minute = int(anslist[1][2:4])
                second = int(anslist[1][4:6])
                if len(anslist[1]) > 6:
                    ms = int(float(anslist[1][6:]) * 1000)
                else:
                    ms = 0
                d = date.today()
                res['datetime'] = datetime(d.year, d.month, d.day, hour, minute, second, ms)
                mul = 1 if anslist[3] == 'N' else -1
                res['latitude'] = Angle(mul * float(anslist[2]), 'NMEA')
                mul = 1 if anslist[5] == 'E' else -1
                res['longitude'] = Angle(mul * float(anslist[4]), 'NMEA')
                res['quality'] = int(anslist[6])
                res['nsat'] = int(anslist[7])
                res['altitude'] = float(anslist[9])
                res['hdop'] = float(anslist[8])
            except:
                logging.error(" invalid nmea sentence: " + ans)
                return None
        return res

    @staticmethod
    def MeasureMsg():
        """ NMEA sentence type for lat,lon

            :returns: GGA
        """
        return "GGA"

if __name__ == '__main__':
    ans = "$GPGGA,183730,3907.356,N,12102.482,W,1,05,1.6,646.4,M,-24.1,M,,*75"
    #ans = "$GPZDA,050306,29,10,2003,,*43"
    nmeaunit = NmeaGnssUnit()
    print (nmeaunit.Result("GGA", ans))
