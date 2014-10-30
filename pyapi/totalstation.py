#!/usr/bin/env python
"""
.. module:: totalstation.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>, Moka Daniel <mokadaniel@citromail.hu>

"""

from instrument import *
from angle import *

class TotalStation(Instrument):
    """
        This class contains the general functions for total stations
    """
    def __init__(self, name, measureUnit, measureInterf):
        # call super class init
        super(TotalStation, self).__init__(name, measureUnit, measureInterf)

    def SetATR(self, atr):
        msg = self.measureUnit.SetATRMsg(atr)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetATR(self):
        msg = self.measureUnit.GetATRMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetLock(self,lock):
        msg = self.measureUnit.SetLockMsg(lock)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetLock(self):
        msg = self.measureUnit.GetLockMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetAtmCorr(self,valueOfLambda, pres, dryTemp, wetTemp):
        msg = self.measureUnit.SetAtmCorrMsg(valueOfLambda, pres, dryTemp, wetTemp)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAtmCorr(self):
        msg = self.measureUnit.GetAtmCorrMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetRefCorr(self, status, earthRadius, refracticeScale):
        msg = self.measureUnit.SetRefCorrMsg(status, earthRadius, refracticeScale)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetRefCorr(self):
        msg = self.measureUnit.GetRefCorrMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetStation(self, easting, northing, zenith):
        msg = self.measureUnit.SetStationMsg(easting, northing, zenith)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetStation(self):
        msg = self.measureUnit.GetStationMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetEDMMode(self, mode):
        msg = self.measureUnit.SetEDMModeMsg(mode)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetEDMMode(self):
        msg = self.measureUnit.GetEDMModeMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetOri(self, ori):
        clMsg = self.measureUnit.ClearDistanceMsg()
        ans = self.measureInterf.Send(clMsg)
        errorCode = self.measureUnit.Result(clMsg, ans)
        if errorCode['errorCode'] != 0:
            return errorCode
        msg = self.measureUnit.SetOriMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetRCS(self, rcs):
        msg = self.measureUnit.SetRCSMsg(rcs)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Move(self, hz, v, units='RAD', atr=0):
        msg = self.measureUnit.MoveMsg(hz, v, units, atr)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Measure(self, prg = 1, wait = 12000, incl = 0):
        msg = self.measureUnit.MeasureMsg(prg, wait, incl)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def MeasureDistAng(self):
        msg = self.measureUnit.MeasureDistAngMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Coords(self, wait = 1000, incl = 0):
        clMsg = self.measureUnit.ClearDistanceMsg()
        ans = self.measureInterf.Send(clMsg)
        errorCode = self.measureUnit.Result(clMsg, ans)
        if errorCode['errorCode'] != 0:
            return errorCode
        msg = self.measureUnit.CoordsMsg(wait, incl)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAngles(self):
        msg = self.measureUnit.GetAnglesMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def ClearDistance(self):
        msg = self.measureUnit.ClearDistanceMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def ChangeFace(self):
        msg = self.measureUnit.ChangeFaceMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def MoveRel(hz_rel, v_rel, units='RAD', atr=0):
        #get the actual direction
        msg = self.measureUnit.GetAnglesMsg()
        ans = self.measureInterf.Send(msg)
        res = self.measureUnit.Result(msg,ans)
        hz = Angle(res['hz'],units)
        return 0




if __name__ == "__main__":
    from leicameasureunit import *
    from serialinterface import *
    mu = LeicaMeasureUnit("TCA 1800")
    iface = SerialInterface("rs-232", "COM4")
    ts = TotalStation("Leica", mu, iface)
    print (ts.Move(0,0))
