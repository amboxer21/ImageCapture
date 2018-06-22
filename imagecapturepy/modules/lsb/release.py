#!/usr/bin/env python

import subprocess,re

def release():
    comm = subprocess.Popen(["lsb_release -irs"], shell=True, stdout=subprocess.PIPE)
    return re.search("(\w+)", str(comm.stdout.read())).group()
