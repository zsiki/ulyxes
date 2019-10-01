#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: bluetoothiface.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results. GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki.zoltan@epito.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>,
    Kecskeméti Máté <kecskemeti.mate3@gmail.com>
"""

import logging
import bluetooth
import time
from iface import Iface

class BluetoothIface(Iface):
    """ Interface to communicate through bluetooth interfacei as a client. 
        This class depends on pybluez.

            :param name: name of bluetooth interface (str)
            :param mac: mac address of server to connect
            :param port: bluetooth port, default 3
            :param eomRead: end of message char from instrument (str), default '\\r\\n'
            :param eomWrite: end of message char from computer (str), default '\\r\\n'
    """

    def __init__(self, name, mac, port=3, timeout=5, eomRead='\r\n',
                 eomWrite='\r\n'):
        """ Constructor for bluetooth client
        """
        super(BluetoothIface, self).__init__(name)
        self.mac = mac
        self.port = port
        self.timeout = timeout
        self.eomRead = eomRead
        self.eomWrite = eomWrite
        self.socket = None
        self.Open()

    def __del__(self):
        """ Destructor for bluetooth client
        """
        self.Close()
        self.socket = None

    def Open(self):
        """ Open bluetooth communication
        """
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            self.socket.connect((self.mac, self.port))
        except:
            logging.error(" error opening bluetooth connection")
            self.state = self.IF_SOURCE
            self.socket = None

    def Close(self):
        """ Close bluetooth communication
        """
        try:
            self.socket.close()
        except:
            pass

    def GetLine(self):
        """ read a line from bluetooth
        """
        if self.socket is None or self.state != self.IF_OK:
            logging.error(" bluetooth connection not opened or in error state")
            return None
        # read answer till end of message marker
        ans = ''
        w = -1 * len(self.eomRead)
        while ans[w:] != self.eomRead:
            ch = ''
            try:
                ch = (self.socket.recv(1)).decode('ascii')
            except:
                self.state = self.IF_READ
                logging.error(" cannot read bluetooth connection")
                break
            if ch == '':
                # timeout exit loop
                self.state = self.IF_TIMEOUT
                logging.error(" timeout on bluetooth")
                break
            ans += ch
        # remove end of line
        logging.debug(" message got: %s", ans)
        ans = ans.strip(self.eomRead)
        return ans

    def PutLine(self, msg):
        """ Send message through bluetooth

            :param msg: message to send (str)
            :returns: 0 - on OK, -1 on error or interface is in error state
        """
        # do nothing if interface is in error state
        if self.socket is None or self.state != self.IF_OK:
            logging.error(" bluetooth connection not opened or in error state")
            return -1
        # add CR/LF to message end
        w = -1 * len(self.eomWrite)
        if msg[w:] != self.eomWrite:
            msg += self.eomWrite
        # remove special characters
        msg = msg.encode('ascii', 'ignore')
        # send message to bluetooth interface
        logging.debug(" message sent: %s", msg)
        try:
            self.socket.settimeout(self.timeout)
            self.socket.send(msg)
        except:
            self.state = self.IF_WRITE
            logging.error(" cannot write to bluetooth connection")
            return -1
        return 0

    def Send(self, msg):
        """ send message to bluetooth and wait for answer

            :param msg: message to send, it can be multipart message separated by '|' (str)
            :returns: answer from instrument (str)
        """
        msglist = msg.split("|")
        res = ''
        #sending
        for m in msglist:
            if self.PutLine(m) == 0:
                time.sleep(5)
                res += self.GetLine() + '|'
        if res.endswith('|'):
            res = res[:-1]
        return res

if __name__ == "__main__":
    a = BluetoothIface('test', '00:12:F3:04:ED:06', 1)
    if a.GetState() == a.IF_OK:
        print(a.Send('%R1Q,2008:1,0'))
        print(a.GetState())
