import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security
from com.uconnect.core.member import Member
from com.uconnect.core.activity import Activity

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

        self.myClass = self.__class__.__name__

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

    def __createAMember(self,argRequestDict):
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
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        try:
            ## we need to check who called this function, must be from register
            #print(self.utilityInstance.whoAmi())
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Main','Address','Contact']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=myMainArgData))

            ''' Preparing value to create a new member build initial data '''
            myMemberData = self.memberInstance._Member__buildInitMembderData({'Main':myMainArgData['Main'],'Address':myMainArgData['Address'],'Contact':myMainArgData['Contact']})
            myMemberId = myMemberData['_id'] 

            ''' Creating a member '''
            myModuleLogger.info('Creating new member, data [{doc}]'.format(doc=myMemberData))
            myMemberResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__memberColl, myMemberData)
            myModuleLogger.info('Member [{id}] created, result[{result}]'.format(id=myMemberId, result=myMemberResult))

            ''' Building response data, we can not retrieve member information because we dont have Auth ket yet, will return member id created'''

            '''
            myRequestDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myMemberId}})
            myRequestDict = self.getAMemberDetail(myResponseDataDict)
            myResponse = self.utilityInstance.buildResponseData(self.globalInstance._Global__InternalRequest,myMemberResult,'Insert',myResponseData)
            '''
            myResponse = myMemberResult['_id']

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            raise

    def getAllInformation4Member(self,argRequestDict):
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
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Main','Auth']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=myMainArgData))
            #fi

            ''' Preparing document:    '''
            myMemberId = myMainArgData['MemberId']
            myCriteria = {'_id':myMemberId}
            # remove emty key from key argument
            myMainData = self.utilityInstance.convList2Dict(myMainArgData['Main'])

            myModuleLogger.info('Updating Member [{member}] Main[{address}]' .format(
                member=myMemberId, Main=myMainData))

            ''' Executing document update '''

            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myMainData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myMainData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myAddressData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myContactData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')
           
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            raise error

    def updateMemberSettings(self,argRequestDict):
        pass    

    def AddANewMemberConnection(self, argRequestDict):
        ''' 
            Description:    Linke a member 2 existing member
                            Requestor --> MemberId (member made request)
                            Invitee   --> ConnectMemberId (member to whom request was made)
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MainArg': {'MemberId':'','ConnectMemberId':'','Auth':'','ResponseMode'}}
            usage:          <AddANewMemberConnection(<argRequestDict>)
            Return:         Json object

        '''
        try:

            ''' we need to find a way to enforce that these methods cant be called directly, must be called from BPS process '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                #print(self.utilityInstance.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))

            ''' building connection '''
            myConnectionResults = self.memberInstance._Member__AddMember2MemberConnection(myMainArgData)

            ''' check if building connection was successful; get all the connection for this memner, in future Connection type ned to be changed to ALL ???'''
            if myConnectionResults.get('Status') == self.globalInstance._Global__Success:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Can not add requested connection')
            #fi

            ''' recording activity '''
            self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(
                myMainArgData['MemberId'],self.globalInstance._Global__member,self.globalInstance._Global__External,'Member [{member}] added a connection with [{cmember}], awaiting acceptance '.
                    format(member=myMainArgData['MemberId'], cmember=myMainArgData['ConnectMemberId']), myMainArgData['Auth']))

            # will return all the existing connection any way
            myResponseArgData = {'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
            myMemberConnections = self.getAMemberConnections(myResponseArgData)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnections)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            #raise error
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, error.message)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            #raise error
            return myResponse

    def ExecConnectionAction(self, argRequestDict):
        ''' 
            Description:    ExecConnectionAction (Only Invitee can accept the connection)
                            Requestor --> MemberId (Invitee)
                            Invitee   --> ConnectMemberId (Requestor, member who requeste connection initially)
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MainArg': {'MemberId':'','ConnectMemberId':'','Auth':'','ResponseMode'}}
            usage:          <ExecConnectionAction(<argReqJsonDict>)
            Return:         Json object

        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Action','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myActivityDetails = ''

            ''' validating arguments '''
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))
            #fi            
            if myMainArgData['Action'] not in self.globalInstance._Global__Connection_Action:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Action must be one of the value in[{ation}]'.format(action=self.globalInstance._Global__ConnectionAction))
            #fi

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))

            if myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Accepted:
                myConnectionResults = self.memberInstance._Member__acceptInvitation(myMainArgData)
                myActivityDetails = 'Member [{member}] accepted [{cmember}] connection request '.format(member=myMainArgData.MemberId, cmember=myMainArgData['ConnectMemberId'])
            elif myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Rejected:
                myConnectionResults = self.memberInstance._Member__rejectInvitation(myMainArgData)
                myActivityDetails = 'Member [{member}] rejected [{cmember}] connection request '.format(member=myMainArgData.MemberId, cmember=myMainArgData['ConnectMemberId'])
            elif  myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Removed:
                myConnectionResults = self.memberInstance._Member__removeConnection(myMainArgData)
                myActivityDetails = 'Member [{member}] removed [{cmember}] connection '.format(member=myMainArgData.MemberId, cmember=myMainArgData['ConnectMemberId'])
            #fi                

            ''' check if connection action was successful; get all the connection for this memner, 
            in future Connection type need to be changed to ALL ???'''

            if myConnectionResults.get('Status') == self.globalInstance._Global__Success:
                myResponseArgData = {'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
                myResponseData = self.getAMemberConnections(myResponseArgData)
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myResponseData,'Find')

                ''' recording activity '''
                self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(
                    myMainArgData['MemberId'],self.globalInstance._Global__member,self.globalInstance._Global__External,myActivityDetails, myMainArgData['Auth']))
            else:
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myConnectionResults,'Error')
            #fi
            return myResponse
            
            #myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myConnectionResults,'Update')

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            raise error
    # ends ExecConnectionAction

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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}]'.format(arg = argRequestDict))

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
            myMarkFavoriteStatus =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myFavoriteData, 'set',False)

            ''' build response data '''
            myResponseRequest = self.utilityInstance.builInternalRequestDict({'Data':{'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member'}})
            myResponseData = self.getAMemberConnections(myResponseRequest)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'], myMarkFavoriteStatus,'Update',myResponseData)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myFavoriteData, 'pull',False)
            #myUpdateStatus = self.utilityInstance.getUpdateStatus(myResult)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myBlockedData, 'set',False)
            #myUpdateStatus = self.utilityInstance.getUpdateStatus(myResult)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

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

            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myBlockedData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            raise error

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
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myArgKey = ['Auth','ResponseMode']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            #myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
            #    {'Auth':myMainArgData['Auth']})

            #print(self.myClass,myMainArgData)
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
            myProjection={"Main":1,"Address":1,"Contact":1}
            myModuleLogger.info('Finding member [{member}] details'.format (member=myMainArgData['Auth']['EntityId']))
            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria,myProjection,myFindOne)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

            ''' Building response '''           
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',myMemberData)
            
            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myResponse
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['MemberId','ConnectionType','Auth','ResponseMode']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myAuthArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

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
            myModuleLogger.info('Finding a members connection [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''
            myMemberId = myMainArgData['MemberId']
            myConnectionType = myMainArgData['ConnectionType']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.memberInstance._Member__buildGetAllConnPipeline({'MemberId':myMemberId,'ConnectionType':myConnectionType})
            myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            #myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            #myConnectionRawData = self.mongoDbInstance.ExecCommand(self.memberColl, myAggregateDict)
            
            myAggregateDict = {"aggregate":self.globalInstance._Global__memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myConnectionRawData = self.mongoDbInstance.ExecCommand("member", myAggregateDict)

            if self.utilityInstance.isAllArgumentsValid(myConnectionRawData):
                myMemberConnection = {"Data":self.memberInstance._Member__buildMyConnection({'ConnectionType':self.globalInstance._Global__member,'ConnectionRawData':myConnectionRawData})}
            else:
                myMemberConnection = {}
            #fi

            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnection)

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnection)
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{myerror}]'.format(myerror=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberConnection)
            return myResponse

    def searchMembers(self,argRequestDict):
        pass


