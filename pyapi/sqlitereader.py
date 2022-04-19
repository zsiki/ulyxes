#!/usr/bin/env python
"""
.. module:: sqlitereader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>

OBSOLATE USE dbreader.py
"""

import os.path
import logging
import sqlite3
from reader import Reader

class SqLiteReader(Reader):
    """ Class to read observations/coordinates from a local sqlite database

            :param name: name of reader (str)
            :param angle: angle unit to use (str), DMS not supported
            :param dist: distance and coordinate format (str)
            :param dt: date/time format (str), default ansi
            :param filt: list of allowed keys (list)
            :param db: name of database file (str)
    """

    tables = {'coo': 'monitoring_coo', 'obs': 'monitoring_obs', 'met': 'monitoring_met'}

    def __init__(self, db, sql, name=None, filt=None):
        """ Constructor
        """
        super(SqLiteReader, self).__init__(name, filt)
        self.angle = 'GON'
        if os.path.isfile(db):
            self.db = db
            # connect to local db
            self.conn = sqlite3.connect(db)
        else:
            self.db = self.conn = self.cur = None
            logging.fatal('SqLite database does not exists: ' + db)
            return
        self.cur = self.conn.cursor()
        self.cur.execute(sql)
        self.keys = [description[0] for description in self.cur.description]
        #self.typs = [description[1] for description in self.cur.description]

    def __del__(self):
        try:
            self.cur.close()
            self.conn.close()
        except Exception:
            pass

    def GetNext(self):
        """ Get next line from cursor

            :returns: dictionary with values
        """
        r = self.cur.fetchone()
        if r:
            res = dict(zip(self.keys, r))
        else:
            res = None
        return res

if __name__ == "__main__":
    myfile = SqLiteReader(db="/home/siki/tanszek/szelkapu/szk1/szk1.db",
                          sql="SELECT * FROM monitoring_obs WHERE datetime between '2017-11-17 12:00:00' and '2017-11-22 12:00:00' ORDER BY datetime")
    print(myfile.GetNext())
