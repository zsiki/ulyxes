#!/usr/bin/env python
"""
.. module:: instrument.py 
  :platform: Unix, Windows
  :synopsis: Ulyxes - an open source project to drive total stations and
      publish observation results.
      GPL v2.0 license
      Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>, Moka Daniel <mokadaniel@citromail.hu>

"""

import re

class Instrument(object):
    """
        Base class for different instruments
    """
    def __init__(self, name, measureUnit, measureInterf):
        self.name = name
        self.measureUnit = measureUnit
        self.measureInterf = measureInterf

    def GetInterface(self):
        """ Get the measure interface

            :returns: reference to interface
        """
        return self.measureInterf

    def GetMeasureUnit(self):
        """ Get the measure unit

            :returns: reference to measure unit
        """
        return self.measureUnit
    
    def GetName(self):
        """ Get the name of the Instrument
        
            :returns: instrument name
        """
        return self.name

if __name__ == "__main__":
    from interface import Interface
    from measureunit import MeasureUnit

    mu = MeasureUnit('Test', 'Proba')
    iface = Interface('interf')
    print mu.GetName()
    print mu.GetType()
    print iface.GetName()
    print iface.GetState()
    a = Instrument("test instrument", mu, iface)
