#!/usr/bin/env python

import socket,sys

print sys.argv[1]
print sys.argv[2]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((sys.argv[1],int(sys.argv[2])))

while 1: 
    msg = raw_input("message: ")
    sock.send(msg)
    sock.recv(10)
sock.close()
