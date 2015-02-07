#!/usr/bin/env python
"""
.. module:: trimble5500.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results. GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""

from measureunit import MeasureUnit
from angle import Angle
import re

class Trimble5500(MeasureUnit):
    """ This class contains the Trimble 5500 robotic total station specific
        functions

            :param name: name of ts (str), default 'Trimble 5500'
            :param type: type of ts (str), default 'TPS'
    """
    # Constants for message codes
    codes = {
        'STN': 2,
        'IH': 3,
        'PCODE': 4,
        'PNO': 5,
        'SH': 6,
        'HA': 7,
        'VA': 8,
        'SD': 9,
        'PC': 20,
        'HAREF': 21,
        'SVA': 26,
        'SHA': 27,
        'PPM': 30,
        'PRISMC': 32,
        'NORTHING': 37,
        'EASTING': 38,
        'ELE': 39
    }

    # Constants for EMD modes
    edmMode = {'DEFAULT': None}
    edmProg = {'DEFAULT': None}

    def __init__(self, name = 'Trimble 5500', typ = 'TPS'):
        """ Constructor to leica generic ts
        """
        # call super class init
        super(Trimble5500, self).__init__(name, typ)

    @staticmethod
    def GetCapabilities():
        """ Get instrument specialities

            :returns: empty list, do not use generic instrument
        """
        return ['ROBOT', 'ANGLE', 'EDM', 'RL', 'LASER', 'POSITION']

    def Result(self, msgs, anss):
        """ Parse answer from message

            :param msgs: messages sent to instrument
            :param anss: answers got from instrument
            :returns: dictionary
        """
        msgList = re.split('\|', msgs)
        ansList = re.split('\|', anss)
        res = {}
        for msg, ans in zip(msgList, ansList):
            if len(msg.strip()) == 0:
                continue
            # get command id form message
            ansBufflist = re.split('\n=', ans)
            commandID = ansBufflist[0]
            if commandID == self.codes['HA']:
                res['hz'] = Angle(float(ansBufflist[1]), 'PDEG')
            elif commandID == self.codes['VA']:
                res['v'] = Angle(float(ansBufflist[1]), 'PDEG')
            elif commandID == self.codes['SD']:
                res['distance'] = float(ansBufflist[1])
            elif commandID == self.codes['EASTING']:
                res['easting'] = float(ansBufflist[1])
            elif commandID == self.codes['NORTHING']:
                res['northing'] = float(ansBufflist[1])
            elif commandID == self.codes['ELE']:
                res['elevation'] = float(ansBufflist[1])
        return res

    def SetPcMsg(self, pc):
        """ Set prism constant

            :param pc: prism constant [mm]
            :returns: set prism constant message
        """
        return 'WG,{0:d}={1:.3f}'.format(self.codes['PC'], pc / 1000.0)

    def SetAtmCorrMsg(self, valueOfLambda, pres, dry, wet):
        """
        Message function for set atmospheric correction settings
        
        :param valueOfLambda: Constant for the instrument not changeable, use GetAtmCorr to get value
        :param pres: pressure value
        :param dry: dry temperature
        :param wet: wet temperature
        :rtype: 0 or error code
          
        """
        pass # TODO

    def GetAtmCorrMsg(self):
        """
        Message function for get atmospheric correction settings
        
        :rtype: atmospheric settings as a dictionary
          
        """
        pass # TODO

    def SetRefCorrMsg(self, status, earthRadius, refracticeScale):
        """
        Message function for set refraction correction settings
        
        :param status: 0/1 = off/on
        :param earthRadius: radius ot the Earth
        :param refracticeScale: refractice scale
        :rtype: 0 or error code
          
        """
        pass # TODO

    def GetRefCorrMsg(self):
        """
        Message function for get refraction correction setting
      
        :rtype: refraction correction as a dictionary
          
        """
        pass # TODO

    def SetStationMsg(self, e, n, z=None):
        """
        Message function for set station coordinates
        
        :param e: easting
        :param n: northing
        :param z: elevation
        :returns: set station coordinates message
          
        """
        # TODO SEASTING
        msg = 'WG,{0:d}={1:.3f}|WG,{2:d}={3:.3f}'.format(
            self.codes['SEASTING'], e, self.codes['SNORTHING'], n)
        if z is not None:
            msg += '|WG,{0:d}={1:.3f}'.format(self.codes['SELE'], z)
        return msg

    def GetStationMsg(self):
        """ Message function for get station co-ordinates
        
        :returns: get station coordinates message
          
        """
        # TODO SEASTING
        pass

    def SetEDMModeMsg(self, mode):
        """ Set EDM mode
        
        :param mode: string name 
        :returns: gset edm mode message
        """
        pass # TODO

    def GetEDMModeMsg(self):
        """ Get EDM mode
        
            :returns: get edm mode message
        """
        pass # TODO

    def SetOriMsg(self, ori):
        """ Set orientation angle
        
        :param ori: bearing of direction (Angle)
        :returns: set orientation angle message
          
        """
        return 'WG,{0:d}={1:.4f}'.format(self.codes['HAREF'],
            ori.GetAngle('PDEG'))

    def MoveMsg(self, hz, v, dummy=None):
        """ Rotate instrument to direction
        
            :param hz: horizontal direction (Angle)
            :param v: zenith angle (Angle)
            :param dummy: dummy parameter for compatibility with Leica
            :returns: rotate message

        """
        # change angles to pseudo DMS
        hz_pdms = hz.GetAngle('PDEG')
        v_pdms = v.GetAngle('PDEG')
        return 'WG,26={0:.4f}|WG,27={1:.4f}|WS=PH02V02'.format(v_pdms, hz_pdms)

    def MeasureMsg(self, dummy1=None, dummy2=None):
        """ Measure distance
        
            :param dummy1: dummy parameter for compatibility with Leica
            :param dummy2: dummy parameter for compatibility with Leica
            :returns: measure message
        """
        return 'TG'
        
    def GetMeasureMsg(self, dummy1=None, dummy2=None):
        """ Get measured distance

            :param dummy1: dummy parameter for compatibility with Leica
            :param dummy2: dummy parameter for compatibility with Leica
            :returns: get measurement message
        """
        return 'RG'

    def MeasureDistAngMsg(self, prg):
        """ Measure angles and distance

            :param prg: EDM program
            :returns: measure angle distance message

        """
        return 'TG|RG'

    def CoordsMsg (self, wait = 1000, incl = 0):
        """ Get coordinates
        
            :param wait: wait-time in ms, optional (default 1000)
            :param incl: inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
            :returns: get coordinates message
        """
        return 'RG,{0:d}|RG{1:d}|RG{2:d}'.format(self.codes['NORTHING'],
            self.codes['EASTING'], self.codes['ELE'])

    def GetAnglesMsg(self):
        """ Get angles

                :returns: get angles message
        """
        return 'RG,{0:d}|RG,{1:d}'.format(self.codes['HA'], self.codes['VA'])

    def ChangeFaceMsg(self):
        """ Change face

            :returns: None
        """
        return None
