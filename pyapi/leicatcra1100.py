#!/usr/bin/env python
"""
.. module:: leicatcra1100.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results. GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokadaniel@citromail.hu>

"""

from leicameasureunit import LeicaMeasureUnit

class LeicaTCRA1100(LeicaMeasureUnit):
    """ This class contains the Leica TCRA1100 robotic total station specific functions
    """

    def __init__(self, name = 'Leica TCRA1100', typ = 'TPS'):
        """ Constructor to leica generic ts

            :param name: name of ts (str), default=TCRA1100
            :param type: type od ts (str), default=TPS
        """
        # call super class init
        super(LeicaTCRA1100, self).__init__(name, typ)

    # Constants for message codes
    codes = {
        'SETPC': 2024,
        'GETPC': 2023,
        'SETATR': 18005,
        'GETATR': 18006,
        'SETLOCK': 18007,
        'GETLOCK': 18008,
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
    # RT = Reflector Tape, RL = Reflectorless, LR = Long Range
    edmMode = {'RTSTANDARD': 1, 'STANDARD': 2, 'FAST': 3, 'LRSTANDARD': 4, \
                'RLSTANDARD': 5, 'TRACK': 6, 'RLTRACK': 8, 'TRACK2': 9, \
                'AVERAGING': 10, 'RLAVERAGING': 11, 'LRAVERAGING': 12}

    @staticmethod
    def GetCapabilities():
        """ Get instrument specialities

            :returns: List of specialities
        """
        return ['ROBOT', 'ANGLE', 'EDM', 'ATR', 'LOCK', 'RL', \
            'LASER', 'POSITION']

    def SetRedLaserMsg(self, on):
        """ Set red laser on/off

            :param on: 0/1 turn off/on read laser
            :returns: red laser on/off message
        """
        return '%R1Q,{0:d}:{1:d}'.format(self.codes['SETREDLASER'], on)

