import json, os, sys
from pymongo import MongoClient

class ExecuteMongo:
    def __init__(self):
        print "constructor"

    def execStatement(self, mongoDbConn, Collection, criteria, projection, limit, skip):
        print "execStatement: conn [%s], Col [%s], Crit [%s], Proj [%s], limit [%d],skip [%d]", mongoDbConn,Collection,criteria,projection,limit,skip
    
    def execStatement(self, mongoDbConn, statement):
        print "execStatement: conn [%s], statement [%s] ", mongoDbConn, statement 

if __name__ == "__main__":
    myExecMongo = ExecuteMongo()
    myExecMongo.execStatement('myConn','myCol','{"a":1}','{"_id":true}',0,0)
    myExecMongo.execStatement('myConn','Member.find().skip(1),limit(2)')
