import grp,pwd,os,glob
import subprocess,errno,re

from shutil import copy2

class Build():

    def __init__(self):
        self.PICTURE_DIRECTORY = "/home/" + str(user_name()) + "/.imagecapture/pictures"
        if not dir_exists(self.PICTURE_DIRECTORY):
            mkdir_p(self.PICTURE_DIRECTORY)
        if not file_exists(self.PICTURE_DIRECTORY + "/capture1.png"):
            create_file(self.PICTURE_DIRECTORY + "/capture1.png")

    def user_name():
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()

    def incrementBackupNumber():
        _list = []
        os.chdir(self.PICTURE_DIRECTORY)
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(int(num.group(2)))
        return int(max(_list))

    def copyFile(source,destination):
        if not file_exists(destination) and file_exists(source):
            copy2(source,destination)
        elif file_exists(destination) and file_exists(source):
            copy2(source,destination + ".backup")

    def file_exists(file_name):
        return os.path.isfile(file_name)

    def create_file(file_name):
        if not file_exists(file_name):
            open(file_name, 'w')

    def chwon(dir_path,user_name,group_name):
        uid = pwd.getpwnam(user_name).pw_uid
        gid = grp.getgrnam(group_name).gr_gid
        os.chown(dir_path, uid, gid)

    def chmod(dir_path,mode):
        #0775
        os.chmod(dir_path, mode)
    

    def dir_exists(dir_path):
        return os.path.isdir(dir_path)

    def mkdir_p(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and dir_exists(dir_path):
                pass
            else:
                raise
