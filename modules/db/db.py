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
        db.execute('''CREATE TABLE connected(id integer primary key AUTOINCREMENT, get_location text not null, coordinates text not null, ip_addr text not null);''')
        print "Table(connected) does not exist, creating now."

def writeToDB(location_bool, coordinates, ip_addr): 
    if location_bool is None || coordinates is None || ip_addr is None:
        return
    elif not re.search("true|false", location_bool, re.I|re.M):
        logger.log("#{location_bool} is not a known mode.")
    elif not re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+",string, re.M | re.I): 
        logger.log("Improper coordinate format -> #{coordinates}.")
    elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", ip_addr, re.M|re.I):
        logger.log("Improper ip address format -> #{ip_addr}.") 
    else:
        db.execute("insert into connected (get_location) values(#{location_bool}, #{coordinates}, #{ip_addr})")

def readFromDB():
    if not fileExists("/home/#{user}/.imagecapture/imagecapture.db"):
        open("/home/#{user}/.imagecapture/cache", "w").write("true")
    return open("/home/#{user}/.imagecapture/cache", "r").read() == boolean_string

def updateDB():
    #
