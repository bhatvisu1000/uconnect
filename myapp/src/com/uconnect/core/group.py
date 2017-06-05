import datetime,json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.member import Member
from com.uconnect.core.activity import Activity

myLogger = logging.getLogger('uConnect')

@Singleton
class Group(object):
    def __init__(self):
        ''' 
            Description:    Initialization internal method, called internally
            usage:          Called internally
            Return:         N/A
        '''        
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.globalInstance = Global.Instance()
        self.memberInstance = Member.Instance()
        self.activityInstance = Activity.Instance()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def __buildInitGroupData(self, argRequestDict):

        #argMainDict,argAddressDict,argContactDict
        try:
            # Preparing document:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            

            ''' validating arguments '''
            myArgKey = ['GroupName','OwnerMemberId']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myInitGroupData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__group)
            myInitGroupData['Main']['GroupName'] = myMainArgData['GroupName']
            myInitGroupData['Main']['OwnerMemberId'] = myMainArgData['OwnerMemberId']
            myGroupId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__groupColl)
            myInitGroupData['_id'] = myGroupId

            ''' build initial history data '''
            myInitGroupData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
            self.myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitGroupData))

            return myInitGroupData

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise

    #__buildInitGroupData Ends here
    def __createAGroup(self,argRequestDict):
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
            myArgKey = ['Main','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myArgKey = ['GroupName','OwnerMemberId']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            
            # validating memberid (owner of this group)
            myMemberValArg = {'_id':myMainArgData['Main']['OwnerMemberId'], 'ResponseMode':self.globalInstance._Global__InternalRequest}
            self.myModuleLogger.debug(myMemberValArg)
            if not(self.memberInstance._Member__isAValidMember(myMemberValArg)):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Invalid member [{member}]'.format(member=myParticipant['_id']))

            # validating group name, if its already in use by this member
            myGroupNameValArg = {myMainArgData['Main']}
            if self.__isAMemberGroupInUse(myGroupNameValArg):
                raise com.uconnect.core.error.DuplicateGroup('Duplicate group Name [{group}]'.\
                    format(group=myMainArgData['Main']['GroupName']))
            #fi

            # Preparing document:
            myGroupData = self.__buildInitGroupData(myMainArgData['Main'])
            self.myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))

            #persisting group data
            print(myGroupData)
            myDbResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__groupColl, myGroupData)
            myGroupId = myDbResult['_id']
            myGroupResultStatus = self.utilityInstance.getCreateStatus(myDbResult)
            self.myModuleLogger.debug('Group id [{id}] created, status[{status}] '.format(id=myGroupId, status = myGroupResultStatus))

            # we need to add owner of this group as a 1st participant
            if myGroupResultStatus == self.globalInstance._Global__Success:
                myParticipantArgData = \
                    {'_id': myGroupId, 'ResponseMode': self.globalInstance._Global__InternalRequest,\
                     'Participants':[{'MemberId': myMainArgData['Main']['OwnerMemberId'], 'Action': 'Add'}]}
                myDbStatus = self.__updateGroupParticipants(myParticipantArgData)
                print('Db Status',myDbStatus, myDbStatus)
                if myDbStatus['Status'] == self.globalInstance._Global__Success:
                    print('Status is Success')
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                else:
                    # removing newly created group
                    self.mongoDbInstance.DeleteDoc(self.globalInstance._Global__groupColl,{'_id':myGroupId}, False)
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myDbStatus.get('Message'))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess)
            #fi
            
            return myRequestStatus
        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            return myRequestStatus
    #end 

    def __updateGroupParticipants(self, argRequestDict):
        ''' 
            Description:    Adding a participant to group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'_id':'','Participants':['MemberId']}}
            usage:          <createAMemGroup(<argRequestDict>)
            Return:         Json object
            Collection:     Group: add a participant to group
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
            myArgKey = ['_id','ResponseMode','Participants']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # Participants validation and adding to group
            if self.utilityInstance.isList(myMainArgData['Participants']):
                myAllParticipantsList = myMainArgData['Participants']
            else:
                myAllParticipantsList = [myMainArgData['Participants']]
            #fi

            # adding participant to group
            myArgKey = ['MemberId','Action']
            myGroupCriteria = {'_id':myMainArgData['_id']}
            print(myAllParticipantsList)
            for myParticipant in myAllParticipantsList:
                ''' validating Participant arguments '''
                myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myParticipant, myArgKey)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
                #fi
                if myParticipant['Action'] == 'Add':
                    myOperation = 'addToSet'
                elif myParticipant['Action'] == 'Remove':
                    myOperation = 'pull'
                #fi
                myMemberValidationArg = {'_id':myParticipant['MemberId'], 'ResponseMode': self.globalInstance._Global__InternalRequest}
                if self.memberInstance._Member__isAValidMember(myMemberValidationArg):
                    myParticipantsData = {'Participants':{'MemberId':myParticipant['MemberId']}}
                    self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__groupColl, myGroupCriteria, myParticipantsData, myOperation, False)
                    self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__groupColl, myGroupCriteria, {'Main.TotalParticipants':1}, 'inc', False)
                #fi
            #end for

            #building response
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            return myRequestStatus            
        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            return myRequestStatus
    #end 

    def __isAMemberGroupInUse(self, argRequestDict):
        ''' check if the group name is already in use for this member'''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            isGroupNameInUse = self.globalInstance._Global__False 

            # validating arguments
            myArgKey = ['GroupName','OwnerMemberId']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myCriteria = {'Main.GroupName':myMainArgData['Main']['GroupName'],'Main.OwnerMemberId':myMainArgData['Main']['OwnerMemberId']}

            if self.mongoDbInstance.findTotDocuments(self.globalInstance._Global__groupColl, myCriteria) > 0:
                print('group found',self.globalInstance._Global__groupColl,myCriteria)
                return self.globalInstance._Global__True 
                #myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__True,'GroupName [{group}] is not in use'.format(group=str(myMainArgData['Main']['GroupName'])))
            else:
                return self.globalInstance._Global__False 
                #myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__False)
            #fi                

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise
            #return self.globalInstance._Global__Error
    # end 
