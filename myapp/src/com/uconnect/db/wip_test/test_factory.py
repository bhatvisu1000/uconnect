from pymongo import MongoClient
import mongodb
from com.uconnect.core.connection.singleton01 import Singleton

@Singleton
class UcProcess(object):
    def __init__(self):
        db = "test"
        mongoUri="mongodb://localhost:27017/test?connectTimeoutMS=300000&maxPoolSize=100&minPoolSize=10&w=1"
        myconn = MongoClient(mongoUri)
        myDbconn = conn.get_database(db)
        mydb = MongoDB()

    def processRequest(self, argRequest):
        # find the
        # check if request is a valid request
        if (argRequest == None): 
            print ("null request")
        
        processToExecute =  findRelProcess (argRequest)
        classtoImport = 
 
        methodToCall = 

    def findRelProcess(self, argRequest):
        process = {'class':'mongodb','method':'findTotDocuments('}
        return  

    def executeProcess(argProcess):

class DynamicImporter:
    '''
    #----------------------------------------------------------------------
    '''
    def __init__(self, module_name, class_name):
        """Constructor"""
        module = __import__(module_name)
        my_class = getattr(module, class_name)
        instance = my_class()
        print instance
 
if __name__ == "__main__":
    DynamicImporter("com.uconnect.db.mongodb", "findTotDocuments")


class process:

    def __init__(self):
        pass
    def 