#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: serialiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results. GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>,
    Daniel Moka <mokadaniel@citromail.hu>
"""

import logging
import serial
from iface import Iface

class SerialIface(Iface):
    """ Interface to communicate through serial interface. This class depends
        on pyserial.

            :param name: name of serial interface (str)
            :param port: port name e.g. com1: or /dev/stty1
            :param baud: communication speed (int), default 9600
            :param byteSize: byte size in communication (int), default 8
            :param parity: parity of bytes even/odd/none, default none
            :param stop: number of stop bits (int), default 1
            :param timeout: communication timeout seconds (int), default 12
            :param eomRead: end of message char from instrument (str), default '\\r\\n'
            :param eomWrite: end of message char from computer (str), default '\\r\\n'
    """
    def __init__(self, name, port, baud=9600, byteSize=8,
                 parity=serial.PARITY_NONE, stop=1, timeout=17, eomRead='\r\n',
                 eomWrite='\r\n'):
        """ Constructor for serial interface
        """
        super(SerialIface, self).__init__(name)
        # open serial port
        self.ser = None
        self.Open(port, baud, byteSize, parity, stop, timeout)
        self.eomRead = eomRead
        self.eomWrite = eomWrite

    def __del__(self):
        """ Destructor for serial interface
        """
        self.Close()

    def Open(self, port, baud=9600, byteSize=8,
             parity=serial.PARITY_NONE, stop=1, timeout=12):
        """ Open searial line
        """
        try:
            self.ser = serial.Serial(port, baud, byteSize, parity, stop, timeout)
            self.opened = True
            self.state = self.IF_OK
        except:
            self.opened = False
            self.state = self.IF_ERROR
            logging.error(" cannot open serial line")

    def Close(self):
        """ Close serial line
        """
        try:
            self.ser.close()
            self.opened = False
            self.state = self.IF_OK
        except:
            self.state = self.IF_ERROR
            logging.error(" cannot close serial line")

    def GetLine(self):
        """ read from serial interface until end of line

        :returns: line read from serial (str) or empty string on timeout or error, state is set also
        """
        if self.ser is None or not self.opened or self.state != self.IF_OK:
            logging.error(" serial line not opened")
            return None
        # read answer till end of message marker
        ans = ''
        w = -1 * len(self.eomRead)
        while ans[w:] != self.eomRead:
            ch = ''
            try:
                ch = (self.ser.read(1)).decode('ascii')
            except:
                self.state = self.IF_READ
                logging.error(" cannot read serial line")
            if ch == '':
                # timeout exit loop
                self.state = self.IF_TIMEOUT
                logging.error(" timeout on serial line")
                break
            ans += ch
        # remove end of line
        logging.debug(" message got: %s", ans)
        ans = ans.strip(self.eomRead)
        return ans

    def PutLine(self, msg):
        """ send message through the serial line

            :param msg: message to send (str)
            :returns: 0 - on OK, -1 on error or interface is in error state
        """
        # do nothing if interface is in error state
        if self.ser is None or not self.opened or self.state != self.IF_OK:
            logging.error(" serial line not opened or in error state")
            return -1
        # add CR/LF to message end
        w = -1 * len(self.eomWrite)
        if msg[w:] != self.eomWrite:
            msg += self.eomWrite
        # remove special characters
        msg = msg.encode('ascii', 'ignore')
        # send message to serial interface
        logging.debug(" message sent: %s", msg)
        try:
            self.ser.write(msg)
        except:
            self.state = self.IF_WRITE
            logging.error(" cannot write serial line")
            return -1
        return 0

    def Send(self, msg):
        """ send message to serial line and read answer

            :param msg: message to send, it can be multipart message separated by '|' (str)
            :returns: answer from instrument (str)
        """
        msglist = msg.split("|")
        res = ''
        #sending
        for m in msglist:
            if self.PutLine(m) == 0:
                res += self.GetLine() + '|'
        if res.endswith('|'):
            res = res[:-1]
        return res

if __name__ == "__main__":
    a = SerialIface('test', '/dev/ttyUSB0', eomRead='>')
    print(a.GetName())
    print(a.GetState())
    #print(a.Send('%R1Q,2008:1,0'))
    print(a.Send('TG'))
    print(a.Send('WG,20=0.008'))
    print(a.Send('RG,20'))
    print(a.GetState())
