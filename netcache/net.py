#!/usr/bin/env python
# coding: interpy

import urllib2,re,subprocess
from subprocess import Popen, check_call
from urllib2 import urlopen, HTTPError, URLError

comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
user = re.search("(\w+)", str(comm.stdout.read())).group()

def connected():
    try:
        urllib2.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib2.URLError as err:
        return False

def fileOp(mode,msg):
    if msg is None:
        return open("/home/#{user}/.imagecapture/cache", mode).read()
    else:
        open("/home/#{user}/.imagecapture/cache", mode).write(msg)

def setCache(boolean): 
    if re.search("true|false", boolean, re.I|re.M)
    fileOp("w", boolean)
