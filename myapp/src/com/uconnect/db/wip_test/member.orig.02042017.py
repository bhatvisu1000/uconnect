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
        
        myModuleLogger.debug("Initialization details: myConnection[{myConn}], myPageSize[{myPageSize}]".format(myConn=self.myConnection, myPageSize=self.myPageSize))
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

        myModuleLogger.debug("TotDoc [{totdoc}], TotPages [{totpage}]".format(totdoc=totDocuments,totpage=totPages))
        myModuleLogger.debug("Summary Result [{summary}]".format(summary=summaryResult))
        
        return summaryResult

    def getAMemberDetail(self,meberId):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberDB')
        myModuleLogger.debug("args received: memberid[{memberid}]".format(memberid=meberId))
        myModuleLogger.debug("connection [{conn}] will be used to get this member information".format(conn=self.myConnection))        

        memberData = self.myConnection.Member.find_one({"_id":meberId})

        myModuleLogger.debug("Member data [{data}]".format(data=memberData['Main']))

        myModuleLogger.debug("completed ...")
        return memberData

    def getAllMemberDetails(self,page = 0):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberDB')
        myModuleLogger.debug("args received: page[{page}]".format(page=page))

        myResults = []
        myResults.append(self.getRequestSummary(self.myConnection, 'Member', {},int(page)))

        skipPage = int(page) * (self.myPageSize)

        memberData = self.myConnection.Member.find({}).skip(skipPage).limit(self.myPageSize)

        for x in memberData:
            myResults.append(x)

        myModuleLogger.debug("completed ...")

        return myResults

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
