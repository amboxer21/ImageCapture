import re
import os
import sys
from optparse import OptionParser

class ConfigFile(object):

    def __init__(self, file_name):
        self.args_list = []
        self.file_name = file_name

    def config_options(self):
        if not self.file_name:
            return
        elif not os.path.exists(str(self.file_name)):
            print("Config file does not exist.")
            sys.exit(0)
        config_file = open(self.file_name,'r').read().splitlines()
        for line in config_file:
            comm = re.search(r'(^.*)=(.*)', str(line), re.M | re.I)
            if comm is not None:
                if not comm.group(2):
                    config_dict[1].append(comm.group(1))
                config_dict[0][comm.group(1)] = comm.group(2)
        return config_dict

    def override_config_options(self):
        pass

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

class ImageCapture(ConfigFile):
    def __init__(self,config_dict={},file_name=''):
        super(ImageCapture, self).__init__(self,file_name)
        configFile = configFile(options.configfile)
        configFile.config_options() 
        print("config_dict[1] => " + str(config_dict[1]))
        print("config_dict[0][email] => " + str(config_dict[0]['email']))

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
        dest='clear', action="store_true", default=False,
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

    config_dict  = [{
        'email': '', 'password': '', 'video': '',
        'verbose': '', 'port': '', 'attempts': '',
        'location': '', 'logfile': '', 'enablecam': '','autologin': '',
        'website': '', 'clearautologin': '', 'allowsucessful': '', 'browser': ''}, []]

    ImageCapture(config_dict)
