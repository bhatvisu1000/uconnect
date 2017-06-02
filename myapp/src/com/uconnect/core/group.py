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
class Group(object):
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
    def __buildInitGroupData(self, argRequestDict):

        #argMainDict,argAddressDict,argContactDict
        try:
            # Preparing document:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['GroupName','MemberId']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myInitGroupData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__member)
            myInitGroupData['GroupName'] = myMainArgData['GroupName']
            myInitGroupData['MemberId'] = myMainArgData['MemberId']
            myGroupId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__groupColl)
            myInitMemberData['_id'] = myMemberId

            ''' build initial history data '''
            myInitGroupData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
            myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitGroupData))

            return myInitGroupData

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
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

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgKey = ['GroupName','Auth','ResponseMode','Participants']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi
            
            myAllParticipantLists = myMainArgData['Participants']
            if not(self.utilityInstance.isList(myAllParticipantLists)):
                myAllParticipantLists = [myAllParticipantLists]
            #fi
            
            # validating participants, need to ensure all member id is valid
            for myParticipant in myAllParticipantLists:
                if not(self.memberInstance._Member__isAValidMember()):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Invalid member [{member}]'.format(member=myParticipant['MemberId']))

            # validating auth argument
            if (myMainArgData['Auth']['EntityType'] != self.globalInstance._Global__member):
                raise com.uconnect.core.error.MissingArgumentValues('Auth Arg validation error; entitytype key must be "Member"')
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            # validating group name
            myGroupNameValArg = {'Main':{'GroupName':myMainArgData['GroupName'], 'MemberId': myMainArgData['MemberId']}}
            if self.isAMemberGroupNameInUse(myGroupNameValArg):
                raise com.uConnect.core.error.DuplicateGroup('Duplicate group Name [{group}]'.\
                    format(group=myMainArgData['GroupName']))
            #fi

            # Preparing document:
            myGroupData = self.__buildInitGroupData(myMainArgData['Main'])
            myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))

            #creating a member group
            myGroupResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global_groupColl, myGroupData)
            myGroupId = myGroupResult['_id']
            myGroupResultStatus = self.utilityInstance.getCreateStatus(myGroupResult)

            # we need to add participants
            if myGroupResultStatus == self.globalInstance._Global__Success:
                for myParticipant in myAllParticipantLists:
                    myParticipantData = {'Participants':{'MemberId':myParticipant['MemberId']}}
                    self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myParticipantData, 'addToSet',False)
                # end for

                # Building response data
                
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                myGroupArg = {'_id':myGroupId,'ResponseMode':self.globalInstance._Global__InternalRequest}
                myGroupDetail = self.getAGroupDetail(myGroupArg)
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find', myGroupDetail)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess)                
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find')
            #fi
            

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except com.uConnect.core.error.DuplicateGroup as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.message)) 
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise
            #fi
    #end 
