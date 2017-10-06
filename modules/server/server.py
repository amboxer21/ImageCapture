#!/usr/bin/env python
# coding: interpy

import socket,sys

import modules.logging.logger as logger

def __init__(self,host='127.0.0.1',port=8080)
    # 
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logger.log('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((host, port))
except socket.error as msg:
    logger.log('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
logger.log('Socket bind complete')
 
s.listen(10)

logger.log('Socket now listening')
 

while 1:
    conn, addr = s.accept()
    logger.log('Connected with ' + addr[0] + ':' + str(addr[1]))
    data = conn.recv(1024)
    logger.log("mesg: #{data}")
     
s.close()
