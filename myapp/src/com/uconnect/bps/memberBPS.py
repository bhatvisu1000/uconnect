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

#@Singleton
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
        self.factory = Factory()
        self.util = Utility()
        self.mongo = MongoDB()
        self.globaL = Global()
        self.sec = Security()
        self.member = Member()
        self.activity = Activity()
        self.conn = Connections()

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
            #print(self.util.whoAmi())
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Main','Address','Contact']

            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Preparing value to create a new member build initial data '''
            myMemberData = self.member._Member__buildInitMembderData({'Main':myMainArgData['Main'],'Address':myMainArgData['Address'],'Contact':myMainArgData['Contact']})
            myMemberId = myMemberData['_id'] 

            ''' Creating a member '''
            self.myModuleLogger.info('Creating new member, data [{doc}]'.format(doc=myMemberData))
            myMemberResult =  self.mongo.InsertOneDoc(self.globaL._Global__memberColl, myMemberData)
            self.myModuleLogger.info('Member [{id}] created, result[{result}]'.format(id=myMemberId, result=myMemberResult))

            ''' Building response data, we can not retrieve member information because we dont have Auth ket yet, will return member id created'''

            '''
            myRequestDict = self.util.builInternalRequestDict({'Data':{'_id':myMemberId}})
            myRequestDict = self.getAMemberDetail(myResponseDataDict)
            myResponse = self.util.buildResponseData(self.global._Global__InternalRequest,myMemberResult,'Insert',myResponseData)
            '''
            myResponse = myMemberResult['_id']
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
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
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Auth','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' validating Auth arg '''
            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                #print(self.util.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))
            #fi

            ''' Preparing document:    '''
            myMemberId = myMainArgData['Auth']['EntityId']
            myCriteria = {'_id':myMemberId}

            # get Member Details
            myMemberDetails = self.getAMemberDetail({'ResponseMode':self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            # get All Connections (Member)
            myConnectionArgData = {'ConnectionType':'Member','ResponseMode': self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']}
            myMemberConnections = self.getAMemberConnections(myResponseArgData)
            # Get All Group this member participates to (owner of a group is also member)
           
            # we need to combine all results in one result sets
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
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
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            ''' validating arguments '''
            myArgKey = ['Auth']

            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
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
            myMainArgData['Auth'] = self.sec._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.global._Global__member,'EntityId':myMainArgData['_id']})
            '''

            ''' validating auth args '''
            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                #print(self.util.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))
            #fi

            #we need to find the block which is beieng changed in Member collection dcoument
            if 'Main' in myMainArgData and myMainArgData['Main']:
                self.myModuleLogger.debug('Got Main[{main}] information which changed'.format(main=myMainArgData['Main']))
                myUpdateResult = self.member._Member__updateMemberMain(myMainArgData)
                #print('MainUpdateResult',myUpdateResult,myMainArgData)
            #fi
            if 'Address' in myMainArgData and myMainArgData['Address']:
                #print('In Address')
                self.myModuleLogger.debug('Got Address[{address}] information which changed'.format(address=myMainArgData['Address']))
                myUpdateResult = self.member._Member__updateMemberAddress(myMainArgData)

            #fi
            if 'Contact' in myMainArgData and myMainArgData['Contact']:
                #print('In Contact')
                self.myModuleLogger.debug('Got Contact[{contact}] information which changed'.format(contact=myMainArgData['Contact']))
                myUpdateResult = self.member._Member__updateMemberContact(myMainArgData)

            #fi

            # rebuilding tag and recording this activity 
            self.myModuleLogger.info('Updating Tag for member [{member}]' .format(member=myMainArgData['Auth']['EntityId']))
            myTagUpdateResult = self.member._Member__updateMemberTag({'_id':myMainArgData['Auth']['EntityId']})

            #record this activity
            self.activity._Activity__logActivity(self.util.buildActivityArg(
                myMainArgData['Auth']['EntityId'],self.globaL._Global__member,self.globaL._Global__External,'Member [{member}] detail [{change}] changed'.
                    format(member=myMainArgData['Auth']['EntityId'], change=myMainArgData), myMainArgData['Auth']))

            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)

            ''' get all the information of a member '''
            myMemberDetailResults = self.getAMemberDetail({'ResponseMode':self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            #print(myMemberDetailResults)

            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberDetailResults)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

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
            myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globaL._Global__False
            myActivityDetails = ''
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            # validating arguments
            myArgKey = ['UpdateConnections','Auth','ResponseMode']
            myConnectionArgs = myMainArgData['UpdateConnections']

            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # if connection is passed as dict, converting to list
            if not(self.util.isList(myConnectionArgs)):
                myConnectionArgs = [myConnectionArgs]

            # we might get more than one connection request
            for myConnections in myConnectionArgs:
                myArgKey = ['Id','Type','Action']
                if myConnections['Action'] not in self.globaL._Global__Connection_Action:
                    raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Action must be one of the value in[{action}]'.format(action=self.globaL._Global__Connection_Action))
                #fi
                myArgValidationResults = self.util.valRequiredArg(myConnections, myArgKey)
                myArgValidation = self.util.extractValFromTuple(myArgValidationResults,0)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                        format(arg=myConnections.keys(), key=self.util.extractValFromTuple(myArgValidationResults,1)))
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
            myMainArgData['Auth'] = self.sec._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.global._Global__member,'EntityId':myMainArgData['_id']})
            '''

            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))
            #fi

            # lets perform action
            for myConnections in myConnectionArgs:
                myConnectionArgData = {'_id':myMainArgData['Auth']['EntityId'],'Type':self.globaL._Global__member,
                                    'ConnectionId': myConnections['Id'], 'ConnectionType': myConnections['Type']}
                # we need to populate favorite and block dict as well
                #print('processing connection request [{request}]'.format(request=myConnectionArgData))
                if myConnections['Action'] == self.globaL._Global__Connection_Action_Invite:
                    myConnectionResults = self.conn._Connections__AddAConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] added [{conn}] as a connection '.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif myConnections['Action'] == self.globaL._Global__Connection_Action_Accepted:
                    myConnectionResults = self.conn._Connections__acceptInvitation(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] accepted connection request from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif myConnections['Action'] == self.globaL._Global__Connection_Action_Rejected:
                    myConnectionResults = self.conn._Connections__rejectInvitation(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] rejected connection request from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globaL._Global__Connection_Action_Removed:
                    myConnectionResults = self.conn._Connections__removeConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] removed connection from [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globaL._Global__Connection_Action_Favorite:
                    #print('Fav',myConnections)
                    myConnectionArgData.update({'Favorite':myConnections['Favorite']}) 
                    myConnectionResults = self.conn._Connections__favoriteConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] updated favorite attribute of connection [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                elif  myConnections['Action'] == self.globaL._Global__Connection_Action_Block:
                    myConnectionArgData.update({'Blocked':myConnections['Blocked']})
                    myConnectionResults = self.conn._Connections__blockConnection(myConnectionArgData)
                    myActivityDetails = 'Member [{member}] updated block attribute of connection [{conn}]'.\
                        format(member=myMainArgData['Auth']['EntityId'], conn=myConnectionArgData['ConnectionType'] + ' ' + \
                            str(myConnectionArgData['ConnectionId']))
                #fi
                #print('in BPS result',myConnectionResults)
                if myConnectionResults.get('Status') == self.globaL._Global__Success:
                    ''' recording activity '''
                    myActivityDetails = 'Success,' + myActivityDetails
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                else:
                    myActivityDetails = 'UnSuccess: ' + myActivityDetails
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess,myConnectionResults.get('Message'))
                    #print('reqStatus',myRequestStatus)
                #fi
                self.myModuleLogger.info(myActivityDetails)
            # end for loop                

            ''' preparing response; get all connection member details for this member '''
            myResponseArgData = {'ConnectionType':'Member','ResponseMode': self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']}
            myResponseData = self.getAMemberConnections(myResponseArgData)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',myResponseData)

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse
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
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            myArgKey = ['Auth','ResponseMode']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if myMainArgData['ResponseMode']  == self.globaL._Global__InternalRequest:
                if not (self.sec._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
                #fi
            else:
                if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
                #fi
            #fi
            ''' preparing value needed to find member details'''
            myCriteria = {'_id':myMainArgData['Auth']['EntityId']}
            myFindOne = self.globaL._Global__True
            myProjection={"Main":1,"Address":1,"Contact":1,"Tag":1}

            self.myModuleLogger.info('Finding member [{member}] details'.format (member=myMainArgData['Auth']['EntityId']))
            myMemberData = self.mongo.findDocument(self.globaL._Global__memberColl, myCriteria,myProjection,myFindOne)
            
            # get the connection information
            myConnectionArgs = {'MemberId': myMainArgData['Auth']['EntityId'], 'ConnectionType':self.globaL._Global__member,\
                                 'ResponseMode':self.globaL._Global__InternalRequest}
            myMemberConnections = self.member._Member__getAMemberConnections(myConnectionArgs)
            # will update connection information to current result sets, there are only one document in 'Data'
            if 'Data' in myMemberConnections and 'Connections' in myMemberConnections['Data']:
                myMemberData['Data'][0].update({'Connections':myMemberConnections['Data']['Connections']})
            else:
                myMemberData['Data'][0].update({'Connections':[]})                
            #fi

            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)

            ''' Building response '''           
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',myMemberData)
            
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

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
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['ConnectionType','Auth','ResponseMode']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if myMainArgData['ResponseMode'] == self.globaL._Global__InternalRequest:
                if not (self.sec._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
                #fi
            else:
                if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                    raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                        format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
                #fi
            #fi             

            ''' preparing value needed to find member connections'''
            self.myModuleLogger.info('Finding a members connection [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''

            myMemberId = myMainArgData['Auth']['EntityId']
            myConnectionType = myMainArgData['ConnectionType']
            
            ''' 
            commenting below, this has been moved to Memebr
            build aggregate pipeline 
            myAggregatePipeLine = self.member._Member__buildGetAllConnPipeline({'MemberId':myMemberId,'ConnectionType':myConnectionType})
            self.myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            #myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            #myConnectionRawData = self.mongo.ExecCommand(self.memberColl, myAggregateDict)
            
            myAggregateDict = {"aggregate":self.global._Global__memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myConnectionRawData = self.mongo.ExecCommand(myAggregateDict)

            if self.util.isAllArgumentsValid(myConnectionRawData):
                myMemberConnection = {"Data":self.member._Member__buildMyConnection({'ConnectionType':self.global._Global__member,'ConnectionRawData':myConnectionRawData})}
            else:
                myMemberConnection = {}
            #fi
            '''
            myMemberConnectionsArg = {'MemberId':myMemberId,'ConnectionType':myConnectionType,\
                                        'ResponseMode':self.globaL._Global__InternalRequest}
            myMemberConnection = self.member._Member__getAMemberConnections(myMemberConnectionsArg)

            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnection)

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def SearchMember(self,argRequestDict):
        ''' 
            Description:    Search memebr based of argument passed
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
                            {'SearchCriteria','Page',Auth','ResponseMode'}
            usage:          <SearchMember(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))            
            myArgKey = ['SearchCriteria','Page','Auth','ResponseMode']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
            #fi 
            
            # preparing documemt for search
            mySearchCriteria = myMainArgData['SearchCriteria'].upper()
            #print('Search',mySearchCriteria)
            myTextSearhDocArgDict = \
                {'Collection':'Member', 'Search':"\"mySearchCriteria\"",'Projection':{'_id':1,'Main':1}, 'Limit':10, 'Skip':"0"}
            mySearchResults = self.mongo.SearchText(myTextSearhDocArgDict)
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)

            # building response
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', mySearchResults)

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse
