#!/usr/bin/env python
"""
    <p>Ulyxes - an open source project to drive total stations and
           publish observation results</p>
    <p>GPL v2.0 license</p>
    <p>Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu></p>
    @author Zoltan Siki
    @author Daniel Moka
    @version 1.1
"""

from interface import *
import serial

class SerialInterface(Interface):

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
	if self.PutLine(msg) == 0:
            return self.GetLine()
        else:
            return b''

if __name__ == "__main__":
    a = SerialInterface('test', 'COM4')
    print a.GetName()
    print a.GetState()
    #print a.Send("%R1Q,9027:0,0,0,0,0")
    while 1:
        print a.GetLine()
        print a.GetState()
