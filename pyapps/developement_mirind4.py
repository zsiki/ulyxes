
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
    stationtype2 = '1100'
    stationtype3 = '5500'
    iface = LocalIface('local1')
    iface2 = LocalIface('local2')
    iface3 = LocalIface('local3')
    mu = LeicaTPS1200()
    mu2 = LeicaTCRA1100()
    mu3 = Trimble5500()
    totalStat1 = TotalStation(stationtype1, mu, iface)
    totalStat2 = TotalStation(stationtype2, mu2, iface2)
    totalStat3 = TotalStation(stationtype3, mu3, iface3)


    print ('Loop over all instances so far created:')
    for ts in TotalStation:
        print (ts)

    print ('\n')
    print('Using __str__ and __repr__ representation:')
    print ('Result of __str__: ', str(totalStat1))
    print ('Result of __repr__: ',repr(totalStat1))

