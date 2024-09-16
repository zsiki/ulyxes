#!/usr/bin/env python
"""
.. module:: axis10.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results. GPL v2.0 license Copyright (C)
       2024- Zoltan Siki <siki.zoltan@emk.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@emk.bme.hu>,
"""

from leicatps1200 import LeicaTPS1200

class Axis10(LeicaTPS1200):
    """ This class contains STEC Axis10 robotic total station specific
        functions

            :param name: name of ts (str), default=TPS1200
            :param type: type od ts (str), default=TPS
    """

    HZ_TOL = 0.087  # 5 degree for atr tolerance
    V_TOL = 0.087

    def __init__(self, name='Axis 10', typ='TPS'):
        """ Constructor to leica 1200 ts
        """
        # call super class init
        super().__init__(name, typ)

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
        msg = f"%R1Q,{self.codes['MOVE']}:{hz_rad},{v_rad},0,0,0"
        if atr:
            msg += f"|%R1Q,{self.codes['FINEADJ']}:{self.HZ_TOL},{self.V_TOL},0,0,0"
        return msg
