#!/usr/bin/env python

# PEP8 compliant import structure.
import os
import re
import sys
import cv2
import time
import fcntl
import socket
import struct
import logging
import sqlite3
import smtplib
import webbrowser
import subprocess
import logging.handlers
 
from tailf import tailf
from urllib2 import urlopen
from threading import Thread
from optparse import OptionParser
from subprocess import Popen,call
from email.MIMEImage import MIMEImage
from distutils.spawn import find_executable
from email.MIMEMultipart import MIMEMultipart

# importing urllib2 works on my Linux Mint
# box but not my Gentoo box and here is the fix!
try:
    import urllib2
except ImportError:
    import urllib

class Logging():

    def log(self,level,message):
        if re.search("(WARN|INFO|ERROR)", str(level), re.M) is None:
            print(level + " is not a level. Use: WARN, ERROR, or INFO!")
            return
        handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE","/var/log/messages"))
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(os.environ.get("LOGLEVEL", str(level)))
        root.addHandler(handler)
        logging.exception("(" + str(level) + ") " + "ImageCapture - " + str(message))
        return

class ConfigFile(object):

    def __init__(self, file_name):
        self.args_list = []
        self.file_name = file_name

    def config_options(self):
        if not self.file_name:
            for default_opt in config_dict[0].keys():
                config_dict[0][default_opt][0] = config_dict[0][default_opt][1]
                logger.log("INFO", "Setting option(" + default_opt
                    + "): " + str(config_dict[0][default_opt][0]))
            return
        if not os.path.exists(str(self.file_name)):
            logger.log("ERROR", "Config file does not exist.")
            sys.exit(0)
        config_file = open(self.file_name,'r').read().splitlines()
        for line in config_file:
            comm = re.search(r'(^.*)=(.*)', str(line), re.M | re.I)
            if comm is not None:
                if not comm.group(2):
                    config_dict[1].append(comm.group(1))
                config_dict[0][comm.group(1)][0] = comm.group(2)
        return config_dict

    def override_config_options(self):
        pass

    def populate_empty_options(self):
        if config_dict[1] and self.config_file_supplied():
            for opt in config_dict[1]:
                config_dict[0][opt][0] = config_dict[0][opt][1]

    def config_file_supplied(self):
        if re.search(r'(\-C|\-\-config\-file)',str(sys.argv[1:]), re.M) is None:
            return False
        return True

    # This method is written this way instead of just returning
    # len(sys.argv[1:] because this method only grabs the command
    # line switches and not its counterpart. So this method grabs
    # the -v and not the 0 here -> -v 0, making the count 1 and not 2.
    def number_of_args_passed(self):
        for arg in sys.argv[1:]:
            comm = re.search('(\-[a-z])', str(arg), re.M | re.I)
            if comm is not None:
                self.args_list.append(comm.group())
        return len(self.args_list)

    def command_line_options(self):
        pass

    def default_options(self):
        pass

class ImageCapture(ConfigFile):

    def __init__(self,config_dict={},file_name=''):
        super(ImageCapture, self).__init__(file_name)
        configFile = ConfigFile(options.configfile)
        configFile.config_options()
        configFile.populate_empty_options()
        configFile.override_config_options()

        self.ip_addr        = urlopen('http://ip.42.pl/raw').read()
        self.send_email     = False

        self.logfile_sanity_check(options.logfile)
        database.add_ip_to_db(self.ip_addr)

        self.credential_sanity_check()
        self.broswer_path_sanity_check()
        self.location_sanity_check()
        self.verbose()

    def verbose(self):
        if config_dict[0]['verbose'][0]:
            #print(options)
            logger.log("INFO", "Options: " + str(options))

    def broswer_path_sanity_check(self):
        if re.match("(\/)",config_dict[0]['browser'][0]) is None and config_dict[0]['location'][0]:
            logger.log("ERROR", "Please provide full path to browser!")
            sys.exit(0)

    def location_sanity_check(self):
        if config_dict[0]['location'][0]:
            if not self.send_email:
                logger.log("ERROR", "The location options requires an E-mail and password!")
                parser.print_help()
                sys.exit(0)
            elif not config_dict[0]['autologin'][0]:
                logger.log("ERROR","The location feature requires the autologin option to be set.")
                sys.exit(0)
            elif not len(os.listdir(fileOpts.root_directory())) > 2:
                self.get_location('init')

    # PEP8 states lines should not be over 80 characters line so I
    # wrote mulitline if/else statements enclosed in parenthesis.
    def credential_sanity_check(self):
        if (not str(config_dict[0]['password'][0]) == 'password' and
            not str(config_dict[0]['email'][0]) == 'example@gmail.com'):
                self.send_email = True
        elif (str(config_dict[0]['password'][0]) == 'password' and
            str(config_dict[0]['email'][0]) == 'example@gmail.com'):
                self.send_email = False
        elif (str(config_dict[0]['password'][0]) == 'password' and
            not str(config_dict[0]['email'][0]) == 'example@gmail.com' or
            str(config_dict[0]['email'][0]) == 'example@gmail.com' and
            not str(config_dict[0]['password'][0]) == 'password'):
                logger.log("ERROR", "Must supply both the E-mail and password options or none at all!")
                parser.print_help()
                sys.exit(0)

    def logfile_sanity_check(self,logfile):
        if os.path.exists(logfile):
            config_dict[0]['logfile'][0] = logfile
            logger.log("INFO", "logfile(1): " + str(config_dict[0]['logfile'][0]))
        elif logfile == '/var/log/auth.log' and not os.path.exists(logfile):
            for log_file in ['messages']:
                if os.path.exists('/var/log/' + str(log_file)):
                    config_dict[0]['logfile'][0] = '/var/log/' + str(log_file)
                    #config_dict[0]['logfile'][0] = '/var/log/' + str(log_file)
                    logger.log("INFO", "logfile(2): " + str(config_dict[0]['logfile'][0]))
                    break
                else:
                    logger.log("ERROR","Log file " + logfile
                        + " does not exist. Please specify which log to use.")
                    sys.exit(0)

    def is_loction_supported(self,process):
        return find_executable(process) is not None
    
    def get_location(self,init=None):
        if not config_dict[0]['location'][0]:
            return
        elif config_dict[0]['location'][0] and not self.send_email:
            logger.log("ERROR",
                "Cannot E-mail your location without your E-mail and password. "
                + "Please use the help option and search for -e and -p.")
            sys.exit(0)

        while database.read_from_db('location_bool') == 'true' or init == 'init':
            if net.connected():
                time.sleep(3)
                database.add_location_to_db('false')
                if self.send_email:
                    try:
                        logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.send_mail(
                            config_dict[0]['email'][0],
                            config_dict[0]['email'][0],
                            config_dict[0]['password'][0],
                            config_dict[0]['port'][0],
                            "Failed GDM login from IP " + str(self.ip_addr) + "!",
                            "Someone tried to login into your computer and failed "
                            + str(config_dict[0]['attempts'][0]) + "times.")
                    except:
                        pass
                try:
                    logger.log("INFO","ImageCapture - Grabbing location now.")
                    GetLocation(config_dict[0]['website'][0],
                        config_dict[0]['email'][0],
                        config_dict[0]['browser'][0]).start()
                    if init == 'init':
                        break
                except:
                    logger.log("WARNING","ImageCapture - Could not open your browser.")
                    pass
            else:
                break

    def executable_exists(self,executable_name):
        return find_executable(executable_name)
    
    def take_picture(self):
        if not config_dict[0]['enablecam'][0]:
            return
        camera = cv2.VideoCapture(config_dict[0]['video'][0])
        if not camera.isOpened():
            logger.log("ERROR","ImageCapture - No cam available at "
                + str(config_dict[0]['video'][0]) + ".")
            config_dict[0]['enablecam'][0] = False
            return
        elif not config_dict[0]['enablecam'][0]:
            logger.log("WARNING","ImageCapture - "
                + "Taking pictures from webcam was not enabled.")
            return
        elif not camera.isOpened() and config_dict[0]['video'][0] == 0:
            logger.log("WARNING","ImageCapture - ImageCapture does not detect a camera.")
            config_dict[0]['enablecam'][0] = False
            return
        elif self.executable_exists() is None:
            logger.log("WARNING", "OpenCV is not installed.")
            config_dict[0]['enablecam'][0] = False
            return
        logger.log("INFO","ImageCapture - Taking picture.")
        time.sleep(0.1) # Needed or image will be dark.
        image = camera.read()[1]
        cv2.imwrite(fileOpts.picture_path(), image)
        del(camera)
    
    def send_mail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            if config_dict[0]['enablecam'][0]:
                message.attach(MIMEImage(file(fileOpts.picture_path()).read()))
            mail = smtplib.SMTP('smtp.gmail.com', port)
            mail.starttls()
            mail.login(sender,password)
            mail.send_mail(sender, to, message.as_string())
            logger.log("INFO","ImageCapture - Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            logger.log("ERROR","ImageCapture - Could not athenticate with password and username!")
        except:
            logger.log("ERROR","ImageCapture - Unexpected error in send_mail():")
    
    def failed_login(self,count):
      logger.log("INFO", "count: " + str(count))
      if count == int(config_dict[0]['attempts'][0]) or config_dict[0]['allowsucessful'][0]:
          logger.log("INFO", "failed_login True")
          return True
      else:
          logger.log("INFO", "failed_login False")
          return False
    
    def tail_file(self,logfile):
    
        count = 0
    
        gdm.auto_login_remove(config_dict[0]['autologin'][0], user.name())
    
        for line in tailf(logfile):
    
            s = re.search("(^.*\d+:\d+:\d+).*password.*pam: unlocked login keyring", line, re.I | re.M)
            f = re.search("(^.*\d+:\d+:\d+).*pam_unix.*:auth\): authentication failure", line, re.I | re.M)
    
            if f and not config_dict[0]['allowsucessful'][0]:
                count += 1
                sys.stdout.write("Failed login via GDM at " + f.group(1) + ":\n" + f.group() + "\n\n")
                if self.failed_login(count):
                    logger.log("INFO", "user: " + user.name())
                    gdm.auto_login(config_dict[0]['autologin'][0], user.name())
                    self.take_picture()
                    database.add_location_to_db('true')
                    self.get_location()
                    if not config_dict[0]['enablecam'][0] and self.send_email:
                        try:
                            logger.log("INFO","ImageCapture - Sending E-mail now.")
                            self.send_mail(
                                config_dict[0]['sender'][0],
                                config_dict[0]['email'][0],
                                config_dict[0]['password'][0],
                                config_dict[0]['port'][0],
                                "Failed GDM login from IP " + self.ip_addr + "!",
                                "Someone tried to login into your computer and failed " + config_dict[0]['attempts'][0] + " times.")
                        except:
                            pass
                time.sleep(1)
            if s and config_dict[0]['allowsucessful'][0]:
                sys.stdout.write("Sucessful login via GDM at " + s.group(1) + ":\n" + s.group() + "\n\n")
                gdm.auto_login(config_dict[0]['autologin'][0], user.name())
                self.take_picture()
                database.add_location_to_db('true')
                self.get_location()
                if not config_dict[0]['enablecam'][0] and self.send_email:
                    try:
                        logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.send_mail(
                            config_dict[0]['sender'][0],
                            config_dict[0]['email'][0],
                            config_dict[0]['password'][0],
                            config_dict[0]['port'][0],
                            "Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed "
                            + config_dict[0]['attempts'][0] + " times.")
                    except:
                        pass
                time.sleep(1)

        db.add_ip_to_db(self.ip_addr)

    def main(self):

        _version_ = re.search('2.7',str(version.python()), re.M | re.I)
        if _version_ is None:
            logger.log("ERROR", "Only python version 2.7 is supported.")
            sys.exit(0)

        gdm.clear_auto_login(config_dict[0]['clearautologin'][0], user.name())
        self.get_location()

        while True:
            try:
                self.tail_file(config_dict[0]['logfile'][0])
            except IOError as ioError:
                logger.log("ERROR", "IOError: " + str(ioError))
            except KeyboardInterrupt:
                logger.log("INFO", " [Control C caught] - Exiting ImageCapturePy now!")
                break

class GetLocation(Thread):

    def __init__(self,website,email,browser):
        Thread.__init__(self)
        self.count = 0
        config_dict[0]['email'][0]   = email
        config_dict[0]['website'][0] = website
        config_dict[0]['browser'][0] = browser

    def browser_exists(self,browser):
        return find_executable(browser)

    def run(self):
        for b in ['/opt/google/chome/chrome','/usr/bin/firefox','/usr/bin/opera']:
            if self.browser_exists(config_dict[0]['browser'][0]) and self.count == 0:
                browser = re.match("(\/\w+)(.*\/)(\w+)",config_dict[0]['browser'][0]).group(3)
                break
            self.count += 1
            if self.count > len(b):
                logger.log("ERROR",
                    "Only the following browsers are supported: Chrome, Opera, and Firefox.")
            elif self.browser_exists(b):
                browser = re.match("(\/\w+)(.*\/)(\w+)",b).group(3)
                break
        if browser == 'chrome':
            call([config_dict[0]['browser'][0],
                "--user-data-dir=" + str(fileOpts.root_directory()), "--no-sandbox",
                "" + config_dict[0]['website'][0] + "?Email=" + config_dict[0]['email'][0]])
        elif browser == 'firefox':
            call([browser,"--new-window", "" + config_dict[0]['website'][0]
                + "?Email=" + config_dict[0]['email'][0] + "\""])
        #elif browser == 'opera':
        else:
            logger.log("WARNING", "\n\nBrowser not "
                + "found and location functionality will not work.\n\n")
            sys.sleep(2)

class Database():

    def __init__(self):
        self.db_file = fileOpts.database_path()
        self.db      = sqlite3.connect(self.db_file)

        try:
            query = self.db.execute("select * from connected")
        except sqlite3.OperationalError:
            self.db.execute("CREATE TABLE connected(id integer primary key AUTOINCREMENT, "
                + "location_bool text not null, coordinates text not null, ip_addr text not null);")
            logger.log("INFO","Table(connected) does not exist, creating now.")

    def file_exists(self,file_name):
        return os.path.exists(file_name)

    def write_to_db(self,location_bool,coordinates,ip_addr):
        if location_bool is None or coordinates is None or ip_addr is None:
            return
        elif not re.search("true|false|NULL", location_bool, re.I|re.M):
            logger.log("ERROR", str(location_bool) + " is not a known mode.")
        elif not re.search("\A\((\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+\)|NULL", coordinates, re.M | re.I):
            logger.log("ERROR", "Improper coordinate format -> " + str(coordinates) + ".")
        elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$|NULL", ip_addr, re.M|re.I):
            logger.log("ERROR", "Improper ip address format -> " + str(ip_addr) + ".")
        else:
            coor = re.sub("[\(\)]", "", str(coordinates))
            self.db.execute("insert into connected (location_bool, coordinates, ip_addr) "
                + "values(\"" + str(location_bool) + "\", \"" + str(coor) + "\", \"" + str(ip_addr) + "\")")
            self.db.commit()

    def read_from_db(self,column):
        query = self.db.execute("select * from connected")
        for row in query:
            if column == 'location_bool' and row[1] is not None:
                return str(row[1])
            elif column == 'coordinates' and row[2] is not None:
                return str(row[2])
            elif column == 'ip_addr' and row[3] is not None:
                return str(row[3])
            else:
                logger.log("ERROR", "Not a known column or DB is empty.")
                return

    def update_db(self,column,value):
        if column is None or value is None:
            return
        try:
            if (self.read_from_db('location_bool') is None or
                self.read_from_db('coordinates') is None or 
                self.read_from_db('ip_addr') is None):
                    self.logger.log("ERROR", "You must write to the database first before updating!")
                    return
            elif re.search("true|false", value, re.I|re.M) and column == 'location_bool':
                self.db.execute("update connected set location_bool = \"" + value + "\"")
                self.db.commit()
            elif re.search("\A(\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+", value, re.M | re.I) and column == 'coordinates':
                self.db.execute("update connected set coordinates = \"" + value + "\"")
                self.db.commit()
            elif re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$", value, re.M|re.I) and column == 'ip_addr':
                self.db.execute("update connected set ip_addr = \"" + value + "\"")
                self.db.commit()
            else:
                logger.log("ERROR", str(column) + " is not a known column for the connected table in the imagecapture db.")
                return
        except sqlite3.OperationalError:
            logger.log("ERROR", "The database is lock, could not add coordinates to DB.")

    def add_location_to_db(self,location_bool):
        try:
            if self.read_from_db('location_bool') is None:
                write_to_db(location_bool,'NULL','NULL')
                logger.log("INFO", "Writing location_bool to DB.")
            elif self.read_from_db('location_bool') != location_bool and self.read_from_db('location_bool') is not None:
                self.update_db('location_bool', location_bool)
                logger.log("INFO", "Updating location_bool variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            logger.log("ERROR", "The database is locked, could not add location_bool to DB.")
            pass

    def add_coordinates_to_db(self,coordinates):
        try:
            if self.read_from_db('coordinates') is None:
                self.write_to_db('NULL', coordinates,'NULL')
                logger.log("INFO", "Writing coordinates to DB.")
            elif not self.read_from_db('coordinates') == coordinates and self.read_from_db('coordinates') is not None:
                self.update_db('coordinates', ip_addr)
                logger.log("INFO", "Updating coordinates variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            logger.log("ERROR", "The database is locked, could not add coordinates to DB.")
            pass

    def add_ip_to_db(self,ip_addr):
        try:
            if self.read_from_db('ip_addr') is None:
                self.write_to_db('NULL','NULL', ip_addr)
                logger.log("INFO", "Writing ip_addr to DB.")
            elif self.read_from_db('ip_addr') != ip_addr and self.read_from_db('ip_addr') is not None:
                self.update_db('ip_addr', ip_addr)
                logger.log("INFO", "Updating ip_addr variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            logger.log("ERROR", "The database is locked, could not add IP address to DB.")
            pass

class GraphicalDisplayManager():

    def __init__(self):
        pass

    def add_to_group(self,user):
        os.system("sudo usermod -a -G nopasswdlogin " + str(user))

    def remove_from_group(self,user):
        os.system("sudo gpasswd -d " + str(user) + " nopasswdlogin")

    def user_present(self,user):
        with open("/etc/group", "r") as f:
            for line in f:
                nop = re.search("^nopasswdlogin.*(" + str(user) + ")", line)
                if nop is not None and nop:
                    return True
                elif nop is not None and not nop:
                    return False

    def auto_login_remove(self,autologin,user):
        if not autologin and self.user_present(user):
            logger.log("INFO", "Removing user " + str(user) + " from nopasswdlogin group.")
            self.remove_from_group(user)
            sys.exit(0)
        elif not self.user_present(user):
            logger.log("WARN", "User " + str(user)
                + " is not present in the nopasswdlogin group.")
            sys.exit(0)
        elif autologin:
            logger.log("WARN", "Cannot remove user " + str(user)
                + " from nopasswdlogin group while using the location feature.")
            sys.exit(0)
        else:
            print("Test")
            sys.exit(0)

    def clear_auto_login(self,clear,user):
        if len(sys.argv) > 2 and clear:
            logger.log("ERROR", "Too many arguments for clear given. Exiting now.")
            sys.exit(0)
        if clear and self.user_present(user):
            self.remove_from_group(user)
            logger.log("INFO", "Removing user " + str(user) + " from group nopasswdlogin")
            sys.exit(0)
        elif clear and not self.user_present(user):
            logger.log("WARN", "Username " + str(user) + " is not in nopasswdlogin group.")
            sys.exit(0)
        else:
            print("clear => " + str(clear))
            print("self.user_present(user) => " + str(self.user_present(user)))

    def auto_login(self,autologin,user):
        if autologin:
            logger.log("INFO", "Automatically logging you in now.")
            self.add_to_group(user)

    def pam_d(self):
        if version.system_package_manager() == 'rpm':
            return ('password-auth',)
        elif version.system_package_manager() == 'apt':
            return ('common-auth',)
        elif self.version.system_package_manager() == 'eix':
            return ('system-login',)

class User():

    def name(self):
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()
    
class Net():

    def connected(self):
        try:
            urllib2.urlopen('http://www.google.com', timeout=1)
            return True
        except urllib2.URLError as err:
            return False

    def get_hardware_address(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])

class Version():

    def python(self):
        python_version = re.search('\d\.\d\.\d', str(sys.version), re.I | re.M)
        if python_version is not None:
            return python_version.group()
        return "None"

    def release(self):
        comm = subprocess.Popen(["lsb_release -irs"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()

    def system_package_manager(self):
        package_manager = {
            'rpm': ('centos','fedora','scientific','opensuse'),
            'apt': ('debian','ubuntu','linuxmint'),
            'eix': ('gentoo',)}
        for key,value in package_manager.items():
            manager = re.search(release().lower(),str(value), re.I | re.M)
            if manager is not None:
                return key
        if manager is None:
            return False

class FileOpts():

    def __init__(self):
        pass

    def home_directory(self):
        return "/home/" + user.name()

    def root_directory(self):
        return "/home/" + str(user.name()) + "/.imagecapture"

    def picture_directory(self):
        return "/home/" + str(user.name()) + "/.imagecapture/pictures"

    def picture_path(self):
        return str(self.picture_directory()) + '/capture.png'

    def database_path(self):
        return str(self.root_directory()) + '/imagecapture.db'

    def current_directory(self):
        return str(os.getcwd())

    def file_exists(self,file_name):
        return os.path.isfile(file_name)

    def create_file(self,file_name):
        if not self.file_exists(file_name):
            open(file_name, 'w')

    def chown(self,dir_path,user_name,group_name):
        uid = pwd.getpwnam(user_name).pw_uid
        gid = grp.getgrnam(group_name).gr_gid
        os.chown(dir_path, uid, gid)

    def chmod(self,dir_path,mode):
        os.chmod(dir_path, mode)

    def dir_exists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdir_p(self,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and self.dir_exists(dir_path):
                pass
            else:
                raise

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-e", "--email",
        dest='email', default="example@gmail.com",
        help="E-mail address to send notofications to.")
    parser.add_option("-p", "--password",
        dest='password', default="password",
        help="Password used to sign-in to your E-mail account.")
    parser.add_option("-V", "--video",
        dest='video', default=0,
        help="Specify camera location.")
    parser.add_option("-v", "--verbose",
        dest='verbose', action="store_true", default=False,
        help="Print the options passed to ImageCapturePy.")
    parser.add_option("-P", "--port",
        dest='port', default=587,
        help="E-mail port defaults to 587 if not specified.")
    parser.add_option("-a", "--attempts",
        dest='attempts', default=3,
        help="Number of failed attempts defaults to 3.")
    parser.add_option("-L", "--location",
        dest='location', action="store_true", default=False,
        help="Enable location capturing.")
    parser.add_option("-l", "--log-file",
        dest='logfile', default='/var/log/auth.log',
        help="Tail log defaults to /var/log/auth.log.")
    parser.add_option("-c", "--enable-cam",
        dest='enablecam', action="store_true", default=False,
        help="Enable cam capture of intruder.")
    parser.add_option("-A", "--auto-login",
        dest='autologin', action="store_true",  default=False,
        help="Auto login user after no of failed attempts.")
    parser.add_option("-w", "--website",
        dest='website', default='https://imagecapturepy.herokuapp.com/index.html',
        help="Use alternate website to capture location.")
    parser.add_option("-X", "--clear-autologin",
        dest='clearautologin', action="store_true", default=False,
        help="Remove autologin. Must be root to use this feature.")
    parser.add_option("-s", "--allow-sucessful",
        dest='allowsucessful', action="store_true", default=False,
        help="Run ImageCapture even if login is sucessful.")
    parser.add_option("-B", "--browser",
        dest="browser", default="/opt/google/chrome/chrome",
        help="Select the browser used to grab geolocation data.")
    parser.add_option("-C", "--config-file",
        dest="configfile", default="",
        help="Configuration file path.")
    (options, args) = parser.parse_args()

    net      = Net()
    user     = User()
    logger   = Logging()
    version  = Version()
    fileOpts = FileOpts()
    database = Database()
    gdm      = GraphicalDisplayManager()

    # Easiest way to share variables between clases without wanting to 
    # chop my computer up with an fucking axe! The key is used for reference
    # while the first value is reserved for config files values and if they 
    # are blank then they are filled in with the 2nd values value. The array 
    # inside the array after the dictionary declaration is reserved for when 
    # the config file option is passed but an option has no value. That key
    # name is stored in this array.

    config_dict = [{
        'email': ['', options.email], 'password': ['', options.password],
        'video': ['', options.video], 'verbose': ['', options.verbose],
        'port': ['', options.port], 'attempts': ['', options.attempts],
        'location': ['', options.location], 'logfile': ['', options.logfile],
        'enablecam': ['', options.enablecam], 'autologin': ['', options.autologin],
        'website': ['', options.website], 'clearautologin': ['', options.clearautologin],
        'allowsucessful': ['', options.allowsucessful], 'browser': ['', options.browser]}, []]

    # This will recursivley check for and or
    # create the program's directory tree structure.

    fileOpts = FileOpts()

    if not fileOpts.file_exists(fileOpts.picture_path()):
        if not fileOpts.dir_exists(fileOpts.picture_directory()):
            if not fileOpts.dir_exists(fileOpts.root_directory()):
                fileOpts.mkdir_p(fileOpts.root_directory())
                fileOpts.mkdir_p(fileOpts.picture_directory())
                fileOpts.create_file(fileOpts.picture_path())
            fileOpts.mkdir_p(fileOpts.picture_directory())
            fileOpts.create_file(fileOpts.picture_path())            
        fileOpts.create_file(fileOpts.picture_path())

    imagecapture = ImageCapture(config_dict)
    imagecapture.main()
