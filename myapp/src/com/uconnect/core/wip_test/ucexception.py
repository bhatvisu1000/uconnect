from com.uconnect.core.singleton import Singleton

#handle the exception in super class
#define allexception must be inherittance of super class which is sub class of exception
# we need to know the current function and or class name so this can be passed as an argument and should be recorded

class ucException(Exception):
    def __init__(self,errorMsg):
        self.errorMsg = errorMsg
    def __str__(self):
        return repr(self.errorMsg)

#@Singleton
class MissingConfigFile(Exception):
    pass
#@Singleton
class MissingArgumentValue(ucException):
    pass
#@Singleton
class MissingConfigFile(ucException):
    pass
#@Singleton
class BootStrapError(ucException):
    pass
#@Singleton
class MyError(ucException):
    pass
