
"""
.. module::developement_mirind4.py

.. moduleauthor:: Daniel Moka

This module file stands for sharing developement information created by mirind4(git).

"""

import sys
import logging

sys.path.append('../pyapi/')

from totalstation import TotalStation
from localiface import LocalIface
from leicatcra1100 import LeicaTCRA1100
from leicatps1200 import LeicaTPS1200
from trimble5500 import Trimble5500

logging.getLogger().setLevel(logging.WARNING)

if __name__ == "__main__":
    stationtype1 = '1200'
    iface = LocalIface('local1')

    mu = LeicaTPS1200()

    totalStat1 = TotalStation(stationtype1, mu, iface)

    print ('\n')
    print('Using __str__ and __repr__ representation:')
    print ('Result of __str__: ', str(totalStat1))
    print ('Result of __repr__: ',repr(totalStat1))

