#!/usr/bin/env python
    
import modules.db.db as db
import modules.net.net as net
import modules.gdm.gdm as gdm
import modules.name.user as user
import modules.logging.logger as logger

from tailf import tailf
from urllib2 import urlopen
from threading import Thread
from optparse import OptionParser
from subprocess import Popen, call
from email.MIMEImage import MIMEImage
from distutils.spawn import find_executable
from email.MIMEMultipart import MIMEMultipart

import sys,os,re,smtplib,fcntl,webbrowser,logging
import subprocess,time,cv2,socket,struct,urllib2,logging.handlers

class GetLocation(Thread):
    def __init__(self,website,email,browser):
        Thread.__init__(self)
        if re.match("(\/)",browser) is None:
            print("Please provide full path to browser. Exiting now!") and sys.exit(0)
        self.count   = 0
        self.email   = email
        self.website = website
        self.browser = browser

    def browser_exists(self,browser):
        return find_executable(browser)

    def run (self):
        for b in ['/usr/bin/firefox','/usr/bin/opera','/opt/google/chome/chrome']:
            if self.browser_exists(self.browser) and self.count == 0:
                browser = re.match("(\/\w+)(.*\/)(\w+)",self.browser).group(3)
                break
            self.count += 1
            if self.count > len(Browsers):
                print("ImageCapturePy only supports Chrome, Opera, and Firefox. Please install one if able.")
            elif self.browser_exists(b):
                browser = re.match("(\/\w+)(.*\/)(\w+)",b).group(3)
                break
        if browser == 'chrome':
            call([self.browser, "--user-data-dir=/home/" + user.name() + "/.imagecapture", "--no-sandbox",
                "" + self.website + "?Email=" + self.email])
        elif browser == 'firefox':
            call([browser, "--new-window \'" + self.website + "?Email=" + self.email + "\'"])
        #elif browser == 'opera':

class ImageCapture():
    
    def __init__(self):
        parser = OptionParser()
        parser.add_option("-e", "--email", dest='email',
            default="example@gmail.com")
        parser.add_option("-p", "--password", dest='password',
            default="password")
        parser.add_option("-V", "--video", dest='video',
            default=0, help="Specify camera location.")
        parser.add_option("-v", "--verbose", dest='verbose', action="store_true",
            default=False, help="Print the options passed to ImageCapturePy.")
        parser.add_option("-P", "--port", dest='port',
            default=587, help="E-mail port defaults to 587 if not specified.")
        parser.add_option("-a", "--attempts", dest='attempts',
            default=3, help="Number of failed attempts defaults to 3.")
        parser.add_option("-L", "--location", dest='location', action="store_true",
            default=False, help="Enable location capturing.") 
        parser.add_option("-l", "--log-file", dest='logfile',
            default='/var/log/auth.log', help="Tail log defaults to /var/log/auth.log.")
        parser.add_option("-c", "--enable-cam", dest='enablecam', action="store_true",
            default=False, help="Enable cam capture of intruder.")
        parser.add_option("-A", "--auto-login", dest='autologin', action="store_true", 
            default=False, help="Auto login user after no of failed attempts.")
        parser.add_option("-w", "--website", dest='website',
            default='https://justdrive-app.com/imagecapture/index.html', help="Use alternate website to capture location.")
        parser.add_option("-C", "--clear-autologin", dest='clear', action="store_true",
            default=False, help="Remove autologin. Must be root to use this feature.")
        parser.add_option("-s", "--allow-sucessful", dest='allowsucessful', action="store_true",
            default=False, help="Run ImageCapture even if login is sucessful.")
        parser.add_option("-B", "--browser", dest="browser",
            default="/opt/google/chrome/chrome", help="Select the browser used to grab geolocation data.")
        (options, args) = parser.parse_args()

        self.port           = options.port
        self.clear          = options.clear
        self.email          = options.email
        self.video          = options.video
        self.website        = options.website
        self.verbose        = options.verbose
        self.browser        = options.browser
        self.password       = options.password
        self.attempts       = options.attempts
        self.location       = options.location
        self.enablecam      = options.enablecam
        self.autologin      = options.autologin
        self.allowsucessful = options.allowsucessful
        self.ip_addr        = urlopen('http://ip.42.pl/raw').read()
        self.send_email     = False

        db.addIpToDB(self.ip_addr)

        if os.path.exists(options.logfile):
            self.logfile = options.logfile

        if options.email is not None:
            self.sender,self.to = options.email,options.email

        if options.password is not None:
            self.password = options.password

        if not str(self.password) == 'password' and not str(self.sender) == 'example@gmail.com':
            self.send_email = True
        elif str(self.password) == 'password' and str(self.sender) == 'example@gmail.com':
            self.send_email = False
        elif (str(self.password) == 'password' and not str(self.sender) == 'example@gmail.com' or
            str(self.sender) == 'example@gmail.com' and not str(self.password) == 'password'):
                print("\nERROR: Must supply both the E-mail and password options or none at all!\n")
                parser.print_help()
                sys.exit(0)

        if self.location:
            if not self.send_email:
                print("\nERROR: The location options requires an E-mail and password!\n")
                parser.print_help()
                sys.exit(0)
            elif not len(os.listdir('/home/' + user.name() + '/.imagecapture/')) > 2:
                self.getLocation('init')

        if options.verbose:
            print "\nOPTIONS => " + str(options) + "\n"

    def isLoctionSupported(self,process):
        return find_executable(process) is not None
    
    def getLocation(self,init=None):
        if not self.location:
            return
        elif self.location and not self.send_email:
            logger.log("Cannot E-mail your location without your E-mail and password. Please use the help option and search for -e and -p.\n")
            sys.exit(0)

        while db.readFromDB('location_bool') == 'true' or init == 'init':
            if net.connected():
                time.sleep(3)
                db.addLocationToDB('false')
                if self.send_email:
                    try:
                        logger.log("ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,password,port,"Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed " + attempts + "times.")
                    except:
                        pass
                try:
                    logger.log("ImageCapture - Grabbing location now.")
                    GetLocation(self.website,self.to,self.browser).start()
                    if init == 'init':
                        break
                except:
                    logger.log("ImageCapture - Could not open your browser.")
                    pass
            else:
                break
    
    def takePicture(self):
        camera = cv2.VideoCapture(self.video)
        if not camera.isOpened():
            logger.log("ImageCapture - No cam available at " + str(self.video) + ".")
            return
        elif not self.enablecam:
            logger.log("ImageCapture - Taking pictures from webcam was not enabled.")
            return
        elif not camera.isOpened() and self.video == 0:
            logger.log("ImageCapture - ImageCapture does not detect a camera.")
            return
        logger.log("ImageCapture - Taking picture.")
        time.sleep(0.1) # Needed or image will be dark.
        image = camera.read()[1]
        cv2.imwrite("/home/" + user.name() + "/.imagecapture/intruder.png", image)
        del(camera)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            if self.enablecam:
              message.attach(MIMEImage(file("/home/" + user.name() + "/.imagecapture/intruder.png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            logger.log("ImageCapture - Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            logger.log("ImageCapture - Could not athenticate with password and username!")
        except:
            logger.log("ImageCapture - Unexpected error in sendMail():")
    
    def failedLogin(self,count):
        print("count -> " + str(count))
        if count == int(self.attempts) or self.allowsucessful:
            print("return True")
            return True
        else:
            print("return False")
            return False
    
    def tailFile(self,logfile):
    
        count = 0
    
        gdm.autoLoginRemove(self.autologin, user.name())
    
        for line in tailf(logfile):
    
            s = re.search("(^.*\d+:\d+:\d+).*password.*pam: unlocked login keyring", line, re.I | re.M)
            f = re.search("(^.*\d+:\d+:\d+).*pam_unix.*:auth\): authentication failure", line, re.I | re.M)
    
            if f and not self.allowsucessful:
                count += 1
                sys.stdout.write("Failed login via GDM at " + f.group(1) + ":\n" + f.group() + "\n\n")
                if self.failedLogin(count):
                    print("user -> " + user.name())
                    gdm.autoLogin(self.autologin, user.name())
                    self.takePicture()
                    db.addLocationToDB('true')
                    self.getLocation()
                    if not self.enablecam and self.send_email:
                        try:
                            logger.log("ImageCapture - Sending E-mail now.")
                            self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + self.ip_addr + "!",
                                "Someone tried to login into your computer and failed " + self.attempts + " times.")
                        except:
                            pass
                time.sleep(1)
            if s and self.allowsucessful:
                sys.stdout.write("Sucessful login via GDM at " + s.group(1) + ":\n" + s.group() + "\n\n")
                gdm.autoLogin(self.autologin, user.name())
                self.takePicture()
                db.addLocationToDB('true')
                self.getLocation()
                if not self.enablecam and self.send_email:
                    try:
                        logger.log("ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed " + self.attempts + " times.")
                    except:
                        pass
                time.sleep(1)

        db.addIpToDB(self.ip_addr)

    def main(self):

        gdm.clearAutoLogin(self.clear, user.name())
        self.getLocation()

        while True:
            if not self.logfile:
                print("Could not find logfile -> " + self.logfile + ". Exiting now.")
                break
            try:
                self.tailFile(self.logfile)
            except KeyboardInterrupt:
                print(" [Control C caught] - Exiting ImageCapturePy now!")
                break
    
imagecapture = ImageCapture()
imagecapture.main()
