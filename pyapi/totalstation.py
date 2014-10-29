#!/usr/bin/env python
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

class TotalStation(Instrument):

    def __init__(self, name, measureUnit, measureInterf):
        # call super class init
        super(TotalStation, self).__init__(name, measureUnit, measureInterf)

    def Move(self, hz, v, units='RAD', atr=0):
        msg = self.measureUnit.MoveMsg(hz, v, units, atr)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

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

    def SetAtmCorr(self,valueOfLambda, pres, dry, wet):
        msg = self.measureUnit.SetAtmCorrMsg(valueOfLambda, pres, dry, wet)
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

    def SetStation(self, e, n, z):
        msg = self.measureUnit.SetStation(e, n, z)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetStation(self):
        msg = self.measureUnit.GetStation()
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

    def SetOri(self):
        msg = self.measureUnit.SetOriMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetRCS(self, rcs):
        msg = self.measureUnit.SetRCSMsg(rcs)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Measure(self, prg = 1, wait = 12000, incl = 0):
        msg = self.measureUnit.MeasureMsg(rcs)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

if __name__ == "__main__":
    from leicameasureunit import *
    from serialinterface import *
    mu = LeicaMeasureUnit("TCA 1800")
    iface = SerialInterface("rs-232", "COM4")
    ts = TotalStation("Leica", mu, iface)
    print ts.Move(0,0)
