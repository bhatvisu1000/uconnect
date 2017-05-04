import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security
from com.uconnect.utility.memberUtility import MemberUtility
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
        self.dbutilityInstance = DBUtility.Instance()
        self.globalInstance = Global.Instance()
        self.securityInstance = Security.Instance()
        self.memberUtilInstance = MemberUtility.Instance()

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
            myArgKey = ['Main','Address','Contact']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=myMainArgData))

            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            ''' Preparing value to create a new member build initial data '''
            myMemberData = self.memberUtilInstance._MemberUtility__buildInitMembderData(myMainArgData['Main'],myMainArgData['Address'],myMainArgData['Contact'])
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
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

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
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
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
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                print(self.utilityInstance.whoAmI())
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))

            ''' building connection '''
            myConnectionResults = self.memberUtilInstance._MemberUtility__AddMember2MemberConnection(myMainArgData)

            ''' check if building connection was successful; get all the connection for this memner, in future Connection type ned to be changed to ALL ???'''
            if myConnectionResults.get('Status') == self.globalInstance._Global__Success:
                myResponseArgData = {'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
                myResponseData = self.getAMemberConnections(myResponseArgData)
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myResponseData,'Find')
            else:
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myConnectionResults,'Error')
            #fi
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

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
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.utilityInstance.whoAmI()))

            if myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Accepted:
                myConnectionResults = self.memberUtilInstance._MemberUtility__acceptInvitation(myMainArgData)
            elif myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Rejected:
                myConnectionResults = self.memberUtilInstance._MemberUtility__rejectInvitation(myMainArgData)
            elif  myMainArgData['Action'] == self.globalInstance._Global__Connection_Action_Removed:
                myConnectionResults = self.memberUtilInstance._MemberUtility__removeConnection(myMainArgData)
            #fi                

            ''' check if connection action was successful; get all the connection for this memner, 
            in future Connection type need to be changed to ALL ???'''

            if myConnectionResults.get('Status') == self.globalInstance._Global__Success:
                myResponseArgData = {'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member','ResponseMode': self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
                myResponseData = self.getAMemberConnections(myResponseArgData)
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myResponseData,'Find')
            else:
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myConnectionResults,'Error')
            #fi
            return myResponse
            
            #myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myConnectionResults,'Update')

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
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
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
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
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['MemberId','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' preparing value needed to find member details'''
            myCriteria = {'_id':myMainArgData['MemberId']}
            myFindOne = self.globalInstance._Global__True
            myProjection={"Main":1,"Address":1,"Contact":1}
            myModuleLogger.info('Finding member [{member}] details'.format (member=myMainArgData['MemberId']))
            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria,myProjection,myFindOne)

            ''' Building response '''            
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myMemberData,'Find')
            
            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['MemberId','ConnectionType','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' preparing value needed to find member connections'''
            myModuleLogger.info('Finding a members connection [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''
            myMemberId = myMainArgData['MemberId']
            myConnectionType = myMainArgData['ConnectionType']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.memberUtilInstance._MemberUtility__buildGetAllConnPipeline(myMemberId,myConnectionType)
            myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            #myAggregateDict = {"aggregate":self.memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            #myConnectionRawData = self.mongoDbInstance.ExecCommand(self.memberColl, myAggregateDict)
            
            myAggregateDict = {"aggregate":self.globalInstance._Global__memberColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myConnectionRawData = self.mongoDbInstance.ExecCommand("member", myAggregateDict)

            if self.utilityInstance.isAllArgumentsValid(myConnectionRawData):

                myMemberConnection = {"Data":self.memberUtilInstance._MemberUtility__buildMyConnection('Member',myConnectionRawData)}
                myModuleLogger.info("MyMemberConnection Data: {memberConn}".format(memberConn=myMemberConnection))
            else:
                myMemberConnection = {}

            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myMemberConnection,'Find')

            #print ("response",myResponse)
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def searchMembers(self,argRequestDict):
        pass


    '''
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    GGGGGGGGGGGGG       RRRRRRRRRRR          OOOOOOOOOOOO       UU          UU      PPPPPPPPPPPP
    GG                  RR       RR         OO          OO      UU          UU      PP         PP
    GG                  RR       RR         OO          OO      UU          UU      PP         PP
    GG    GGGGGGG       RRRRRRRRRRR         OO          OO      UU          UU      PPPPPPPPPPPP
    GG         GG       RR        RR        OO          OO      UU          UU      PP
    GG         GG       RR         RR       OO          OO      UU          UU      PP
    GGGGGGGGGGGGG       RR          RR       OOOOOOOOOOOO       UUUUUUUUUUUUUU      PP
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    '''

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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myArgKey = ['MemberId','GroupName','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' Preparing document:
            '''
            #myArgRequestData['Request']['MainArg']['Settings']=self.envInstance.defaultsData['Group']['Settings']
            myGroupData = self.envInstance.getTemplateCopy('Group')
            myGroupData['Main']['GroupName'] = myMainArgData['GroupName']
            myGroupData['Main']['MemberId'] = myMainArgData['MemberId']
            myGroupData['_History'] = self.utilityInstance.buildInitHistData() 

            #myGroupId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global_groupColl)
            #myGroupData['_id'] = myGroupId

            myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))
            myGroupResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global_groupColl, myGroupData)
            
            myGroupResultStatus = self.utilityInstance.getCreateStatus(myGroupResult)

            ''' building link between owner of memeber and newly created group '''
            if myGroupResultStatus == self.globalInstance._Global__Success:

                myGroupId = myGroupResult['_id'] 
                myMainArgData.update({'GroupId':myGroupId})
                myLogger.info('Group [{group}] creation is successful, now linking to member[{member}]'.
                    format(group=myGroupId, member=myGroupData['Main']['MemberId']))
                
                myLinkedResult = self.linkAMember2Group(myLinkedData)
                myLinkedResultStatus = self.utilityInstance.getUpdateStatus(myLinkedResult)
                
                if myLinkedResultStatus == self.globalInstance._Global__UnSuccess:
                    ''' Link was unsuccessful, need to clean up the data (delete group collection just got inserted) '''
                    myLogger.info('Linking group [{group}] to member[{member}] is unsuccessful, removing group'.
                        format(group=myGroupId, member=myGroupData['Main']['MemberId']))
                    myDeleteResult = self.mongoDbInstance.DeleteDoc(self.globalInstance._Global_groupColl,{'_id':myGroupId})
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

    def getAllGroup4AMember(self,argRequestDict):
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

        # raise an user defined exception here
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            myArgKey = ['MemberId','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData, key=myArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            myModuleLogger.info('Finding a group details [{arg}]'.format(arg=myMainArgData))

            myCriteria = {'_id':myMainArgData['GroupId']}
            myProjection={'Main':1,'Address':1,'Contact':1}
            myFindOne = True

            myGroupData = self.mongoDbInstance.findDocument(self.globalInstance._Global__groupColl, myCriteria,myProjection,myFindOne)
            
            ''' build response data '''            
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myGroupData,'Find')

            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))
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
            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myLinkedData, 'addToSet',False)
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
                myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global_groupColl, myCriteria, myParticipantdData, 'addToSet',False)

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

