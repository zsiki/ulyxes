#!/usr/bin/python
"""
.. module:: digitallevel.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C) 2010-
       Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>, Daniel Moka <mokbme@gmail.com>
"""

from instrument import Instrument

class DigitalLevel(Instrument):
    """ Class to handle Leica DNA digital level

            :param name: name of digital lvel instrument
            :param measureUnit: reference to measure unit
            :param measureIface: reference to measure interface
            :param writerUnit: store data
    """

    #def __init__(self, name, measureUnit, measureIface, writerUnit=None):
    #    """ Constructor to Leica DNA level
    #    """
    #    # call super class init
    #    super().__init__(name, measureUnit, measureIface, writerUnit)

    def Measure(self):
        """ Start reading on staff
        """
        msg = self.measureUnit.MeasureMsg()
        return self._process(msg)

    def SetAutoOff(self, par):
        """ set automatic turning off to on/off

            :param par: 1/0 on/off
            :returns: empty dictionary
        """
        msg = self.measureUnit.SetAutoOffMsg(par)
        return self._process(msg)

    def GetAutoOff(self):
        """ Query auto off state

            :returns: auto off state
        """
        msg = self.measureUnit.GetAutoOffMsg()
        return self._process(msg)

    def Temperature(self):
        """ Get temperature

            :returns: internal temperature
        """
        msg = self.measureUnit.TemperatureMsg()
        return self._process(msg)

if __name__ == "__main__":
    from leicadnaunit import LeicaDnaUnit
    from serialiface import SerialIface
    from csvwriter import CsvWriter

    mu = LeicaDnaUnit()
    iface = SerialIface('x', '/dev/ttyUSB0')
    wrt = CsvWriter(angle='DMS', dist='.5f',
                    filt=['id', 'distance', 'staff', 'datetime'],
                    fname='stdout', mode='a', sep=';')
    dna = DigitalLevel('DNA03', mu, iface, wrt)
    dna.SetAutoOff(0)
    #print (dna.GetAutoOff())
    print (dna.Temperature())
    for i in range(10):
        dna.Measure()
