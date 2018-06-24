#!/usr/bin/env python

import sys
import os
import fcntl
import subprocess
from optparse import OptionParser
import select

# Mwa-ha-ha, this is easiest way. Hardly portable to windowz, but who cares?
TAILF_COMMAND = ['/usr/bin/tail', '-F', '-n']

def tailf_init(filename, start_count, tailf_command):
    process = subprocess.Popen(tailf_command + [str(start_count), filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # set non-blocking mode for file
    fl = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
    fcntl.fcntl(process.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    fl = fcntl.fcntl(process.stderr, fcntl.F_GETFL)
    fcntl.fcntl(process.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    return process

def tailf(filename, start_count=0, ignore_stderr=True, tailf_command=TAILF_COMMAND):
    
    
    process = tailf_init(filename, start_count, tailf_command)
    
    buf = ''
    
    while True:
        reads, writes, errors = select.select([process.stdout, process.stderr], [], [process.stdout, process.stderr], 0.1)
        if process.stdout in reads:
            buf += process.stdout.read()
            lines = buf.split('\n')
            
            if lines[-1] == '':
                #whole line received
                buf = ''
            else:
                buf = lines[-1]
            lines = lines[:-1]

            if lines:
                for line in lines:
                    if ignore_stderr:
                        yield line
                    else:
                        yield (line, None)
                
        if process.stderr in reads:
            stderr_input = process.stderr.read()
            if not ignore_stderr:
                yield (None, stderr_input)

        if process.stderr in errors or process.stdout in errors:
            print "Error received. Errors: ", errors
            process = tailf_init(filename, tailf_command)
            

if __name__ == "__main__":
    
    parser = OptionParser(usage=u"%prog <filename>\nWatch for file tail (with retry) and process all incoming data")
    parser.add_option("-n", "--lines", dest="start_count", type="int", default=0, help="Output last N lines (default: %DEFAULT)")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("Please provide filename as argument")
    
    for line in tailf(args[0], options.start_count):
        print line
    
