import importlib,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global


#from com.uconnect.bps.scheduleBPS import Schedule

myLogger = logging.getLogger('uConnect')

class Transaction(object):

    def __init__(self):
        pass

    def postDirtyRead(self, argRequestDict):

        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            myArgKey = ['Main','Auth']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myArgKey = ['EntityId','EntityType','Subject','Details']

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData['Main'].keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            myDirtyReadData = 
            myCriteria = {'_id':myMainArgData['Main']['MemberId']}
            myProjection={'_id':1}
            myFindOne = True

            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, myFindOne)
            #print(myCriteria,myProjection,myMemberData)
            ''' we need to make sure if "Data" key is in Result set, it must not be empty and must have "_id" key in it'''
            if 'Data' in myMemberData and myMemberData.get('Data') and '_id' in myMemberData.get('Data')[0]:
                myMemberId = self.utilityInstance.extr1stDocFromResultSets(myMemberData)['_id'] 
            else:
                myMemberId = None
            #fi
            if myMemberId and (myMemberId == myMainArgData['Main']['MemberId']):
                isValidMember = self.globalInstance._Global__True 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                isValidMember = self.globalInstance._Global__False 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'MemberID [{member}] does not exist'.format(member=str(myMainArgData['Main']['MemberId'])))                
            #fi

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',isValidMember)
            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            print('Error',error.errorMsg)
            myModuleLogger.exception('InvalidAuthKey: error [{errmsg}]'.format(errmsg=error.errorMsg))
            isValidMember = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Invalid Auth Key; error [{errmsg}] occurred'.format(errmsg=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            return myResponse
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{errmsg}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Arg validation error; error [{errmsg}] occurred'.format(errmsg=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{errmsg}]'.format(errmsg=error.message))
            isValidMember = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'An error [{errmsg}] occurred'.format(errmsg=error.message))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            return myResponse
