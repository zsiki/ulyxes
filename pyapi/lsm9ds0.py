#!/usr/bin/env python
"""
.. module:: lsm9ds0.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>
"""

from instrument import Instrument
from lsm9ds0unit import LSM9DS0Unit, A_SCALE_2G, A_ODR_3125, \
            M_SCALE_2GS, M_ODR_3125, G_SCALE_245DPS, G_ODR_95_BW_125

class LSM9DS0(Instrument):
    """ LSM9DS0 9DOF sensor

            :param name: name of instrument (str)
            :param measureUnit: measure unit of the instrument (MeasureUnit)
            :param measureIfaces: interfaces to physical intruments (tuple of two I2CIfaces, first for accelerometer/magnetometer, second for gyroscope)
            :param writerUnit: unit to save observed data (Writer), optional, default None
    """

    def __init__(self, name, measureUnit, measureIfaces, writerUnit=None):
        """ Constructor
        """
        super(LSM9DS0, self).__init__(name, measureUnit, measureIfaces, \
            writerUnit)
        self.Init() # default parameters for init

    def _process(self, msg, i):
        """ Send message to measure unit and process answer

            :param msg: message to send
            :param i: iface index using to send message (int) 0/1
            :returns: parsed answer (dictionary)
        """
        ans = self.measureIface[i].Send(msg)
        if self.measureIface[i].state != self.measureIface[i].IF_OK:
            return {}
        res = self.measureUnit.Result(msg, ans, ['accel', 'gyro'][i])
        if self.writerUnit is not None and res is not None and len(res) > 0:
            self.writerUnit.WriteData(res)
        return res

    def Init(self, a_sc=A_SCALE_2G, a_odr=A_ODR_3125, \
            m_sc=M_SCALE_2GS, m_odr=M_ODR_3125, \
            g_sc=G_SCALE_245DPS, g_odr=G_ODR_95_BW_125):
        """ initialize sensors: accelometer/magnetometer and gyroscope
        """
        msg = self.measureUnit.WhoAmIMsg()
        whoami_a = self._process(msg, 0)
        whoami_g = self._process(msg, 1)
        if whoami_a['data'] != 0b01001001 or \
            whoami_g['data'] != 0b11010100:
            raise IOError('Sensor not found')
            return
        msg = self.measureUnit.InitAccelMsg(a_sc, a_odr)
        accel = self._process(msg, 0)
        msg = self.measureUnit.InitMagMsg(m_sc, m_odr)
        accel.update(self._process(msg, 0))
        msg = self.measureUnit.InitGyroMsg(m_sc, m_odr)
        accel.update(self._process(msg, 1))
        return accel

    def GetGyro(self):
        """ get gyro data

            :returns: 3 axis gyro data
        """
        msg = self.measureUnit.GetGyroMsg()
        return self._process(msg, 1)

    def GetAccel(self):
        """ get accelerometer data

            :returns: 3 axis accel data
        """
        msg = self.measureUnit.GetAccelMsg()
        return self._process(msg, 0)

    def GetMag(self):
        """ get magnetometer data

            :returns: 3 axis magneto data
        """
        msg = self.measureUnit.GetMagMsg()
        return self._process(msg, 0)

if __name__ == '__main__':
    import math
    from i2ciface import I2CIface
    from echowriter import EchoWriter

    i1d = I2CIface('accel', 0x1d)   # iface for acellero/magnetic
    i6b = I2CIface('gyro', 0x6b)    # iface for gyroscope
    munit = LSM9DS0Unit()
    wunit = EchoWriter()

    s9dof = LSM9DS0('9 DOF', munit, [i1d, i6b], wunit)
    for i in range(5):
        print("Accelerometer")
        w = s9dof.GetAccel()
        print(math.sqrt(w['acc_x']**2 + w['acc_y']**2 + w['acc_z']**2))
        print("Magnetometer")
        w = s9dof.GetMag()
        print(math.sqrt(w['mag_x']**2 + w['mag_y']**2 + w['mag_z']**2))
        #print("Gyro")
        #w = s9dof.GetGyro()
        #print(math.sqrt(w['gyro_x']**2 + w['gyro_y']**2 + w['gyro_z']**2))
