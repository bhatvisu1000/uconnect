import platform, sys, os

def linux_distribution():
    try:
        return platform.linux_distribution()
    except:
        return 'N/A'
#linux
print("""Python version: %s
dist: %s
linux dist: %s
system: %s
machine: %s
platform: %s
uname: %s
version: %s
mac_ver: %s
""" % (
sys.version.split('\n'),
str(platform.dist()),
linux_distribution(),
platform.system(),
platform.machine(),
platform.platform(),
platform.uname(),
platform.version(),
platform.mac_ver(),
))

#windows
#linux
print("""Python version: %s
dist: %s
system: %s
machine: %s
platform: %s
uname: %s
version: %s
mac_ver: %s
Processor: %s
""" % (
sys.version.split('\n'),
str(platform.dist()),
platform.system(),
platform.machine(),
platform.platform(),
platform.uname(),
platform.version(),
platform.mac_ver(),
platform.processor(),
))

## CPU count in linux using command
import commands
n = commands.getoutput("grep -c processor /proc/cpuinfo")

## Finding cpu in windows
import _winreg
with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"Hardware\DESCRIPTION\System\CentralProcessor") as key:
    (N_CPUS, N_values, time) = _winreg.QueryInfoKey(key)
    for CPU in range(N_CPUS):
        with _winreg.OpenKey(key, str(CPU) ) as key2:
            (Identifier, n) = _winreg.QueryValueEx(key2,"Identifier")
            (ProcessorName, n) = _winreg.QueryValueEx(key2,"ProcessorNameString")

print "CPU: ",CPU,Identifier,ProcessorName

# Unix/Linux CPU info
grep 'physical id' /proc/cpuinfo | sort | uniq | wc -l
#Number of physical cores that is associated with every CPU core entry in
#cpuinfo:
grep 'cpu cores' /proc/cpuinfo