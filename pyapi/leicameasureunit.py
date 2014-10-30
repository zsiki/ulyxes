#!/usr/bin/env python
"""
.. module:: leicameasureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>, Moka Daniel <mokadaniel@citromail.hu>

"""

from measureunit import *
from angle import *
import re

class LeicaMeasureUnit(MeasureUnit):
    """
        This class contains the Leica TCA1800/RTS1101 specific functions
    """
    def __init__(self, name = 'Leica generic', type = 'TPS'):
        # call super class init
        super(LeicaMeasureUnit, self).__init__(name, type)

    def Result(self, msgs, anss):
        """
        This function ....
        """
        msgList = re.split('\|', msgs)
        ansList = re.split('\|', anss)
        res = {}
        for msg, ans in zip(msgList, ansList):
            # get command id form message
            msgBufflist = re.split(':|,',msg)
            commandID = msgBufflist[1]
        # get error code from answer
            ansBufflist = re.split(':|,',ans)
            errCode = ansBufflist[3]
            if errCode != '0':
                # ??? TODO ?Logging?
                return {'errorCode': errCode}
            else:
                res['errorCode'] = 0
                #Measure()

                if commandID == '2108':
                    hz = Angle(float(ansBufflist[4]))
                    v = Angle(float(ansBufflist[5]))
                    dist = ansBufflist[6]
                    res['hz'] = hz.GetAngle('DMS')
                    res['v'] = v.GetAngle('DMS')
                    res['distance'] = dist
                #MeasureDistAng
                elif commandID == '17017':
                    hz = Angle(float(ansBufflist[4]))
                    v = Angle(float(ansBufflist[5]))
                    dist = ansBufflist[6]
                    res['hz'] =hz.GetAngle('DMS')
                    res['v'] =v.GetAngle('DMS')
                    res['distance'] = dist
                #GetATR()
                elif commandID == '9019':
                    atrStat = ansBufflist[4]
                    res['atrStatus'] = atrStat
                #GetLockStatus()
                elif commandID == '9021':
                    lockStat = ansBufflist[4]
                    res['lockStat'] = lockStat
                #GetAtmCorr()
                elif commandID == '2029':
                    res['lambda']= ansBufflist[4]
                    res['pressure'] = ansBufflist[5]
                    res['dryTemp'] = ansBufflist[6]
                    res['wetTemp'] = ansBufflist[7]
                #GetRefCorr()
                elif commandID == '2031':
                    res['status'] = ansBufflist[4]
                    res['earthRadius'] = ansBufflist[5]
                    res['refractiveScale'] = ansBufflist[6]
                #GetStation()
                elif commandID == '2009':
                    res['easting'] = ansBufflist[4]
                    res['northing'] = ansBufflist[5]
                    res['elevation'] = ansBufflist[6]
                # GetEDMMode()
                #PASTE the hashed(commented) part TO 1200 UNIT
                elif commandID == '2021':
                    res['edmMode'] = ansBufflist[4]
                    #edmModeMap={'0': 'IR Std', '1': 'IR Fast', '2': 'LO Std', '3': 'RL Std', '4': 'IR Trk', '6': 'RL Trk', '7': 'IR Avg', '8': 'LO Avg', '9': 'RL Avg'}
                #Coords()
                elif commandID == '2082':
                    res['y'] = ansBufflist[4]
                    res['x'] = ansBufflist[5]
                    res['z'] = ansBufflist[6]
                #GetAngles()
                elif commandID == '2003':
                    hz = Angle(float(ansBufflist[4]))
                    v = Angle(float(ansBufflist[5]))
                    res['hz'] = hz.GetAngle('DMS')
                    res['v'] = v.GetAngle('DMS')
        return res

    def SetATRMsg(self, atr):
        """
        Message function for set ATR status on/off
        
        :param atr: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        return '%%R1Q,9018:%d' % (atr)

    def GetATRMsg(self):
        """
        Message function for get ATR status
        :rtype: 0 or error code
          
        """
        return '%R1Q,9019:'

    def SetLockMsg(self, lock):
        """
        Message function for get Lock status on/off
        
        :param lock: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        return '%%R1Q,9020:%d' % (lock)

    def GetLockMsg(self):
        """
        Message function for get Lock status
       
        :rtype: 0 or error code
          
        """
        return '%R1Q,9021:'

    def SetAtmCorrMsg(self, valueOfLambda, pres, dry, wet):
        """
        Message function for set atmospheric correction settings
        
        :param valueOfLambda: Constant for the instrument not changeable, use GetAtmCorr to get value
        :param pres: pressure value
        :param dry: dry temperature
        :param wet: wet temperature
        :rtype: 0 or error code
          
        """
        return '%%R1Q,2028:%f,%f,%f,%f' % (valueOfLambda, pres, dry, wet)

    def GetAtmCorrMsg(self):
        """
        Message function for get atmospheric correction settings
        
        :rtype: atmospheric settings as a dictionary
          
        """
        return '%R1Q,2029:'

    def SetRefCorrMsg(self, status, earthRadius, refracticeScale):
        """
        Message function for set refraction correction settings
        
        :param status: 0/1 = off/on
        :param earthRadius: radius ot the Earth
        :param refracticeScale: refractice scale
        :rtype: 0 or error code
          
        """
        return '%%R1Q,2030:%d,%f,%f' % (status, earthRadius, refracticeScale)

    def GetRefCorrMsg(self):
        """
        Message function for get refraction correction setting
      
        :rtype: refraction correction as a dictionary
          
        """
        return '%R1Q,2031:'

    def SetStationMsg(self, e, n, z):
        """
        Message function for set station coordinates
        
        :param e: easting
        :param n: northing
        :param z: elevation
        :rtype: 0 or error code
          
        """
        return '%%R1Q,2010:%f,%f,%f' % (e, n, z)

    def GetStationMsg(self):
        """
        Message function for get station co-ordinates
        
        :rtype: list {{37 N} {38 E} {39 Z}}
          
        """
        return '%R1Q,2009:'

    def SetEDMModeMsg(self, mode):
        """
        Message function for set ATR status on/off
        
        :param atr: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        #2 = IR
        #5 = Rl
        return '%%R1Q,2020:%d' % (mode)

    def GetEDMModeMsg(self):
        """
        Message function for set ATR status on/off
        
        :param atr: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        return '%R1Q,2021:'

    def SetOriMsg(self, ori, units ='RAD'):
        """
        Message function for set ATR status on/off
        
        :param atr: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        ori_rad = Angle(ori, units).GetAngle('RAD')
        return '%%R1Q,2113:%f' % (ori_rad)

    def SetRCSMsg(self, rcs):
        """
        Message function for set ATR status on/off
        
        :param atr: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        return '%%R1Q,18009:%f' % (rcs)

    def MoveMsg(self, hz, v, units='RAD', atr=0):
        """
        Message function to rotate instrument to given direction
        
        :param hz: horizontal direction
        :param v: zenith angle
        :param units: units for angles, optional (default RAD)
        
        
        :rtype: 0 or error code   

        Example::

        >>> mu = LeicaMeasureUnit("TCA 1800")
        >>> iface = SerialInterface("rs-232", "COM4")
        >>> ts = TotalStation("Leica", mu, iface)
        >>> print (ts.Move())

        """
        
        hz_rad = ChangeAngle(hz,units,'RAD')
        v_rad = ChangeAngle(v,units,'RAD')
        # change angles to radian
        hz_rad = Angle(hz, units).GetAngle('RAD')
        v_rad = Angle(v, units).GetAngle('RAD')
        return '%%R1Q,9027:%f,%f,0,%d,0' % (hz_rad, v_rad, atr)

    def MeasureMsg(self, prg = 2, wait = 12000, incl = 0):
        """
        Message function for measuring distance
        
        :param prg: measure program 1/2/3/... = default/track/clear..., optional (default 1)
        :param wait: time in ms, optional (default 12000)
        :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
       
        :rtype: -  
        """
        return '%%R1Q,2008:%d,%d|%%R1Q,2108:%d,%d' % (prg, incl, wait, incl)

    def MeasureDistAngMsg(self):
        """
        Message function for

        """
        return '%R1Q,17017:2'

    def CoordsMsg (self, wait = 1000, incl = 0):
        """
        Message function for reading coordinates from instrument calculated from last distance measurement
        
        :param wait: wait-time in ms, optional (default 1000)
        :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
        :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
       
        :rtype: -  
        """
        return '%%R1Q,2082:%d,%d' % (wait, incl)

    def GetAnglesMsg(self):
        """
        Message function for reading angles from instrument

        """
        return '%R1Q,2003:0'

    def ClearDistanceMsg(self):
        """
        Message for clearing distance

        """
        return '%R1Q,2082:1000,1'

    def ChangeFaceMsg(self):
        """
        Message for changing the face of instrument

        """
        return '%R1Q,9028:'


