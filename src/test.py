import re
import os
import sys
from optparse import OptionParser

class ConfigFile(object):

    def __init__(self):
        pass

    def config_options(self,file_name):
        if not os.path.exists(str(file_name)):
            print("Config file does not exist.")
        config_file = open(file_name,'r').read().splitlines()
        for line in config_file:
            comm = re.search(r'(^.*)=(.*)', str(line), re.M | re.I)
            if comm is not None:
                config_dict[comm.group(1)] = comm.group(2)
        print("sys.argv => " + str(sys.argv[1:]))
        print("argv len = " + str(self.number_of_args_passed))
        return config_dict

    def config_file_supplied(self):
        if re.search(r'(\-C|\-\-config\-file)',str(sys.argv[1:]), re.M) is None:
            return False
        return True

    def number_of_args_passed(self):
        return len(sys.argv[1:])

class ImageCapture(ConfigFile):
    def __init__(self,config_dict={}):
        super(ImageCapture, self).__init__()
        parser = OptionParser()
        parser.add_option("-e", "--email", dest='email',
            default="example@gmail.com")
        parser.add_option("-p", "--password", dest='password',
            default="password")
        parser.add_option("-V", "--video", dest='video', action="store",
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
        parser.add_option("-X", "--clear-autologin", dest='clear', action="store_true",
            default=False, help="Remove autologin. Must be root to use this feature.")
        parser.add_option("-s", "--allow-sucessful", dest='allowsucessful', action="store_true",
            default=False, help="Run ImageCapture even if login is sucessful.")
        parser.add_option("-B", "--browser", dest="browser",
            default="/opt/google/chrome/chrome", help="Select the browser used to grab geolocation data.")
        parser.add_option("-C", "--config-file", dest="configfile",
            default="", help="Configuration file path.")
        (self.options, args) = parser.parse_args()
        configFile = ConfigFile()
        configFile.config_options('test.conf') 

if __name__ == '__main__':
    config_dict = {
        'email': '', 'password': '', 'video': '',
        'verbose': '', 'port': '', 'attempts': '',
        'location': '', 'logfile': '', 'enablecam': '','autologin': '',
        'website': '', 'clearautologin': '', 'allowsucessful': '', 'browser': ''}
    ImageCapture(config_dict)
