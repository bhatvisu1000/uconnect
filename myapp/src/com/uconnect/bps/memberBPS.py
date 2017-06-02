import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security
from com.uconnect.core.member import Member
from com.uconnect.core.activity import Activity
from com.uconnect.core.entityconnection import Connections

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
        self.factoryInstance = Factory.Instance()
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.globalInstance = Global.Instance()
        self.securityInstance = Security.Instance()
        self.memberInstance = Member.Instance()
        self.activityInstance = Activity.Instance()
        self.connectionsInstance = Connections.Instance()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
    '''
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    MMM       MMM   EEEEEEEEEE   MMM       MMM   BBBBBBBBBBB    EEEEEEEEEE   RRRRRRRRRRRR
    MMMM     MMMM   EE           MMMM     MMMM   BB        BB   EE           RR        RR
    MM MM   MM MM   EE           MM MM   MM MM   BB        BB   EE           RR        RR
    MM  MM MM  MM   EEEEEEEEEE   MM  MM MM  MM   BBBBBBBBBBBB   EEEEEEEEEE   RRRRRRRRRRRR
    MM   MMM   MM   EE           MM   MMM   MM   BB        BB   EE           RR        RR
    MM         MM   EE           MM         MM   BB        BB   EE           RR         RR
    MM         MM   EEEEEEEEEE   MM         MM   BBBBBBBBBBB    EEEEEEEEEE   RR          RR
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    '''

    def ____createAMember(self,argRequestDict):
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
        #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        try:
            ## we need to check who called this function, must be from register
            #print(self.utilityInstance.whoAmi())
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Main','Address','Contact']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=myMainArgData))

            ''' Preparing value to create a new member build initial data '''
            myMemberData = self.memberInstance._Member__buildInitMembderData({'Main':myMainArgData['Main'],'Address':myMainArgData['Address'],'Contact':myMainArgData['Contact']})
            myMemberId = myMemberData['_id'] 

            ''' Creating a member '''
            self.myModuleLogger.info('Creating new member, data [{doc}]'.format(doc=myMemberData))
            myMemberResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__memberColl, myMemberData)
            self.myModuleLogger.info('Member [{id}] created, result[{result}]'.format(id=myMemberId, result=myMemberResult))

            ''' Building response data, we can not retrieve member information because we dont have Auth ket yet, will return member id created'''

            '''
            myRequestDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myMemberId}})
            myRequestDict = self.getAMemberDetail(myResponseDataDict)
            myResponse = self.utilityInstance.buildResponseData(self.globalInstance._Global__InternalRequest,myMemberResult,'Insert',myResponseData)
            '''
            myResponse = myMemberResult['_id']
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg            
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            raise
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])            
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise

    def getAllInformation4Member(self,argRequestDict):
        # wip
        ''' 
            We need to combine all update of a Member
            Description:    Update Member's Main information (LastName,FirstName,NickName,Sex)
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Main':[{'Key':'Value'},...]
                            }
            usage:          <getAllInformation4Member(<argReqJsonDict>)
                            MainArg{'MemberId':'','Main':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            
            ''' Initialization & Validation '''

            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Auth','ResponseMode']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' validating Auth arg '''
            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                #print(self.utilityInstance.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))
            #fi

            ''' Preparing document:    '''
            myMemberId = myMainArgData['Auth']['EntityId']
            myCriteria = {'_id':myMemberId}

            # get Member Details
            myMemberDetails = self.getAMemberDetail({'ResponseMode':self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            # get All Connections (Member)
            myConnectionArgData = {'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
            myMemberConnections = self.getAMemberConnections(myResponseArgData)
            # Get All Group this member participates to (owner of a group is also member)
           
            # we need to combine all results in one result sets
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            raise error

    def updateMemberDetail(self, argRequestDict):
        ''' 
            Description:    Update member information
                            Main      --> Member's Main information
                            Address   --> Member's Address information
                            Contact   --> Member's Contact information
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Main','Address','Contact','Auth',ResponseMode'}
            usage:          <updateMemberDetail(<argRequestDict>)
            Return:         Json object

        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            ''' validating arguments '''
            myArgKey = ['Auth']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # will check either Main/Address/Contact/Settings information is passed for update
            #{'a','d'} <= set(a), need to fix this
            if not(any (block in myMainArgData.keys() for block in ['Main','Address','Contact','Settings'])):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], expecting Main/Address/Contact/Settings'.\
                    format(arg=myMainArgData.keys()))
            
            ''' commenting below code, we will get the entityid from AUTH 
            will overwrite EntityType and EntityId if passed in Auth dictionary. 
            This is to ensure that Auth key must belong to this Member
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['_id']})
            '''

            ''' validating auth args '''
            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                #print(self.utilityInstance.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))
            #fi

            #we need to find the block which is beieng changed in Member collection dcoument
            if 'Main' in myMainArgData and myMainArgData['Main']:
                self.myModuleLogger.debug('Got Main[{main}] information which changed'.format(main=myMainArgData['Main']))
                myUpdateResult = self.memberInstance._Member__updateMemberMain(myMainArgData)
                print('MainUpdateResult',myUpdateResult,myMainArgData)
            #fi
            if 'Address' in myMainArgData and myMainArgData['Address']:
                print('In Address')
                self.myModuleLogger.debug('Got Address[{address}] information which changed'.format(address=myMainArgData['Address']))
                myUpdateResult = self.memberInstance._Member__updateMemberAddress(myMainArgData)

            #fi
            if 'Contact' in myMainArgData and myMainArgData['Contact']:
                print('In Contact')
                self.myModuleLogger.debug('Got Contact[{contact}] information which changed'.format(contact=myMainArgData['Contact']))
                myUpdateResult = self.memberInstance._Member__updateMemberContact(myMainArgData)

            #fi

            # rebuilding tag and recording this activity 
            self.myModuleLogger.info('Updating Tag for member [{member}]' .format(member=myMainArgData['Auth']['EntityId']))
            myTagUpdateResult = self.memberInstance._Member__updateMemberTag({'_id':myMainArgData['Auth']['EntityId']})

            #record this activity
            self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(
                myMainArgData['Auth']['EntityId'],self.globalInstance._Global__member,self.globalInstance._Global__External,'Member [{member}] detail [{change}] changed'.
                    format(member=myMainArgData['Auth']['EntityId'], change=myMainArgData), myMainArgData['Auth']))

            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

            ''' get all the information of a member '''
            myMemberDetailResults = self.getAMemberDetail({'ResponseMode':self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            print(myMemberDetailResults)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberDetailResults)

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        finally:
            print('myResponse' in locals())
            if 'myResponse' in locals():
                return myResponse
            else:
                raise

    def updateMemberSettings(self,argRequestDict):
        pass    

    def UpdateConnectionDetails(self, argRequestDict):
        ''' 
            Description:    UpdateConnectionDetails (Only Invitee can accept the connection)
                            Requestor   --> _id 
                            Invitee     --> [])
                            Action      --> Invite/Remove/Accept/Reject/Remove 
                                Requestor:  Invite/Remove
                                Invitee:    Accept/Reject/Remove
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MainArg': {'_id':'','Connections':[{'MemberId':'','Actions':''}],'Auth':'','ResponseMode'}}
            usage:          <UpdateConnectionDetails(<argReqJsonDict>)
            Return:         Json object
        '''
        try:
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            myActivityDetails = ''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            # validating arguments
            myArgKey = ['Connections','Auth','ResponseMode']
            myConnectionArgs = myMainArgData['Connections']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # if connection is passed as dict, converting to list
            if not(self.utilityInstance.isList(myConnectionArgs)):
                myConnectionArgs = [myConnectionArgs]

            # we might get more than one connection request
            for myConnections in myConnectionArgs:
                myArgKey = ['Id','Type','Action']
                if myConnections['Action'] not in self.globalInstance._Global__Connection_Action:
                    raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Action must be one of the value in[{action}]'.format(action=self.globalInstance._Global__Connection_Action))
                #fi
                myArgValidationResults = self.utilityInstance.valRequiredArg(myConnections, myArgKey)
                myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                        format(arg=myConnections.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
                #fi
                if (myConnections['Action'] == 'Favorite') and ('Favorite' not in myConnections):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Mainarg validation error; missing "Favorite" key')
                #fi
                if (myConnections['Action'] == 'Blocked') and ('Blocked' not in myConnections):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Mainarg validation error; missing "Blocked" key')
                #fi
            #end for loop

            ''' commenting out below code as its not needed, we will pick entity id from AUTH
            will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['_id']})
            '''

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))
            #fi

            # lets perform action
            for myConnections in myConnectionArgs:
                myConnectionArgData = {'_id':myMainArgData['Auth']['EntityId'],'Type':self.globalInstance._Global__member,
                                    'ConnectionId': myConnections['Id'], 'ConnectionType': myConnections['Type']}
                # we need to populate favorite and block dict as well
                print('processing connection request [{request}]'.format(request=myConnectionArgData))
                if myConnections['Action'] == self.globalInstance._Global__Connection_Action_Invite:
                    myConnectionResults = self.connectionsInstance._Connections__AddAConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] added [{conn}] as a connection '.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif myConnections['Action'] == self.globalInstance._Global__Connection_Action_Accepted:
                    myConnectionResults = self.connectionsInstance._Connections__acceptInvitation(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] accepted connection request from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif myConnections['Action'] == self.globalInstance._Global__Connection_Action_Rejected:
                    myConnectionResults = self.connectionsInstance._Connections__rejectInvitation(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] rejected connection request from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globalInstance._Global__Connection_Action_Removed:
                    myConnectionResults = self.connectionsInstance._Connections__removeConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] removed connection from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globalInstance._Global__Connection_Action_Favorite:
                    print('Fav',myConnections)
                    myConnectionArgData.update({'Favorite':myConnections['Favorite']}) 
                    myConnectionResults = self.connectionsInstance._Connections__favoriteConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] updated favorite attribute of connection [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globalInstance._Global__Connection_Action_Block:
                    myConnectionArgData.update({'Blocked':myConnections['Blocked']})
                    myConnectionResults = self.connectionsInstance._Connections__blockConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] updated block attribute of connection [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                #fi
                #print('in BPS result',myConnectionResults)
                if myConnectionResults.get('Status') == self.globalInstance._Global__Success:
                    ''' recording activity '''
                    myActivityDetails = 'Success,' + myActivityDetails
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                else:
                    myActivityDetails = 'UnSuccess: ' + myActivityDetails
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myConnectionResults.get('Message'))
                    print('reqStatus',myRequestStatus)
                #fi
                self.myModuleLogger.info(myActivityDetails)
            # end for loop                

            ''' preparing response; get all connection member details for this member '''
            myResponseArgData = {'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
            myResponseData = self.getAMemberConnections(myResponseArgData)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',myResponseData)

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            print('Error',myErrorMessage)
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise
            #fi
    # ends ExecConnectionAction

    def getAMemberDetail(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'MemberId','Auth','ResponseMode'}
            usage:          <getAMemberDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        #print (argRequestDict)
        ''' frollowing import is placed here; this is to avoid error while import module in each other '''

        try:
            
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myArgKey = ['Auth','ResponseMode']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if myMainArgData['ResponseMode']  == self.globalInstance._Global__InternalRequest:
                if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
                #fi
            else:
                if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
                #fi
            #fi
            ''' preparing value needed to find member details'''
            myCriteria = {'_id':myMainArgData['Auth']['EntityId']}
            myFindOne = self.globalInstance._Global__True
            myProjection={"Main":1,"Address":1,"Contact":1,"Tag":1}

            self.myModuleLogger.info('Finding member [{member}] details'.format (member=myMainArgData['Auth']['EntityId']))
            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria,myProjection,myFindOne)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

            ''' Building response '''           
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',myMemberData)
            
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])            
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise

    def getAMemberConnections(self,argRequestDict):
        ''' 
            Description:    Find a member's all connections details
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {}}
                            }
            usage:          <getsAMemberDetail(<argReqJsonDict>)
                    http://www.jsoneditoronline.org/?id=ae36cfdc68b1255530150d286d14bab8          
                    '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        #print (argRequestDict)
        # raise an user defined exception here
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['ConnectionType','Auth','ResponseMode']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' commeting out below code
            will overwrite EntityType and EntityId if passed in Auth dictionary. 
            This is to ensure that Auth key must belong to this Member 
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['_id']})
            '''

            ''' Validate auth key for this request'''
            if myMainArgData['ResponseMode'] == self.globalInstance._Global__InternalRequest:
                if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
                #fi
            else:
                if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
                #fi
            #fi             

            ''' preparing value needed to find member connections'''
            self.myModuleLogger.info('Finding a members connection [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''

            myMemberId = myMainArgData['Auth']['EntityId']
            myConnectionType = myMainArgData['ConnectionType']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.memberInstance._Member__buildGetAllConnPipeline({'MemberId':myMemberId,'ConnectionType':myConnectionType})
            self.myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            #myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            #myConnectionRawData = self.mongoDbInstance.ExecCommand(self.memberColl, myAggregateDict)
            
            myAggregateDict = {"aggregate":self.globalInstance._Global__memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myConnectionRawData = self.mongoDbInstance.ExecCommand(myAggregateDict)

            if self.utilityInstance.isAllArgumentsValid(myConnectionRawData):
                myMemberConnection = {"Data":self.memberInstance._Member__buildMyConnection({'ConnectionType':self.globalInstance._Global__member,'ConnectionRawData':myConnectionRawData})}
            else:
                myMemberConnection = {}
            #fi

            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnection)

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise

    def SearchMember(self,argRequestDict):
        ''' 
            Description:    Search memebr based of argument passed
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'SearchCriteria','Page',Auth','ResponseMode'}
            usage:          <getAMemberDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))            
            myArgKey = ['SearchCriteria','Page','Auth','ResponseMode']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
            #fi 
            
            # preparing documemt for search
            mySearchCriteria = myMainArgData['SearchCriteria'].upper()
            print('Search',mySearchCriteria)
            myTextSearhDocArgDict = \
                {'Collection':'Member', 'Search':"\"mySearchCriteria\"",'Projection':{'_id':1,'Main':1}, 'Limit':10, 'Skip':"0"}
            mySearchResults = self.mongoDbInstance.SearchText(myTextSearhDocArgDict)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', mySearchResults)
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise
            #fi
