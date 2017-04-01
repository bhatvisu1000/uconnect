from abc import ABCMeta
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from ReadInfra import Environment

class __init__:
	pass

class DBConnection:
	#__metaclass__ = ABCMeta

	#MyConnection.register(tuple)
	#assert issubclass(tuple, MyConnection)
	#assert isinstance((), MyConnection)

	def getConnection(self):
		pass

class MongoDbConnection:

	#app = Flask(__name__)

	def __init__(self):
		print "initialzing mongo db connection"
		# this is the place we will read ReadInfra
	def getConnection(self):
		print "I am in MongoDBConnection.getConnection"
		self.app = Flask(__name__)
		self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
		self.app.config['MONGO_MAX_POOL_SIZE'] = 100
		self.app.config['MONGO_CONNECT'] = True
		self.mongo = PyMongo(self.app)
		return self
		#print conn
		#return conn

class OracleDBConnection(MyConnection):
	def getConnection(self):
		pass

class ConnectionBuilder:
	def buildConnection(self,dbType):
		if (dbType == "MongoDB" ):
			#MognoDBCon = MongoDBConnection()
			print "I am in ConnectionBuilder"
			MongoDBConn = MongoDbConnection()
			myMongoDbConn = MongoDBConn.getConnection()
			return myMongoDbConn


#if ( __name__ == "__main__" ):
#	myConnectionBuilder = ConnectionBuilder()
#	myMongoDb = myConnectionBuilder.buildConnection("MongoDB") 
#	myConnection = myMongoDb.mongo
#	print "This is main"
#	print myConnection
#	#mongo = PyMongo(app)
#	#Member = myConnection.db.Member	
#	output = []
#	with myMongoDb.app.app_context():
#		for MemberData in myConnection.db.Member.find():
#			output.append({'_id' :MemberData['_id']});
#			print MemberData['_id']		
