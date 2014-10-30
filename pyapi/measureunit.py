#!/usr/bin/env python
"""
.. module:: measureunit.py

   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltán <siki@agt.bme.hu>, Moka Dániel <mokbme@gmail.com>

"""

class MeasureUnit(object):
    """
        This class contains general functions for Measure Units.
    """
    def __init__(self, name = 'None', type = 'None'):
        self.name = name
        self.type = type

    def GetName(self):
        return self.name

    def GetType(self):
        return self.type

    def Result(self, msg, ans):
        return None

    def Move(self, hz, v, units='RAD', atr=0):
        pass

if __name__ == "__main__":
    a = MeasureUnit()
    print (a.GetName())
    print (a.GetType())
