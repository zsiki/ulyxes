#!/usr/bin/env python
"""
.. module:: totalstation.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>

"""

from instrument import Instrument
from angle import Angle

class TotalStation(Instrument):
    """ Generic total station instrument
    """
    def __init__(self, name, measureUnit, measureInterf):
        """ Constructor

            :param name: name of instrument
            :param measureUnit: measure unit part of instrument 
            :param measureInterf: interface to measure unit
        """
        # call super class init
        super(TotalStation, self).__init__(name, measureUnit, measureInterf)

    def SetATR(self, atr):
        """ Set ATR on 

            :param atr: 0/1 ATR off/on
            :returns: processed answer from instrument
        """
        msg = self.measureUnit.SetATRMsg(atr)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetATR(self):
        """ Get ATR status of instrument

            :returns: 0/1 ATR off/on
        """
        msg = self.measureUnit.GetATRMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetLock(self, lock):
        """ Set lock on prism

            :param lock: 0/1 lock off/on
            :returns: processed answer from instrument
        """
        msg = self.measureUnit.SetLockMsg(lock)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetLock(self):
        """ Get lock status

            :returns: lock status of the instrument 0/1 on/off
        """
        msg = self.measureUnit.GetLockMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetAtmCorr(self,valueOfLambda, pres, dryTemp, wetTemp):
        """ Set atmospheric correction

            :param valueOfLambda: ????
            :param pres: air presure
            :param dryTemp: dry temperature
            :param wetTemp: wet temperature
        """
        msg = self.measureUnit.SetAtmCorrMsg(valueOfLambda, pres, dryTemp, wetTemp)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAtmCorr(self):
        """ Get atmospheric correction

            :returns: atmospheric corrections (dictionary)
        """
        msg = self.measureUnit.GetAtmCorrMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetRefCorr(self, status, earthRadius, refracticeScale):
        """ Set refraction correction

            :param status: ???
            :param earthRadius: radius of earth
            :param refracticeScale: ???
        """
        msg = self.measureUnit.SetRefCorrMsg(status, earthRadius, refracticeScale)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetRefCorr(self):
        """ Get refraction correction

            :returns: refraction correction (dictionary)
        """
        msg = self.measureUnit.GetRefCorrMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetStation(self, easting, northing, elevation):
        """ Set station coordinates

            :param easting: easting of station
            :param northing: northing of station
            :param elevation: elevation of station
            :returns: ???
        """
        msg = self.measureUnit.SetStationMsg(easting, northing, zenith)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def    GetStation(self):
        """ Get station coordinates

            :returns: station coordinates (dictionary)
        """
        msg = self.measureUnit.GetStationMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetEDMMode(self, mode):
        """ Set EDM mode

            :param mode: mode name/id as listed in measure unit
            :returns: ???
        """
        msg = self.measureUnit.SetEDMModeMsg(mode)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetEDMMode(self):
        """ Get EDM mode

            :returns: actual EDM mode
        """
        msg = self.measureUnit.GetEDMModeMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def SetOri(self, ori):
        """ Set orientation

            :param ori: bearing to direction (Angle)
            :returns: ???
        """
        clMsg = self.measureUnit.ClearDistanceMsg()  # TODO is it neccessary?
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

    def Move(self, hz, v, atr=0):
        """ Rotate instrument to a given direction

            :param hz: horizontal direction (Angle)
            :param v: zenith (Angle)
            :param atr: 0/1 ATR on/off
        """
        msg = self.measureUnit.MoveMsg(hz, v, atr)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Measure(self, prg='DEFAULT', incl=0):
        """ Measure distance

            :param prg: EDM program, DEFAULT use actual
            :param incl: inclination ...
            :returns: ???
        """
        if prg == 'DEFAULT':
            prg = GetEDMMode()['edmMode']
        msg = self.measureUnit.MeasureMsg(prg, incl)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetMeasure(self, wait = 12000, incl = 0):
        """ Get measured values

            :param wait: waiting time in ms
            :param inc: inclination ...
            :returns: observations in a dictionary
        """
        msg = self.measureUnit.GetMeasureMsg(wait, incl)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def MeasureDistAng(self):
        """ ???
        """
        msg = self.measureUnit.MeasureDistAngMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def Coords(self, wait = 1000, incl = 0):
        """ Read coordinates from instrument

            :param wait: waiting time ms
            :param incl: inclination
            :returns: coordinates in a dictionary
        """
        msg = self.measureUnit.CoordsMsg(wait, incl)
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def GetAngles(self):
        """ Get angles from instrument

            :returns: angles in a dictionary
        """
        msg = self.measureUnit.GetAnglesMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def ClearDistance(self):
        """ Clear measured distance on instrument
        """
        msg = self.measureUnit.ClearDistanceMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def ChangeFace(self):
        """ Change face

            :returns: ???
        """
        msg = self.measureUnit.ChangeFaceMsg()
        ans = self.measureInterf.Send(msg)
        return self.measureUnit.Result(msg, ans)

    def MoveRel(hz_rel, v_rel, atr=0):
        """ Rotate the instrument relative to actual direction

            :param hz_rel: relative horizontal rotation (Angle)
            :param v_rel: relative zenith rotation (Angle)
            :param atr: 0/1 atr on/off
        """
        #get the actual direction
        msg = self.measureUnit.GetAnglesMsg()
        ans = self.measureInterf.Send(msg)
        res = self.measureUnit.Result(msg, ans)
        return self.Move(res['hz'] + hz_rel, res['v'] + v_rel, atr)

if __name__ == "__main__":
    from leicameasureunit import *
    from serialinterface import *
    mu = LeicaMeasureUnit("TCA 1800")
    iface = SerialInterface("rs-232", "/dev/ttyUSB0")
    ts = TotalStation("Leica", mu, iface)
    print (ts.GetEDMMode())
    print (ts.GetATR())
    print (ts.SetATR(1))
    print (ts.GetATR())
    if ts.GetATR()['atrStatus'] == 0:
        ts.SetATR(1)
    print (ts.GetAngles())
    #ts.Measure()
    #print ts.GetMeasure()
    #print (ts.Move(Angle(0), Angle(90, 'DEG')))
    #print (ts.ChangeFace())
