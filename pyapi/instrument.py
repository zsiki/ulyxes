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
    Bence Turak <bence.turak@gmail.com>


codes handles by descendent classes:

- atrStatus: 0/1 ATR on/off, totalstation
- crossincline: angle from vertical, totalstation
- distance: measured distance, totalstation
- dryTemp: dry temperature, met sensor
- earthRadius: radius of Earth, totalstation
- east: coordinate, totalstation, GPS
- edmMode: distance measurement mode, totalstation
- elev: elevation, totalstation, GPS
- errorCode: error code from sensor, any instrument
- hz: horizontal angle, totalstation
- hzRange: horizontal search range, totalstation
- ih: instrument height, totalstation
- instrName: name of instrument, any
- instrNo: product number, any
- intTemp: internal temperature of instrument, totalstation, level
- lambda: ..., totalstation
- lengthincline: angle from vertical, totalstation
- lockStat: lock status, totalstation
- north: coordinate, totalstation, GPS
- pc: prism constant, totalstation
- pressure: air pressure, met sensor
- pt: prism type, totalstation
- refractiveScale: ..., totalstation
- status: ...,...
- v: zenith angle, totalstation
- vRange: vertical search range, totalstation
- wetTemp: wet temperature, met sensor
"""
import sys
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

    def _process(self, msg, pic = None):
        """ Send message to measure unit and process answer

            :param msg: message to send
            :param pic: when using a camera you have tive give writable binary file
            :returns: parsed answer (dictionary)
        """
        ans = self.measureIface.Send(msg)
        if self.measureIface.state != self.measureIface.IF_OK:
            return {}
        res = self.measureUnit.Result(msg, ans)

        if self.writerUnit is not None and res is not None and len(res) > 0:
            self.writerUnit.WriteData(res)
        try:
            if res['binsize'] and res['binsize'] > 0:
                res = self.measureIface.GetLine(res['binsize'])
                if pic != None:
                    file.write(res)
                    res['pic'] = pic
        except:
            pass
        return res

if __name__ == "__main__":
    from iface import Iface
    from measureunit import MeasureUnit
    from writer import Writer

    mu = MeasureUnit('Test', 'Proba')
    iface = Iface('iface')
    wrt = Writer()
    print (mu.GetName())
    print (mu.GetType())
    print (iface.GetName())
    print (iface.GetState())
    a = Instrument("test instrument", mu, iface, wrt)
