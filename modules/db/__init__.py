#!/usr/bin/env python
# coding: interpy

import sqlite3
import modules.name.user as username
import modules.logging.logger as logger

user    = username.name()
DB_PATH = "/home/" + user + "/.imagecapture"
DB_FILE = "" + DB_PATH + "/imagecapture.db"
db      = sqlite3.connect(DB_FILE)

try:
    query = db.execute("select * from connected")
except sqlite3.OperationalError:
    db.execute('''CREATE TABLE connected(id integer primary key AUTOINCREMENT, location_bool text not null, coordinates text not null, ip_addr text not null);''')
    logger.log("Table(connected) does not exist, creating now.")
