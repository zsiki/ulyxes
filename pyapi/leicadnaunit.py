#!/usr/bin/env python
"""
.. module:: leicadnaunit.py

   :platform: Unix, Windows
      :synopsis: Ulyxes - an open source project to drive total stations and
             publish observation results.
            GPL v2.0 license
           Copyright (C) 2010-2013 Zoltan Siki <siki@agt.bme.hu>

  .. moduleauthor:: Zoltan Siki <siki@agt.bme.hu>, Daniel Moka <mokbme@gmail.com>
"""

from measureunit import MeasureUnit

class LeicaDnaUnit(MeasureUnit):
    """ Leica DNA measure unit
    """

    def __init__(self, name = 'Leica level', typ = 'Level'):
        """ Construnctor for leica dna unit

            :param name: name of measure unit
            :param typ: type of measure unit
        """
        # call super class init
        super(LeicaDnaUnit, self).__init__(name, typ)

    def Result(self, msg, ans):
        # TODO
        pass

    def Measure(self):
        # TODO
        pass
