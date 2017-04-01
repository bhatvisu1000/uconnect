from com.uconnect.core.singleton import Singleton


class ucException(Exception):
    def __init__(self,errorMsg):
        self.errorMsg = errorMsg
    def __str__(self):
        return repr(self.errorMsg)

@Singleton
class MissingConfigFile(ucException):
    pass
#@Singleton
class MissingArgumentValues(ucException):
    pass
@Singleton
class NullKeyValue(ucException):
    pass
@Singleton
class BootStrapError(ucException):
    pass
@Singleton
class InvalidCollection(ucException):
    pass
@Singleton
class MongoDBError(ucException):
    pass
@Singleton
class NotListValue(ucException):
    pass
@Singleton
class InvalidOperator(ucException):
    pass