#!/usr/bin/env python
# coding: interpy

import socket,sys
import modules.logging.logger as logger

class Server:

    def __init__(self,host='127.0.0.1',port=8081):
        global s
        self.host = host
        self.port = port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.log('Socket created')

    def bindToSocket(self):
        try:
            s.bind((self.host, self.port))
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

S = Server()
S.bindToSocket()
