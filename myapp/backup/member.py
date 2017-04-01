from DBConnection import ConnectionBuilder

class __init__:
    pass

class MemberDB:

    def __init__(self):
        #declare and initialize all global variables here
        #self.iCurMemberResults = ""
        self.myConnectionBuilder = ConnectionBuilder()
        self.myMongoDb = self.myConnectionBuilder.buildConnection("MongoDB")
        self.myConnection = self.myMongoDb.mongo

    def getMemberDetails(self,meberId):
        # need connection
		#myConnectionBuilder = ConnectionBuilder()
		#myMongoDb = myConnectionBuilder.buildConnection("MongoDB")
		#myConnection = myMongoDb.mongo
		# define context so we can retrieve the data, will append to ResultSets

		with self.myMongoDb.app.app_context():
			memberResults = self.myConnection.db.Member.find({"_id":meberId},{'_id':1,'Main':1})
            # following code is needed when global var is declared as an array, because append is not an attribute
            # of a string
            #self.memberResults(myConnection.db.Member.find({"_id":meberId},{'_id':1,'Main':1}))
			#output.append({'_id' :MemberData['_id']});
			#print MemberData['_id']			
		    #print memberResults

		return memberResults

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


	