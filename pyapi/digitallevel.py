#!/usr/bin/python
"""
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""

from instrument import *
from measureunit import *

class DigitalLevel(Instrument):

    def __init__(self, name, measureUnit, measureInterf):
        # call super class init
        super(DigitalLevel, self).__init__(name, measureUnit, measureInterf)

    def Measure(self):
        msg = self.measureUnit.MeasureMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetAutoOff(self, par):
        msg = self.measureUnit.SetAutoOffMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAutoOff(self):
        msg = self.measureUnit.SetAutoOnMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)
