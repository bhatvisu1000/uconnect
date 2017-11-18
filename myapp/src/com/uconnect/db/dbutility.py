import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility

#@Singleton
class DBUtility(object, metaclass=Singleton):
    def __init__(self):
        self.mongoDbInstance = MongoDB()
        self.globalInstance = Global()

    def isIdExists(self, argCollection, argId):

        myCollection = argCollection
        myCriteria  = {"_id":argId}
        
        myDocCount = self.mongoDbInstance.findTotDocuments(myCollection, myCriteria)
        if myDocCount == 0:
            return self.globalInstance._Global__False
        else:
            return self.globalInstance._Global__True
