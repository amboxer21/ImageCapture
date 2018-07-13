import re,sys

def number():
  regex   = "(major)=(\d),\s(minor)=(\d),\s(micro)=(\d)"
  version = re.search(regex, str(sys.version_info), re.I | re.M)
  if version is not None:
      return str(version.group(2)) + "." + str(version.group(4)) + "." + str(version.group(6))
  return "None"
