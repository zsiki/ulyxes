#!/usr/bin/env python
"""
.. module:: dbreader.py
   :platform: Unix, Windows
   :synopsis: Ulyxes - an open source project to drive total stations and
       publish observation results.
       GPL v2.0 license
       Copyright (C) 2010- Zoltan Siki <siki.zoltan@epito.bme.hu>

.. moduleauthor:: Zoltan Siki <siki.zoltan@epito.bme.hu>
"""

import os.path
import logging
import sqlite3
import psycopg2
from reader import Reader

class DbReader(Reader):
    """ Class to read observations/coordinates from a database

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
        super().__init__(name, filt)
        self.angle = 'GON'
        self.db = db
        if os.path.isfile(db):
            # connect to local db
            try:
                self.conn = sqlite3.connect(db)
            except Exception:
                logging.fatal("Cannot ope database")
                return
        else:
            try:
                self.conn = psycopg2.connect(db)
            except Exception:
                logging.fatal("Cannot ope database")
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
        r = None
        try:
            r = self.cur.fetchone()
        except Exception:
            logging.error('Cannot read data from DB')
        if r:
            res = dict(zip(self.keys, r))
        else:
            res = None
        return res

if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        db = argv[1]
    else:
        db = ""
    myfile = DbReader(db=db,
                      sql="SELECT * FROM monitoring_obs ORDER BY datetime")
    res = myfile.GetNext()
    while res:
        print(res)
        res = myfile.GetNext()
