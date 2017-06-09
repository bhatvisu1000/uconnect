import json, os, sys, logging, datetime, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.globals import Global

@Singleton
class Activity(object):
    def __init__(self):
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.globalInstance = Global.Instance()

        self.myClass = self.__class__.__name__

    def __buildInitActivityData(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['EntityId','EntityType','ActivityType','Activity']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myArgKey))

            # deleting the password from Auth
            self.utilityInstance.removeKeyFromDict(myMainArgData, 'Password')

            # retrieve the template 
            myInitActivityLogData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__activityLogColl)
            myModuleLogger.debug('ActivityLog template [{template}]'.format(template=myInitActivityLogData))        

            myInitActivityLogData['EntityId'] = myMainArgData['EntityId']
            myInitActivityLogData['EntityType'] = myMainArgData['EntityType']
            #myInitActivityLogData['ActivityType'] = myMainArgData['ActivityType']
            myInitActivityLogData['Activity'] = myMainArgData['Activity']
            myInitActivityLogData['ActivityDate'] = datetime.datetime.utcnow()            
            myInitActivityLogData['Acknowledged'] = self.globalInstance._Global__False
            if 'Auth' in myMainArgData:
                myInitActivityLogData['Auth'] = myMainArgData['Auth']
                

            #myInitActivityLogData.update({'_History' : self.utilityInstance.buildInitHistData()}) 

            myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitActivityLogData))

            return myInitActivityLogData

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise

    def __logActivity(self, argRequestDict):
        '''
        Desccription: Log all activity for an entity
        Arguments:  [EntityId, EntityType, ActivityDetails, 'Auth']
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            myArgKey = ['EntityId','EntityType','ActivityType','Activity','Auth']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            #print('activitylog',myMainArgData.keys(), myArgKey)
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], expected key[{key}]'.
                    format(arg=myMainArgData.keys(), key=myArgKey))
            #fi

            ''' valdiating authorization '''
            ''' we dont need Auth validation
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi
            '''

            myActivityLogData = self.__buildInitActivityData(myMainArgData)
            myDbResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__activityLogColl, myActivityLogData)

            print('Activity',myDbResult)
            ''' we need to make sure if "Data" key is in Result set, it must not be empty and must have "_id" key in it'''
            if myDbResult[self.globalInstance._Global__StatusKey] == self.globalInstance._Global__TrueStatus:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success,None,myDbResult['_id'])
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'could not create acitvity log')
            #fi
            return myRequestStatus

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            raise

    def acknowledgeActivity(self, argRequesDict):
        pass
    def getActivity(self, argRequesDict):
        pass