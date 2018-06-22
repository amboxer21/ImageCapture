from shutil import copy2

import grp,pwd,os,glob
import subprocess,errno,re

import modules.name.user as user
import modules.lsb.release as lsb
import modules.logging.logger as logger

class Build():

    def __init__(self):
        if not self.dir_exists(self.root_directory()):
            self.mkdir_p(self.root_directory())

    def root_directory(self):
        return "/home/" + str(user.name()) + "/.imagecapture"

    def incrementBackupNumber(self):
        _list = []
        os.chdir(self.PICTURE_DIRECTORY)
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(int(num.group(2)))
        return int(max(_list))

    def copyFile(self,source,destination):
        if not self.file_exists(destination) and self.file_exists(source):
            copy2(source,destination)
        elif self.file_exists(destination) and self.file_exists(source):
            logger.log("WARN","File already exists! Backing up before copying to destination!")
            copy2(source,destination + ".backup")
            copy2(source,destination)

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
        #0775
        os.chmod(dir_path, mode)
    

    def dir_exists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdir_p(self,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and dir_exists(dir_path):
                pass
            else:
                raise

    def pam_d(self):
        pkg_manager = {'rpm': ('centos','fedora'), 'apt': ('debian','ubuntu')}
        for key,value in pkg_manager.items():
            manager = re.search(lsb.release().lower(),str(value))
            if manager is not None:
                if key == 'rpm':
                    return 'rpm/password-auth','rpm/password-auth'
                elif key == 'apt':
                    return 'apt/common-auth','apt/mdm.conf'

if __name__ == '__main__':

    build = Build()
    build.chmod(build.root_directory(),0777)
    build.chown(build.root_directory(),user.name(),user.name())

    if not build.dir_exists(build.root_directory() + "/pictures"):
        build.mkdir_p(build.root_directory() + "/pictures")
        build.chmod(build.root_directory() + "/pictures",0777)
        build.chown(build.root_directory() + "/pictures",user.name(),user.name())
    else:
        logger.log("WARN","Directory \"" + build.root_directory() + "/pictures\" " + "exists!")
    if not build.file_exists(build.root_directory() + "/pictures" + "/capture1.png"):
        build.create_file(build.root_directory() + "/pictures" + "/capture1.png")
        build.chmod(build.root_directory() + "/pictures" + "/capture1.png",0775)
        build.chown(build.root_directory() + "/pictures" + "/capture1.png",user.name(),user.name())
    else:
        logger.log("WARN","File \"" + build.root_directory() + "/pictures" + "/capture1.png\" " + "exists!")
    if not build.file_exists(build.root_directory() + "/credentials.conf"):
        build.create_file(build.root_directory() + "/credentials.conf")
        build.chmod(build.root_directory() + "/credentials.conf",0775)
        build.chown(build.root_directory() + "/credentials.conf",user.name(),user.name())
    else:
        logger.log("WARN","File \"" + build.root_directory() + "/credentials.conf\" " + "exists!")

    logger.log("INFO","OS release = " + lsb.release())

    for module in build.pam_d():
        build.copyFile('build/autologin/' + module,'/etc/pam.d/')
