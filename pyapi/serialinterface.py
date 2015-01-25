#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: serialinterface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results. GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>. This module depends on pyserial.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Danieli Moka <mokadaniel@citromail.hu>

"""

from interface import Interface
import serial
import re
import logging

class SerialInterface(Interface):
    """ Interface to communicate through serial interface
    """
    def __init__(self, name, port, baud=9600, byteSize=8, \
        parity=serial.PARITY_NONE, stop=1, timeout=12):
        """ Constructor for serial interface

            :param name: name of serial interface
            :param port: port name e.g. com1: or /dev/stty1
            :param baud: communication speed
            :param byteSize: byte ize in communication
            :param parity: parity of bytes even/odd/none
            :param stop: number of stop bits
            :param timeout: communication timeout seconds
        """
        super(SerialInterface, self).__init(name)
        # open serial port
        try:
            self.ser = serial.Serial(port, baud, byteSize, parity, stop, timeout)
        except:
            self.state = self.ERR_OPEN
            logging.error(" cannot open serial line")

    def __del__(self):
        """ Destructor for serial interface
        """
        try:
            self.ser.close()
        except:
            pass

    def GetLine(self):
        """ read from serial interface until end of line
            
        :returns: line read from serial or empty string on timeout state is set in case of error or timeout
        """
        # read answer till end of line
        ans = b''
        ch = b''
        while (ch != b'\n'):
            ch = b''
            try:
                ch = self.ser.read(1)
            except:
                self.state = self.ERR_READ
                logging.error(" cannot read serial line")
            if ch == b'':
                # timeout exit loop
                self.state = self.ERR_TIMEOUT
                logging.error(" timeout on serial line")
                break
            ans += ch
        # remove end of line
        ans = ans.strip(b'\r\n')
        logging.debug(" message got: %s", ans)
        return ans

    def PutLine(self, msg):
        """ send message through the serial line

            :param msg: message to send
            :returns: 0 - on OK, -1 on error or interface is in error state
        """
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
        logging.debug(" message sent: %s", msg)
        try:
            self.ser.write(msg)
        except:
            self.state = self.ERR_WRITE
            logging.error(" cannot write serial line")
            return -1
        return 0

    def Send(self, msg):
        """ send message to serial line and read answer

            :param msg: message to send, it can be multipart message separated by '|'
            :returns: answer from instrument
        """
        msglist = re.split("\|", msg)
        res = b""
        #sending
        for m in msglist:
            if self.PutLine(m) == 0:
                res += self.GetLine() + b"|"
        if res.endswith(b"|"):
            res = res[:-1]
        return res

if __name__ == "__main__":
    a = SerialInterface('test', '/dev/ttyUSB0')
    print (a.GetName())
    print (a.GetState())
    print (a.Send('%R1Q,2008:1,0'))
