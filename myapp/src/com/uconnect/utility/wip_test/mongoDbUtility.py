import json, os, sys, pymongo
from pymongo import MongoClient
from com.uconnect.core.connection.dbconnection import ConnectionBuilder
from com.uconnect.core.connection.infra import Environment
from com.uconnect.core.connection.singleton01 import Singleton

@Singleton
class MongoDbUtility(object):

    def __init__(self):
        self.myConnectionBuilder = ConnectionBuilder()
        #print self.myConnectionBuilder
        self.myConnection = self.myConnectionBuilder.buildConnection("MongoDB")
        #print self.myConnection
        self.myEnvironment = Environment.Instance()
        self.myPageSize = self.myEnvironment.maxPageSize
        self.myResults=[]

    def isValidCollection(self, argMongoConn, argMongoDbName, argCollectionName):
        return argCollectionName in argMongoConn[argMongoDbName].collection_names()

    def isValidDb(self, argMongoConn, argMongoDbName):
        return argMongoDbName in argMongoConn.database_names()
    
    def getSelectQueryHeader(self, **kwargs):
        myArguments = kwargs['arg']
        #print "getMongoQuerySumm [{arg}]".format(arg=myArguments)
        self.validateMongoQueryArgs(arg=myArguments)
        #myHostInfo = self.myConnection.serverStatus()
        #print myHostInfo
        myDb = self.myConnection[self.myCollection]
        mySummaryResult = []
        print "skip", self.mySkip
        print "page size", self.myPageSize
        totDocuments = myDb.find(self.myCriteria).skip(int(self.mySkip)).limit(int(self.myPageSize)).count()
        #.skip(int(self.mySkip)).limit(int(self.myPageSize)
        if totDocuments == 0:
            return mySummaryResult
        else:
            totPages = totDocuments / self.myPageSize

        if self.curPage is None:
          self.curPage = 0 
        mySummaryResult = []
        mySummaryResult.append({"summary":{"TotalDocuments":totDocuments,"TotalPages":totPages,"CurrentPage":self.curPage , "PageSize":self.myPageSize,
                         "Displaying": str(self.curPage + 1) + " of " + str(totPages) }})
        #print mySummaryResult
        ## Following are components of serverstatus of mongo database 
        ## process pid connections locks storageEngine globalLock extra_info uptimeEstimate uptime network uptimeMillis
        ## version localTime mem opcountersRepl wiredTiger opLatencies metrics host tcmalloc opcounters ok asserts
        myServerKey = ['connections','host','uptime','process']
        #print "totDoc [%s] totPages [%s]", totDocuments, totPages
        myServerInfo = {}
        for key in myServerKey:
            myServerInfo.update({key:self.myConnection.command("serverStatus")[key]})

        myServerInfo = {"serverInfo": myServerInfo}
        #mySummaryResult = mySummary
        mySummaryResult.append(myServerInfo)
        return mySummaryResult

    def isArgNone(self, *args):
        if len(args) == 0:
            return True
        else:
            return False
    
    def getKeyValueFromDict(self, key, dict):
        try:
            return dict[key]
        except KeyError as err:
            print err
            return None

    def validateMongoQueryArgs(self, **kwargs):
        myArguments = kwargs['arg']
        myRequiredKey = ['MongoConn','Collection','Criteria','Projection','Skip','Limit']
        #print myArguments
        if not (self.isArgNone(myArguments)):
            self.myConnection = self.getKeyValueFromDict('MongoConn',myArguments)
            self.myCollection = self.getKeyValueFromDict('Collection',myArguments)
            self.myCriteria   = self.getKeyValueFromDict('Criteria',myArguments)
            self.myProjection = self.getKeyValueFromDict('Projection',myArguments)
            #self.mySkip       = self.getKeyValueFromDict('Skip',myArguments)
            #self.mylimit      = self.getKeyValueFromDict('Limit',myArguments)
            self.curPage      = self.getKeyValueFromDict('CurPage',myArguments)
            #print "Conn [{conn}], coll [{coll}]".\
            #    format(conn=self.myConnection,coll=self.myCollection)

            #print "criteria [{criteria}], proj [{proj}], skip[{skip}], limit [{limit}]".\
            #    format(criteria=self.myCriteria, proj=self.myProjection, skip=self.mySkip, limit=self.mylimit)

            if self.myConnection is None:
                print "Connection argument is empty !!!"

            if self.myCollection is None:
                print "Collection argument is empty !!!"

            if self.myCriteria is None:
                print "Criteria argument is empty !!!"

            if self.myProjection is None:
                print "Projection argument is empty !!!"
            #if self.mySkip is not None:
            #    self.mySkip =

    def getSelectQueryDetail(self, **kwargs):
        myArguments = kwargs
        #print "getMongoQueryDetail [{arg}]".format(arg=myArguments)
        self.validateMongoQueryArgs(arg=myArguments)
        myDb = self.myConnection[self.myCollection]
        myResults = myQueryResults = []
        ## overriding skip and limit
        self.mySkip = self.myPageSize * (self.curPage)
        myQueryResultCur = myDb.find(self.myCriteria,self.myProjection).skip(int(self.mySkip)).limit(int(self.myPageSize))
        if myQueryResultCur.count() > 0:
            myResults.append(self.getMongoQuerySumm(arg=myArguments))
            for x in myQueryResultCur:
                myResults.append(x)
        #myResults = {"data":myResults}
        #myResults.append({"data":myQueryResults})
        return myResults

if __name__ == "__main__":
    myMongo = mongoDbUtility()

    #myResults = myMongo.getMongoQueryDetail(MongoConn=myMongo.myConnection,Collection='products',Criteria={},Projection={'_id':1},Skip=0,Limit=10,CurPage=2)
    myResults = myMongo.getSelectQueryDetail(MongoConn=myMongo.myConnection,Collection='Member',Criteria={},Projection={'_id':1,'Main.LastName':1, 'Main.FirstName':1},CurPage=2)
    #myHostInfo = myMongo.hostInfo()    
    #print (myResults)
    for x in myResults:
        print(x)
'''
refer variable from function; u can use self keyword to assign and refer
def testFunc(**kwargs):
    print "arguments {args}".format(args=kwargs)
    print "Total args {totArg}".format(totArg=len(kwargs))
    if len(kwargs) == 0:
        print "No argyments received "
        #sys.exit(-1)
        #raise
    else:
        myArguments = kwargs
        myConnection = myArguments['MongoConn']
        myCollection = myArguments['Collection']
        myCriteria   = myArguments['Criteria']
        mySkip       = myArguments['Skip']
        mySkip       = myArguments['Skip']

        for key, value in kwargs.iteritems():
            #print "Key {key}, Value{value} ".format(key=key,value=kwargs[x])
            print "{key} : {value} ".format(key=key,value=value)

testFunc(conn="Myconn", collection="Member", limit=0, skip=0,projection={"_id":1})

def getKeyValueFromDict(key,dict):
    try:
        return dict[key]
    except KeyError as err:
        return None
'''