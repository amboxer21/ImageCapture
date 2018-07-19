#!/usr/bin/env python
    
from tailf import tailf
from urllib2 import urlopen
from threading import Thread
from optparse import OptionParser
from subprocess import Popen,call
from email.MIMEImage import MIMEImage
from distutils.spawn import find_executable
from email.MIMEMultipart import MIMEMultipart

import sys,os,re,smtplib,fcntl,webbrowser,logging,sqlite3
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
        self.count    = 0
        self.email    = email
        self.website  = website
        self.browser  = browser

        self.user     = User()
        self.logger   = Logging()
        self.fileOpts = FileOpts()

    def browser_exists(self,browser):
        return find_executable(browser)

    def run(self):
        for b in ['/opt/google/chome/chrome','/usr/bin/firefox','/usr/bin/opera']:
            if self.browser_exists(self.browser) and self.count == 0:
                browser = re.match("(\/\w+)(.*\/)(\w+)",self.browser).group(3)
                break
            self.count += 1
            if self.count > len(b):
                self.logger.log("ERROR", "ImageCapturePy only supports Chrome, Opera, and Firefox. Please install one if able.")
            elif self.browser_exists(b):
                browser = re.match("(\/\w+)(.*\/)(\w+)",b).group(3)
                break
        if browser == 'chrome':
            call([self.browser, "--user-data-dir=" + str(fileOpts.rootDirectory()), "--no-sandbox",
                "" + self.website + "?Email=" + self.email])
        elif browser == 'firefox':
            call([browser, "--new-window", "" + self.website + "?Email=" + self.email + "\""])
        #elif browser == 'opera':
        else:
            self.logger.log("WARNING", "\n\nBrowser not found and location functionality will not work.\n\n")
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
        self.logfile        = options.logfile

        self.net      = Net()
        self.user     = User()
        self.logger   = Logging()
        self.version  = Version()
        self.database = Database()
        self.gdm      = GraphicalDisplayManager()

        self.database.addIpToDB(self.ip_addr)

        if os.path.exists(options.logfile):
            self.logfile = options.logfile
        else:
            self.logger.log("ERROR","Log file " + options.logfile + " does not exist. Please specify which log to use.")
            sys.exit(0)

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
                self.logger.log("ERROR", "Must supply both the E-mail and password options or none at all!")
                parser.print_help()
                sys.exit(0)

        if re.match("(\/)",self.browser) is None:
            self.logger.log("ERROR", "Please provide full path to browser!")
            sys.exit(0)

        if self.location:
            if not self.send_email:
                self.logger.log("ERROR", "The location options requires an E-mail and password!")
                parser.print_help()
                sys.exit(0)
            elif not self.autologin:
                self.logger.log("ERROR","The location feature requires the autologin option to be set.")
                sys.exit(0)
            elif not len(os.listdir(fileOpts.rootDirectory())) > 2:
                self.getLocation('init')

        if options.verbose:
            self.logger.log("INFO", "OPTIONS: " + str(options))

    def isLoctionSupported(self,process):
        return find_executable(process) is not None
    
    def getLocation(self,init=None):
        if not self.location:
            return
        elif self.location and not self.send_email:
            self.logger.log("ERROR","Cannot E-mail your location without your E-mail and password. Please use the help option and search for -e and -p.\n")
            sys.exit(0)

        while self.database.readFromDB('location_bool') == 'true' or init == 'init':
            if self.net.connected():
                time.sleep(3)
                self.database.addLocationToDB('false')
                if self.send_email:
                    try:
                        self.logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + str(self.ip_addr) + "!",
                            "Someone tried to login into your computer and failed " + str(self.attempts) + "times.")
                    except:
                        pass
                try:
                    self.logger.log("INFO","ImageCapture - Grabbing location now.")
                    GetLocation(self.website,self.to,self.browser).start()
                    if init == 'init':
                        break
                except:
                    self.logger.log("WARNING","ImageCapture - Could not open your browser.")
                    pass
            else:
                break

    def executableExists(self,executable_name):
        return find_executable(executable_name)
    
    def takePicture(self):
        if not self.enablecam:
            return
        camera = cv2.VideoCapture(self.video)
        if not camera.isOpened():
            self.logger.log("ERROR","ImageCapture - No cam available at " + str(self.video) + ".")
            self.enablecam = False
            return
        elif not self.enablecam:
            self.logger.log("WARNING","ImageCapture - Taking pictures from webcam was not enabled.")
            return
        elif not camera.isOpened() and self.video == 0:
            self.logger.log("WARNING","ImageCapture - ImageCapture does not detect a camera.")
            self.enablecam = False
            return
        elif self.executableExists() is None:
            logger.log("WARNING", "OpenCV is not installed.")
            self.enablecam = False
            return
        self.logger.log("INFO","ImageCapture - Taking picture.")
        time.sleep(0.1) # Needed or image will be dark.
        image = camera.read()[1]
        cv2.imwrite(fileOpts.picturePath(), image)
        del(camera)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            if self.enablecam:
                message.attach(MIMEImage(file(fileOpts.picturePath()).read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            self.logger.log("INFO","ImageCapture - Sent email successfully!")
        except smtplib.SMTPAuthenticationError:
            self.logger.log("ERROR","ImageCapture - Could not athenticate with password and username!")
        except:
            self.logger.log("ERROR","ImageCapture - Unexpected error in sendMail():")
    
    def failedLogin(self,count):
      self.logger.log("INFO", "count: " + str(count))
      if count == int(self.attempts) or self.allowsucessful:
          self.logger.log("INFO", "failedLogin True")
          return True
      else:
          self.logger.log("INFO", "failedLogin False")
          return False
    
    def tailFile(self,logfile):
    
        count = 0
    
        self.gdm.autoLoginRemove(self.autologin, self.user.name())
    
        for line in tailf(logfile):
    
            s = re.search("(^.*\d+:\d+:\d+).*password.*pam: unlocked login keyring", line, re.I | re.M)
            f = re.search("(^.*\d+:\d+:\d+).*pam_unix.*:auth\): authentication failure", line, re.I | re.M)
    
            if f and not self.allowsucessful:
                count += 1
                sys.stdout.write("Failed login via GDM at " + f.group(1) + ":\n" + f.group() + "\n\n")
                if self.failedLogin(count):
                    self.logger.log("INFO", "user: " + self.user.name())
                    self.gdm.autoLogin(self.autologin, self.user.name())
                    self.takePicture()
                    self.database.addLocationToDB('true')
                    self.getLocation()
                    if not self.enablecam and self.send_email:
                        try:
                            self.logger.log("INFO","ImageCapture - Sending E-mail now.")
                            self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + self.ip_addr + "!",
                                "Someone tried to login into your computer and failed " + self.attempts + " times.")
                        except:
                            pass
                time.sleep(1)
            if s and self.allowsucessful:
                sys.stdout.write("Sucessful login via GDM at " + s.group(1) + ":\n" + s.group() + "\n\n")
                self.gdm.autoLogin(self.autologin, self.user.name())
                self.takePicture()
                self.database.addLocationToDB('true')
                self.getLocation()
                if not self.enablecam and self.send_email:
                    try:
                        self.logger.log("INFO","ImageCapture - Sending E-mail now.")
                        self.sendMail(self.sender,self.to,self.password,self.port,"Failed GDM login from IP " + self.ip_addr + "!",
                            "Someone tried to login into your computer and failed " + self.attempts + " times.")
                    except:
                        pass
                time.sleep(1)

        self.db.addIpToDB(self.ip_addr)

    def main(self):

        v = re.search('2.7',str(self.version.python()), re.M | re.I)
        if v is None:
            self.logger.log("ERROR", "Only python version 2.7 is supported.")
            sys.exit(0)

        self.gdm.clearAutoLogin(self.clear, self.user.name())
        self.getLocation()

        while True:
            try:
                self.tailFile(self.logfile)
            except IOError as ioError:
                self.logger.log("ERROR", "IOError: " + str(ioError))
            except KeyboardInterrupt:
                self.logger.log("INFO", " [Control C caught] - Exiting ImageCapturePy now!")
                break

class Database():
    def __init__(self):
        self.user    = User()
        self.logger  = Logging()
        fileOpts     = FileOpts()
        self.db_file = fileOpts.databasePath()
        self.db      = sqlite3.connect(self.db_file)

        try:
            query = self.db.execute("select * from connected")
        except sqlite3.OperationalError:
            self.db.execute('''CREATE TABLE connected(id integer primary key AUTOINCREMENT, location_bool text not null, coordinates text not null, ip_addr text not null);''')
            self.logger.log("INFO","Table(connected) does not exist, creating now.")

    def fileExists(self,file_name):
        return os.path.exists(_file_name)

    def writeToDB(self,location_bool,coordinates,ip_addr):
        if location_bool is None or coordinates is None or ip_addr is None:
            return
        elif not re.search("true|false|NULL", location_bool, re.I|re.M):
            self.logger.log("ERROR", str(location_bool) + " is not a known mode.")
        elif not re.search("\A\((\d|\-\d)+\.\d+,\s(\d|\-\d)+\.\d+\)|NULL", coordinates, re.M | re.I):
            self.logger.log("ERROR", "Improper coordinate format -> " + str(coordinates) + ".")
        elif not re.search("\A\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$|NULL", ip_addr, re.M|re.I):
            self.logger.log("ERROR", "Improper ip address format -> " + str(ip_addr) + ".")
        else:
            coor = re.sub("[\(\)]", "", str(coordinates))
            self.db.execute("insert into connected (location_bool, coordinates, ip_addr) values(\"" + str(location_bool) + "\", \"" + str(coor) + "\", \"" + str(ip_addr) + "\")")
            self.db.commit()

    def readFromDB(self,column):
        query = self.db.execute("select * from connected")
        for row in query:
            if column == 'location_bool' and row[1] is not None:
                return str(row[1])
            elif column == 'coordinates' and row[2] is not None:
                return str(row[2])
            elif column == 'ip_addr' and row[3] is not None:
                return str(row[3])
            else:
                self.logger.log("ERROR", "Not a known column or DB is empty.")
                return

    def updateDB(self,column,value):
        if column is None or value is None:
            return
        try:
            if self.readFromDB('location_bool') is None or self.readFromDB('coordinates') is None or self.readFromDB('ip_addr') is None:
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
                self.logger.log("ERROR", str(column) + " is not a known column for the connected table in the imagecapture db.")
                return
        except sqlite3.OperationalError:
          self.logger.log("ERROR", "The database is lock, could not add coordinates to DB.")

    def addLocationToDB(self,location_bool):
        try:
            if self.readFromDB('location_bool') is None:
                writeToDB(location_bool,'NULL','NULL')
                self.logger.log("INFO", "Writing location_bool to DB.")
            elif self.readFromDB('location_bool') != location_bool and self.readFromDB('location_bool') is not None:
                self.updateDB('location_bool', location_bool)
                self.logger.log("INFO", "Updating location_bool variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            self.logger.log("ERROR", "The database is locked, could not add location_bool to DB.")
            pass

    def addCoordinatesToDB(self,coordinates):
        try:
            if self.readFromDB('coordinates') is None:
                self.writeToDB('NULL', coordinates,'NULL')
                self.logger.log("INFO", "Writing coordinates to DB.")
            elif not self.readFromDB('coordinates') == coordinates and self.readFromDB('coordinates') is not None:
                self.updateDB('coordinates', ip_addr)
                self.logger.log("INFO", "Updating coordinates variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            self.logger.log("ERROR", "The database is locked, could not add coordinates to DB.")
            pass

    def addIpToDB(self,ip_addr):
        try:
            if self.readFromDB('ip_addr') is None:
                self.writeToDB('NULL','NULL', ip_addr)
                self.logger.log("INFO", "Writing ip_addr to DB.")
            elif self.readFromDB('ip_addr') != ip_addr and self.readFromDB('ip_addr') is not None:
                self.updateDB('ip_addr', ip_addr)
                self.logger.log("INFO", "Updating ip_addr variable in DB.")
            else:
                return
        except sqlite3.OperationalError:
            call(['/usr/bin/rm', self.db_file])
            self.logger.log("ERROR", "The database is locked, could not add IP address to DB.")
            pass

class GraphicalDisplayManager():
    def __init__(self):
        self.logger  = Logging()
        self.version = Version()

    def addToGroup(self,user):
        os.system("sudo usermod -a -G nopasswdlogin " + str(user))

    def removeFromGroup(self,user):
        os.system("sudo gpasswd -d " + str(user) + " nopasswdlogin")

    def userPresent(self,user):
        with open("/etc/group", "r") as f:
            for line in f:
                nop = re.search("^nopasswdlogin.*(" + str(user) + ")", line)
                if nop is not None and nop:
                    return True
                elif nop is not None and not nop:
                    return False

    def autoLoginRemove(self,autologin,user):
        if not autologin and self.userPresent(user):
            self.removeFromGroup(user)

    def clearAutoLogin(self,clear,user):
        if len(sys.argv) > 2 and clear:
            self.logger.log("ERROR", "Too many arguments for clear given. Exiting now.")
            sys.exit(1)
        if clear and self.userPresent(user):
            self.removeFromGroup(user)
            sys.exit(1)
        elif clear and not self.userPresent(user):
            sys.exit(1)

    def autoLogin(self,autologin,user):
        if autologin:
            self.logger.log("INFO", "Automatically logging you in now.")
            self.addToGroup(user)

    def pamD(self):
        if self.version.packageManager() == 'rpm':
            return ('password-auth',)
        elif self.version.packageManager() == 'apt':
            return ('common-auth',)
        elif self.version.packageManager() == 'eix':
            return ('system-login',)

class Logging():
    def log(self,level,message):
        handler = logging.handlers.WatchedFileHandler(
            os.environ.get("LOGFILE", "/var/log/messages"))
        formatter = logging.Formatter(logging.BASIC_FORMAT)
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        root.addHandler(handler)
        logging.exception("(" + str(level) + ") " + "ImageCapture - " + message)
        print("  => (" + str(level) + ") " + "ImageCapture - " + str(message))
        return

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

    def getHwAddr(self,ifname):
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

    def packageManager(self):
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
        self.user = User()

    def homeDirectory(self):
        return "/home/" + self.user.name()

    def rootDirectory(self):
        return "/home/" + str(self.user.name()) + "/.imagecapture"

    def pictureDirectory(self):
        return "/home/" + str(self.user.name()) + "/.imagecapture/pictures"

    def picturePath(self):
        return str(self.pictureDirectory()) + '/capture.png'

    def databasePath(self):
        return str(self.rootDirectory()) + '/imagecapture.db'

    def currentDirectory(self):
        return str(os.getcwd())

    def fileExists(self,file_name):
        return os.path.isfile(file_name)

    def createFile(self,file_name):
        if not self.fileExists(file_name):
            open(file_name, 'w')

    def chown(self,dir_path,user_name,group_name):
        uid = pwd.getpwnam(user_name).pw_uid
        gid = grp.getgrnam(group_name).gr_gid
        os.chown(dir_path, uid, gid)

    def chmod(self,dir_path,mode):
        os.chmod(dir_path, mode)

    def dirExists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdirP(self,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and self.dirExists(dir_path):
                pass
            else:
                raise

if __name__ == '__main__':

    fileOpts = FileOpts()
    if not fileOpts.fileExists(fileOpts.picturePath()):
        fileOpts.createFile(fileOpts.picturePath())

        if not fileOpts.dirExists(fileOpts.pictureDirectory()):
            fileOpts.mkdirP(fileOpts.pictureDirectory())
            fileOpts.createFile(fileOpts.picturePath())

            if not fileOpts.dirExists(fileOpts.rootDirectory()):
                fileOpts.mkdirP(fileOpts.rootDirectory())
                fileOpts.mkdirP(fileOpts.pictureDirectory())
                fileOpts.createFile(fileOpts.picturePath())

    imagecapture = ImageCapture()
    imagecapture.main()
