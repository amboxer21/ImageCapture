#!/usr/bin/env python
# coding: interpy
    
#import webbrowser as wb
#import modules.db.db as db
#import modules.net.net as net
import modules.gdm.gdm as gdm
import modules.name.user as user
#import modules.logging.logger as logger
    
from tailf import tailf
from urllib2 import urlopen
from optparse import OptionParser
from subprocess import Popen, call
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
    
import sys,os,re,smtplib,fcntl,webbrowser,logging
import subprocess,time,cv2,socket,struct,urllib2,logging.handlers

class ImageCapture():
    
    global options, args, parser

    parser = OptionParser()
    parser.add_option("-e",
        "--email", dest='email')
    parser.add_option("-p",
        "--password", dest='password')
    parser.add_option("-v",
        "--video", dest='video', default=0, help="Specify camera location.")
    parser.add_option("-P", 
        "--port", dest='port', default=587, help="E-mail port defaults to 587 if not specified.")
    parser.add_option("-a",
        "--attempts", dest='attempts', default=3, help="Number of failed attempts defaults to 3.")
    parser.add_option("-L",
        "--location", dest='location', action="store_true", default=False, help="Enable location capturing.") 
    parser.add_option("-l",
        "--log-file", dest='logfile', default='/var/log/auth.log', help="Tail log defaults to /var/log/auth.log.")
    parser.add_option("-c",
        "--enable-cam", dest='enablecam', action="store_true", default=False, help="Enable cam capture of intruder.")
    parser.add_option("-A",
        "--auto-login", dest='autologin', action="store_true", default=False, help="Auto login user after no of failed attempts.")
    parser.add_option("-w",
        "--website", dest='website', default='https://justdrive-app.com/imagecapture/index.html', help="Use alternate website to capture location.")
    parser.add_option("-C",
        "--clear-autologin", dest='clear', action="store_true", default=False, help="Remove autologin. Must be root to use this feature.")
    parser.add_option("-s",
        "--allow-sucessful", dest='allowsucessful', action="store_true", default=False, help="Run ImageCapture even if login is sucessful.")
    (options, args) = parser.parse_args()
    
    print "\nOPTIONS => #{options}\n"
    
    def getLocation(self):
        if not self.location:
            return
        elif location and not send_email:
            logger.log("Cannot E-mail your location without your E-mail and password. Please use the help option and search for -e and -p.\n")
            sys.exit(0)
    
        while db.readFromDB('location_bool') == 'true':
            if net.connected():
                time.sleep(3)
                db.addLocationToDB('false')
                if send_email:
                    try:
                        logger.log("ImageCapture - Sending E-mail now.")
                        sendMail(self,sender,to,password,port,"Failed GDM login from IP #{ip_addr}!",
                            "Someone tried to login into your computer and failed #{attempts} times.")
                    except:
                        pass
                try:
                    logger.log("ImageCapture - Grabbing location now.")
                    call(["/opt/google/chrome/chrome",
                        "--user-data-dir=/home/#{user}/.imagecapture", "--no-sandbox",
                        "#{website}?Email=#{to}"])
                except:
                    logger.log("ImageCapture - Could not open your browser.")
                    pass
            else:
                break
    
    def takePicture(self):
        camera = cv2.VideoCapture(video)
        if not camera.isOpened():
            logger.log("ImageCapture - No cam available at #{video}.")
            return
        elif not enablecam:
            logger.log("ImageCapture - Taking pictures from webcam was not enabled.")
            return
        elif not camera.isOpened() and video == 0:
            logger.log("ImageCapture - ImageCapture does not detect a camera.")
            return
        logger.log("ImageCapture - Taking picture.")
        time.sleep(0.1) # Needed or image will be dark.
        image = camera.read()[1]
        cv2.imwrite("/home/#{user}/.imagecapture/intruder.png", image)
        del(camera)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            if enablecam:
              message.attach(MIMEImage(file("/home/#{user}/.imagecapture/intruder.png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            logger.log("ImageCapture - Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            logger.log("ImageCapture - Could not athenticate with password and username!")
        except:
            logger.log("ImageCapture - Unexpected error in sendMail():")
    
    def initiate(self,count):
        if count == attempts or options.allowsucessful:
            return True
        else:
            return False
    
    def tailFile(self,logfile):
    
        count = 0
    
        gdm.autoLoginRemove(options.autologin, user)
    
        for line in tailf(logfile):
    
            s = re.search("(^.*\d+:\d+:\d+).*password.*pam: unlocked login keyring", line, re.I | re.M)
            f = re.search("(^.*\d+:\d+:\d+).*pam_unix.*:auth\): authentication failure", line, re.I | re.M)
    
            if f and not allowsucessful:
                count += 1
                sys.stdout.write("Failed login via GDM at #{f.group(1)}:\n#{f.group()}\n\n")
                if initiate(count):
                    gdm.autoLogin(options.autologin, user)
                    takePicture(self)
                    db.addLocationToDB('true')
                    self.getLocation()
                    if not enablecam and send_email:
                        try:
                            logger.log("ImageCapture - Sending E-mail now.")
                            sendMail(self,sender,to,password,port,"Failed GDM login from IP #{ip_addr}!",
                                "Someone tried to login into your computer and failed #{attempts} times.")
                        except:
                            pass
                time.sleep(1)
            if s and allowsucessful:
                sys.stdout.write("Sucessful login via GDM at #{s.group(1)}:\n#{s.group()}\n\n")
                gdm.autoLogin(options.autologin, user)
                takePicture(self)
                db.addLocationToDB('true')
                self.getLocation()
                if not enablecam and send_email:
                    try:
                        logger.log("ImageCapture - Sending E-mail now.")
                        sendMail(self,sender,to,password,port,"Failed GDM login from IP #{ip_addr}!",
                            "Someone tried to login into your computer and failed #{attempts} times.")
                    except:
                        pass
                time.sleep(1)

        db.addIpToDB(ip_addr)

    def __init__(self):

        import modules.db.db as db
        import modules.name.user as user

        if os.path.exists(options.logfile):
            self.logfile = options.logfile

        if options.video is not None:
            video = options.video

        if options.email is not None:
            sender,to = options.email,options.email

        if options.password is not None:
            password = options.password

        if options.password is not None and options.sender is not None:
            send_email = True

        if options.website is not None:
            website = options.website

        user           = user.name()
        port           = options.port
        clear          = options.clear
        attempts       = options.attempts
        self.location       = options.location
        enablecam      = options.enablecam
        allowsucessful = options.allowsucessful
        ip_addr        = urlopen('http://ip.42.pl/raw').read()

        db.addIpToDB(ip_addr)

    def main(self):
        gdm.clearAutoLogin(options.clear, user)
        self.getLocation()

        while True:
            self.tailFile(self.logfile)
    
imagecapture = ImageCapture()
imagecapture.main()
