from com.uconnect.core.singleton import Singleton

#@Singleton
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
#@Singleton
class NullKeyValue(ucException):
    pass
#@Singleton
class BootStrapError(ucException):
    pass
#@Singleton
class InvalidCollection(ucException):
    pass
#@Singleton
class MongoDBError(ucException):
    pass
#@Singleton
class NotListValue(ucException):
    pass
#@Singleton
class InvalidOperator(ucException):
    pass
#@Singleton
class InvalidTemplate(ucException):
    pass
#@Singleton
class InvalidConnectionType(ucException):
    pass
#@Singleton
class InvalidZipCode(ucException):
    pass
#@Singleton
class InvalidScreen(ucException):
    pass
#@Singleton
class InvalidAction(ucException):
    pass
#@Singleton
class InvalidScreenAction(ucException):
    pass
class DBError(ucException):
    pass
class InvalidAuthKey(ucException):
    pass
class InvalidEntity(ucException):
    pass
class InvalidLogin(ucException):
    pass
class InvalidSecCodeDeliveryOptions(ucException):
    pass
class InvalidSecurityCode(ucException):
    pass    