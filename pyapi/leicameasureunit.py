#!/usr/bin/env python
"""
.. module:: leicameasureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results. GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>

"""

from measureunit import MeasureUnit
from angle import Angle
import re
import logging

class LeicaMeasureUnit(MeasureUnit):
    """ This class contains the Leica robotic total station specific functions
        common to all leica robot TS
    """
    # Constants for message codes
    codes = {
        'SETATR': 9018,
        'GETATR': 9019,
        'SETLOCK': 9020,
        'GETLOCK': 9021,
        'SETATMCORR': 2028,
        'GETATMCORR': 2029,
        'SETREFCORR': 2030,
        'GETREFCORR': 2031,
        'GETSTN': 2009,
        'SETSTN': 2010,
        'SETEDMMODE': 2020,
        'GETEDMMODE': 2021,
        'SETORI': 2113,
        'MOVE': 9027,
        'MEASURE': 2008,
        'GETMEASURE': 2108,
        'MEASUREANGDIST': 17017,
        'COORDS': 2082,
        'GETANGLES': 2003,
        'CHANGEFACE': 9028,
        'CLEARDIST': 2082,
        'SETSEARCHAREA': 9043,
        'POWERSEARCH': 9052,
        'SEARCHNEXT': 9051,
        'SETREDLASER': 1004
    }

    # Constants for EMD modes
    edmMode = {'STANDARD': 0, 'PRECISE': 1, 'FAST': 2, 'TRACKING': 3, 
        'AVERAGING': 4, 'FASTTRACKING': 5}

    def __init__(self, name = 'Leica generic', typ = 'TPS'):
        """ Constructor to leica generic ts

            :param name: name of ts
            :param type: type od ts
        """
        # call super class init
        super(LeicaMeasureUnit, self).__init__(name, typ)

    @staticmethod
    def GetCapabilities():
        """ Get instrument specialities

            :returns: empty list, do not use generic instrument
        """
        return []

    def Result(self, msgs, anss):
        """ Parse answer from message

            :param msgs: messages sent to instrument
            :param anss: aswers got from instrument
            :returns: dictionary
        """
        msgList = re.split('\|', msgs)
        ansList = re.split('\|', anss)
        res = {}
        for msg, ans in zip(msgList, ansList):
            # get command id form message
            msgBufflist = re.split(':|,', msg)
            commandID = int(msgBufflist[1])
            # get error code from answer
            ansBufflist = re.split(':|,', ans)
            try:
                errCode = int(ansBufflist[3])
            except:
                errCode = -1   # invalid answer
            if errCode != 0:
                logging.error(" error from instument: %d", errCode)
                return {'errorCode': errCode}
            if commandID == self.codes['GETMEASURE']:
                res['hz'] = Angle(float(ansBufflist[4]))
                res['v'] = Angle(float(ansBufflist[5]))
                res['distance'] = float(ansBufflist[6])
            # MeasureDistAng
            elif commandID == self.codes['MEASUREANGDIST']:
                res['hz'] = Angle(float(ansBufflist[4]))
                res['v'] = Angle(float(ansBufflist[5]))
                res['distance'] = float(ansBufflist[6])
            elif commandID == self.codes['GETATR']:
                res['atrStatus'] = int(ansBufflist[4])
            #GetLockStatus()
            elif commandID == self.codes['GETLOCK']:
                res['lockStat'] = int(ansBufflist[4])
            #GetAtmCorr()
            elif commandID == self.codes['GETATMCORR']:
                res['lambda'] = ansBufflist[4]
                res['pressure'] = float(ansBufflist[5])
                res['dryTemp'] = float(ansBufflist[6])
                res['wetTemp'] = float(ansBufflist[7])
            #GetRefCorr()
            elif commandID == self.codes['GETREFCORR']:
                res['status'] = ansBufflist[4]
                res['earthRadius'] = float(ansBufflist[5])
                res['refractiveScale'] = float(ansBufflist[6])
            elif commandID == self.codes['GETSTN']:
                res['easting'] = float(ansBufflist[4])
                res['northing'] = float(ansBufflist[5])
                res['elevation'] = float(ansBufflist[6])
            elif commandID == self.codes['GETEDMMODE']:
                res['edmMode'] = int(ansBufflist[4])
            #Coords()
            elif commandID == self.codes['COORDS']:
                res['y'] = float(ansBufflist[4])
                res['x'] = float(ansBufflist[5])
                res['z'] = float(ansBufflist[6])
            #GetAngles()
            elif commandID == self.codes['GETANGLES']:
                res['hz'] = Angle(float(ansBufflist[4]))
                res['v'] = Angle(float(ansBufflist[5]))
                res['crossincline'] = Angle(float(ansBufflist[8]))
                res['lengthincline'] = Angle(float(ansBufflist[9]))
            # Set search area
            elif commandID == self.codes['SETSEARCHAREA']:
                pass
            # PowerSearch
            elif commandID == self.codes['POWERSEARCH']:
                pass
        return res

    def SetATRMsg(self, atr):
        """ Set ATR status on/off
        
        :param atr: 0/1 = off/on
        :return: set atr message string
          
        """
        return '%R1Q,{0:d}:{1:d}'.format(self.codes['SETATR'], atr)

    def GetATRMsg(self):
        """ Get ATR status

        :returns: get atr message
          
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETATR'])

    def SetLockMsg(self, lock):
        """
        Message function for get Lock status on/off
        
        :param lock: 0/1 = off/on
        :rtype: 0 or error code
          
        """
        return '%R1Q,{0:d}:{1:d}'.format(self.codes['SETLOCK'], lock)

    def GetLockMsg(self):
        """
        Message function for get Lock status
       
        :rtype: 0 or error code
          
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETLOCK'])

    def SetAtmCorrMsg(self, valueOfLambda, pres, dry, wet):
        """
        Message function for set atmospheric correction settings
        
        :param valueOfLambda: Constant for the instrument not changeable, use GetAtmCorr to get value
        :param pres: pressure value
        :param dry: dry temperature
        :param wet: wet temperature
        :rtype: 0 or error code
          
        """
        return '%R1Q,{0:d}:{1:f},{2:f},{3:f},{4:f}'.format( \
            self.codes['SETATMCORR'], valueOfLambda, pres, dry, wet)

    def GetAtmCorrMsg(self):
        """
        Message function for get atmospheric correction settings
        
        :rtype: atmospheric settings as a dictionary
          
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETATMCORR'])

    def SetRefCorrMsg(self, status, earthRadius, refracticeScale):
        """
        Message function for set refraction correction settings
        
        :param status: 0/1 = off/on
        :param earthRadius: radius ot the Earth
        :param refracticeScale: refractice scale
        :rtype: 0 or error code
          
        """
        return '%R1Q,{0:d}:{1:d},{2:f},{3:f}'.format(self.codes['SETREFCORR'], \
            status, earthRadius, refracticeScale)

    def GetRefCorrMsg(self):
        """
        Message function for get refraction correction setting
      
        :rtype: refraction correction as a dictionary
          
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETREFCORR'])

    def SetStationMsg(self, e, n, z):
        """
        Message function for set station coordinates
        
        :param e: easting
        :param n: northing
        :param z: elevation
        :rtype: 0 or error code
          
        """
        return '%R1Q,{0:d}:{1:f},{2:f},{3:f}'.format(self.codes['SETSTN'], \
            e, n, z)

    def GetStationMsg(self):
        """
        Message function for get station co-ordinates
        
        :rtype: list {{37 N} {38 E} {39 Z}}
          
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETSTN'])

    def SetEDMModeMsg(self, mode):
        """ Set EDM mode
        
        :param mode: string name 
        :returns: set edm mode message
        """
        if type(mode) is str:
            imode = self.edmMode[mode]
        else:
            imode = mode
        return '%R1Q,{0:d}:{1:d}'.format(self.codes['SETEDMMODE'], imode)

    def GetEDMModeMsg(self):
        """ Get EDM mode
        
            :returns: get edm mode message
        """
        return '%R1Q,{0:d}:'.format(self.codes['GETEDMMODE'])

    def SetOriMsg(self, ori):
        """ Set orientation angle
        
        :param ori: bearing of direction (Angle)
        :rtype: 0 or error code
          
        """
        ori_rad = ori.GetAngle('RAD')
        return '%R1Q,{0:d}:{1:f}'.format(self.codes['SETORI'], ori_rad)

    # TODO remove from generic
    def SetRCSMsg(self, rcs):
        """ Set remote control
        
        :param rcs: 0/1 = off/on
        :returns: set remote control message
          
        """
        return '%%R1Q,18009:%f' % (rcs)

    def MoveMsg(self, hz, v, atr=0):
        """ Rotate instrument to direction with ATR or without ATR
        
            :param hz: horizontal direction (Angle)
            :param v: zenith angle (Angle)
            :param atr: 0/1 atr off/on, default off
            :returns: rotate message

        """
        # change angles to radian
        hz_rad = hz.GetAngle('RAD')
        v_rad = v.GetAngle('RAD')
        return '%R1Q,{0:d}:{1:f},{2:f},0,{3:d},0'.format(self.codes['MOVE'], \
            hz_rad, v_rad, atr)

    def MeasureMsg(self, prg = 1, incl = 0):
        """ Measure distance
        
            :param prg: measure program 1/2/3/... = default/track/clear..., optional (default 1, mode set before)
            :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
       
            :returns: measure message
        """
        return '%R1Q,{0:d}:{1:d},{2:d}'.format(self.codes['MEASURE'], prg, incl)
        
    def GetMeasureMsg(self, wait = 12000, incl = 0):
        """ Get measured distance

            :param wait: time in ms, optional (default 12000)
            :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
            :returns: get simple measurement message
        """
        return '%R1Q,{0:d}:{1:d},{2:d}'.format(self.codes['GETMEASURE'], \
            wait, incl)

    def MeasureDistAngMsg(self, prg):
        """ Measure angles and distance

            :param prg: EDM program
            :returns: measure angle distance message

        """
        if type(prg) is str:
            prg = self.edmMode[prg]
        return '%R1Q,{0:d}:{1:d}'.format(self.codes['MEASUREANGDIST'], prg)

    def CoordsMsg (self, wait = 1000, incl = 0):
        """ Get coordinates
        
            :param wait: wait-time in ms, optional (default 1000)
            :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
            :returns: get coordinates message
        """
        return '%R1Q,{0:d}:{1:d},{2:d}'.format(self.codes['COORDS'], \
            wait, incl)

    def GetAnglesMsg(self):
        """ Get angles

                :returns: get angles message
        """
        return '%R1Q,{0:d}:0'.format(self.codes['GETANGLES'])

    def ClearDistanceMsg(self):
        """ Clearing distance

                :returns: clear distance message

        """
        return self.MeasureMsg(self, 3)

    def ChangeFaceMsg(self):
        """ Change face

            :returns: change face message
        """
        return '%R1Q,{0:d}:'.format(self.codes['CHANGEFACE'])
