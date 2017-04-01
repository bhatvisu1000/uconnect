#com.uconnect.core.connection.dbconnection.infra import Environment
from com.uconnect.core.connection.dbconnection import ConnectionBuilder
from com.uconnect.core.connection.infra import Environment
import logging, com.uconnect.utility.ucLogging
#import com.uconnect.utility.ucException

# lets the parent logger from config file
myLogger = logging.getLogger('uConnect')

class __init__:
    pass

class MemberDB:
    def __init__(self):
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberDB')
        myModuleLogger.debug("initializing ...")
        self.myConnectionBuilder = ConnectionBuilder()
        self.myConnection = self.myConnectionBuilder.buildConnection("MongoDB")
        self.myEnvironment = Environment()
        self.myPageSize = self.myEnvironment.maxPageSize
        myModuleLogger.debug("Initialization details: myConnection[{myConn}], myPageSize[{myPageSize}]".format(myConn = self.myConnection, myPageSize))
        myModuleLogger.debug("initialization completed")

        ## validate all the collections

    def getRequestSummary(self, mongoConn, collection, criteria, curPage = None):
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberDB')
        myModuleLogger.debug("arg(s) received: mongoConn[{conn}], collection[{col}], criteria[{criteria}], curPage[{curPage}]".format(conn=mongoConn,col=collection,criteria=criteria,curPage=curPage))
 
        myDb = mongoConn[collection]

        myModuleLogger.debug("myDb value after assigning collection [{col}]: [{mydb}]".format(col=collection,mydb=myDb))

        totDocuments = myDb.find(criteria).count()
        totPages = totDocuments / self.myPageSize 
        #summaryResult=[]
        summaryResult = {"TotalDocuments":totDocuments,"TotalPages":totPages,"CurrentPage":curPage, "PageSize":self.myPageSize,
                         "Displaying": str(curPage * self.myPageSize) + " to " }
        print "totDoc [%s] totPages [%s]", totDocuments, totPages
        return summaryResult

    def getAMemberDetail(self,meberId):
        # since we are not using flask to connect to db, following code is not needed
	    #with self.myMongoDb.app.app_context():
              #memberData = self.myConnection.db.Member.find_one_or_400({"_id":meberId},{'_id':1,'Main':1})
              #memberData = self.myConnection.db.Member.find(filter={"_id":meberId})
        print self.myConnection
        memberData = self.myConnection.Member.find_one({"_id":meberId})
        return memberData

    def getAllMemberDetails(self,page = 0):
        # since we are not using flask to connect to db, following code is not needed
        #with self.myMongoDb.app.app_context():
              #memberData = self.myConnection.db.Member.find_one(filter={"_id":meberId})
        #print "Max Page Size:", self.myPageSize
        myResults = []
        #self.getRequestSummary(self.myConnection, 'Member', {},int(page))
        myResults.append(self.getRequestSummary(self.myConnection, 'Member', {},int(page)))
        #print mySummary
        #myResults.append(mySummary)
        #myResults = myResults.append(self.getRequestSummary(self.myConnection, 'Member', {},int(page)))

        '''if (int(page) == 0):
        totDocuments = self.myConnection.Member.find({}).count()
        totPages = totDocuments / self.myPageSize
        myResults.append({"totalDocuments":totDocuments,"totalPages":totPages})
        '''
        skipPage = int(page) * (self.myPageSize)

        #print "Page#:", page, "SkipPage:", skipPage
        #if isValidConnection(self.myConnection, 'Member'):
        memberData = self.myConnection.Member.find({}).skip(skipPage).limit(self.myPageSize)
        #print memberData.count()
        #build the result sets
        for x in memberData:
            myResults.append(x)
        return myResults

'''
Following code is for testing purpose only

if ( __name__ == "__main__" ):
    print "In main, I am being called to perform some task"
    myResult = ""
    myMemberDB = MemberDB()
    myResult = myMemberDB.getMemberDetails("MEM201981") 
    #myMemberDB.getMemberDetails("MEM201981",myResult)
    #myMemberDB.getMemberDetails("MEM201981",self.myResult)
    #print len(myMemberDB.memberResults)
    #list(myMemberDB.memberResults);
    totalRecords = myResult.count()
    print "Total %s" % totalRecords ," member found"
    for x in myResult:
		print x
'''