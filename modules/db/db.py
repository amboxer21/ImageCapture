#!/usr/bin/env python
# coding: interpy

import sqlite3,os,re
import modules.name.user as username
import modules.logging.logger as logger

user = username.name()
DB_PATH = "/home/#{user}/.imagecapture"
DB_FILE = "#{DB_PATH}/imagecapture.db"

def fileExists(_file):
    return os.path.exists(_file)

def init():
    if fileExists(DB_FILE):
        db = sqlite3.connect("#{DB_FILE}")
    else:
        logger.log("File(#{DB_FILE}) does not exist. Exiting now.")
        print "File(#{DB_FILE}) does not exist. Exiting now."
    

def findOrCreateTable():
    try:
        query = db.execute("select * from connected")
        print "Table(connected) already exists."
    except sqlite3.OperationalError:
        db.execute('''CREATE TABLE connected(id integer primary key AUTOINCREMENT, get_location text not null);''')
        print "Table(connected) does not exist, creating now."

def writeToDB(value): 
    if value is None:
        return
    if re.search("true|false", value, re.I|re.M):
        db.execute("insert into connected (get_location) values(#{value})")
    elif not re.search("true|false", value, re.I|re.M):
        raise NameError("#{value} is not a known mode.")

def readFromDB():
    if not fileExists("/home/#{user}/.imagecapture/imagecapture.db"):
        open("/home/#{user}/.imagecapture/cache", "w").write("true")
    return open("/home/#{user}/.imagecapture/cache", "r").read() == boolean_string
