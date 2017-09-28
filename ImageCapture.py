#!/usr/bin/env python
# coding: interpy

import webbrowser as wb

import sys,os,re,smtplib,fcntl,webbrowser
import subprocess,time,cv2,socket,struct

from tailf import tailf
from optparse import OptionParser

from email.MIMEImage import MIMEImage
from subprocess import Popen, check_call
from email.MIMEMultipart import MIMEMultipart

parser = OptionParser()
parser.add_option("-e", "--email", dest='email')
parser.add_option("-p", "--password", dest='password')
parser.add_option("-v", "--video", dest='video', default=0, help="Specify camera location.")
parser.add_option("-P", "--port", dest='port', default=587, help="E-mail port defaults to 587 if not specified.")
parser.add_option("-a", "--attempts", dest='attempts', default=3, help="Number of failed attempts defaults to 3.")
parser.add_option("-L", "--location", dest='location', action="store_true", default=False, help="Enable location capturing.") 
parser.add_option("-l", "--log-file", dest='logfile', default='/var/log/auth.log', help="Tail log defaults to /var/log/auth.log.")
parser.add_option("-c", "--enable-cam", dest='enablecam', action="store_true", default=False, help="Enable cam capture of intruder.")
parser.add_option("-A", "--auto-login", dest='autologin', action="store_true", default=False, help="Auto login user after no of failed attempts.")
parser.add_option("-C", "--clear-autologin", dest='clear', action="store_true", default=False, help="Remove autologin. Must be root to use this feature.")
parser.add_option("-s", "--allow-sucessful", dest='allowsucessful', action="store_true", default=False, help="Run ImageCapture even if login is sucessful.")
(options, args) = parser.parse_args()

print "options: #{options}\n"

def file_exists(file):
    return os.path.exists(file)

if not file_exists(options.logfile):
    logfile = '/var/log/auth.log'
else:
    logfile = options.logfile

if options.video is not None:
    video = options.video
else:
    video = 0

if options.email is not None:
    send_email = True
    sender,to = options.email,options.email

if options.password is not None:
    send_email = True
    password = options.password

if options.password is None or options.email is None:
    send_email = False

port           = options.port
clear          = options.clear
attempts       = options.attempts
location       = options.location
enablecam      = options.enablecam
allowsucessful = options.allowsucessful
comm           = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
user           = re.search("(\w+)", str(comm.stdout.read())).group()

def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

#print getHwAddr('wlo1')

def get_location():
    if not location:
        return
    time.sleep(3)
    Popen(["/opt/google/chrome/chrome --user-data-dir=/home/#{user}/.imagecapture --no-sandbox https://justdrive-app.com/imagecapture/index.html?Email=#{sender}"], shell=True) 

def add_to_group():
    os.system("sudo usermod -a -G nopasswdlogin #{user}")

def remove_from_group():
    os.system("sudo gpasswd -d #{user} nopasswdlogin")

def take_picture():
    camera = cv2.VideoCapture(video)
    if not camera.isOpened():
        print "No cam available at #{video}"
        return
    elif not enablecam:
        print "Taking pictures from webcam was not enabled."
        return
    elif not camera.isOpened() and video == 0:
        print "ImageCapture does not detect a camera."
        return
    print "Taking picture."
    time.sleep(0.1) # Needed or image will be dark.
    return_value, image = camera.read()
    cv2.imwrite("intruder.png", image)
    del(camera)

def send_mail(sender,to,password,port,subject,body):
    try:
        message = MIMEMultipart()
        message['Body'] = body
        message['Subject'] = subject
        message.attach(MIMEImage(file("intruder.png").read()))
        mail = smtplib.SMTP('smtp.gmail.com',port)
        mail.starttls()
        mail.login(sender,password)
        mail.sendmail(sender, to, message.as_string())
        print "\nSent email successfully.\n"
    except smtplib.SMTPAuthenticationError:
        print "\nCould not athenticate with password and username!\n"

def user_present(username):
    with open("/etc/group", "r") as f:
        for line in f:
            nop = re.search("^nopasswdlogin.*(#{username})",line)
            if nop is not None and nop:
                return True
            elif nop is not None and not nop:
                return False 

def auto_login_remove():
    if not options.autologin and user_present(user):
        remove_from_group()

def clear_auto_login():
    if len(sys.argv) > 2 and clear:
        print "Too many arguments for clear given. Exiting now." 
        sys.exit(1)
    if clear and user_present(user):
        remove_from_group()
        sys.exit(1)
    elif clear and not user_present(user):
        sys.exit(1)

def auto_login():
    if options.autologin:
        print "Automatically logging you in now."
        add_to_group()
  
def initiate(count):
    if count == attempts or options.allowsucessful:
        return True
    else:
        return False

def tail_file(logfile):

    count = 0

    auto_login_remove()

    for line in tailf(logfile):

        s = re.search("(^.*\d+:\d+:\d+).*password.*pam: unlocked login keyring", line, re.I | re.M)
        f = re.search("(^.*\d+:\d+:\d+).*pam_unix.*:auth\): authentication failure", line, re.I | re.M)

        if f and not allowsucessful:
            count += 1
            sys.stdout.write("Failed login via GDM at #{f.group(1)}:\n#{f.group()}\n\n")
            if initiate(count):
                auto_login()
                take_picture()
                get_location()
                if send_email:
                    send_mail(sender,to,password,port,'Failed GDM login!',"Someone tried to login into your computer and failed #{attempts} times.")
            time.sleep(1)
        if s and allowsucessful:
            sys.stdout.write("Sucessful login via GDM at #{s.group(1)}:\n#{s.group()}\n\n")
            auto_login()
            take_picture()
            get_location()
            if send_email:
                send_mail(sender,to,password,port,'Sucessful GDM login!',"Someone logged into your computer.")
            time.sleep(1)

clear_auto_login()

while True:
    tail_file(logfile)
