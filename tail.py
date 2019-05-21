#!/usr/bin/env python
    
import os
import sys
import fcntl
import select
import subprocess
    
from optparse import OptionParser
    
class Tail(object):

    def __init__(self):
        self.buffer       = str()
        self.tail_command = ['/usr/bin/tail', '-F', '-n0']

    def process(self,filename):

        process = subprocess.Popen(
            self.tail_command + [filename], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    
        # set non-blocking mode for file
        function_control = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
        fcntl.fcntl(process.stdout, fcntl.F_SETFL, function_control | os.O_NONBLOCK)
    
        function_control = fcntl.fcntl(process.stderr, fcntl.F_GETFL)
        fcntl.fcntl(process.stderr, fcntl.F_SETFL, function_control | os.O_NONBLOCK)
        
        return process
    
    def f(self, filename, ignore_stderr=True):

        process = self.process(filename)
        
        while True:
            reads, writes, errors = select.select(
                [process.stdout, process.stderr], [], [process.stdout, process.stderr], 0.1
            )
            if process.stdout in reads:
                self.buffer += process.stdout.read()
                lines = self.buffer.split('\n')
                
                if '' in lines[-1]:
                    #whole line received
                    self.buffer = str()
                else:
                    self.buffer = lines[-1]
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
                print("Error received. Errors: ", errors)
                process = self.process(filename)
                
    
if __name__ == "__main__":
        
    parser = OptionParser()
    parser.add_option("-n", "--lines",
        dest="file_name", help="File for program tail.")
        
    (options, args) = parser.parse_args()
        
    if len(args) != 1:
        parser.error("Please provide filename as argument")     

    tail = Tail()   

    for line in tail.f(args[0]):
        print(line)
