#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
.. module:: instrument.py 
  :platform: Unix, Windows
  :synopsis: Ulyxes - an open source project to drive total stations and
      publish observation results.
      GPL v2.0 license
      Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>

"""

class Instrument(object):
    """ Base class for different instruments

            :param name: name of instrument (str)
            :param measureUnit: measure unit of the instrument (MeasureUnit)
            :param MeasureIface: interface to physical intrument (Iface)
            :param writerUnit: unit to save observed data (Writer), optional
    """
    def __init__(self, name, measureUnit, measureIface, writerUnit = None):
        """ constructor
        """
        self.name = name
        self.measureUnit = measureUnit
        self.measureIface = measureIface
        self.writerUnit = writerUnit

    def GetIface(self):
        """ Get the measure interface

            :returns: reference to interface
        """
        return self.measureIface

    def GetMeasureUnit(self):
        """ Get the measure unit

            :returns: reference to measure unit
        """
        return self.measureUnit
 
    def GetWriterUnit(self):
        """ Get the writer unit

            :returns: reference to writer unit
        """
        return self.writerUnit
    
    def GetName(self):
        """ Get the name of the Instrument
        
            :returns: instrument name
        """
        return self.name

    def _process(self, msg):
        """ Send message to measure unit and process answer

            :param msg: message to send
            :returns: parsed answer (dictionary)
        """
        ans = self.measureIface.Send(msg)
        if self.measureIface.state != self.measureIface.IF_OK:
            return {'error': self.measureIface.state}  # TODO logical???
        res = self.measureUnit.Result(msg, ans)
        if self.writerUnit is not None and len(res) > 0:
            self.writerUnit.WriteData(res)
        return res

if __name__ == "__main__":
    from iface import Iface
    from measureunit import MeasureUnit
    from writer import Writer

    mu = MeasureUnit('Test', 'Proba')
    iface = Iface('iface')
    wrt = Writer()
    print mu.GetName()
    print mu.GetType()
    print iface.GetName()
    print iface.GetState()
    a = Instrument("test instrument", mu, iface, wrt)
