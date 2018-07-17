#!/usr/bin/env python

import sqlite3,os,re

from lib.db import db 
from lib.db import user 
from subprocess import call

import lib.logging.logger as logger

def fileExists(_file):
    return os.path.exists(_file)

def writeToDB(location_bool, coordinates, ip_addr): 
    if location_bool is None or coordinates is None or ip_addr is None:
        return
    elif not re.search("true|false|NULL", location_bool, re.I|re.M):
        logger.log("ERROR", str(location_bool) + " is not a known mode.")
    elif not re.search("\A\((\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+\)|NULL", coordinates, re.M | re.I): 
        logger.log("ERROR", "Improper coordinate format -> " + str(coordinates) + ".")
    elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$|NULL", ip_addr, re.M|re.I):
        logger.log("ERROR", "Improper ip address format -> " + str(ip_addr) + ".") 
    else:
        coor = re.sub("[\(\)]", "", str(coordinates))
        db.execute("insert into connected (location_bool, coordinates, ip_addr) values(\"" + str(location_bool) + "\", \"" + str(coor) + "\", \"" + str(ip_addr) + "\")")
        db.commit()

def readFromDB(column):
    query = db.execute("select * from connected")
    for row in query:
        if column == 'location_bool' and row[1] is not None:
            return str(row[1])
        elif column == 'coordinates' and row[2] is not None:
            return str(row[2])
        elif column == 'ip_addr' and row[3] is not None:
            return str(row[3])
        else:
            logger.log("ERROR", "Not a known column or DB is empty.") 
            return

def updateDB(column,value):
    if column is None or value is None:
        return
    try:
        if readFromDB('location_bool') is None or readFromDB('coordinates') is None or readFromDB('ip_addr') is None:
            logger.log("ERROR", "You must write to the database first before updating!")
            return
        elif re.search("true|false", value, re.I|re.M) and column == 'location_bool':
            db.execute("update connected set location_bool = \"" + value + "\"")
            db.commit()
        elif re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+", value, re.M | re.I) and column == 'coordinates':    
            db.execute("update connected set coordinates = \"" + value + "\"")
            db.commit()
        elif re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", value, re.M|re.I) and column == 'ip_addr':
            db.execute("update connected set ip_addr = \"" + value + "\"")
            db.commit()
        else:
            logger.log("ERROR", str(column) + " is not a known column for the connected table in the imagecapture db.")
            return
    except sqlite3.OperationalError:
      logger.log("ERROR", "The database is lock, could not add coordinates to DB.")

def addLocationToDB(location_bool):
    try:
        if readFromDB('location_bool') is None:
            writeToDB(location_bool,'NULL','NULL')
            logger.log("INFO", "Writing location_bool to DB.")
        elif readFromDB('location_bool') != location_bool and readFromDB('location_bool') is not None:
            updateDB('location_bool', location_bool)
            logger.log("INFO", "Updating location_bool variable in DB.")
        else:
            return
    except sqlite3.OperationalError:
        call(['/usr/bin/rm', '/home/' + user.name() + '/.imagecapture/imagecapture.db'])
        logger.log("ERROR", "The database is locked, could not add location_bool to DB.")
        pass

def addCoordinatesToDB(coordinates):
    try:
        if readFromDB('coordinates') is None:
            writeToDB('NULL', coordinates,'NULL')
            logger.log("INFO", "Writing coordinates to DB.")
        elif not readFromDB('coordinates') == coordinates and readFromDB('coordinates') is not None:
            updateDB('coordinates', ip_addr)
            logger.log("INFO", "Updating coordinates variable in DB.")
        else:
            return
    except sqlite3.OperationalError:
        call(['/usr/bin/rm', '/home/' + user.name() + '/.imagecapture/imagecapture.db'])
        logger.log("ERROR", "The database is locked, could not add coordinates to DB.")
        pass

def addIpToDB(ip_addr):
    try:
        if readFromDB('ip_addr') is None:
            writeToDB('NULL','NULL', ip_addr)
            logger.log("INFO", "Writing ip_addr to DB.")
        elif readFromDB('ip_addr') != ip_addr and readFromDB('ip_addr') is not None:
            updateDB('ip_addr', ip_addr)
            logger.log("INFO", "Updating ip_addr variable in DB.")
        else:
            return
    except sqlite3.OperationalError:
        call(['/usr/bin/rm', '/home/' + user.name() + '/.imagecapture/imagecapture.db'])
        logger.log("ERROR", "The database is locked, could not add IP address to DB.")
        pass
