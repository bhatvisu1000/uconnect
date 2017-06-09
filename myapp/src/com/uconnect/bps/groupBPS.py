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
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.globalInstance = Global.Instance()
        self.activityInstance = Activity.Instance()
        self.groupInstance = Group.Instance() 
        self.securityInstance = Security.Instance() 

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
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            isGroupNameInUse = self.globalInstance._Global__False 

            ''' validating arguments '''
            myArgKey = ['Main','Auth','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myArgKey = ['GroupName']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi
            myGroupValidationData = {'GroupName':myMainArgData['Main']['GroupName'],'OwnerMemberId':myMainArgData['Auth']['EntityId']}
            isGroupNameInUse = self.groupInstance._Group__isAMemberGroupInUse(myGroupValidationData)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)                
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',isGroupNameInUse)
            return myResponse

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
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
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' validating arguments '''
            myArgKey = ['Main','Auth','ResponseMode','Participants']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            
            myArgKey = ['GroupName']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            # create Member Group
            myGroupData = {'Main':myMainArgData['Main'],'ResponseMode':self.globalInstance._Global__InternalRequest}
            myGroupData['Main'].update({'OwnerMemberId':myMainArgData['Auth']['EntityId']})
            myGroupDbResult = self.groupInstance._Group__createAMemGroup(myGroupData)

            if myGroupDbResult['Status'] == self.globalInstance._Global__Success:
                myGroupId = myGroupDbResult['Data']['_id']
                
                self.myModuleLogger.info('New group [{group}] craeted for member [{member}]'\
                    .format(group=myGroupData['Main']['GroupName'] + ':' + str(myGroupId), member=myGroupData['Main']['OwnerMemberId']))
                # add allparticipants to this group
                myAllParticipantLists = myMainArgData['Participants']
                if not(self.utilityInstance.isList(myAllParticipantLists)):
                    myAllParticipantLists = [myAllParticipantLists]
                #fi
                
                myParticipantData = {'_id':myGroupId,'ResponseMode':self.globalInstance._Global__InternalRequest,\
                                        'Participants':myAllParticipantLists}
                self.groupInstance._Group__updateGroupParticipants(myParticipantData)
                # Building response data
                
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                myGroupArg = {'_id':myGroupId,'ResponseMode':self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']}
                myGroupFindResult = self.getAGroupDetail(myGroupArg)
                if myGroupFindResult['Status'] == self.globalInstance._Global__UnSuccess:
                    myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myGroupFindResult,'Error')
                else:
                    myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find', myGroupFindResult)
                #fi
            else:
                #myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myGroupDbResult['Message'] )                
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myGroupDbResult,'Error')
            #fi
            return myResponse
        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            print('In Error',myRequestStatus)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
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
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' validating arguments '''
            myArgKey = ['Auth','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi
            myMemberId = myMainArgData['Auth']['EntityId']
            self.myModuleLogger.info('Finding all group for this member [{member}]'.format(member=myMemberId))

            myCriteria = {'Participants.MemberId':myMemberId}
            myProjection={'_id':1, 'Main':1}
            myFindOne = True

            myGroupData = self.mongoDbInstance.findDocument(self.globalInstance._Global__groupColl, myCriteria,myProjection,myFindOne)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            ''' build response data '''            
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find', myGroupData)

            return myResponse

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
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
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            
            ''' validating arguments '''
            myArgKey = ['_id','ResponseMode','Auth']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
            #fi             

            ''' preparing value needed to find member connections'''
            self.myModuleLogger.info('Finding all member participants for a group [{arg}]'.format(arg=myMainArgData))
            ''' we need threading for following request using threading of python '''

            myGroupId = myMainArgData['_id']
            
            ''' build aggregate pipeline '''
            myAggregatePipeLine = self.groupInstance._Group__buildGetAllGroupMemberPipeline({'GroupId':myGroupId})['Data']
            self.myModuleLogger.debug("Pipeline [{pipeline}] will be used to execute the aggregate function")

            myAggregateDict = {"aggregate":self.globalInstance._Global__groupColl,"pipeline":myAggregatePipeLine,"allowDiskUse":True}
            myAllParticipantsRawData = self.mongoDbInstance.ExecCommand(myAggregateDict)['result']
            print('Participants',myAllParticipantsRawData)
            myAllPArticipants = self.groupInstance._Group__formatParticipantsData(myAllParticipantsRawData)
            
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myAllPArticipants)

            return myResponse

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
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
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            
            ''' validating arguments '''
            myArgKey = ['_id','ResponseMode','Auth']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            if not(self.utilityInstance.isAnyKeyInDict(['Main','Participants'], myMainArgData)):  
                raise com.uconnect.core.error.MissingArgumentValues('Either Main/Participants key is required ')
            #fi

            # validating if this member is associated with this group
            if not(self.groupInstance._Group__isValidGroupForMember({'GroupId':myMainArgData['_id'],'MemberId':myMainArgData['Auth']['EntityId']})):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Member {member} is not associated with group {group}'.\
                     format(member=myMainArgData['Auth']['EntityId'], group=myMainArgData['_id']))
            #fi

            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
            #fi             

            ''' Performing update '''
            # see if an update is requested in Main
            if 'Main' in myMainArgData and myMainArgData['Main']:
                myGroupName = myMainArgData['Main']['GroupName']
                myGroupUpdateStatus = self.groupInstance._Group__updateGroupMain(\
                    {'_id':myMainArgData['_id'], 'GroupName':myGroupName})
            #
            if  'Participants' in myMainArgData and myMainArgData['Participants']: 
                myAllPArticipants = myMainArgData['Participants']
                myGroupUpdateStatus = self.groupInstance._Group__updateGroupParticipants(\
                    {'_id':myMainArgData['_id'],'Participants':myAllPArticipants})
            #
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myGroupDetail = self.getAGroupDetail(\
                {'_id':myMainArgData['_id'],'ResponseMode':self.globalInstance._Global__InternalRequest,'Auth':myMainArgData['Auth']})
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus, 'Find',myGroupDetail)
            return myResponse

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            return myRequestStatus
# end
