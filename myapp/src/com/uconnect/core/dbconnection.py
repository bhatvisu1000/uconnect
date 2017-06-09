from pymongo import MongoClient
from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
import logging, com.uconnect.utility.ucLogging

# lets the parent logger from config file
myLogger = logging.getLogger('uConnect')

@Singleton
class DbConnection(object):

   #__metaclass__ = ABCMeta
   #MyConnection.register(tuple)
   #assert issubclass(tuple, MyConnection)
   #assert isinstance((), MyConnection)

   def getConnection(self):
     pass

@Singleton
class MongoDbConnection(object):
   '''
     MongoDbConnection class
   '''
   def __init__(self):
      myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDbConnection')
      self.envInstance = Environment.Instance()

   def getConnection(self):
      try:
         myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDbConnection')
         myModuleLogger.debug("Reading MONGO_URI details ...")
         myEnvironment = self.envInstance.getCurrentEnvironment()
         mongoDbEnvDetail = self.envInstance.getEnvironmentDetails(myEnvironment)
         mongoDbMongoURI  = mongoDbEnvDetail['MongoUri']
         mongoDbDBName = mongoDbEnvDetail['MongoDBName']

         myModuleLogger.debug(" MONGO_URI details [{mongoUri}]".format(mongoUri=mongoDbMongoURI))
         myModuleLogger.debug(" MongoDb Name [{mongoDB}]".format(mongoDB=mongoDbDBName))

         myMongoClient = MongoClient(mongoDbMongoURI)
         myMongoConn = myMongoClient.get_database(mongoDbDBName)

         myModuleLogger.debug(" MongoDb Connection [{mongoConn}]".format(mongoConn=myMongoConn))

         myLogger.info(myMongoConn)
         return myMongoConn

      except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise

@Singleton
class OracleDBConnection(object):
   def getConnection(self):
      pass

@Singleton
class ConnectionBuilder(object):
   def buildConnection(self, argDbType):
      ''' 
         Description:    Initializes dbconnection for a given environment and database. This method calls getConnection
                         method of relevant DB class 
         argEnvType:     dbType (currently only Mongo is supported)
         usage:          buildConnection(<dbType>)
         Return:         db connection
      '''		
      myModuleLogger = logging.getLogger('uConnect.dbconnection.'+__name__)
      
      if (argDbType == "MongoDB" ):
         myModuleLogger.info('Connection request is for [{db}] database'.format(db=argDbType))
         mongoDbConnInstance = MongoDbConnection.Instance()
         myMongoDbConn = mongoDbConnInstance.getConnection()
      
      return myMongoDbConn

'''
if ( __name__ == "__main__" ):
	myConnectionBuilder = ConnectionBuilder()
	myMongoDb = myConnectionBuilder.buildConnection("MongoDB") 
	myConnection = myMongoDb.mongo
	print "This is main"
	print myConnection
	#mongo = PyMongo(app)
	with myMongoDb.app.app_context():
		Member = myConnection.db.Member	
		output = []
	#with myMongoDb.app.app_context():
		for MemberData in myConnection.db.Member.find():
			output.append({'_id' :MemberData['_id']});
			print MemberData['_id']		
'''