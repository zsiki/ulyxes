#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: webmetmeasureunit.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.  GPL v2.0 license Copyright (C)
       2010-2013 Zoltan Siki <siki@agt.bme.hu>.

.. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>

"""
from measureunit import MeasureUnit

class WebMetMeasureUnit(MeasureUnit):
    """ Web meteorological sensor

            :param name: name of measure unit (str), default None
            :param typ: type of measure unit (str), default None
    """
    def __init__(self, name=None, typ='met sensor', msg=None):
        """ constructor for measure unit
        """
        super(WebMetMeasureUnit, self).__init__(name, typ)
        self.msg = msg

    def GetTempMsg(self):
        """ Read temperature message

            :returns: read temperature message
        """
        return self.msg

    def GetPressureMsg(self):
        """ Read pressure message

            :returns read pressure message
        """
        return self.msg

    def Result(self, msg, ans):
        if ans is not None and 'main' in ans:
            return ans['main']
        else:
            return None
