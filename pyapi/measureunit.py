#!/usr/bin/env python
"""
.. module:: measureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and publish observation results.  GPL v2.0 license Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>.
.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokbme@gmail.com>

"""

class MeasureUnit(object):
    """ Virtual base clase for measure units
    """
    def __init__(self, name = 'None', type = 'None'):
        """ constructor for measure unit

            :param name: name of measure unit
            :param type: type of measure unit
        """
        self.name = name
        self.type = type

    def GetName(self):
        """ Get name of measure unit

            :returns: name of measure unit
        """
        return self.name

    def GetType(self):
        """ Get type of measure unit

            :returns: type of measure unit
        """
        return self.type

if __name__ == "__main__":
    a = MeasureUnit()
    print (a.GetName())
    print (a.GetType())
