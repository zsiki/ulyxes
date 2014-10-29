#!/usr/bin/env python

"""
only for testing purposes
using leica GeoCom commands
"""
from interface import *

class LocalInterface(Interface):
    def __init__(self, name = 'Local'):
        super(LocalInterface, self).__init__(name)
        self.atr = 0
	self.lock = 0
        self.edmmode = 0

    def Send(self, msg):
        id = int(msg.split(',')[1].split(':')[0])
        ans = '%R1P,0,0:0'
	if id == 9027:
            # move
            ans = '%R1P,0,0:0'
        elif id == 18005:
            # setatr
            self.atr = int(msg.split(':')[1])
            ans = '%R1P,0,0:0'
        elif id == 18006:
            # getatr
            ans = '%%R1P,0,0:0,%d' % self.atr
        elif id == 18007:
            # setlock
            self.lock = int(msg.split(':')[1])
            ans = '%R1P,0,0:0'
        elif id == 18008:
            # getlock
            ans = '%%R1P,0,0:0,%d' % self.lock
        elif id == 2020:
            # setedmmode
            self.edmmode = int(msg.split(':')[1])
            ans = '%R1P,0,0:0'
        elif id == 2021:
            # getedmmode
            ans = '%%R1P,0,0:0,%d' % self.edmmode
        return ans

if __name__ == "__main__":
    a = LocalInterface()
    print a.GetName()
    print a.GetState()
    print a.Send('%R1Q,9018:1')
