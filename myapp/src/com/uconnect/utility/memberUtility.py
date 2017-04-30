import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security

myLogger = logging.getLogger('uConnect')

@Singleton
class MemberUtility(object):
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
        self.dbutilityInstance = DBUtility.Instance()
        self.globalInstance = Global.Instance()
        self.securityInstance = Security.Instance()

        self.myClass = self.__class__.__name__

    def __buildInitMembderData(self,argMainDict,argAddressDict,argContactDict):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{Main}], [{Address}], [{Contact}] received'.
            format(Main=argMainDict,Address=argAddressDict,Contact=argContactDict))

        myZipCode = argAddressDict['ZipCode']
        myCityNState = self.envInstance.getAddressCityState(myZipCode)
        myCity = myCityNState[0]
        myState = myCityNState[1]

        myInitMemberData = self.envInstance.getTemplateCopy(self.globalInstance._Global__member)
        myModuleLogger.debug('Member template [{template}]'.format(template=myInitMemberData))        

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
        myMemberId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__memberColl)
        myInitMemberData['_id'] = myMemberId

        ''' build initial history data '''
        myInitMemberData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
        myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitMemberData))

        return myInitMemberData

    def __buildGetAllConnPipeline(self, argMemberId, argConnectionType):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{member}], [{conntype}]  received'.format(member=argMemberId,conntype=argConnectionType))
        myModuleLogger.debug('Building pipeline for aggregate function')

        #if argConnectionType == 'member':
        #    myFromCollection = self.memberColl
        if argConnectionType == self.globalInstance._Global__memberColl:
            myFromCollection = self.globalInstance._Global__memberColl
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

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{conn}], [{data}] received'.format(conn=argConnectionType, data=argConnectionRawData))
        myModuleLogger.debug('Building [{conn}] Connection '.format(conn=argConnectionType))

        myConnectionRawData = argConnectionRawData

        if argConnectionType == self.globalInstance._Global__memberColl:
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

    def __getConnectionInfo(self, argRequestDict):
        '''
        Need to find if connectmember is already an accepted connection
        RequestorMemberId, InviteeMemberId, CheckConnectionFor, Auth
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myArgKey = ['RequestorMemberId', 'InviteeMemberId', 'CheckConnectionFor', 'Auth']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            ''' validating arguments '''
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal( {'AuthKey':myMainArgData['Auth']['AuthKey'] } )):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' Preparing '''
            if (myMainArgData['CheckConnectionFor'] == self.globalInstance._Global__RequestorMember):
                myCriteria = {'_id':myMainArgData['RequestorMemberId'], 'Connections.MemberId':myMainArgData['InviteeMemberId'], 'Connections.Type':'Member'}                
            elif (myMainArgData['CheckConnectionFor'] == self.globalInstance._Global__InviteeMember):
                myCriteria = {'_id':myMainArgData['InviteeMemberId'], 'Connections.MemberId':myMainArgData['RequestorMemberId'], 'Connections.Type':'Member'}                
            myProjection = {'_id':1,'Connections.Status':1}

            ''' Finding document '''
            myResult = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, True)
            myMemberConnData = self.utilityInstance.extr1stDocFromResultSets(myResult)

            ''' 
            performing check; 
                If request is for Requestor and connection status is "Accepted", then this is vald connection 
                If request is for Invitee and connection status is "Valid", then this is vald connection 
            '''

            if myMemberConnData and ('Connections' in myMemberConnData) and ('Status' in myMemberConnData['Connections'][0]  ):
                myMemberConnStatus = {'Exists':True,'Status': myMemberConnData['Connections'][0]['Status']}
            else
                myMemberConnStatus = {'Exists':False,'Status':None}     
                '''if (myMainArgData['CheckConnectionFor'] == self.globalInstance._Global__RequestorMember):
                    if  myMemberConnStatus == self.globalInstance._Global__Accepted_Requestor_MemConnectionStatus:
                        isMemberAConnection = self.globalInstance._Global__True
                elif (myMainArgData['CheckConnectionFor'] == self.globalInstance._Global__InviteeMember):
                    if  myMemberConnStatus == self.globalInstance._Global__Accepted_Invitee_MemConnectionStatus:
                        isMemberAConnection = self.globalInstance._Global__True
                '''
            return myMemberConnStatus

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise
        
        def __getMemberConnStatus4Action(self, argRequestDict):
        
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myArgKey = ['ConnectionExists','CurrentStatus','Action','ActionBy','Auth']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            ''' validating arguments '''
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal( {'AuthKey':myMainArgData['Auth']['AuthKey'] } )):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' we need to validate if right action and actionby key is passed'''
            if not (myMainArgData['ActionBy'] in self.globalInstance._Global__MemberConnections.get('New').keys() ):
                raise com.uconnect.core.error.MissingArgumentValues('Expecting [{expectVal}] in [ActionBy] key, got [{argActionBy}] '.
                    format(expectVal=self.globalInstance._Global__MemberConnections.get('New').keys(), argActionBy=myMainArgData['ActionBy']))

            if not ( myMainArgData['Action'] in self.globalInstance._Global__MemberConnections.keys() ):
                raise com.uconnect.core.error.MissingArgumentValues('Expecting [{expectVal}] in [ActionBy] key, got [{argActionBy}] '.
                    format(expectVal=self.globalInstance._Global__MemberConnections.keys(), argActionBy=myMainArgData['Action']))

            ''' we need to determine the next status for a member connection for a given connection'''
            if myMainArgData and myMainArgData['Action'] in self.globalInstance._Global__MemberConnections:
                myNextStatus = self.globalInstance._Global__MemberConnections.get(myMainArgData['Action']).
                                    get(myMainArgData['ActionBy']).
                                    replace('CurrentStatus',myMainArgData['CurrentStatus'])

            if myMainArgData['Action'] == 'New Connection':
            elif myMainArgData['']
        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __ConnectAMemebr2Member(self, argRequestDict):
        ''' This is being called for invitation status will be as "Pending
            usage:          <__linkAMember2Member(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
            Return:         Json object
        '''
        try:
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            isReqConnectionAdded = False
            myArgKey = ['MemberId','ConnectMemberId','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal( { 'AuthKey':myMainArgData['Auth']['AuthKey'] } )):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' Preparing Requestor/Invitee member connection document '''
            myRequestorConn = self.envInstance.getConnTemplateCopy(self.globalInstance._Global__member)
            myInviteeConn = self.envInstance.getConnTemplateCopy(self.globalInstance._Global__member)

            ''' Requestor connection '''
            myRequestorCriteria = {'_id':myMainArgData['MemberId']}
            myRequestorConn['MemberId'] = myMainArgData['ConnectMemberId']
            myRequestorConn['Status'] = self.globalInstance._Global__Default_Requestor_MemConnectionStatus

            ''' Invitee  (reverse connection)'''
            myInviteeCriteria = {'_id':myMainArgData['ConnectMemberId']}
            myInviteeConn['MemberId'] = myMainArgData['MemberId']
            myInviteeConn['Status'] = self.globalInstance._Global__Default_Invitee_MemConnectionStatus

            myModuleLogger.debug('Requestor [{requestor}] connection document [{doc}] prepared'.
                format(requestor=myMainArgData['MemberId'], doc=myRequestorConn))
            myModuleLogger.debug('Invitee [{invitee}] connection document [{doc}] prepared'.
                format(invitee=myMainArgData['ConnectMemberId'],doc=myInviteeConn))

            ''' checking, if Requestor/Invitee connection exists. Add connection if it doesnt exist  '''

            if self.__isAValidMemberConnection(
                    {'RequestorMemberId':myMainArgData['MemberId'],
                     'InviteeMemberId':myMainArgData['ConnectMemberId'],
                     'CheckConnectionFor':self.globalInstance._Global__RequestorMember}): 
                ''' Requestor's connection found, skiping adding this connection '''
                isReqConnSkipped = self.globalInstance._Global__True 
            else:
                ''' Requestor's connection not document, will add a requestor's connection '''
                isReqConnSkipped = self.globalInstance._Global__False
                myConnectionResult =  self.mongoDbInstance.UpdateDoc(
                    self.globalInstance._Global__memberColl, myRequestorCriteria, {'Connections':myRequestorConn}, 'addToSet',False)
                
                myModuleLogger.debug('Requestor connection [{conn}] creation result [{result}]'.
                    format(conn = str(myMainArgData['MemberId'])  + ' -> ' + str(myMainArgData['ConnectMemberId']), result=myConnectionResult))

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:
                    isReqConnectionSuccess = True
                else:
                    isReqConnectionSuccess = False
                #fi
            #fi

            if self.__isAValidMemberConnection(
                {'RequestorMemberId':myMainArgData['MemberId'],
                 'InviteeMemberId':myMainArgData['ConnectMemberId'],
                'CheckConnectionFor':self.globalInstance._Global__InviteeMember}): 
                ''' Invitee's connection found, skiping adding this connection '''
            else:
                ''' Requestor's connection not document, will add a requestor's connection '''
                myConnectionResult =  self.mongoDbInstance.UpdateDoc(
                    self.globalInstance._Global__memberColl, myInviteeCriteria, {'Connections':myInviteeConn}, 'addToSet',False)
                myModuleLogger.debug('Invitee connection [{conn}] creation result [{result}]'.
                    format(conn = str(myMainArgData['ConnectMemberId'])  + ' -> ' + str(myMainArgData['MemberId']), result=myConnectionResult))

                ''' 
                if invitee connection is unsuccessful, we need to remove the Requestor connection, only if we built in this request.
                This is to ensure the data consistency
                '''
                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__UnSuccess:
                    if (not isReqConnSkipped) and (isReqConnectionSuccess == self.globalInstance._Global__True):
                        self.__remAMemConnFromMember(myMainArgData)
                    #fi
                #fi
            #fi
            return myConnectionResult

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

            ''' Build response data 
            myResponseRequest = self.utilityInstance.builInternalRequestDict({'Data':{'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member'}})
            myResponseData = self.getAMemberConnections(myResponseRequest)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myBuildConnectStatus,'Update',myResponseData)

            return myResponse
            '''
    def __remAMemConnFromMember(self, argRequestDict):
        ''' This is being called for invitation status will be as "Pending
            usage:          <__linkAMember2Member(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
            Return:         Json object
        '''
        try:
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Auth']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance.__isValAuthKeyInternal( { 'AuthKey':myMainArgData['Auth']['AuthKey'] } )):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' deleting Requestors connections '''
            myCriteria = {'_id':myMainArgData['MemberId']}
            myConnections = {'MemberId': myMainArgData['ConnectMemberId'],'Type':self.globalInstance._Global__member}
            myConnectionData = {'Connections':myConnections}            
            myReqConnResults =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl,myCriteria, myConnectionData, 'pull',False)

            ''' deleting Invitee connections '''
            myCriteria = {'_id':myMainArgData['ConnectMemberId']}
            myConnections = {'MemberId': myMainArgData['MemberId'],'Type':self.globalInstance._Global__member}
            myConnectionData = {'Connections':myConnections}            
            myInviteeConnResults =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myConnectionData, 'pull',False)

            myModuleLogger.debug('Connection between [{member}] and [{connectMember}] removed, result [{result}]'.
                format(member=myMemberId, connectMember=myConnectMemberId, result=myReqConnResults + ',' + myInviteeConnResults))

            return myInviteeConnResults
        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __acceptInvitation(self, argRequestDict):
        pass
    def __rejectInvitation(self, argRequestDict):
        pass

    def isAValidMember(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MemnberId':'','AuthId':''}
            usage:          <getAGroupDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            myArgKey = ['MemberId','Auth','ResponseMode']
            isValidMember = False 
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData, key=myArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            myCriteria = {'_id':myMainArgData['MemberId']}
            myProjection={'_id':1}
            myFindOne = True

            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, myFindOne)
            myMemberId = self.utilityInstance.extr1stDocFromResultSets(myMemberData)['_id'] 

            if myMemberId and (myMemberId == myMainArgData['MemberId']):
                  isValidMember = True 

            ''' build response data '''            
            return isValidMember

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise
