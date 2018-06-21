import os,errno,pwd,grp,re

from shutil import copy2

def incrementBackupNumber():
    _list = []
    os.chdir("/home/anthony/.imagecapture/pictures")
    for file_name in glob.glob("*.backup"):
        num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
        _list.append(int(num.group(2)))
    return max(_list)

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
