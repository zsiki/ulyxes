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
from datetime import datetime
from angle import Angle
from measureunit import MeasureUnit

class NmeaGnssUnit(MeasureUnit):

    """ NMEA measure unit

            :param filt: NMEA sentence filter list e.g. ["GGA", "GNS"]
            :param name: name of nmea unit (str), default 'Nmea Gnss'
            :param typ: type of nmea unit (str), default None
    """
    # set item positions in NMEA messages
    MSGS_KEYS = {
        "GGA": {'datetime': 1, 'latitude': 2, 'ns': 3, 'longitude': 4, 'ew': 5,
                'quality': 6, 'nsat': 7, 'hdop': 8, 'altitude': 9,
                'alt_unit': 10, 'geoid': 11, 'geoid_unit': 12, 'age': 13,
                'ref': 14},
        "GNS": {'datetime': 1, 'latitude': 2, 'ns': 3, 'longitude': 4, 'ew': 5,
                'quality': 6, 'nsat': 7, 'hdop': 8, 'altitude': 9, 'geoid': 10,
                'age': 11, 'ref': 12},
        "ZDA": {'datetime': 1, 'day': 2, 'month': 3, 'year': 4, 'offset_h': 5,
                'offset_m': 6},
        "RMC": {'datetime': 1, 'quality': 2, 'latitude': 3, 'longitude': 4,
                'speed': 5, 'angle': 6, 'date': 7, 'magnetic': 8},
        "GLL": {'latitude': 1, 'ns': 2, 'longitude': 3, 'ew': 4,
                'datetime': 5, 'quality': 6}
    }
    SUPPORTED_MSGS = list(MSGS_KEYS.keys())

    def __init__(self, filt=None, name='Nmea Gnss', typ=None):
        """ constructor for nmea measure unit
        """
        # call super class init
        super(NmeaGnssUnit, self).__init__(name, typ)
        self.filt = self.SUPPORTED_MSGS  # default filter accept all
        if filt is not None:
            self.filt = [msg for msg in filt if msg in self.SUPPORTED_MSGS]
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

    @staticmethod
    def NmeaDateTime(msg):
        """ get date/time from ZDA message

            :param msg: NMEA ZDA sentence
            :returns: dete/time or None
        """
        d = None
        lst = re.split(r'[,\*]', msg)
        if len(lst) < 5:
            logging.error("Invalid ZDA message, few fields: %s", msg)
            return None
        try:
            day = int(lst[2])
            month = int(lst[3])
            year = int(lst[4])
            hour = int(lst[1][0:2])
            minute = int(lst[1][2:4])
            second = int(lst[1][4:6])
            ms = 0
            if len(lst[1]) > 6:
                ms = int(float(lst[1][6:]) * 1000)
            d = datetime(year, month, day, hour, minute, second, ms)
        except Exception:
            logging.error("Invalid date/time: %s", msg)
        return d

    def Nmea2Coo(self, msg):
        """ process GGA nmea message

            :param msg: NMEA GGA/GNS/RMC/GLL sentence
            :returns: dictionary of data
        """
        msg_type = msg[3:6]
        msg_keys = self.MSGS_KEYS[msg_type]
        lst = re.split(r'[,\*]', msg)
        if len(lst) < len(msg_keys):
            logging.error("Invalid message, few fields: %s", msg)
            return None
        res = {}
        try:
            if 'datetime' in msg_keys:
                if self.date_time is None:
                    d1 = datetime.utcnow() # UTC at server
                else:
                    d1 = self.date_time       # timestamp from ZDA
                # UTC time from sentence
                index = msg_keys['datetime']
                hour = int(lst[index][0:2])
                minute = int(lst[index][2:4])
                second = int(lst[index][4:6])
                ms = 0
                if len(lst[index]) > 6:
                    ms = int(float(lst[index][6:]) * 1000)
                d = datetime(d1.year, d1.month, d1.day, hour, minute, second, ms)
                # check day change
                if abs((d1 - d).total_seconds()) > 10:
                    logging.debug("day change %s - %s", d, d1)
                d = d1          # TODO time from GGA/GNS overwritten!
                res['datetime'] = d
            if 'latitude' in msg_keys:
                mul = 1 if lst[msg_keys['ns']] == 'N' else -1
                res['latitude'] = Angle(mul * float(lst[msg_keys['latitude']]), 'NMEA')
            if 'longitude' in msg_keys:
                mul = 1 if lst[msg_keys['ew']] == 'E' else -1
                res['longitude'] = Angle(mul * float(lst[msg_keys['longitude']]), 'NMEA')
            if 'quality' in msg_keys:
                res['quality'] = lst[msg_keys['quality']]
            if 'nsat' in msg_keys:
                res['nsat'] = int(lst[msg_keys['nsat']])
            if 'hdop' in msg_keys:
                res['hdop'] = float(lst[msg_keys['hdop']])
            if 'altitude' in msg_keys:
                res['altitude'] = float(lst[msg_keys['altitude']])
        except Exception as e:
            logging.error('Invalid message, invalid value: %s', msg)
            logging.error(e)
            self.date_time = None    # drop previous DZA time
            res = None
        self.date_time = None    # drop previous DZA time
        return res

    def Result(self, msgs, ans):
        """ process the answer from GNSS

            :param msgs: MNEA messages to get (list), None means to use filter
            :param ans: NMEA message from GNSS unit
            :returns: processed message or None if msg and ans do not match
        """
        if msgs is None:
            msgs = self.filt
        msg = ans[3:len(msgs[0])+3]
        if msg not in msgs:
            return None     # no process for this message
        # check checksum
        if not self.NmeaChecksum(ans):
            logging.error(' Checksum error')
            return None
        res = None
        if msg == 'ZDA':
            self.date_time = self.NmeaDateTime(ans)  # datetime
        elif msg in self.SUPPORTED_MSGS:
            res = self.Nmea2Coo(ans)     # position
        return res

    def MeasureMsg(self):
        """ NMEA sentence type for lat,lon

            :returns: accepted messages
        """
        return self.filt

if __name__ == '__main__':
    nmeaunit = NmeaGnssUnit(("GGA", "ZDA", "GNS"))
    ans = "$GPZDA,050306,29,10,2003,,*43"
    print(nmeaunit.Result(None, ans))
    #ans = "$GPGGA,183730,3907.356,N,12102.482,W,1,05,1.6,646.4,M,-24.1,M,,*75"
    ans = "$GNGGA,000501.00,4728.1158076,N,01904.0281549,E,4,12,0.57,124.585,M,39.322,M,1.0,0207*64"
    print(nmeaunit.Result(None, ans))
    ans = "$GNGNS,082456.00,4733.9695486,N,01900.4864959,E,RRNN,17,0.63,198.744,39.430,1.0,0207,V*35"
    print(nmeaunit.Result(None, ans))
