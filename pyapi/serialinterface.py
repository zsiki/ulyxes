#!/usr/bin/env python
"""
.. module:: serialinterface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
           publish observation results.
           GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

.. moduleauthor:: dr. Siki Zoltan <siki@agt.bme.hu>, Moka Daniel <mokadaniel@citromail.hu>

"""

from interface import *
import serial
import re

class SerialInterface(Interface):
    """
        This class contains ...
    """
    def __init__(self, name, port, baud=9600, byteSize=8, parity=serial.PARITY_NONE, stop=1, timeout=12):
        self.state = self.IF_OK
        self.name = name
        # open serial port
        try:
            self.ser = serial.Serial(port, baud, byteSize, parity, stop, timeout)
        except:
            self.state = self.ERR_OPEN

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass

    def GetLine(self):
        # read answer till end of line
        ans = b''
        ch = b''
        while (ch != b'\n'):
            ch = b''
            try:
                ch = self.ser.read(1)
            except:
                self.state = self.ERR_READ
            if ch == b'':
                # timeout exit loop
                self.state = self.ERR_TIMEOUT
                break
            ans += ch
        # remove end of line
        ans = ans.strip(b'\r\n')
        return ans

    def PutLine(self, msg):
        ans = b''
	# do nothing if interface is in error state
        if self.state != self.IF_OK:
            return -1
        # add CR/LF to message end
        if (msg[-2:] != '\r\n'):
            msg += '\r\n'
        # remove special characters
        msg = msg.encode('ascii', 'ignore')
        # send message to serial interface
        try:
            self.ser.write(msg)
        except:
            self.state = self.ERR_WRITE
            return -1
        return 0

    def Send(self, msg):
        msglist = re.split("\|", msg)
        res = b""
        #sending
        for m in msglist:
            if self.PutLine(m) == 0:
                res += self.GetLine() + b"|"
        if res.endswith(b"|"):
            res = res[:-1]
        w = ''.join(chr(x) for x in res)
        return w

if __name__ == "__main__":
    a = SerialInterface('test', 'COM4')
    print (a.GetName())
    print (a.GetState())
    print (a.Send('%R1Q,2008:1,0'))

