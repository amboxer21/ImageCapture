#!/usr/bin/env python
    
import modules.db.db as db
import modules.net.net as net
import modules.gdm.gdm as gdm
import modules.name.user as user
import modules.logging.logger as logger
import modules.version.number as version

from tailf import tailf
from urllib2 import urlopen
from threading import Thread
from optparse import OptionParser
from subprocess import Popen, call
from email.MIMEImage import MIMEImage
from distutils.spawn import find_executable
from email.MIMEMultipart import MIMEMultipart

import sys,os,re,smtplib,fcntl,webbrowser,logging
import subprocess,time,cv2,socket,struct,logging.handlers

# importing urllib2 works on my Linux Mint box
# but not my Gentoo box and here is the fix!
try:
    import urllib2
except ImportError:
    import urllib

class GetLocation(Thread):
    def __init__(self,website,email,browser):
        Thread.__init__(self)
        self.count   = 0
        self.email   = email
        self.website = website
        self.browser = browser

    def browser_exists(self,browser):
        return find_executable(browser)

    def run(self):
        for b in ['/opt/google/chome/chrome','/usr/bin/firefox','/usr/bin/opera']:
            if self.browser_exists(self.browser) and self.count == 0:
                browser = re.match("(\/\w+)(.*\/)(\w+)",self.browser).group(3)
                break
            self.count += 1
            if self.count > len(b):
                logger.log("ERROR", "ImageCapturePy only supports Chrome, Opera, and Firefox. Please install one if able.")
            elif self.browser_exists(b):
                browser = re.match("(\/\w+)(.*\/)(\w+)",b).group(3)
                break
        if browser == 'chrome':
            call([self.browser, "--user-data-dir=/home/" + user.name() + "/.imagecapture", "--no-sandbox",
                "" + self.website + "?Email=" + self.email])
        elif browser == 'firefox':
            call([browser, "--new-window", "" + self.website + "?Email=" + self.email + "\""])
        #elif browser == 'opera':
        else:
            logger.log("WARNING", "\n\nBrowser not found and location functionality will not work.\n\n")
            sys.sleep(2)

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
            default='https://imagecapturepy.herokuapp.com/index.html', help="Use alternate website to capture location.")
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
                logger.log("ERROR", "Must supply both the E-mail and password options or none at all!")
                parser.print_help()
                sys.exit(0)

        if re.match("(\/)",self.browser) is None:
            logger.log("ERROR", "Please provide full path to browser!")
            sys.exit(0)

        if self.location:
            if not self.send_email:
                logger.log("ERROR", "The location options requires an E-mail and password!")
                parser.print_help()
                sys.exit(0)
            elif not self.autologin:
                logger.log("ERROR","The location feature requires the autologin option to be set.")
                sys.exit(0)
            elif not len(os.listdir('/home/' + user.name() + '/.imagecapture/')) > 2:
                self.getLocation('init')

        if options.verbose:
            logger.log("INFO", "OPTIONS: " + str(options))

    def isLoctionSupported(self,process):
        return find_executable(process) is not None
    
    def getLocation(self,init=None):
        if not self.location:
            return
        elif self.location and not self.send_email:
            logger.log("ERROR","Cannot E-mail your location without your E-mail and password. Please use the help option and search for -e and -p.\n")
            sys.exit(0)

        while db.readFromDB('location_bool') == 'true' or init == 'init':
            if net.connected():
                time.sleep(3)
                db.addLocationToDB('false')
                if self.send_email:
                    try:
                        logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,password,port,"Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed " + attempts + "times.")
                    except:
                        pass
                try:
                    logger.log("INFO","ImageCapture - Grabbing location now.")
                    GetLocation(self.website,self.to,self.browser).start()
                    if init == 'init':
                        break
                except:
                    logger.log("WARNING","ImageCapture - Could not open your browser.")
                    pass
            else:
                break
    
    def takePicture(self):
        if not self.enablecam:
            return
        camera = cv2.VideoCapture(self.video)
        if not camera.isOpened():
            logger.log("ERROR","ImageCapture - No cam available at " + str(self.video) + ".")
            return
        elif not self.enablecam:
            logger.log("WARNING","ImageCapture - Taking pictures from webcam was not enabled.")
            return
        elif not camera.isOpened() and self.video == 0:
            logger.log("WARNING","ImageCapture - ImageCapture does not detect a camera.")
            return
        logger.log("INFO","ImageCapture - Taking picture.")
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
            logger.log("INFO","ImageCapture - Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            logger.log("ERROR","ImageCapture - Could not athenticate with password and username!")
        except:
            logger.log("ERROR","ImageCapture - Unexpected error in sendMail():")
    
    def failedLogin(self,count):
      logger.log("INFO", "count: " + str(count))
        if count == int(self.attempts) or self.allowsucessful:
            logger.log("INFO", "failedLogin True")
            return True
        else:
            logger.log("INFO", "failedLogin False")
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
                    logger.log("INFO", "user: " + user.name())
                    gdm.autoLogin(self.autologin, user.name())
                    self.takePicture()
                    db.addLocationToDB('true')
                    self.getLocation()
                    if not self.enablecam and self.send_email:
                        try:
                            logger.log("INFO","ImageCapture - Sending E-mail now.")
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
                        logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed " + self.attempts + " times.")
                    except:
                        pass
                time.sleep(1)

        db.addIpToDB(self.ip_addr)

    def main(self):

        if not version.number() == '2.7.5':
            logger.log("ERROR", "Only python version 2.7.5 is supported.")
            sys.exit(0)

        gdm.clearAutoLogin(self.clear, user.name())
        self.getLocation()

        while True:
            try:
                self.tailFile(self.logfile)
            except IOError as ioError:
                logger.log("ERROR", "IOError: " + str(ioError))
            except KeyboardInterrupt:
                logger.log("INFO", " [Control C caught] - Exiting ImageCapturePy now!")
                break
    
if __name__ == '__main__':
    imagecapture = ImageCapture()
    imagecapture.main()
