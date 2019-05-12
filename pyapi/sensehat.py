#!/usr/bin/python

"""
.. module:: sensehat.py
   :platform: Unix(Raspbian)
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: Bence Turak <bence.turak@gmail.com>
"""
from instrument import Instrument
from angle import Angle
import sense_hat
import time



class SenseHat(Instrument, sense_hat.SenseHat):
    def __init__(self, name, writerUnit=None):
        """ constructor
        """
        Instrument.__init__(self,name, None, None, writerUnit)
        sense_hat.SenseHat.__init__(self)
    def write(self, res):
        if self.writerUnit is not None and res is not None and len(res) > 0:
            self.writerUnit.WriteData(res)

    def get_humidity(self):
        res =  super(SenseHat, self).get_humidity()
        res['time'] = time.time()
        self.write({'hum': res})
        return res

    @property
    def humidity(self):
        return self.get_humidity()

    def get_temperature_from_humidity(self):
        res =  super(SenseHat, self).get_temperature_from_humidity()
        res['time'] = time.time()
        self.write({'temp_hum': res})
        return res
    def get_temperature_from_pressure(self):
        res =  super(SenseHat, self).get_temperature_from_pressure()
        res['time'] = time.time()
        self.write({'temp_pres': res})
        return res
    def get_temperature(self):
        """
        Returns the temperature in Celsius
        """

        return self.get_temperature_from_humidity()
    @property
    def temp(self):
        return self.get_temperature_from_humidity()
    @property
    def temperature(self):
        return self.get_temperature_from_humidity()

    def get_pressure(self):
        res =  super(SenseHat, self).get_pressure()
        res['time'] = time.time()
        self.write({'pres': res})

        return res

    def get_orientation_radians(self):
        res =  super(SenseHat, self).get_orientation_radians()
        res['time'] = time.time()
        self.write(res)

        return res
    @property
    def orientation_radians(self):
        return self.get_orientation_radians()
    @property
    def orientation(self):
        res =  super(SenseHat, self).get_orientation_radians()
        res2 = {}
        for key, val in res.items():
            res2['ori_'+key] = Angle(val)
        res2['time'] = time.time()
        self.write(res2)

        return res2


    def get_compass_raw(self):
        res =  super(SenseHat, self).get_compass_raw()
        res2 = {}
        for key, val in res.items():
            res2['comp_raw_'+key] = val
        res2['time'] = time.time()
        self.write(res2)

        return res2
    @property
    def compass_raw(self):
        return self.get_compass_raw()


    @property
    def gyro(self):
        return self.get_gyroscope()

    @property
    def gyroscope(self):
        return self.get_gyroscope()

    def get_gyroscope_raw(self):
        """
        Gyroscope x y z raw data in radians per second
        """

        res = super(SenseHat, self).get_gyroscope_raw()

        res2 = {}
        for key, val in res.items():
            res2['gyro_raw_'+key] = Angle(val)
        res2['time'] = time.time()
        self.write(res2)

        return res2

    @property
    def gyro_raw(self):
        return self.get_gyroscope_raw()

    @property
    def gyroscope_raw(self):
        return self.get_gyroscope_raw()

    def get_accelerometer(self):
        res = super(SenseHat, self).get_accelerometer_raw()


        res2 = {}
        for key, val in res.items():
            res2['accel_'+key] = val
        res2['time'] = time.time()
        self.write(res2)

        return res2

    @property
    def accel(self):
        return self.get_accelerometer()








if __name__ == '__main__':

    from csvwriter import CsvWriter

    wrt = CsvWriter(fname = '/home/bence/proba.csv', dist='.17f', filt=['hum', 'ori_pitch', 'ori_roll', 'ori_yaw', 'gyro_raw_x', 'gyro_raw_y', 'gyro_raw_z', 'accel_x', 'accel_y', 'accel_z'])
    a = SenseHat('test', wrt)
    while 1:
        a.accel
        time.sleep(0.5)
