#!/usr/bin/env python
"""
.. module:: nmeagnssunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
        publish observation results.  GPL v2.0 license Copyright (C)
        2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>,
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

    @staticmethod
    def NmeaChecksum(msg):
        """ NMEA message checksum

            :param msg: NMEA message
            :returns: True/False
        """
        data, cksum = msg.split('*')
        cksum1 = 0
        for s in data[1:]:
            cksum1 ^= ord(s)
        if cksum.lower() != hex(cksum1).lower()[-2:]:
            return False
        return True

    def Result(self, msgs, ans):
        """ process the answer from GNSS

            :param msg: MNEA messages to get (list)
            :param ans: NMEA message from GNSS unit
            :returns: processed message or None if msg and ans do not match
        """
        res = {}
        msg = ans[3:len(msgs[0])+3]
        if msg not in msgs:
            return None     # no process
        # check checksum
        if not self.NmeaChecksum(ans):
            logging.error(' Checksum error')
            return None
        anslist = ans.split(',')
        if msg == 'GGA':
            if int(anslist[6]) == 0:
                return None     # no position
            try:
                hour = int(anslist[1][0:2])
                minute = int(anslist[1][2:4])
                second = int(anslist[1][4:6])
                ms = 0
                if len(anslist[1]) > 6:
                    ms = int(float(anslist[1][6:]) * 1000)
                if self.date_time is None:
                    d = datetime.utcnow()   # UTC time
                else:
                    # date from DZA
                    d = datetime(self.date_time.year, self.date_time.month,
                                 self.date_time.day, hour, minute, second, ms)
                res['datetime'] = d
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
        elif msg == 'ZDA':
            anslist = re.split(r'[,\*]', ans)
            try:
                day = int(anslist[2])
                month = int(anslist[3])
                year = int(anslist[4])
                self.date_time = date(year, month, day)
            except Exception as e:
                logging.error(" invalid nmea sentence: %", ans)
            return None # no output
        return res

    @staticmethod
    def MeasureMsg():
        """ NMEA sentence type for lat,lon

            :returns: GGA
        """
        return "GGA"

if __name__ == '__main__':
    nmeaunit = NmeaGnssUnit()
    ans = "$GPZDA,050306,29,10,2003,,*43"
    print(nmeaunit.Result(("GGA", "ZDA"), ans))
    ans = "$GPGGA,183730,3907.356,N,12102.482,W,1,05,1.6,646.4,M,-24.1,M,,*75"
    print(nmeaunit.Result(("GGA", "ZDA"), ans))
