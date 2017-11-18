from com.uconnect.core.singleton import Singleton

#@Singleton
class ucException(Exception, metaclass=Singleton):
    def __init__(self,errorMsg):
        self.errorMsg = errorMsg
    def __str__(self):
        return repr(self.errorMsg)

#@Singleton
class MissingConfigFile(ucException, metaclass=Singleton):
    pass
#@Singleton
class MissingArgumentValues(ucException, metaclass=Singleton):
    pass
#@Singleton
class NullKeyValue(ucException, metaclass=Singleton):
    pass
#@Singleton
class BootStrapError(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidCollection(ucException, metaclass=Singleton):
    pass
#@Singleton
class MongoDBError(ucException, metaclass=Singleton):
    pass
#@Singleton
class NotListValue(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidOperator(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidTemplate(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidConnectionType(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidZipCode(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidScreen(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidAction(ucException, metaclass=Singleton):
    pass
#@Singleton
class InvalidScreenAction(ucException, metaclass=Singleton):
    pass
class DBError(ucException, metaclass=Singleton):
    pass
class InvalidAuthKey(ucException, metaclass=Singleton):
    pass
class InvalidEntity(ucException, metaclass=Singleton):
    pass
class InvalidLogin(ucException, metaclass=Singleton):
    pass
class InvalidSecCodeDeliveryOptions(ucException, metaclass=Singleton):
    pass
class InvalidSecurityCode(ucException, metaclass=Singleton):
    pass    
class DuplicateGroup(ucException, metaclass=Singleton):
    pass        