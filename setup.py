#!/usr/bin/env python

import subprocess,re,sys

import src.lib.gdm.gdm as gdm
import src.lib.name.user as user
import src.lib.version.version as version

from subprocess import Popen, call
from setuptools import setup, find_packages
from distutils.errors import DistutilsError

class PrepareBuild():
    def modifyConfFiles(self,username):
        subprocess.Popen(["find src/system/* -type f -iname *.conf -exec sed -i 's/username/" + username + "/g' {} \;"],
        shell=True, stdout=subprocess.PIPE)

    def cronTab(self):
        command="/bin/bash /home/root/.ssh/is_imagecapture_running.sh"
        cron = CronTab(user='root')
        job = cron.new(command=command)
        job.minute.every(1)
        for item in cron:
            install = re.search('install', str(sys.argv[1]), re.M | re.I)
            if install is not None:
                cron.write()

    def pipInstallPackage(self,package):
        print("[INFO] - Installing opencv-python via pip")
        #subprocess.Popen(['pip install --user ' + package], shell=True, stdout=subprocess.PIPE)
        #subprocess.Popen(["su " + str(user.name()) + " -c 'pip install --user " + str(package) + "'"], shell=True, stdout=subprocess.PIPE)
        subprocess.Popen(["su " + str(user.name()) + " -c 'pip install --user " + str(package) + "'"], shell=True)

if __name__ == '__main__':

    prepareBuild = PrepareBuild()

    try:

        username = str(user.name())
        pam      = str(gdm.pamD()[0])
        pkgm     = str(version.packageManager())

        conf_path = 'src/system/autologin/conf'
        conf_name = [conf_path+'/slim.conf',conf_path+'/mdm.conf',conf_path+'/gdm.conf']

        prepareBuild.modifyConfFiles(username)

        setup(name='ImageCapturePy',
        version='1.0.0',
        url='https://github.com/amboxer21/ImageCapturePy',
        license='NONE',
        author='Anthony Guevara',
        author_email='amboxer21@gmail.com',
        description='A program to capture a picture and geolocation data upon 3 incorrect or'
            + 'number of specified attempts at the login screen. This data is then e-mailed to you.',
        packages=find_packages(exclude=['tests']),
        long_description=open('README.md').read(),
        data_files=[
            ('/etc/pam.d/', [conf_name[0],conf_name[1],conf_name[2]]),
            ('/etc/pam.d/', ['src/system/autologin/' + pkgm + '/pam/' + pam]),
            ('/usr/local/bin/', ['src/imagecapture.py']),
            ('/home/root/.ssh/' ,['src/system/home/user/.ssh/is_imagecapture_running.sh'])],
        zip_safe=True,
        setup_requires=['pytailf', 'opencv-python','python-crontab'],
        test_suite='nose.collector')

        from crontab import CronTab
        print("[INFO] - prepareBuild.cronTab()")
        #prepareBuild.cronTab()

    except DistutilsError:
        print("[ERROR] - Exception DistutilsError")
        prepareBuild.pipInstallPackage('opencv-python')
