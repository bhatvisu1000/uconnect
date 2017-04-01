from abc import ABCMeta
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

class MyConnection(object):
	__metaclass__ = ABCMeta

	#MyConnection.register(tuple)

	#assert issubclass(tuple, MyConnection)
	#assert isinstance((), MyConnection)

	def getConnection(self):
		pass	

class MongoDbConnection():
	def getConnection():
		app = Flask(__name__)

		app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
		app.config['MONGO_MAX_POOL_SIZE'] = 100
		app.config['MONGO_CONNECT'] = True

class OracleDBConnection():
	def getConnection():
		pass

class ConnectionBuilder():
	def buildConnection(dbType):
		if (dbType == "MongoDB" ):
			MongoDbConnection.getConnection
