#!/usr/bin/python
# -*- coding: UTF-8 -*-

import math
import re

RO = 180 * 60 * 60 / math.pi

class Angle(object):
    """ Angle class, value stored in radian internally
    """
    def __init__(self, value, unit='RAD'):
        """ Constructor for an angle instance.

            :param value: angle value
            :param unit: angle unit (available units RAD/DMS/DEG/GON/NMEA/PDEG/SEC/MIL)
        """
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
        try:
            a = math.radians(angle)
        except (ValueError, TypeError):
            a = None
        return a

    def _gon2rad(self, angle):
        try:
            a = angle / 200.0 * math.pi
        except (ValueError, TypeError):
            a = None
        return a

    def _dms2rad(self, dms):
        if re.search('^[0-9]{1,3}(-[0-9]{1,2}){0,2}$', dms):
            items = [float(item) for item in dms.split('-')]
            div = 1.0
            a = 0.0
            for i, val in enumerate(items):
                a += val / div
                div *= 60.0
            a = math.radians(a)
        else:
            a = None
        return a

    def _dm2rad(self, angle):
        "DDMM.nnnnnn NMEA angle to radian"
        try:
            w = angle / 100.0
            d = int(w)
            a = math.radians(d + (w - d) * 100.0 / 60.0)
        except (ValueError, TypeError):
            a = None
        return a

    def _pdeg2rad(self, angle):
        "dd.mmss to radian"
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
        try:
            a = angle / RO
        except (ValueError, TypeError):
            a = None
        return a

    def _mil2rad(self, angle):
        try:
            a = angle / 6400.0 * 2.0 * math.pi
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2gon(self):
        try:
            a = self.value / math.pi * 200.0
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2sec(self):
        try:
            a = self.value * RO
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2deg(self):
        try:
            a = math.degrees(self.value)
        except (ValueError, TypeError):
            a = None
        return a

    def _dms(self):
        try:
            secs = round(self._rad2sec())
            min, sec = divmod(secs, 60)
            deg, min = divmod(min, 60)
            deg = int(deg)
            dms = "%d-%02d-%02d" % (deg, min, sec)
        except (ValueError, TypeError):
            dms = None
        return dms

    def _rad2dm(self):
        try:
            w = self.value / math.pi * 180.0
            d = int(w)
            a = d * 100 + (w - d) * 60
        except (ValueError, TypeError):
            a = None
        return a

    def _rad2pdeg(self):
        try:
            secs = round(self._rad2sec())
            min, sec = divmod(secs, 60)
            deg, min = divmod(min, 60)
            deg = int(deg)
            pdeg = deg + min / 100.0 + sec / 10000.0
        except (ValueError, TypeError):
            pdeg = None
        return pdeg

    def _rad2mil(self):
        try:
            w = self.value / math.pi / 2.0 * 6400.0
        except (ValueError, TypeError):
            w = None
        return w

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


if __name__ == "__main__":
    a = Angle("152-23-45", "DMS")
    for unit in ['RAD', 'DMS', 'GON', 'NMEA', 'DEG', 'PDEG', 'MIL']:
        print a.GetAngle(unit)
    b = Angle(1.1111, 'PDEG')
    print b.GetAngle("DMS")
    c = a + b
    print c.GetAngle("DMS")
    print (a-b).GetAngle("DMS")
