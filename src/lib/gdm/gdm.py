#!/usr/bin/env python

import os, re, sys

from subprocess import Popen, call

import src.lib.logging.logger as logger
import src.lib.version.version as version

def addToGroup(user):
    os.system("sudo usermod -a -G nopasswdlogin " + str(user))

def removeFromGroup(user):
    os.system("sudo gpasswd -d " + str(user) + " nopasswdlogin")

def userPresent(user):
    with open("/etc/group", "r") as f:
        for line in f:
            nop = re.search("^nopasswdlogin.*(" + str(user) + ")", line)
            if nop is not None and nop:
                return True
            elif nop is not None and not nop:
                return False

def autoLoginRemove(autologin, user):
    if not autologin and userPresent(user):
        removeFromGroup(user)

def clearAutoLogin(clear, user):
    if len(sys.argv) > 2 and clear:
        logger.log("ERROR", "Too many arguments for clear given. Exiting now.")
        sys.exit(1)
    if clear and userPresent(user):
        removeFromGroup(user)
        sys.exit(1)
    elif clear and not userPresent(user):
        sys.exit(1)

def autoLogin(autologin, user):
    if autologin:
        logger.log("INFO", "Automatically logging you in now.")
        addToGroup(user)

def pamD():
    if version.packageManager() == 'rpm':
        return ('password-auth',)
    elif version.packageManager() == 'apt':
        return ('common-auth',)
    elif version.packageManager() == 'eix':
        return ('system-login',)

