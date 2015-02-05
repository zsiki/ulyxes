#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
.. module:: angle.py 
  :platform: Unix, Windows
  :synopsis: Ulyxes - an open source project to drive total stations and
      publish observation results.
      GPL v2.0 license
      Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Zoltan Siki <siki@agt.bme.hu>
"""

import math
import re

RO = 180 * 60 * 60 / math.pi

class Angle(object):
    """ Angle class, value stored in radian internally. Angle units supported:

* RAD  radians (e.g. 1.54678432)
* DMS sexagesimal (Degree-Minit-Second, e.g. 123-54-24)
* DEG decimal degree (e.g. 25.87659)
* GON gradian whole circle is 400g (e.g. 387.7857)
* NMEA ddmm.mmmm used in NMEA sentences (e.g. 47.338765)
* PDEG pseudo sexagesimal (e.g. 156.2745 = 156-27-45)
* SEC sexagesimal seconds
* MIL mills the whole circle is 6400 mills

Operators supported:

* \+ add two angles (e.g. c = Angle(180, 'DEG') + Angle('12-34-56', 'DMS'))
* \- substract two angles (e.g. d = Angle(180, 'DEG') - Angle('12-34-56', 'DMS'))
* += increment angle (e.g. c += Angle(1, 'GON'))
* -= decrement angle (e.g. d -= Angle(1, 'GON'))
* str() convert angle to GON string, used in print
    """
    def __init__(self, value, unit='RAD'):
        """ Constructor for an angle instance.

            :param value: angle value
            :param unit: angle unit (available units RAD/DMS/DEG/GON/NMEA/PDEG/SEC/MIL)
        """
        self.value = None
        self.SetAngle(value, unit)

    def GetAngle(self, out='RAD'):
        """ Get angle value in different units

            :param out: output unit (str RAD/DMS/DEG/GON/NMEA/PDEG/SEC/MIL)
            :returns: value (float or string)
        """
        if self.value is None:
            output = None
        elif out == 'RAD':
            output = self.value
        elif out == 'DMS':
            output = self._dms()
        elif out == 'DEG':
            output = self._rad2deg()
        elif out == 'GON':
            output = self._rad2gon()
        elif out == 'NMEA':
            output = self._rad2dm()
        elif out == 'PDEG':
            # pseudo decimal DMS ddd.mmss
            output = self._rad2pdeg()
        elif out == 'SEC':
            output = self._rad2sec()
        elif out == 'MIL':
            output = self._rad2mil()
        else:
            output = None
        return output

    def SetAngle(self, value, unit='RAD'):
        """ Set or change value of angle.

            :param value: new value for angle (str or float)
            :param unit: unit for the new value (str)
        """
        if unit == 'RAD' or value is None:
            self.value = value
        elif unit == 'DMS':
            self.value = self._dms2rad(value)
        elif unit == 'DEG':
            self.value = self._deg2rad(value)
        elif unit == 'GON':
            self.value = self._gon2rad(value)
        elif unit == 'NMEA':
            self.value = self._dm2rad(value)
        elif unit == 'PDEG':
            self.value = self._pdeg2rad(value)
        elif unit == 'SEC':
            self.value = self._sec2rad(value)
        elif unit == 'MIL':
            self.value = self._mil2rad(value)
        else:
            # unknown unit
            self.value = None
        # move angle to 0 - 2*PI interval
        if self.value is not None:
            while self.value >= 2.0 * math.pi:
                self.value -= 2.0 * math.pi
            while self.value < 0.0:
                self.value += 2.0 * math.pi

    def _deg2rad(self, angle):
        """ Convert DEG to RAD
        """
        try:
            a = math.radians(angle)
        except (ValueError, TypeError):
            a = None
        return a

    def _gon2rad(self, angle):
        """ Convert GON to RAD
        """
        try:
            a = angle / 200.0 * math.pi
        except (ValueError, TypeError):
            a = None
        return a

    def _dms2rad(self, dms):
        """ Convert DMS to RAD
        """
        if re.search('^[0-9]{1,3}(-[0-9]{1,2}){0,2}$', dms):
            items = [float(item) for item in dms.split('-')]
            div = 1.0
            a = 0.0
            for val in items:
                a += val / div
                div *= 60.0
            a = math.radians(a)
        else:
            a = None
        return a

    def _dm2rad(self, angle):
        """ Convert DDMM.nnnnnn NMEA angle to radian"
        """
        try:
            w = angle / 100.0
            d = int(w)
            a = math.radians(d + (w - d) * 100.0 / 60.0)
        except (ValueError, TypeError):
            a = None
        return a

    def _pdeg2rad(self, angle):
        """ Convert dd.mmss to radian
        """
        try:
            d = math.floor(angle)
            angle = round((angle - d) * 100, 10)
            m = math.floor(angle)
            s = round((angle - m) * 100, 10)
            a = math.radians(d + m / 60.0 + s / 3600.0)
        except (ValueError, TypeError):
            a = None
        return a

    def _sec2rad(self, angle):
        """ Convert seconds to radian
        """
        try:
            a = angle / RO
        except (ValueError, TypeError):
            a = None
        return a

    def _mil2rad(self, angle):
        """ Convert mills to radian
        """
        try:
            a = angle / 6400.0 * 2.0 * math.pi
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2gon(self):
        """ Convert radian to GON
        """
        try:
            a = self.value / math.pi * 200.0
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2sec(self):
        """ Convert radian to seconds
        """
        try:
            a = self.value * RO
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2deg(self):
        """ Convert radian to decimal degrees
        """
        try:
            a = math.degrees(self.value)
        except (ValueError, TypeError):
            a = None
        return a

    def _dms(self):
        """ Convert radian to DMS
        """
        try:
            secs = round(self._rad2sec())
            mi, sec = divmod(secs, 60)
            deg, mi = divmod(mi, 60)
            deg = int(deg)
            dms = "%d-%02d-%02d" % (deg, mi, sec)
        except (ValueError, TypeError):
            dms = None
        return dms

    def _rad2dm(self):
        """ Convert radian to NMEA DDDMM.nnnnn
        """
        try:
            w = self.value / math.pi * 180.0
            d = int(w)
            a = d * 100 + (w - d) * 60
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2pdeg(self):
        """ Convert radian to pseudo DMS ddd.mmss
        """
        try:
            secs = round(self._rad2sec())
            mi, sec = divmod(secs, 60)
            deg, mi = divmod(mi, 60)
            deg = int(deg)
            pdeg = deg + mi / 100.0 + sec / 10000.0
        except (ValueError, TypeError):
            pdeg = None
        return pdeg

    def _rad2mil(self):
        """ Convert radian to mills
        """
        try:
            w = self.value / math.pi / 2.0 * 6400.0
        except (ValueError, TypeError):
            w = None
        return w

    def __str__(self):
        """ GON string representation of angle

            :returns: GON string
        """
        return "{0:.4f}".format(self.GetAngle('GON'))

    def __add__(self, a):
        """ add angles

            :param a: Angle to add
            :returns: sum of the two angles (Angle)
        """
        return Angle(self.value + a.GetAngle('RAD'), 'RAD')

    def __iadd__(self, a):
        """ add an agle to current

            :param a: Angle to add
        """
        self.value += a.GetAngle('RAD')
        return self

    def __sub__(self, a):
        """ substract angles

            :param a: Angle to substract
            :returns: difference of the two angles (Angle)
        """
        return Angle(self.value - a.GetAngle('RAD'), 'RAD')

    def __isub__(self, a):
        """ substract an agle from current

            :param a: Angle to substract
        """
        self.value -= a.GetAngle('RAD')
        return self

if __name__ == "__main__":
    a1 = Angle("152-23-45", "DMS")
    for u in ['RAD', 'DMS', 'GON', 'NMEA', 'DEG', 'PDEG', 'MIL']:
        print a1.GetAngle(u)
    b1 = Angle(1.1111, 'PDEG')
    print b1.GetAngle("DMS")
    c1 = a1 + b1
    print c1.GetAngle("DMS")
    print c1
    print (a1-b1).GetAngle("DMS")
