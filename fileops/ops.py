#!/usr/bin/env python
# coding: interpy

import re, os

def writeFile(boolean_string, user):
    if boolean_string is None:
        return
    if re.search("true|false", boolean_string, re.I|re.M):
        open("/home/#{user}/.imagecapture/cache", "w").write(boolean_string)
    elif not re.search("true|false", boolean_string, re.I|re.M):
        raise NameError("#{boolean_string} is not a known mode.")

def readFile(boolean_string, user):
    if not fileExists("/home/#{user}/.imagecapture/cache"):
        open("/home/#{user}/.imagecapture/cache", "w").write("true")
    return open("/home/#{user}/.imagecapture/cache", "r").read() == boolean_string

def fileExists(_file):
    return os.path.exists(_file)
