#!/usr/bin/env python
"""
    Leica TCA1800/RTS1200 specific functions
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""

from measureunit import *
from angle import *

class LeicaMeasureUnit(MeasureUnit):
    def __init__(self, name = 'Leica generic', type = 'TPS'):
        # call super class init
        super(LeicaMeasureUnit, self).__init__(name, type)

    def Result(self, msg, ans):
        # get command id form message
# TODO re.split!!!
	id = int(msg.split(',')[1].split(':')[0])
	# get error code from answer
	err = int(ans.split(':')[-1].split(',')[0])
        if err != 0:
            # ??? TODO
            return err
        else:
            # TODO
            pass
        return 0

    def MoveMsg(self, hz, v, units='RAD', atr=0):
        # change angles to radian
        hz_rad = Angle(hz,units).GetAngle('RAD')
        v_rad = Angle(v,units).GetAngle('RAD')
        return '%%R1Q,9027:%f,%f,0,%d,0' % (hz_rad, v_rad, atr)

    def SetATRMsg(self, atr):
        return '%R1Q,9018:%d' % (atr)

    def GetATRMsg(self):
        return '%R1Q,9019:'

    def SetLockMsg(self, lock):
        return '%R1Q,9020:%d' % (lock)

    def GetLockMsg(self):
        return '%R1Q,9021:'

# TODO folytatni Msg a nevbe + % formattalas
    def SetAtmCorr(self, valueOfLambda, pres, dry, wet):
        return 'R1Q,2028:{},{},{},{}'.format(valueOfLambda, pres, dry, wet)

    def getAtmCorr(self):
        return '%R1Q,2029:'

    def setRefCorr(self, status, earthRadius, refracticeScale):
        return '%R1Q,2030:{},{},{}'.format(status, earthRadius, refracticeScale)

    def getRefCorr(self):
        return '%R1Q,2031:'

    def setStation(self, e, n, z):
        return '%R1Q,2010:{},{},{}'.format(e, n, z)

    def getStation(self):
        return '%R1Q,2009:'

    def setEDMMode(self, mode):
        return '%R1Q,2020:{}'.format(mode)

    def getEDMMode(self):
        return '%R1Q,2021:'

    def setOri(self):
        #todo
        pass

    def setRCS(self, rcs):
        return '%R1Q,18009:{}'.format(rcs)

    def measure(self, prg = 1, wait = 12000, incl = 0):
        pass
