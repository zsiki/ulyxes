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
PI2 = 2 * math.pi

def _deg2rad(angle):
    """ Convert DEG to RAD
    """
    return math.radians(angle)

def _gon2rad(angle):
    """ Convert GON to RAD
    """
    return angle / 200.0 * math.pi

def _dms2rad(dms):
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
        raise ValueError("Angle invalid argument", dms)
    return a

def _dm2rad(angle):
    """ Convert DDMM.nnnnnn NMEA angle to radian"
    """
    w = angle / 100.0
    d = int(w)
    return math.radians(d + (w - d) * 100.0 / 60.0)

def _pdeg2rad(angle):
    """ Convert dd.mmss to radian
    """
    d = math.floor(angle)
    angle = round((angle - d) * 100, 10)
    m = math.floor(angle)
    s = round((angle - m) * 100, 10)
    return math.radians(d + m / 60.0 + s / 3600.0)

def _sec2rad(angle):
    """ Convert seconds to radian
    """
    return angle / RO

def _mil2rad(angle):
    """ Convert mills to radian
    """
    return angle / 6400.0 * 2.0 * math.pi

def _rad2gon(value):
    """ Convert radian to GON
    """
    return value / math.pi * 200.0

def _rad2sec(value):
    """ Convert radian to seconds
    """
    return value * RO

def _rad2deg(value):
    """ Convert radian to decimal degrees
    """
    return math.degrees(value)

def _dms(value):
    """ Convert radian to DMS
    """
    secs = round(_rad2sec(value))
    mi, sec = divmod(secs, 60)
    deg, mi = divmod(mi, 60)
    deg = int(deg)
    return "%d-%02d-%02d" % (deg, mi, sec)

def _rad2dm(value):
    """ Convert radian to NMEA DDDMM.nnnnn
    """
    w = value / math.pi * 180.0
    d = int(w)
    return d * 100 + (w - d) * 60

def _rad2pdeg(value):
    """ Convert radian to pseudo DMS ddd.mmss
    """
    secs = round(_rad2sec(value))
    mi, sec = divmod(secs, 60)
    deg, mi = divmod(mi, 60)
    deg = int(deg)
    return deg + mi / 100.0 + sec / 10000.0

def _rad2mil(value):
    """ Convert radian to mills
    """
    return value / math.pi / 2.0 * 6400.0

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

:param value: angle value
:param unit: angle unit (available units RAD/DMS/DEG/GON/NMEA/PDEG/SEC/MIL)
    """

    # jump table to import from
    im = {'DMS': _dms2rad, 'DEG': _deg2rad,
        'GON': _gon2rad, 'NMEA': _dm2rad,
        'PDEG': _pdeg2rad, 'SEC': _sec2rad,
        'MIL': _mil2rad}
    # jump table for convert to
    ex = {'DMS': _dms, 'DEG': _rad2deg,
        'GON': _rad2gon, 'NMEA': _rad2dm,
        'PDEG': _rad2pdeg, 'SEC': _rad2sec,
        'MIL': _rad2mil}

    def __init__(self, value, unit='RAD'):
        """ Constructor for an angle instance.
        """
        self.value = None
        self.SetAngle(value, unit)

    def GetAngle(self, out='RAD'):
        """ Get angle value in different units

            :param out: output unit (str RAD/DMS/DEG/GON/NMEA/PDEG/SEC/MIL)
            :returns: value (float or string)
        """
        if out == 'RAD' or self.value is None:
            output = self.value  # no conversion
        elif out in self.ex:
            output = self.ex[out](self.value)  # call converter based on output format
        else:
            output = None  # unsupported output format
        return output

    def SetAngle(self, value, unit='RAD'):
        """ Set or change value of angle.

            :param value: new value for angle (str or float)
            :param unit: unit for the new value (str)
        """
        if unit == 'RAD' or value is None:
            self.value = value
        elif unit in self.im:
            self.value = self.im[unit](value)
        else:
            # unknown unit
            self.value = None
        # move angle to 0 - 2*PI interval
        if self.value is not None:
            while self.value >= PI2:
                self.value -= PI2
            while self.value < -PI2:
                self.value += PI2

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
        print (a1.GetAngle(u))
    b1 = Angle(1.1111, 'PDEG')
    print (b1.GetAngle("DMS"))
    c1 = a1 + b1
    print (c1.GetAngle("DMS"))
    print (c1)
    print ((a1-b1).GetAngle("DMS"))
