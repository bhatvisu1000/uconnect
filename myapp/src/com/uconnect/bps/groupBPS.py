import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.activity import Activity
from com.uconnect.core.group import Group
from com.uconnect.core.security import Security

myLogger = logging.getLogger('uConnect')

@Singleton
class GroupBPS(object):
    def __init__(self):
        ''' 
            Description:    Initialization internal method, called internally
            usage:          Called internally
            Return:         N/A
        '''        
        self.util = Utility()
        self.mongo = MongoDB()
        self.globaL = Global()
        self.activity = Activity()
        self.group = Group() 
        self.sec = Security() 

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
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


    def isAMemberGroupNameInUse(self, argRequestDict):
        ''' check if the group name is already in use for this member'''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            isGroupNameInUse = self.globaL._Global__False 

            ''' validating arguments '''
            myArgKey = ['Main','Auth','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myArgKey = ['GroupName']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.util.whoAmI()))
            #fi
            myGroupValidationData = {'GroupName':myMainArgData['Main']['GroupName'],'OwnerMemberId':myMainArgData['Auth']['EntityId']}
            isGroupNameInUse = self.group._Group__isAMemberGroupInUse(myGroupValidationData)
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)                
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',isGroupNameInUse)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myResponse
    # end 

    def createAMemberGroup(self,argRequestDict):
        ''' 
            Description:    Create a Member's group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MainArg': {'GroupName':'<GroupName>','MeberId':'<owner of group>'}}
            usage:          <createAMemGroup(<argRequestDict>)
            Return:         Json object
            Collection:     Group: Insert a record in Group collection
        '''
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgKey = ['Main','Auth','ResponseMode','Participants']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            
            myArgKey = ['GroupName']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData['Main'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.util.whoAmI()))
            #fi

            # create Member Group
            myGroupData = {'Main':myMainArgData['Main'],'ResponseMode':self.globaL._Global__InternalRequest}
            myGroupData['Main'].update({'OwnerMemberId':myMainArgData['Auth']['EntityId']})
            myGroupDbResult = self.group._Group__createAMemGroup(myGroupData)

            if myGroupDbResult['Status'] == self.globaL._Global__Success:
                myGroupId = myGroupDbResult['Data']['_id']
                
                self.myModuleLogger.info('New group [{group}] craeted for member [{member}]'\
                    .format(group=myGroupData['Main']['GroupName'] + ':' + str(myGroupId), member=myGroupData['Main']['OwnerMemberId']))
                # add allparticipants to this group
                myAllParticipantLists = myMainArgData['Participants']
                if not(self.util.isList(myAllParticipantLists)):
                    myAllParticipantLists = [myAllParticipantLists]
                #fi
                
                myParticipantData = {'_id':myGroupId,'ResponseMode':self.globaL._Global__InternalRequest,\
                                        'Participants':myAllParticipantLists}
                self.group._Group__updateGroupParticipants(myParticipantData)
                # Building response data
                
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                myGroupArg = {'_id':myGroupId,'ResponseMode':self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']}
                myGroupFindResult = self.getAGroupDetail(myGroupArg)
                if myGroupFindResult['Status'] == self.globaL._Global__UnSuccess:
                    myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myGroupFindResult,'Error')
                else:
                    myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find', myGroupFindResult)
                #fi
            else:
                #myRequestStatus = self.util.getRequestStatus(self.global._Global__UnSuccess,myGroupDbResult['Message'] )                
                myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myGroupDbResult,'Error')
            #fi
            return myResponse
        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            #print('In Error',myRequestStatus)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myResponse
    #end 


    def getAllGroupOfAMember(self,argRequestDict):
        ''' 
            Description:    Find all group member participates and all participating member
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
            usage:          <getGroupDetails4AMember(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgKey = ['Auth','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.util.whoAmI()))
            #fi
            myMemberId = myMainArgData['Auth']['EntityId']
            self.myModuleLogger.info('Finding all group for this member [{member}]'.format(member=myMemberId))

            myCriteria = {'Participants.MemberId':myMemberId}
            myProjection={'_id':1, 'Main':1}
            myFindOne = True

            myGroupData = self.mongo.findDocument(self.globaL._Global__groupColl, myCriteria,myProjection,myFindOne)
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            ''' build response data '''            
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find', myGroupData)

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def getAGroupDetail(self,argRequestDict):
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

        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            
            ''' validating arguments '''
            myArgKey = ['_id','ResponseMode','Auth']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
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

            ''' preparing value needed to find member connections'''
            self.myModuleLogger.info('Finding all member participants for a group [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''

            myGroupId = myMainArgData['_id']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.group._Group__buildGetAllGroupMemberPipeline({'GroupId':myGroupId})['Data']
            self.myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            myAggregateDict = {"aggregate":self.globaL._Global__groupColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myAllParticipantsRawData = self.mongo.ExecCommand(myAggregateDict)['result']
            #print('Participants',myAllParticipantsRawData)
            myAllPArticipants = self.group._Group__formatParticipantsData(myAllParticipantsRawData)
            
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myAllPArticipants)

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def UpdateGroupDetails(self,argRequestDict):
        ''' 
            Description:    Update group participants (Add/Remove [participants])
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Main':{'GroupName':''},'Participants':[{'MemberId':'','Action':''}]}
            usage:          <UpdateGroupDetails(<argReqJsonDict>)
            Return:         Status of the operation
        '''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            
            ''' validating arguments '''
            myArgKey = ['_id','ResponseMode','Auth']
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if not(self.util.isAnyKeyInDict(['Main','Participants'], myMainArgData)):  
                raise com.uconnect.core.error.MissingArgumentValues('Either Main/Participants key is required ')
            #fi

            # validating if this member is associated with this group
            if not(self.group._Group__isValidGroupForMember({'GroupId':myMainArgData['_id'],'MemberId':myMainArgData['Auth']['EntityId']})):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Member {member} is not associated with group {group}'.\
                     format(member=myMainArgData['Auth']['EntityId'], group=myMainArgData['_id']))
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globaL._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.sec._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.util.whoAmI()))
            #fi             

            ''' Performing update '''
            # see if an update is requested in Main
            if 'Main' in myMainArgData and myMainArgData['Main']:
                myGroupName = myMainArgData['Main']['GroupName']
                myGroupUpdateStatus = self.group._Group__updateGroupMain(\
                    {'_id':myMainArgData['_id'], 'GroupName':myGroupName})
            #
            if  'Participants' in myMainArgData and myMainArgData['Participants']: 
                myAllPArticipants = myMainArgData['Participants']
                myGroupUpdateStatus = self.group._Group__updateGroupParticipants(\
                    {'_id':myMainArgData['_id'],'Participants':myAllPArticipants})
            #
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            myGroupDetail = self.getAGroupDetail(\
                {'_id':myMainArgData['_id'],'ResponseMode':self.globaL._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus, 'Find',myGroupDetail)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myRequestStatus
# end
