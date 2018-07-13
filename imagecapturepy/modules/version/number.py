import re,sys,subprocess

def python():
    python_version = re.search('\d\.\d\.\d', str(sys.version), re.I | re.M)
    if python_version is not None:
        return python_version.group()
    return "None"

def release():
    comm = subprocess.Popen(["lsb_release -irs"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()
