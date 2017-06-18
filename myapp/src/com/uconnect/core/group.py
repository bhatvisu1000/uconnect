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

    def __buildGetAllGroupMemberPipeline(self, argRequestDict):
        #argMemberId, argConnectionType
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['GroupId']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)

            myGroupId = myMainArgData['GroupId']

            self.myModuleLogger.debug('Building pipeline for aggregate function, for retrieving group member information')

            myFromCollection = self.globalInstance._Global__memberColl
            myPipeLine =  [ 
                    {"$match"  : {"_id":myGroupId}},
                    {"$unwind" : {"path":"$Participants","preserveNullAndEmptyArrays":True}},                    
                    {"$lookup" :
                        {
                            "from":"Member",
                            "localField":"Participants.MemberId",                  
                            "foreignField":"_id",                  
                            "as":"Participants"
                        }      
                    },
                    {"$project": 
                        {
                            "_id":1,
                            "Main":1,
                            "Participants._id":1,
                            "Participants.Main":1
                        }
                    },
                    {
                        "$sort" :
                            {
                                "Participants.Main.LastName":1
                            }
                    }
                ]
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            myRequestStatus.update({'Data':myPipeLine})
            #print(myRequestStatus)
            return myRequestStatus

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            return myRequestStatus

    #__buildGetAllConnPipeline Ends here

    def __formatParticipantsData(self,argRequestDict):
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            myAllParticipantsData = []
            for myParticipant in myMainArgData:
                # we need to make sure Participants array is not empty
                if len(myParticipant['Participants']) > 0:
                    myAllParticipantsData.append(\
                        {'MemberId':myParticipant['Participants'][0]['_id'],'Main':myParticipant['Participants'][0]['Main']})
                #fi
            myResponse = {'_id':myMainArgData[0]['_id'],'Main':myMainArgData[0]['Main'],'Participants':myAllParticipantsData}
            return myResponse
        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            # we would return error in main
            return {'Main':myRequestStatus}

    def __isValidGroupForMember(self,argRequestDict):
        try:

            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            myArgKey = ['MemberId','GroupId']
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            myCriteria = {'_id':myMainArgData['GroupId'], 'Main.OwnerMemberId':myMainArgData['MemberId']}
            myGroupCount = self.mongoDbInstance.findTotDocuments(self.globalInstance._Global__groupColl, myCriteria)
            if myGroupCount == 0:
                return self.globalInstance._Global__False
            else:
                return self.globalInstance._Global__True
            return myResponse
        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            # we would return error in main
            return self.globalInstance._Global__Error

    def __createAMemGroup(self,argRequestDict):
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
            myArgKey = ['Main']
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
            myGroupNameValArg = myMainArgData['Main']
            if self.__isAMemberGroupInUse(myGroupNameValArg):
                raise com.uconnect.core.error.DuplicateGroup('Duplicate group [{group}]'.\
                    format(group=myMainArgData['Main']['GroupName']))
            #fi

            # Preparing document:
            myGroupData = self.__buildInitGroupData(myMainArgData['Main'])
            self.myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))

            #persisting group data
            #print(myGroupData)
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
                #print('Db Status',myDbStatus, myDbStatus)
                if myDbStatus['Status'] == self.globalInstance._Global__Success:
                    #print('Status is Success')
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                    myRequestStatus['Data'] = {'_id':myGroupId}
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

    def __updateGroupMain(self, argRequestDict):
        '''
            Update Group attribute; only Group Name can be changed
        '''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgKey = ['_id','GroupName']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            myCriteria = {'_id':myMainArgData['_id']}
            myGroupData = {'Main.GroupName':myMainArgData['GroupName']}
            myDbResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__groupColl, myCriteria, myGroupData, 'set', False)
            if self.utilityInstance.getUpdateStatus(myDbResult) == self.globalInstance._Global__Success:
                myRequestStatus = self.utilityInstance.getUpdateStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getUpdateStatus(self.globalInstance._Global__UnSuccess,\
                    ' DB result [{result}]'.format(result=myDbResult))
            #fi
            return myRequestStatus

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            return myRequestStatus

    def __updateGroupParticipants(self, argRequestDict):
        ''' 
            Description:    updating Group participants (Add/Remove)
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
            myArgKey = ['_id','Participants']

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
            myCriteria = {'_id':myMainArgData['_id']}
            # need to get the group owner information to ensure group owner is not removed from participants

            myGrouResult = self.mongoDbInstance.findDocument(\
                self.globalInstance._Global__groupColl, myCriteria, {'Main.OwnerMemberId':1,'_id':0}, False)
            
            myGroupOwnerId = self.utilityInstance.extr1stDocFromResultSets(myGrouResult)['Main']['OwnerMemberId']

            #print(myAllParticipantsList)

            for myParticipant in myAllParticipantsList:
                ''' validating Participant arguments '''
                myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myParticipant, myArgKey)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
                #fi
                myParticipantsData = {'Participants':{'MemberId':myParticipant['MemberId']}}
                myMemberValidationArg = {'_id':myParticipant['MemberId'], 'ResponseMode': self.globalInstance._Global__InternalRequest}
                myExecuteOperation = False

                if (myParticipant['Action'] == 'Add')  and (self.memberInstance._Member__isAValidMember(myMemberValidationArg)):
                    myOperation = 'addToSet'
                    myIncrementValue = 1
                    myExecuteOperation = True
                elif (myParticipant['Action'] == 'Remove') and (not(myParticipant['MemberId'] == myGroupOwnerId)):
                    myOperation = 'pull'
                    myIncrementValue = -1
                    myExecuteOperation = True
                #fi
                if myExecuteOperation:
                    myDbResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__groupColl, myCriteria, myParticipantsData, myOperation, False)
                    if self.utilityInstance.getUpdateStatus(myDbResult) == self.globalInstance._Global__Success:
                        self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__groupColl, myCriteria, {'Main.TotalParticipants':myIncrementValue}, 'inc', False)
                    #
                #                    
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
            myArgValidation, myMissingKeys, myArgValMessage = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myCriteria = {'Main.GroupName':myMainArgData['GroupName'],'Main.OwnerMemberId':myMainArgData['OwnerMemberId']}

            if self.mongoDbInstance.findTotDocuments(self.globalInstance._Global__groupColl, myCriteria) > 0:
                #print('group found',self.globalInstance._Global__groupColl,myCriteria)
                return self.globalInstance._Global__True 
            else:
                return self.globalInstance._Global__False 
            #fi                

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise
            #return self.globalInstance._Global__Error
    # end 
