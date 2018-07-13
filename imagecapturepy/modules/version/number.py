import re,sys

def number():
  python_version = re.search('\d\.\d\.\d', str(sys.version), re.I | re.M)
  if python_version is not None:
      return python_version.group()
  return "None"
