#!/usr/bin/env python
"""
.. module:: measureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokbme@gmail.com>

"""

class MeasureUnit(object):
    """ Virtual base clase for measure units

            :param name: name of measure unit (str), default None
            :param typ: type of measure unit (str), default None
    """
    def __init__(self, name = None, typ = None):
        """ constructor for measure unit
        """
        self.name = name
        self.typ = typ

    def GetName(self):
        """ Get name of measure unit

            :returns: name of measure unit
        """
        return self.name

    def GetType(self):
        """ Get type of measure unit

            :returns: type of measure unit
        """
        return self.typ

    def Result(self, msg, ans):
        """ Dummy function it must be implemented in inherited classes

            :param msg: message sent
            :param ans: answer got
        """
        return None

if __name__ == "__main__":
    a = MeasureUnit("alma", "korte")
    print (a.GetName())
    print (a.GetType())
