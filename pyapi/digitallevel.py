#!/usr/bin/python
"""
.. module:: digitallevel.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokbme@gmail.com>
"""

from instrument import Instrument
from measureunit import MeasureUnit

class DigitalLevel(Instrument):
    """ Class to handle Leica DNA digital level
    """

    def __init__(self, name, measureUnit, measureInterf):
        """ Constructor to Leica DNA level

            :param name: name of digital lvel instrument
            :param measureUnit: reference to measure unit
            :param measureInterf: reference to measure interface
        """
        # call super class init
        super(DigitalLevel, self).__init__(name, measureUnit, measureInterf)

    def Measure(self):
        """ Start reading on staff
        """
        msg = self.measureUnit.MeasureMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetAutoOff(self, par):
        """ set automatic turning off to on/off

            :param par: 1/0 on/off
            :returns: empty dictionary
        """
        msg = self.measureUnit.SetAutoOffMsg(par)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAutoOff(self):
        """ Query auto off state

            :returns: auto off state
        """
        msg = self.measureUnit.GetAutoOffMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Temperature(self):
        """ Get temperature

            :returns: internal temperature
        """
        msg = self.measureUnit.TemperatureMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

if __name__ == "__main__":
    from leicadnaunit import LeicaDnaUnit
    from digitallevel import DigitalLevel
    from serialinterface import SerialInterface

    mu = LeicaDnaUnit()
    iface = SerialInterface('x', '/dev/ttyS0')
    dna = DigitalLevel('DNA03', mu, iface)
    dna.SetAutoOff(0)
    print (dna.GetAutoOff())
    print (dna.Temperature())
    print (dna.Measure())
