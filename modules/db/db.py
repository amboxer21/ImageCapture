#!/usr/bin/env python
# coding: interpy

import sqlite3,os,re
import modules.name.user as username
import modules.logging.logger as logger

user    = username.name()
DB_PATH = "/home/#{user}/.imagecapture"
DB_FILE = "#{DB_PATH}/imagecapture.db"
db      = sqlite3.connect(DB_FILE)

def fileExists(_file):
    return os.path.exists(_file)

def findOrCreateTable():
    try:
        query = db.execute("select * from connected")
        print "Table(connected) already exists."
    except sqlite3.OperationalError:
        db.execute('''CREATE TABLE connected(id integer primary key AUTOINCREMENT, location_bool text not null, coordinates text not null, ip_addr text not null);''')
        print "Table(connected) does not exist, creating now."

def writeToDB(location_bool, coordinates, ip_addr): 
    if location_bool is None or coordinates is None or ip_addr is None:
        return
    elif not re.search("true|false", location_bool, re.I|re.M):
        logger.log("#{location_bool} is not a known mode.")
    elif not re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+", coordinates, re.M | re.I): 
        logger.log("Improper coordinate format -> #{coordinates}.")
    elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", ip_addr, re.M|re.I):
        logger.log("Improper ip address format -> #{ip_addr}.") 
    else:
        db.execute("insert into connected (location_bool, coordinates, ip_addr) values(#{location_bool}, #{coordinates}, #{ip_addr})")
        db.commit()

def readFromDB(column):
    query = db.execute("select * from test")
    for row in query:
        if column == 'location_bool':
            return str(row[0])
        elif column == 'coordinates':
            return str(row[1])
        elif column == 'ip_addr':
            return str(row[2])
        else:
            logger.log("Not a known column for the connected table in the imagecapture db.") 
            return

def updateDB(column,value):
    if column is None or value is None:
        return
    elif re.search("true|false", value, re.I|re.M) and column == 'location_bool':
        db.execute("update connected set location_bool = \"#{location_bool}\")")
        db.commit()
    elif re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+",value, re.M | re.I) and column == 'coordinates':    
        db.execute("update connected set coordinates = \"#{coordinates}\")")
        db.commit()
    elif re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", value, re.M|re.I) and column == 'ip_addr':
        db.execute("update connected set ip_addr = \"#{ip_addr}\")")
        db.commit()
    else:
        logger.log("#{column} is not a known column for the connected table in the imagecapture db.")
        return 
