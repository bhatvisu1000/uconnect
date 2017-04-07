import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error
import com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility

myLogger = logging.getLogger('uConnect')

@Singleton
class MemberBPS(object):
    ''' 
    Member BPS class, called from factory method
    '''
    def __init__(self):
        ''' 
            Description:    Initialization internal method, called internally
            usage:          Called internally
            Return:         N/A
        '''        
        self.envInstance = Environment.Instance()
        self.factoryInstance = Factory.Instance()
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.globalInstance = Global.Instance()

        self.groupColl = 'Group'
        self.memberColl = 'Member'
        self.vendorColl = 'Vendor'
        self.vendorLocColl = 'Location'
        self.locAgentColl = 'Agent'
        ''''
        self.MemberConnectionsTemplate = self.envInstance.defaultsData['Connections']['Member']
        self.GroupConnectionsTemplate = self.envInstance.defaultsData['Connections']['Group']
        self.VendorConnectionsTemplate = self.envInstance.defaultsData['Connections']['Vendor']
        '''
    def __buildInitMembderData(self,argMainDict,argAddressDict,argContactDict):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.debug('Argument [{Main}], [{Address}], [{Contact}]'.
            format(Main=argMainDict,Address=argAddressDict,Contact=argContactDict))

        myZipCode = argAddressDict['ZipCode']
        myCityNState = self.envInstance.getAddressCityState(myZipCode)
        myCity = myCityNState[0]
        myState = myCityNState[1]

        myInitMemberData = self.envInstance.getTemplateCopy('Member')
        myModuleLogger.debug('Defaults Member template [{template}]'.format(template=myInitMemberData))        

        ''' Main '''
        if ( 'LastName' in argMainDict ):
            myInitMemberData['Main']['LastName'] = argMainDict['LastName']
        if ( 'FirstName' in argMainDict ):
            myInitMemberData['Main']['FirstName'] = argMainDict['FirstName']
        if ( 'NickName' in argMainDict ):
            myInitMemberData['Main']['NickName'] = argMainDict['NickName']
        if ( 'Street' in argAddressDict ):
            myInitMemberData['Address']['Street'] = argAddressDict['Street']

        ''' Address '''
        if (not (myCity == None)) and (not(myState == None)): 
            myInitMemberData['Address']['City'] = myCity
            myInitMemberData['Address']['State'] = myState
            myInitMemberData['Address']['ZipCode'] = myZipCode
        else:
            myInitMemberData['Address']['ZipCode'] = myZipCode

        ''' Contact '''
        if ( 'Mobile' in argContactDict ):
            myInitMemberData['Contact']['Mobile'] = argContactDict['Mobile']
        if ( 'Email' in argContactDict ):
            myInitMemberData['Contact']['Email'] = argContactDict['Email']

        ''' lets get the memberid for this member '''
        myMemberId = self.mongoDbInstance.genKeyForCollection(self.memberColl)
        myInitMemberData['_id'] = myMemberId

        ''' build initial history data '''
        myInitMemberData['_History'] = self.utilityInstance.buildInitHistData() 
        myModuleLogger.info('Argument [{arg}] returned'.format(arg=myInitMemberData))

        return myInitMemberData

    def __buildGetAllConnPipeline(self, argMemberId, argConnectionType):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.info('Argument [{member}], [{conntype}]'.format(member=argMemberId,conntype=argConnectionType))
        myModuleLogger.info('Building pipeline for aggregate function')

        #if argConnectionType == 'member':
        #    myFromCollection = self.memberColl
        if argConnectionType == self.memberColl:
            myFromCollection = self.memberColl
            myPipeLine =  [ 
                    {"$match"  : {"_id":argMemberId}},
                    {"$unwind" : {"path":"$Connections","preserveNullAndEmptyArrays":True}},  
                    {"$match"  : { "$and": [{"Connections.Type":argConnectionType} ] } },
                    {"$lookup" :
                        {
                            "from":myFromCollection,
                            "localField":"Connections.MemberId",                  
                            "foreignField":"_id",                  
                            "as":"MyMemberConnections"
                        }      
                    },
                    {"$project": 
                        {
                            "_id":1,"Connections":1,
                            "MyMemberConnections.MemberId":1,
                            "MyMemberConnections.Main":1,"MyMemberConnections.Address":1,"MyMemberConnections.Contact":1
                        }
                    },
                    {
                        "$sort" :
                            {
                                "MyMemberConnections.Main.LastName":1
                            }
                    }
                ]

        return myPipeLine

    def __buildMyConnection(self, argConnectionType, argConnectionRawData):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.info('Argument [{conn}], [{data}]'.format(conn=argConnectionType, data=argConnectionRawData))
        myModuleLogger.info('Building [{conn}] Connection '.format(conn=argConnectionType))

        myConnectionRawData = argConnectionRawData

        if argConnectionType == self.memberColl:
            myResultStatus = {"Success":myConnectionRawData['ok']}
            myMemberConnRawData =  myConnectionRawData['result']
            if (myMemberConnRawData): 
                myMemberConnections = {"_id":myMemberConnRawData[0]['_id']}

                myMemberConnections['Connections'] = []
                for x in myMemberConnRawData:
                    x['MyMemberConnections'][0].update({'Favorite':x['Connections']['Favorite']})
                    x['MyMemberConnections'][0].update({'Blocked':x['Connections']['Blocked']})
                    x['MyMemberConnections'][0].update({'MemberId':x['Connections']['MemberId']})
                    myMemberConnections['Connections'].append(x['MyMemberConnections'][0])

                # sorting now
                #myConnection = json.dumps(myMemberConnections, sort_keys=True)    
                myConnection = myMemberConnections    
            else:
                myConnection = {}
            #print json.dumps(myMemberConnections, sort_keys=True)
            #print myMemberConnections

        return myConnection

    def getAMemberDetail(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {}}
                            }
            usage:          <getAMemberDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        #print (argRequestDict)
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.info('validating dict argument [{arg}]'.format(arg=argRequestDict))

        # raise an user defined exception here
        try:
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            myModuleLogger.info('Finding a member details [{arg}]'.format(arg=myMainArgData))
            myCriteria = myMainArgData
            myFindOne = True

            myProjection={"Main":1,"Address":1,"Contact":1}

            myMemberData = self.mongoDbInstance.findDocument(self.memberColl, myCriteria,myProjection,myFindOne)

            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myMemberData,'Find')
            
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def getAGroupDetail(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'Request':
                                {'Header': {'ScreenId':{},'ActionId':{},'Page':''},
                                 'MainArg': {},
                                 'Auth':{}
                                }
                            }            
            usage:          <getAGroupDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        #print (argRequestDict)
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.info('validating dict argument [{arg}]'.format(arg=argRequestDict))

        # raise an user defined exception here
        try:
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            myModuleLogger.info('Finding a group details [{arg}]'.format(arg=myMainArgData))
            myCriteria = myMainArgData
            myFindOne = True

            myProjection={'Main':1,'Address':1,'Contact':1}

            myGroupData = self.mongoDbInstance.findDocument(self.groupColl, myCriteria,myProjection,myFindOne)
        except com.uconnect.core.error.MissingArgumentValues:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

        return myGroupData

    def getAMemberConnections(self,argRequestDict):
        ''' 
            Description:    Find a member's all connections details
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {}}
                            }
            usage:          <getsAMemberDetail(<argReqJsonDict>)
            Return:         Json object
                    {
                      "_id": 1008,
                      "MyConnections": 
                      [
                        {
                          "_id": 1001,
                          "Type": "Member",
                          "Main": {}
                          "Address": {},
                          "Contact": {},
                          Favorite: 0
                          "Metrics": {<Only for group>
                        }
                      ]
                    }  
                    http://www.jsoneditoronline.org/?id=ae36cfdc68b1255530150d286d14bab8          
                    '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        print (argRequestDict)
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
        myModuleLogger.info('validating dict argument [{arg}]'.format(arg=argRequestDict))

        # raise an user defined exception here
        try:
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            myModuleLogger.info('Finding a members connection [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''
            ''' Find Linked Member '''
            myMemberId = myMainArgData['MemberId']
            myConnectionType = myMainArgData['ConnectionType']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.__buildGetAllConnPipeline(myMemberId,myConnectionType)
            myModuleLogger.debug("Pipeline: {pipeline} will be used to execute the aggregate function")

            #myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            #myConnectionRawData = self.mongoDbInstance.ExecCommand(self.memberColl, myAggregateDict)
            
            myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myConnectionRawData = self.mongoDbInstance.ExecCommand("member", myAggregateDict)

            if self.utilityInstance.isAllArgumentsValid(myConnectionRawData):

                myMemberConnection = {"Data":self.__buildMyConnection('Member',myConnectionRawData)}

                myModuleLogger.info("MyMemberConnection Data: {memberConn}".format(memberConn=myMemberConnection))
            else:
                myMemberConnection = {}

            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myMemberConnection,'Find')

            print ("response",myResponse)
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def searchMembers(self,argRequestDict):
        pass
    def createAMember(self,argRequestDict):
        ''' 
            Description:    Create a member
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {<Member data 'Main','Address','Contact'>}}
                            }
                            We will add 'BusyHours', BusyDays' block from default value
            usage:          <createAMember(<argReqJsonDict>)
            Return:         Json object

            Collection:     Member: Insert a record in Member collection
        '''
        try:
            ''' Validating argument '''
            #myArgRequestData = argRequestDict

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Preparing document,
            Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)
            ''' build initial data '''
            myMemberData = self.__buildInitMembderData(myMainArgData['Main'],myMainArgData['Address'],myMainArgData['Contact'])
            myMemberId = myMemberData['_id'] 

            ''' Executing (creating member)'''
            myModuleLogger.info('Creating new member, data [{doc}]'.format(doc=myMemberData))
            myMemberResult =  self.mongoDbInstance.InsertOneDoc(self.memberColl, myMemberData)
            myModuleLogger.info('Member [{id}] created, result[{result}]'.format(id=myMemberId, result=myMemberResult))

            ''' Building response data '''
            myResponseDataDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myMemberId}})
            myResponseData = self.getAMemberDetail(myResponseDataDict)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myMemberResult,'Insert',myResponseData)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def createAMemGroup(self,argRequestDict):
        ''' 
            Description:    Create a Member's group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'GroupName':'<GroupName>','MeberId':'<owner of group>'}}
                            }
            usage:          <createAMemGroup(<argRequestDict>)
                            MainArg{'GroupName':'','MeberId':''}
            Return:         Json object
            Collection:     Group: Insert a record in Group collection
        '''
        try:

            ''' Validating argument '''
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request, 3rd argmemnt returned as tuple is argument data '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            myModuleLogger.info('Argument received [{arg}] '.format(arg=myMainArgData))

            ''' Preparing document:
            '''
            #myArgRequestData['Request']['MainArg']['Settings']=self.envInstance.defaultsData['Group']['Settings']
            myGroupData = self.envInstance.defaultsData['Group']
            myGroupData['Main']['GroupName'] = myMainArgData['Main']['GroupName']
            myGroupData['Main']['MemberId'] = myMainArgData['Main']['MemberId']
            myGroupData['_History'] = self.utilityInstance.buildInitHistData() 

            myGroupId = self.mongoDbInstance.genKeyForCollection(self.groupColl)
            myGroupData['_id'] = myGroupId

            myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))
            myGroupResult =  self.mongoDbInstance.InsertOneDoc(self.groupColl, myGroupData)
            
            myGroupResultStatus = self.utilityInstance.getCreateStatus(myGroupResult)

            ''' building link between owner of memeber and newly created group '''
            if myGroupResultStatus == self.globalInstance._Global__Success:
                myLogger.info('Group [{group}] creation is successful, now linking to member[{member}]'.
                    format(group=myGroupId, member=myGroupData['Main']['MemberId']))

                myModuleLogger.debug('Group [{group}] created, building internal request for linking Group [{groupId}] to Member{memberId}'.
                    format(group=myGroupId, groupId=myGroupId, memberId=myGroupData['Main']['MemberId']))

                myLinkedData = self.utilityInstance.builInternalRequestDict(
                    {'Data':{'GroupId':myGroupId,'MemberId':myGroupData['Main']['MemberId']}})

                myLinkedResult = self.linkAMember2Group(myLinkedData)
                myLinkedResultStatus = self.utilityInstance.getUpdateStatus(myLinkedResult)
                
                if myLinkedResultStatus == self.globalInstance._Global__UnSuccess:
                    ''' Link was unsuccessful, need to clean up the data (delete group collection just got inserted) '''
                    myLogger.info('Linking group [{group}] to member[{member}] is unsuccessful, removing group'.
                        format(group=myGroupId, member=myGroupData['Main']['MemberId']))
                    myDeleteResult = self.mongoDbInstance.DeleteDoc(self.groupColl,{'_id':myGroupId})
                else:
                    myLogger.info('Linking group [{group}] to member[{member}] is successful'.
                        format(group=myGroupId, member=myGroupData['Main']['MemberId']))

                    ''' Building response data '''
                    '''Do We need to find from factory data on method need to be called to return the data ?'''

                    myResponseDataDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myGroupId}})
                    myResponseData = self.getAGroupDetail(myResponseDataDict)
                    print('response data',myResponseData)
                    myResponse = self.utilityInstance.buildResponseData(argRequestDict['Request']['Header']['ScreenId'],myGroupResult,'Insert', myResponseData)

                    return myResponse
                #end if

            else:
                ''' Creation of group was unsuccessful, no need to send the data back '''
                ''' Build response data '''
                myResponse = self.utilityInstance.buildResponseData(
                    argRequestDict['Request']['Header']['ScreenId'],myGroupResult,'Insert')
                return myResponse
            #end if

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def linkAMember2Member(self,argRequestDict):
        ''' 
            Description:    Linke a member 2 existing member
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','ConnectMemberId'}}
                            }
            usage:          <linkAMember2Member(<argReqJsonDict>)
                            MainArg{'MemberId':'','ConnectMemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))
            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document :    '''
            myConnections = self.envInstance.getConnTemplateCopy('Member')
            myMemberId = myMainArgData['MemberId']
            myConnectMemberId = myMainArgData['ConnectMemberId']
            myCriteria = {'_id':myMemberId}
            myConnections['MemberId'] = myConnectMemberId

            myModuleLogger.debug('Preparing document for connection between [{member}] and [{connectMember}]'.format(member=myMemberId, connectMember=myConnectMemberId))
            myConnectionData = {'Connections':myConnections}            

            ''' Saving document in database '''
            myBuildConnectStatus =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myConnectionData, 'addToSet',False)
            myModuleLogger.debug('Connection between [{member}] and [{connectMember}] created, result [{result}]'.
                format(member=myMemberId, connectMember=myConnectMemberId, result=myBuildConnectStatus))

            ''' Preparing document for reverse connection ConnectMember --> Member(requestor):    '''
            myModuleLogger.debug('Creating reverse connection ')

            myConnections = self.MemberConnectionsTemplate
            myMemberId = myMainArgData['ConnectMemberId']
            myConnectMemberId = myMainArgData['MemberId']
            myCriteria = {'_id':myMemberId}
            myConnections['MemberId'] = myConnectMemberId

            myModuleLogger.debug('Preparing document for connection between [{member}] and [{connectMember}]'.format(member=myMemberId, connectMember=myConnectMemberId))
            myConnectionData = {'Connections':myConnections}            

            ''' Saving document in database '''
            myBuildConnectStatus =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myConnectionData, 'addToSet',False)
            myModuleLogger.debug('Connection between [{member}] and [{connectMember}] created, result [{result}]'.
                format(member=myMemberId, connectMember=myConnectMemberId, result=myBuildConnectStatus))

            ''' Build response data '''
            myResponseRequest = self.utilityInstance.builInternalRequestDict({'Data':{'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member'}})
            myResponseData = self.getAMemberConnections(myResponseRequest)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myBuildConnectStatus,'Update',myResponseData)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def linkAMember2Group(self,argRequestDict):
        ''' 
            Description:    Linke a member 2 a Group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'GroupId':'','MemberId'}}
                            }
            usage:          <linkAMember2Member(<argReqJsonDict>)
                            MainArg{'GroupId':'','MemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))
            myLinkedData = {}

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myLinkedData = {'LinkedBy':{'GroupId':myMainArgData['GroupId']}}
            myMemberId = myMainArgData['MemberId']
            myGroupId = myMainArgData['GroupId']
            myCriteria = {'_id':myMemberId}
            myModuleLogger.info('Adding member to a group [{memberId} --> {groupId}]'.format(
                memberId=myMemberId, groupId=myGroupId))

            ''' Updating document (Group Collection, add participant) '''
            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myLinkedData, 'addToSet',False)
            myUpdateStatus = self.utilityInstance.getUpdateStatus(myLinkedResult)
            
            ''' will link member to group in member collection, if member was associated '''

            if myUpdateStatus == self.globalInstance._Global__Success:
                myModuleLogger.info('Member -> Group connection successful, adding participant in group')

                ''' Adding participant in Group collection  '''
                myModuleLogger.info('Adding participant [{memberId}] to group [{groupId}]'.format(
                    memberId=myMemberId, groupId=myGroupId))

                ''' preparing document '''
                myParticipantdData = {'Participants':{'MemberId':myMemberId,'When':datetime.datetime.utcnow()}}
                myCriteria = {'_id':myGroupId}

                '''executing update document '''
                myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.groupColl, myCriteria, myParticipantdData, 'addToSet',False)

                myModuleLogger.info('Member [{memberId} linked to group {groupId}]'.format(
                    memberId=myMemberId, groupId=myGroupId))

            ''' Build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def addMember2Favorite(self,argRequestDict):
        ''' 
            Description:    Mark a memebr as a favorite
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','FavoriteMemberId':''}}
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','FavoriteMemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myMemberId = myMainArgData['MemberId']
            myFavoriteMember = myMainArgData['FavoriteMemberId']
            myCriteria = {'_id':myMemberId,'Connections.MemberId':myFavoriteMember,'Connections.Type':'Member'}
            myFavoriteData = {"Connections.$.Favorite":1}

            myModuleLogger.info('Adding Memebr [{favMember}] to Member [{member}]s Favorite list'.format(
                favMember=myFavoriteMember, member=myMemberId))

            ''' Saving document '''
            ##db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})
            myMarkFavoriteStatus =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myFavoriteData, 'set',False)

            ''' build response data '''
            myResponseRequest = self.utilityInstance.builInternalRequestDict({'Data':{'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member'}})
            myResponseData = self.getAMemberConnections(myResponseRequest)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'], myMarkFavoriteStatus,'Update',myResponseData)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def removeMemberFromFavorite(self,argRequestDict):
        ''' 
            Description:    Remove a Memebr from favorite list
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','FavoriteMemberId':''}}
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','FavoriteMemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            #this is example --> db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})

            myMemberId = myMainArgData['MemberId']
            myFavoriteMember = myMainArgData['FavoriteMemberId']
            #myFavoriteData = {'LinkedBy.$.Favorite':0}
            myFavoriteData = {"Favorite":{"MemberId":myFavoriteMember}}
            myCriteria = {'_id':myFavoriteMember, 'LinkedBy.MemberId':myMemberId}

            myModuleLogger.info('Remove Memebr [{favMember}] from Member [{member}]s Favorite list'.format(
                favMember=myFavoriteMember, member=myMemberId))

            ''' Executing document update '''

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myFavoriteData, 'pull',False)
            #myUpdateStatus = self.utilityInstance.getUpdateStatus(myResult)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def blockMember(self,argRequestDict):
        ''' 
            Description:    Block a Memebr 
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','BlockMemberId':''}}
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','BlockMemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            #this is example --> db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})

            myMemberId = myMainArgData['MemberId']
            myBlockedMember = myMainArgData['BlockMemberId']
            myBlockedData = {'LinkedBy.$.Blocked':1}
            myCriteria = {'_id':myFavoriteMember, 'LinkedBy.MemberId':myMemberId}

            myModuleLogger.info('Block Memebr [{blockMember}] from Member [{member}]'.format(
                blockMember=myBlockedMember, member=myMemberId))

            ''' Executing document update '''

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myBlockedData, 'set',False)
            #myUpdateStatus = self.utilityInstance.getUpdateStatus(myResult)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error


    def unBlockMember(self,argRequestDict):
        ''' 
            Description:    Block a Memebr 
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','BlockMemberId':''}}
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','BlockMemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            #this is example --> db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})

            myMemberId = myMainArgData['MemberId']
            myBlockedMember = myMainArgData['BlockMemberId']
            myBlockedData = {'LinkedBy.$.Blocked':0}
            myCriteria = {'_id':myFavoriteMember, 'LinkedBy.MemberId':myMemberId}

            myModuleLogger.info('Unblock [{blockMember}] from Member [{member}]'.format(
                blockMember=myBlockedMember, member=myMemberId))

            ''' Executing document update '''

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myBlockedData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def updateMemberMain(self,argRequestDict):
        ''' 
            We need to combine all update of a Member
            Description:    Update Member's Main information (LastName,FirstName,NickName,Sex)
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Main':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Main':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myMemberId = myMainArgData['MemberId']
            myCriteria = {'_id':myMemberId}
            # remove emty key from key argument
            myMainData = self.utilityInstance.convList2Dict(myMainArgData['Main'])

            myModuleLogger.info('Updating Member [{member}] Main[{address}]' .format(
                member=myMemberId, Main=myMainData))

            ''' Executing document update '''

            myResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myMainData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def updateMemberAddress(self,argRequestDict):
        ''' 
            Description:    Update Member's Address
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Address':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Contact':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myMemberId = myMainArgData['MemberId']
            myCriteria = {'_id':myMemberId}
            ''' we will get data in same format as it exists in collection, need to remove empty key '''
            #myAddressData = self.utilityInstance.convList2Dict(myMainArgData['Address'])

            myModuleLogger.info('Updating Member [{member}] Address[{address}]' .format(
                member=myMemberId, contact=myAddressData))

            ''' Executing document update '''

            myResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myAddressData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def updateMemberContacts(self,argRequestDict):
        ''' 
            Description:    Update Member's contact 
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Contact':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Contact':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.MemberBPS')
            myModuleLogger.info('validating dict argument [{arg}]'.format(arg = argRequestDict))

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myMemberId = myMainArgData['MemberId']
            ''' we will get data in same format as it exists in collection, need to remove empty key '''
            #myAddressData = self.utilityInstance.convList2Dict(myMainArgData['Address'])


            myCriteria = {'_id':myMemberId}
            myContactData = self.utilityInstance.convList2Dict(myMainArgData['Contact'])

            myModuleLogger.info('Updating Member [{member}] contact[{contact}]' .format(
                member=myMemberId, contact=myContactData))

            ''' Executing document update '''

            myResult =  self.mongoDbInstance.UpdateDoc(self.memberColl, myCriteria, myContactData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

    def updateMemberSettings(self,argRequestDict):
        pass    
