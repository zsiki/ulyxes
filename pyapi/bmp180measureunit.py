#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: ibmp180measureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

Based on Adafruit_BMP created by Tony DiCola
"""
import logging
from measureunit import MeasureUnit

# Operating Modes and delays for modes
BMP180_ULTRALOWPOWER     = 0
BMP180_STANDARD          = 1
BMP180_HIGHRES           = 2
BMP180_ULTRAHIGHRES      = 3
BMP180_DELAY = (0.005, 0.008, 0.014, 0.026)

# BMP085 Registers
BMP180_CAL_AC1           = 0xAA  # R   Calibration data (16 bits)
BMP180_CAL_AC2           = 0xAC  # R   Calibration data (16 bits)
BMP180_CAL_AC3           = 0xAE  # R   Calibration data (16 bits)
BMP180_CAL_AC4           = 0xB0  # R   Calibration data (16 bits)
BMP180_CAL_AC5           = 0xB2  # R   Calibration data (16 bits)
BMP180_CAL_AC6           = 0xB4  # R   Calibration data (16 bits)
BMP180_CAL_B1            = 0xB6  # R   Calibration data (16 bits)
BMP180_CAL_B2            = 0xB8  # R   Calibration data (16 bits)
BMP180_CAL_MB            = 0xBA  # R   Calibration data (16 bits)
BMP180_CAL_MC            = 0xBC  # R   Calibration data (16 bits)
BMP180_CAL_MD            = 0xBE  # R   Calibration data (16 bits)
BMP180_CONTROL           = 0xF4
BMP180_TEMPDATA          = 0xF6
BMP180_PRESSUREDATA      = 0xF6

# Commands
BMP180_READTEMPCMD       = 0x2E
BMP180_READPRESSURECMD   = 0x34

class BMP180MeasureUnit(MeasureUnit):
    """ Adafruit BMP180 digital pressure sensor

            :param name: name of measure unit (str), default None
            :param typ: type of measure unit (str), default None
    """
    def __init__(self, name = None, typ = 'pressure sensor',
                 mode = BMP180_STANDARD):
        """ constructor for measure unit
        """
        super(BMP180MeasureUnit, self).__init__(name, type)
        self.mode = mode
        # calibration data from catalog
        self.cal_AC1 = 7186
        self.cal_AC2 = -1064
        self.cal_AC3 = -14482
        self.cal_AC4 = 33907
        self.cal_AC5 = 25490
        self.cal_AC6 = 15616
        self.cal_B1 = 6515
        self.cal_B2 = 37
        self.cal_MB = -32768
        self.cal_MC = -11786
        self.cal_MD = 2521
        # temperature coefficient
        self.B5 = None

    def LoadCalibrationMsg(self):
        """ Load calibration data from sensor message

            :returns: load calibration data message
        """
        return (('readS16BE', BMP180_CAL_AC1),
                ('readS16BE', BMP180_CAL_AC2),
                ('readS16BE', BMP180_CAL_AC3),
                ('readU16BE', BMP180_CAL_AC4),  # unsigned!
                ('readS16BE', BMP180_CAL_AC5),
                ('readS16BE', BMP180_CAL_AC6),
                ('readS16BE', BMP180_CAL_B1),
                ('readS16BE', BMP180_CAL_B2),
                ('readS16BE', BMP180_CAL_MB),
                ('readS16BE', BMP180_CAL_MC),
                ('readS16BE', BMP180_CAL_MD))

    def GetTempMsg(self):
        """ Read temperature message

            :returns: read temperature message
        """
        return (('write8', BMP180_CONTROL, BMP180_READTEMPCMD),
                ('sleep', BMP180_DELAY[0]),
                ('readU16BE', BMP180_TEMPDATA))

    def GetPressureMsg(self):
        """ Read pressure message

            :returns read pressure message
        """
        return (('write8', BMP180_CONTROL, BMP180_READPRESSURECMD + \
                 (self.mode << 6)),
                ('sleep', BMP180_DELAY[self.mode]),
                ('readU8', BMP180_PRESSUREDATA),
                ('readU8', BMP180_PRESSUREDATA+1),
                ('readU8', BMP180_PRESSUREDATA+2),
                ('op', '((data[0] << 16) + (data[1] << 8) + data[2]) >> (8 - ' + str(self.mode) + ')'))

    def Result(self, msg, ans):
        res = {}
        if len(msg) == 3:
            # temperature
            # Calculations below are taken straight from section 3.5 of the datasheet
            logging.debug("Raw temperature %d" % ans['data'])
            X1 = ((ans['data'] - self.cal_AC6) * self.cal_AC5) >> 15
            X2 = (self.cal_MC << 11) / (X1 + self.cal_MD)
            self.B5 = X1 + X2
            res['temp'] = ((self.B5 + 8) >> 4) / 10.0
        elif len(msg) == 6:
            # air pressure
            logging.debug("Raw pressure %d" % ans['data'])
            B6 = self.B5 - 4000
            X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
            X2 = (self.cal_AC2 * B6) >> 11
            X3 = X1 + X2
            B3 = (((self.cal_AC1 * 4 + X3) << self.mode) + 2) / 4
            X1 = (self.cal_AC3 * B6) >> 13
            X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
            X3 = ((X1 + X2) + 2) >> 2
            B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
            B7 = (ans['data'] - B3) * (50000 >> self.mode)
            if B7 < 0x80000000:
                p = (B7 * 2) / B4
            else:
                p = (B7 / B4) * 2
            X1 = (p >> 8) * (p >> 8)
            X1 = (X1 * 3038) >> 16
            X2 = (-7357 * p) >> 16
            res['pressure'] = (p + ((X1 + X2 + 3791) >> 4)) / 100.0
        elif len(msg) == 11:
            self.cal_AC1 = ans['data'][0]
            self.cal_AC2 = ans['data'][1]
            self.cal_AC3 = ans['data'][2]
            self.cal_AC4 = ans['data'][3]
            self.cal_AC5 = ans['data'][4]
            self.cal_AC6 = ans['data'][5]
            self.cal_B1 = ans['data'][6]
            self.cal_B2 = ans['data'][7]
            self.cal_MB = ans['data'][8]
            self.cal_MC = ans['data'][9]
            self.cal_MD = ans['data'][10]
            res = True
        return res
        
if __name__ == "__main__":
    BMP180Unit = BMP180MeasureUnit()
    print (BMP180Unit.GetTempMsg())
    print (BMP180Unit.GetPressureMsg())
