#!/usr/bin/env python

import urllib2
import modules.db.db as db
from urllib2 import urlopen

ip_addr = urlopen('http://ip.42.pl/raw').read()

db.addIpToDB(ip_addr)
