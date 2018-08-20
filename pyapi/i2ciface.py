#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: i2ciface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2015 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

Based on Adafruit_I2C.py created by Kevin Townsend.
"""

import time
import smbus
from iface import Iface

class I2CIface(Iface):
    """Class for communicating with an I2C device using the smbus library.
    Allows reading and writing 8-bit, 16-bit, and byte array values to registers
    on the device.
    This modul depends on smbus.

        :param name: name of interface (str)
        :param address: address on i2c bus (int)
        :param busnum: i2c bus number (int), default 1 (Raspberry PI B/B+)
    """

    def __init__(self, name, address, busnum=1):
        """Create an instance of the I2C device at the specified address on the
        specified I2C bus number."""
        super(I2CIface, self).__init__(name)
        self._address = address
        self._bus = smbus.SMBus(busnum)

    def writeRaw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        value = value & 0xFF
        self._bus.write_byte(self._address, value)

    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        self._bus.write_byte_data(self._address, register, value)

    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        value = value & 0xFFFF
        self._bus.write_word_data(self._address, register, value)

    def writeList(self, register, data):
        """Write bytes to the specified register."""
        self._bus.write_i2c_block_data(self._address, register, data)

    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        results = self._bus.read_i2c_block_data(self._address, register, length)
        return results

    def readRaw8(self):
        """Read an 8-bit value on the bus (without register)."""
        result = self._bus.read_byte(self._address) & 0xFF
        return result

    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        result = self._bus.read_byte_data(self._address, register) & 0xFF
        return result

    def readS8(self, register):
        """Read a signed byte from the specified register."""
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self._bus.read_word_data(self._address, register) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(register, little_endian=False)

    def Send(self, msg):
        """ send message to device

            :param msg: message (tuple), one item in tuble is a read/write/sleep/op operation. For read and write a register must be specified, the operation name can be any read.../write... method of the class, to read/write 8/16 bit values. After sleep specify time in seconds. After op specify an avaluatable string on the previously read data, data are stored in data list in the order of reading.
        """
        i = 0
        data = []
        res = {}
        for op in msg:
            if op[0][:5] == 'write':
                getattr(self, op[0])(op[1], op[2])
            elif op[0][:8] == 'readList':
                data.append(getattr(self, op[0])(op[1], op[2]))
                i += op[2]
            elif op[0][:4] == 'read':
                data.append(getattr(self, op[0])(op[1]))
                i += 1
            elif op[0][:5] == 'sleep':
                time.sleep(op[1])
            elif op[0][:2] == 'op':
                res['data'] = eval(op[1])
        if len(res) == 0 and len(data) > 0:
            if len(data) > 1:
                res['data'] = data      # return data list
            else:
                res['data'] = data[0]   # return single value
        return res

if __name__ == "__main__":
    mode = 1
    i2c = I2CIface('BMP180', 0x77, 1)
    t = i2c.Send((('write8', 0xF4, 0x2E),
                  ('sleep', 0.005),
                  ('readU16BE', 0xF6)))
    print("raw temperature %d" % t["data"])
    p = i2c.Send((('write8', 0xF4, 0x34 + (1 << 6)),
                  ('sleep', 0.005),
                  ('readU8', 0xF6),
                  ('readU8', 0xF6+1),
                  ('readU8', 0xF6+2),
                  ('op', '((data[0] << 16) + (data[1] << 8) + data[2]) >> (8 - 1)')))
    print("raw pressure %d" % p["data"])
