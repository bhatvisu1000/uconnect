from com.uconnect.core.dbconnection import ConnectionBuilder
from com.uconnect.core.singleton import Singleton
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.utility.ucLogging import logging
from com.uconnect.core.globals import Global
import com.uconnect.core.error

#from com.uconnect.utility.mongoDbUtility import MongoDbUtility



# lets the parent logger from config file
myLogger = logging.getLogger('uConnect')

#@Singleton
class MongoDB(object, metaclass=Singleton):
    def __init__(self):

        ''' Intialization method -- Private
        Instantiating all methods & logger needed for this module
        '''
        
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
        myModuleLogger.debug("initializing ...")

        self.connBuild = ConnectionBuilder()
        self.util = Utility()
        self.globaL = Global()

        self.myPageSize = self.util.getMaxPageSize()
        self.myExclColl4Id = self.util.getExclColl4Id()

        self.conn = self.connBuild.buildConnection("MongoDB")
        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

        myModuleLogger.debug("Initialization details: conn[{myConn}], myPageSize[{myPageSize}]".format(myConn=self.conn, myPageSize=self.myPageSize))
        myModuleLogger.debug("initialization completed")

        ## validate all the collections

    def __getRequestSummary(self, argCollection, argCriteria, argCurPage = None):
        
        ''' 
            Description:    This method is called internally in conjunction with other method in this class
            argCollection:  Collection name
            argCriteria:    Criteria to retrieve document(s)
            argCurPage:     Current page (optional)
            usage:          <__findDocument(<coll>,<criteria>,<curPage (optional)>)
            Return:         Dict object as request summary
        ''' 
        try:
            if not(self.util.isAllArgumentsValid(argCollection)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argCriteria) + ')' ))

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("arg(s) received: collection[{col}], criteria[{criteria}], curPage[{curPage}]".
                format(col=argCollection,criteria=argCriteria,curPage=argCurPage))

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            myModuleLogger.debug("myDb value after assigning collection [{col}]: [{mydb}]".format(col=argCollection,mydb=myDb))

            myTotDocuments = myDb.find(argCriteria).count()

            if argCurPage == None:
                argCurPage = 0

            myReturnValues = self.util.findPagingValue(myTotDocuments, self.myPageSize, argCurPage)
            myStatus = myReturnValues[0]
            myTotPages = myReturnValues[1]
            #myDisplay = myReturnValues[2]

            ''' if total documents is 1 then total page is 1 regardless of pagesize
            if myTotDocuments <=  self.myPageSize:
                myTotPages = 1
            else:
                myTotPages = myTotDocuments / self.myPageSize 
             
            #if requested page is out of bound display message "out of bound"
            if argCurPage > myTotPages:
                myStatus = "ERROR: Out of bound page request"
                myDisplay = "0"
            else:
                myStatus = "OK"
                myDisplay = str( (argCurPage * self.myPageSize) +1 ) + " to " + str(((argCurPage * self.myPageSize) + 1) + self.myPageSize)
            '''

            # we need to reset the curpage to 1 if it was passed 0 or None

            if argCurPage == 0: argCurPage = 1

            summaryResult = {
                "TotalDocuments":myTotDocuments,
                "TotalPages":myTotPages,
                "RequestedPage":int(argCurPage), 
                "PageSize":self.myPageSize,
                "Status":myStatus }

            myModuleLogger.debug("TotDoc [{totdoc}], TotPages [{totpage}]".format(totdoc=myTotDocuments,totpage=myTotPages))
            myModuleLogger.debug("Summary Result [{summary}]".format(summary=summaryResult))

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        '''
        except Exception as error:
            myModuleLogger.error("Error [{error}]".format(error=error.message))
            raise error
        '''
        return summaryResult

    def __updateKeyValue(self, argCollection, argDictDocument):
        
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <__updateKeyValue(<coll>,<DictDocument>)
            Return:         Dictionary object
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')

            myModuleLogger.debug("arg(s) received: collection[{col}], dictDoc[{dictDoc}]".
                format(col=argCollection,dictDoc=argDictDocument))
 
            ##myDb = self.conn

            myModuleLogger.debug("Connection to be used [{conn}]".format(conn=self.conn))

            if not(self.util.isAllArgumentsValid(argCollection,argDictDocument)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argDictDocument) + ')' ))

            '''
            calling mongodb JS function to get the next sequence
            '''
            try:
                myKeyValue = int(self.conn.system_js.getNextSequence(argCollection))
            except Exception as error:
                raise com.uconnect.core.error.MongoDBError('Error executing ({conn}).system_js.getNextSequence({col})'.format(conn=self.conn, col=argCollection))

            ''' we dont need to generate the id for collection which is marked for exclusion'''
            if not (myKeyValue == None): 
                # we need to use repr() for a value to be appeared as string character
                argDictDocument.update({"_id":repr(myKeyValue)})
            elif myKeyValue == None and (argCollection not in self.util.getExclColl4Id()):             
                raise NullKeyValue("Null Key Value found for collection [{coll}]".format(coll=argCollection))

            myModuleLogger.debug("Results: dictionary document, after updating key value [{dict}]".format(dict=argDictDocument))
            return argDictDocument

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.NullKeyValue as error:
            myModuleLogger.exception("NullKeyValue: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.MongoDBError as error:
            myModuleLogger.exception("c: error [{error}]".format(error=error.errorMsg))
            raise error            
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error


    def genKeyForCollection(self, argCollection):
        
        ''' 
            Description:    Generate keyId for a given collection
            argCollection:  Collection name
            usage:          <genKeyForCollection(<coll>)
            Return:         Keyid for passed collection
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')

            myModuleLogger.debug("arg(s) received: collection[{col}]".
                format(col=argCollection))
 
            ##myDb = self.conn

            myModuleLogger.debug("Connection to be used [{conn}]".format(conn=self.conn))

            if not(self.util.isAllArgumentsValid(argCollection)):
                raise com.uconnect.core.error.MissingArgumentValues('Argument [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ')' ))

            '''
            calling mongodb JS function to get the next sequence
            '''
            try:
                myKeyValue = int(self.conn.system_js.getNextSequence(argCollection))
            except Exception as error:
                raise com.uconnect.core.error.MongoDBError('Error executing ({conn}).system_js.getNextSequence({col})'.format(conn=self.conn, col=argCollection))

            if myKeyValue == None:
                raise NullKeyValue("Null Key Value found for collection [{coll}]".format(coll=argCollection))
            
            myModuleLogger.debug("Results: keyId for [{keyVal}] for collection {col}".format(keyVal=myKeyValue, col=argCollection))

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.NullKeyValue as error:
            myModuleLogger.exception("NullKeyValue: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.MongoDBError as error:
            myModuleLogger.exception("c: error [{error}]".format(error=error.errorMsg))
            raise error            
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error

        return myKeyValue

    def findTotDocuments(self, argCollection, argCriteria = None):
        
        ''' 
            Description:    Find document from a collection
            argCollection:  Collection name
            argCriteria:    Criteria in dict {'criteria1' : 'value'}
            usage:          <findDocument(<coll>,<criteria (optional)>
            Return:         Number (total documents)
        '''
        try:
        
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("arg(s) received: collection[{col}], criteria[{criteria}]".
                format(col=argCollection,criteria=argCriteria))
            myTotDocuments = 0

            if not(self.util.isAllArgumentsValid(argCollection)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ')' ))

            #myModuleLogger.debug("checking if collection [{coll}] exists in db [{db}]".format(coll=argCollection))

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            myModuleLogger.debug("myDb value after assigning collection [{col}]: [{mydb}]".format(col=argCollection,mydb=myDb))        
            myModuleLogger.debug("connection [{conn}] will be used to get this member information".format(conn=myDb))        

            myTotDocuments = myDb.find(argCriteria).count()

            myModuleLogger.debug("Total Documents [{totDocuments}]".format(totDocuments=myTotDocuments))
            ## need to find type of data retunned and then use for x in to put it in dict
            myModuleLogger.debug("completed, returning value")

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            #raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            #raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            #raise error
        finally:
            return myTotDocuments

    def findDocument(self, argCollection, argCriteria, argProjection = None, argFindOne = False, argSort = None):
        
        ''' 
            Description:    Find document from a collection without any paging and sort
            argCollection:  Collection name
            argCriteria:    Criteria to retrieve document(s)
            argProjection:  Column which need to be projected/returned
            argFindOne:     Find only one document 
            usage:          <findDocument(<coll>,<criteria>,<projection>, <True/False>)
            Return:         List
        '''
        
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("arg(s) received: collection[{col}], criteria[{criteria}], projection[{proj}], findOne[{findone}]".
                format(col=argCollection,criteria=argCriteria, proj=argProjection,findone=argFindOne))

            if not(self.util.isAllArgumentsValid(argCollection, argCriteria)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argCriteria) + ')' ))            

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            myData = []

            if not argProjection: argProjection = None

            if (argSort == None) or (not isinstance(argSort,list)): 
                argSort = [("_id",1)]
            
            #print('in mongodb, sort:', argSort)
            #myModuleLogger.debug("arg(s) used for finding document: collection[{col}], criteria[{criteria}], projection[{proj}], findOne[{findone}], sort[{sort}]".
            #    format(col=argCollection,criteria=argCriteria, proj=argProjection,findone=argFindOne, sort=argSort))

            myModuleLogger.debug("Arguments [{arg}] will be used for fetching data".\
                format(arg= ''.join([str(myDb), '-', argCollection, '-', str(argCriteria), '-', str(argProjection), '-', str(argFindOne), '-', str(argSort)] )))        
            
            mySummary = (self.__getRequestSummary(argCollection, argCriteria))

            if argFindOne:
                myData =  myDb.find_one(argCriteria,argProjection)
                if (myData == None): 
                    myData = []
                else:
                    myData = [myData]
            else:
                for data in myDb.find(argCriteria,argProjection).sort(argSort): myData.append(data)

            myResults={"Summary":mySummary,"Data":myData}

            myModuleLogger.debug("Document [{data}] type[{type}] ".format(data=myResults, type=type(myResults)))
            myModuleLogger.debug("completed, returning document")

            return myResults

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myErrorMessage = self.util.extractLogError()            
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error

    def findAllDocuments4Page(self, argCollection, argCriteria = None, argProjection = None, argPage = None, argSort = None):

        ''' 
            Description:    Find all documents from a collection with paging and sort
            argCollection:  Collection name
            argCriteria:    Criteria to retrieve document(s)
            argProjection:  Column which need to be projected/returned
            argPage:        Page# which need to be returned            
            argSort:        Sort arguments, defaults to none 
            usage:          <findDocument(<coll>,<criteria>,<projection>, <True/False>)
            Return:         List
        '''

        try:
            #print ("Collection",argCollection)
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: collection[{coll}], page[{page}], sort[{sort}]".format(coll=argCollection, page=argPage,sort=argSort))

            if not(self.util.isAllArgumentsValid(argCollection)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ')' ))            

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            myData = []

            if argProjection:
                if len(argProjection) == 0: argProjection = None

            ''' 
                Sort value in pymongo should be in list not dictionary 
                .sort([('field',1),('field',-1)])
            '''
            if (argPage == None): argPage=0
            if (argSort == None) or (not isinstance(argSort,list)): 
                argSort = [("_id",1)]

            if not(self.util.isList(argSort)):
                raise com.uconnect.core.error.NotListValue("Sort argument passed [{sort}] is not list value (expecting list)".format(sort=argSort))

            skipPage = int(argPage) * (self.myPageSize)
            mySummary = (self.__getRequestSummary(argCollection, argCriteria, int(argPage)))

            myModuleLogger.debug("arg passed to MongoDB: db[{db}].({criteria}).skip({skipPage}).limit({limit}).sort({sort})]".
                format(db=myDb, criteria=argCriteria,skipPage=skipPage,limit=self.myPageSize,sort=argSort))
            
            for data in myDb.find(argCriteria,argProjection).sort(argSort).limit(self.myPageSize).skip(skipPage):
                myData.append(data)

            myResults={"Summary":mySummary,"Data":myData}
            myModuleLogger.debug("completed, returning document(s)")

            return myResults

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.error("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.error("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.NotListValue as error:
            myModuleLogger.error("NotListValue: error [{error}]".format(error=error.errorMsg))
            raise error
        '''
        except Exception as error:
            myModuleLogger.error("Error [{error}]".format(error=error.message))
            raise error
        '''

    
    def InsertOneDoc(self, argCollection, argDocument):
        ''' 
            Description:    Insert a document in a given collection, _ID value will be overwritten
            argCollection:  Collection name
            argDocument:    Document as dict need to be inserted
            usage:          ( InsertOneDoc(<coll><document as dict>)
            <<
                we should incorporate insert many and one in single method
                need to check if multiple doc is passed
                if mutliptle doc is passed we need to generate the key for each document
                may be for future? not right now
            >>
            Return:         Dictionary (_id, status)
        '''

        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: collection[{coll}], document[{docdict}]".format(coll=argCollection, docdict=argDocument))

            ''' call validation method to see if passed collection is a valid collection '''

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            if not(self.util.isAllArgumentsValid(argCollection,argDocument)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argDocument) + ')' ))            
        
            ''' we need key to be generated for this collection, if not passed as argument dict '''
            
            myArgDocument = argDocument

            if (self.util.isKeyInDict(myArgDocument,'_id')):
                myKeyValue =  myArgDocument['_id'] 
                #print( myKeyValue )
                if (not myKeyValue):
                    myArgDocument = self.__updateKeyValue(argCollection, myArgDocument)
            
            myInsertOneResult = myDb.insert_one(myArgDocument)

            myModuleLogger.debug("requested document inserted with [{_id}, {status}]".format(_id=myInsertOneResult.inserted_id, status=myInsertOneResult.acknowledged))
            myresult = {"_id":myInsertOneResult.inserted_id,"Status":myInsertOneResult.acknowledged}
            
            return myresult
        
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error


    def InsertManyDoc(self, argCollection, argDocument):
        ''' 
            Description:    Insert a document in a given collection, _ID value will be overwritten
            argCollection:  Collection name
            argDocument:    Document as dict need to be inserted
            usage:          ( InsertOneDoc(<coll><document as dict>)
            Return:         (_id,status)
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: collection[{coll}], document[{docdict}]".format(coll=argCollection, docdict=argDocument))

            if not(self.util.isAllArgumentsValid(argCollection,argDocument)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argDocument) + ')' ))            

            myConnectionInst = self.conn
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))

            ''' we need key to be generated for this collection '''
            myDictDocument = self.__updateKeyValue(argCollection, argDocument)
            
            ''' check how many documents are passed, if only one document passed, route the call to Insert one'''

            myInsertManyResult = myDb.insert_one(myDictDocument)

            myModuleLogger.debug("requested document inserted with [{_id}, {status}]".format(_id=myInsertManyResult.inserted_id, status=myInsertOneResult.acknowledged))
            
            myresult = {"_id":myInsertManyResult.inserted_id,"status":myInsertManyResult.acknowledged}
            return myresult

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error

        

    def UpdateDoc(self, argCollection, argCriteria, argUpdateValue, argUpdateOperator = 'set', argUpdateMany = False):
        ''' 
            Description:    Update document(s) in a given collection
            argCollection:  Collection name
            argCriteria:    valid criteria for documents to be updated
            argUpdateValue: Value as dict to be updated
            argUpdateOper:  Updated operator to be used ('set','inc')            
            argUpdateMany:  Update all matching documents (True/False)            
            usage:          ( UpdateDoc(<coll><criteria>,<update_value>,<update_oper>,<update_many>)
            Return:         (_id,status)
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: collection[{coll}], data[{data}]".format(coll=argCollection, data=argUpdateValue))

            if not(self.util.isAllArgumentsValid(argCollection, argCriteria, argUpdateValue)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.format(arg='(' + argCollection + ',' + str(argCriteria) + ',' + str(argUpdateValue) + ')' ))            

            myConnectionInst = self.conn

            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))
            
            if (argUpdateMany):
                myDbUpdate = myDb.update_one
            else:
                myDbUpdate = myDb.update_many
            
            if (argUpdateOperator == 'set'):
                updOperator='$set'
            elif (argUpdateOperator == 'inc') :
                updOperator='$inc'
            elif (argUpdateOperator == 'addToSet') :
                updOperator='$addToSet'
            elif (argUpdateOperator == 'pull') :
                updOperator='$pull'
            else:
                raise com.uconnect.core.error.InvalidOperator("Invalid operator [{oper}] passed during update".format(oper=argUpdateOperator))

            myUpdateClause = {updOperator:argUpdateValue}

            myModuleLogger.debug("Performing update: coll[{coll}], criteria[{criteria}], updateClause[{data}]".
                format(coll=argCollection, criteria=argCriteria, data=myUpdateClause))
            try:
                myUpdatedResult = myDbUpdate(argCriteria, myUpdateClause, upsert=True)
                ## History
            except Exception as error:
                myModuleLogger.error("could not perform update request, error stack[{errStack}]".format(errStack=error))
                raise error

            myModuleLogger.debug("requested document updated, matched [{matched}, modified[{modified}], acknowledged{acknowledged}]".
                format(matched=myUpdatedResult.matched_count, modified=myUpdatedResult.modified_count, acknowledged=myUpdatedResult.acknowledged))
            myresult = {"matched":myUpdatedResult.matched_count, 
                        "modified":myUpdatedResult.modified_count, 
                        "status":myUpdatedResult.acknowledged}
            #print ('in mongodb',myresult)
            return myresult
                            
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error        
        
    def DeleteDoc(self, argCollection, argCriteria, argDeleteMany = False):
        ''' 
            Description:    Delete document(s) in a given collection
            argCollection:  Collection name
            argCriteria:    valid criteria for documents to be updated
            argUpdateMany:  Update all matching documents (True/False)            
            usage:          ( DeleteDoc(<coll><criteria><update_many>)
            Return:         (_id,status)
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: collection[{coll}], document[{doc}]".format(coll=argCollection, doc=argCriteria))

            if not(self.util.isAllArgumentsValid(argCollection, argCriteria)):
                raise com.uconnect.core.error.MissingArgumentValues('One/All of the argument(s) [{arg}] is missing or contains null value'.
                    format(arg='(' + argCollection + ',' + str(argCriteria) + ')' ))            

            myConnectionInst = self.conn

            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))
            
            if (argDeleteMany):
                myDbDelete = myDb.delete_one
            else:
                myDbDelete = myDb.delete_many
            
            myModuleLogger.debug("Deleteing document: coll[{coll}], criteria[{criteria}]".
                format(coll=argCollection, criteria=argCriteria))
            try:
                myDeletedResult = myDbDelete(argCriteria)
                ## History
            except Exception as error:
                myModuleLogger.error("could not perform delete request, error stack[{errStack}]".format(errStack=error))
                raise error

            myModuleLogger.debug("requested document deleted, deleted[{deleted}], acknowledged{acknowledged}]".
                format(deleted=myDeletedResult.deleted_count, acknowledged=myDeletedResult.acknowledged))
            myresult = {"deleted":myDeletedResult.deleted_count, 
                        "status":myDeletedResult.acknowledged}
            
            return myresult
                            
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except com.uconnect.core.error.InvalidCollection as error:
            myModuleLogger.exception("InvalidCollection: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error        

    #db.command('aggregate','member',pipeline=pipeLine, allowDiskUse=True)

    def ExecCommand(self, argCommandDict):
        ''' 
            Description:    Executes command passed as argument defined in argCommandDict
            argCollection:  argCommandDict
            usage:          ( ExecCommand(<argCommandDict>)
            Return:         (_id,status)
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MongoDB')
            myModuleLogger.debug("args received: [{arg}]".format(arg=argCommandDict))

            if not(self.util.isAllArgumentsValid(argCommandDict)):
                raise com.uconnect.core.error.MissingArgumentValues('Argument(s) [{arg}] is missing or contains null value'.
                    format(arg='(' + argCommandDict + ')' ))            

            myConnectionInst = self.conn
            myDb = myConnectionInst
            '''
            try:
                myDb = myConnectionInst[argCollection]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))
            '''
            myModuleLogger.debug("Executing document: arg[{arg}]".format(arg=argCommandDict))

            try:
                myResult = myDb.command(argCommandDict)
            except Exception as error:
                myModuleLogger.error("could not perform execute db command, error stack[{errStack}]".format(errStack=error))
                raise error

            myModuleLogger.debug("db command executed, result[{result}]".format(result=myResult))
            
            return myResult
                            
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error        

    def SearchText(self, argRequestDict,):
        ''' 
            Description:    Executes command passed as argument defined in argCommandDict
            argCollection:  argCommandDict
            usage:          ( SearchText(<argRequestDict>)
            Return:         json
        '''
        try:

            myMainArgData = self.util.getCopy(argRequestDict)
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            ''' validating arguments '''
            myArgKey = ['Collection','Search','Projection','Limit']
            myArgValidationResults = self.util.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.util.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.util.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myConnectionInst = self.conn
            myDb = myConnectionInst
            if "score" not in myMainArgData["Projection"]:
                myMainArgData["Projection"].update({"score": { "$meta": "textScore" }})
            #find
            try:
                myDb = myConnectionInst[myMainArgData['Collection']]
            except Exception as error:
                raise com.uconnect.core.error.InvalidCollection("Can not set collection to [{coll}], error[{error}]".format(coll=argCollection,err=error.message))
            #end

            self.myModuleLogger.debug('Argument [{arg}] used'.format(arg=myMainArgData))
            myResult=[]
            try:
                for doc in myDb.find(\
                    {"$text":{"$search":myMainArgData["Search"] }}, myMainArgData["Projection"] ).\
                        sort([('score', {'$meta': 'textScore'})]).\
                        limit(myMainArgData["Limit"]).skip(int(myMainArgData['Skip'])):
                    #myDb.find (\
                    #    {"$text": {"$search": "Anil" }}, {"_id":1,"Main":1,"score": { "$meta": "textScore" }}).\
                    #    sort([('score', {'$meta': 'textScore'})]).limit(10).skip(0):
                    myResult.append(doc)
            except Exception as error:
                self.myModuleLogger.error("could not perform execute db command, error stack[{errStack}]".format(errStack=error))
                raise error

            self.myModuleLogger.debug("db command executed, result[{result}]".format(result=myResult))
            
            return myResult
                            
        except com.uconnect.core.error.MissingArgumentValues as error:
            self.myModuleLogger.exception("MissingArgumentValues: error [{error}]".format(error=error.errorMsg))
            raise error
        except Exception as error:
            self.myModuleLogger.exception("Error [{error}]".format(error=error.message))
            raise error        

if ( __name__ == "__main__" ):
    print ("In main, I am being called to perform some task")
    myResult = ""
    myDocDB = MongoDB()
    myResult = myDocDB.getADocument('MEMBER',"MEM201981") 
    #myMemberDB.getMemberDetails("MEM201981",myResult)
    #myMemberDB.getMemberDetails("MEM201981",self.myResult)
    #print len(myMemberDB.memberResults)
    #list(myMemberDB.memberResults);
    totalRecords = myResult.count()
    print ("Total %s" % totalRecords ," member found")
    for x in myResult:
        print (x)
