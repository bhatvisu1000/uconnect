import json, os, sys, logging, copy, datetime, com.uconnect.utility.ucLogging, com.uconnect.core.error

from bcrypt import hashpw, checkpw, gensalt
from bson.objectid import ObjectId

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.infra import Environment
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.globals import Global
from com.uconnect.core.activity import Activity

myLogger = logging.getLogger('uConnect')

@Singleton
class Security(object):
    def __init__(self):
        self.mongoDbInstance = MongoDB.Instance()
        self.envInstance = Environment.Instance()
        self.utilityInstance = Utility.Instance()
        self.globalInstance = Global.Instance()
        self.activityInstance = Activity.Instance()
        self.myClass = self.__class__.__name__

    def __genHashPassword(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['Password']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            myPasswordText = str(myMainArgData['Password']) 
            hashPassword = hashpw(myPasswordText, gensalt(rounds=8, prefix='2b'))
            #print('hash:' + ':' + myPasswordText + ':' + hashPassword)
            return  hashPassword

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __getLoginInfo(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId']

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            myLoginCriteria = {'_id':myMainArgData['LoginId']}
            myProjection = {}
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__loginColl, myLoginCriteria, myProjection,True)
            #print ('LoginId,Proj,Pass',argLoginId,myLoginCriteria,myProjection,myLoginPassword['Data'][0]['Password'])
        
            if self.utilityInstance.extrStatusFromResultSets(myResults) == self.globalInstance._Global__OkStatus:
                myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
            #fi

            if not(myResultsData == None):
                return myResultsData
            else:
                return None
            #fi

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __buildInitLoginData(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','EntityType','EntityId','Password']

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            # retrieve the template 
            myInitLoginInfoData = self.envInstance.getTemplateCopy(self.globalInstance._Global__loginColl)
            myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitLoginInfoData))        

            myInitLoginInfoData['_id'] = myMainArgData['LoginId']
            myInitLoginInfoData['LoginType'] = myMainArgData['LoginType']
            myInitLoginInfoData['Password'] = myMainArgData['Password']
            myInitLoginInfoData['EntityId'] = myMainArgData['EntityId']
            myInitLoginInfoData['EntityType'] = myMainArgData['EntityType']

            ''' build initial history data '''
            myInitLoginInfoData['_History'] = self.utilityInstance.buildInitHistData() 
            print('initlogininfo',myInitLoginInfoData)
            myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitLoginInfoData))

            return myInitLoginInfoData

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __buildInitAuthData(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityId','AppVer']

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            # retrieve the template 
            myInitAuthData = self.envInstance.getTemplateCopy(self.globalInstance._Global__authColl)
            #print(myInitAuthData, myMainArgData)
            myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitAuthData))        

            myInitAuthData['LoginId'] = myMainArgData['LoginId']
            myInitAuthData['LoginType'] = myMainArgData['LoginType']
            myInitAuthData['DeviceType'] = myMainArgData['DeviceType']
            myInitAuthData['DeviceOs'] = myMainArgData['DeviceOs']
            myInitAuthData['MacAddress'] = myMainArgData['MacAddress']
            myInitAuthData['SessionId'] = myMainArgData['SessionId']
            myInitAuthData['ExpiryDate'] = datetime.datetime.utcnow() + datetime.timedelta(days=self.envInstance.AuthValidDuration)
            myInitAuthData['EntityId'] = myMainArgData['EntityId']
            myInitAuthData['EntityType'] = myMainArgData['EntityType']
            myInitAuthData['AppVer'] = myMainArgData['AppVer']

            ''' build initial history data '''
            myInitAuthData['_History'] = self.utilityInstance.buildInitHistData() 
            myModuleLogger.debug('Data [{arg}] returned'.format(arg=myInitAuthData))

            return myInitAuthData

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __buildInitAuthHistData(self, argRequestDict):

        try:
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['_id','LoginId','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','ExpiryDate','EntityId','AppVer']

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            # retrieve the template 
            myInitAuthHistData = self.envInstance.getTemplateCopy(self.globalInstance._Global__authHistColl)
            myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitAuthHistData))        

            myInitAuthHistData['AuthId'] = myMainArgData['_id']
            myInitAuthHistData['LoginId'] = myMainArgData['LoginId']
            myInitAuthHistData['LoginType'] = myMainArgData['LoginType']
            myInitAuthHistData['DeviceType'] = myMainArgData['DeviceType']
            myInitAuthHistData['DeviceOs'] = myMainArgData['DeviceOs']
            myInitAuthHistData['MacAddress'] = myMainArgData['MacAddress']
            myInitAuthHistData['SessionId'] = myMainArgData['AppVer']
            myInitAuthHistData['ExpiryDate'] = myMainArgData['ExpiryDate']
            myInitAuthHistData['EntityId'] = myMainArgData['EntityId']
            myInitAuthHistData['EntityType'] = myMainArgData['EntityType']
            myInitAuthHistData['AppVer'] = myMainArgData['AppVer']

            ''' build initial history data '''
            myInitAuthHistData['_History'] = self.utilityInstance.buildInitHistData() 
            myModuleLogger.debug('Data [{arg}] returned'.format(arg=myInitAuthHistData))

            return myInitAuthHistData

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __createLogin(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':''}
        '''
        
        try:
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myMainAuthArgData = self.utilityInstance.getCopy(myMainArgData['Auth'])
            print ('login',myMainArgData)
            print ('login',myMainAuthArgData)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['Auth']
            myAuthArgKey =  ['LoginId','Password','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','EntityType','EntityId','AppVer']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' validating Auth arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainAuthArgData, myAuthArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Auth arg validation error; auth arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainAuthArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' This is to ensure if password is encrypted. Do we need this ?'''
            #if not(len(myMainArgData['Password']) == 60 and myMainArgData['Password'].startswith('$2b$')):
            #    myMainArgData['Password'] = self.__genHashPassword({'Password':myMainArgData['Password']})

            ''' Buildkng LoginInfo document'''
            myLoginData = self.__buildInitLoginData(myMainAuthArgData)
            myDbResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__loginColl, myLoginData)

            ''' if login creation is successful, create authentication and return Auth Id'''
            if myDbResult[self.globalInstance._Global__StatusKey] == self.globalInstance._Global__TrueStatus:
                myAuthKey = self.__createAuthentication(myMainAuthArgData)
            else:
                raise com.connect.core.error.DBError('Login creation failed loginifo[{login}]'.format(login=myLoginData))

            return myAuthKey

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.DBError as error:
            myModuleLogger.exception('DBError: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __createAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':'','LoginId':'', 'LoginType':'','DeviceOs':'','SessionId'}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId','LoginType','EntityType','EntityId','DeviceOs','DeviceType','MacAddress','SessionId','AppVer']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            '''Retrieving all Authentication and mark it as expired  '''
            myAllAuthKey = self.__getAuthKey(myMainArgData)
            if myAllAuthKey:
                for myAuthKey in myAllAuthKey:
                    myExpireResult = self.__expireAuthentication({'AuthKey':myAuthKey['_id']})
                    #print(myExpireResult)
                    if myExpireResult['deleted'] == 0:
                        raise com.uconnect.core.error.DBError('Failed to expire auth document AuthKey[{authKey}]'.format(authKey=myAuthKey))
                    #fi
                #end for loop
            #fi
            '''Preparing/Creating new Auth Doc '''
            myModuleLogger.debug('Argument validated, preparing Auth document')
            myAuthDoc = self.__buildInitAuthData(myMainArgData)
            myAuthResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__authColl, myAuthDoc)
            
            ''' recording activity'''
            self.activityInstance._Activity__logActivity(
                {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                 'ActivityType':self.globalInstance._Global__Internal, 
                 'Activity':'Generating new Auth key [{auth}] for [{entity}]'.
                        format(auth=str(myAuthResult['_id']),
                                entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                 'Auth': myMainArgData})

            ''' we need to return string value of object_id '''
            return str(myAuthResult['_id'])

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.DBError as error:
            myModuleLogger.exception('DBError: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise
    
    def __expireAllAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':''}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','EntityId','EntityType']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' Finding all Auth document '''
            myAllAuthKey = self.__getAuthKey(myMainArgData)

            if myAllAuthKey:
                for myAuthKey in myAllAuthKey:
                    myExpireResult = self.__expireAuthentication({'AuthKey':myAuthKey['_id']})
                    #print(myExpireResult)
                    if myExpireResult['deleted'] == 0:
                        raise com.uconnect.core.error.DBError('Failed to expire auth document AuthKey[{authKey}]'.format(authKey=myAuthKey))
                    #fi
                #end for loop
            #fi
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.DBError as error:
            myModuleLogger.exception('DBError: error [{error}]'.format(error=error.errorMsg))
            raise            
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __expireAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':''}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['AuthKey']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' Finding Auth document '''
            myCriteria = {'_id':ObjectId(str(myMainArgData['AuthKey']))}
            myProjection = {}
            myResult = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, myCriteria, {}, True)
            myModuleLogger.debug('Results [{resuts}], after looking for Auth Document'.format (resuts=myResult))
            
            if self.utilityInstance.extrStatusFromResultSets(myResult) == self.globalInstance._Global__OkStatus:

                '''Auth Document found, will archive before expiring this auth document, preparing AuthHistory document '''
                myAuthData = self.utilityInstance.extr1stDocFromResultSets(myResult)
                myAuthHistData = self.__buildInitAuthHistData(myAuthData)   
                myModuleLogger.debug('Auth history document [{authhist}] prepared'.format (authhist=myAuthHistData))

                '''Moving Auth document to History collection, before removing from Auth collection '''
                myAuthHistResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__authHistColl, myAuthHistData)
                #print(myDbResult)
                if myAuthHistResult[self.globalInstance._Global__StatusKey] == self.globalInstance._Global__TrueStatus:
                    myModuleLogger.debug('Auth Key [{AuthKey}]; history document created, deleting Auth document '.format(AuthKey=myMainArgData['AuthKey']))
                    myAuthDelResult = self.mongoDbInstance.DeleteDoc(self.globalInstance._Global__authColl, myCriteria)
                else:
                    myModuleLogger.debug('Auth history document creation failed, aborting operation (expiring Auth document)')
                    raise com.uconnect.core.error.DBError("Error moving Auth data to AuthHistory container AuthKey [{authkey}]".format(authkey=myAuthData['_id']))
            else:
                raise com.uconnect.core.error.DBError("Error while looking for AuthKey [{authkey}]".format(authkey=myAuthData['_id']))                

            return myAuthDelResult

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.DBError as error:
            myModuleLogger.exception('DBError: error [{error}]'.format(error=error.errorMsg))
            raise            
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __getAuthKey(self, argRequestDict):
        '''
            argRequestDict = {'AuthKey':'','LoginId':'', 'LoginType':'','DeviceOs':'','SessionId'}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityId','EntityType','AppVer']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            '''Preparing value '''
            myCriteria = {'LoginId':myMainArgData['LoginId'],
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'EntityId':myMainArgData['EntityId'],
                          'EntityType':myMainArgData['EntityType']}
            myProjection = {'_id':1}

            myAuthResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, myCriteria, myProjection,False)
            myAuthData = self.utilityInstance.extrAllDocFromResultSets(myAuthResults)

            return myAuthData

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __updateAuthEntity(self, argRequestDict):
        '''
            argRequestDict = {'Auth':'','EntityType':'', 'EntityId':''}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['Auth','EntityType','EntityId']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' lets inject EntityType and EnttyId in Auth Dict'''

            myMainArgData['Auth']['EntityType'] = myMainArgData['EntityType']
            myMainArgData['Auth']['EntityId'] = myMainArgData['EntityId']

            return myMainArgData['Auth']

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __isValidAuthentication(self, argRequestDict):
        '''
            argRequestDict = ['ResponseMode','Auth':[]]
               auth:[Key','LoginId','LoginType','DeviceOs','MacAddress','SessionId','AppVer']
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myAuthArgKeys = self.utilityInstance.buildKeysFromTemplate('Auth')
            myAuthArgKeys.append('AuthKey')

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myAuthArgKeys,['ExpiryDate','_id'])
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            '''Preparing value '''
            myCriteria = {'_id':ObjectId(str(myMainArgData['AuthKey'])),
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'SessionId':myMainArgData['SessionId'],
                          'ExpiryDate':{'$gte': datetime.datetime.utcnow()},
                          'AppVer':myMainArgData['AppVer']}
            myProjection = {}
            #print('criteria',myCriteria)
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, myCriteria, myProjection,False)
            myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
            '''if argkey passed and argkey from db is not matching return False '''

            if myResultsData and ('_id' in myResultsData) and (str(myMainArgData['AuthKey']) == str(myResultsData['_id'])):
                return True
            else:
                return False

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            return False
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            return False

    def __isValAuthKeyInternal(self, argRequestDict):
        '''
            argRequestDict = {All authentication information}
        '''

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myAuthArgKey = ['AuthKey','LoginId','LoginType','EntityId','EntityType','DeviceOs','DeviceType','MacAddress','SessionId','AppVer']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myAuthArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' we also need to check if caller is internal, if not return auth key is invalid
            if caller class name and module file is not in list, return Invalid Auth Key
            '''

            '''Preparing value '''
            myCriteria = { '_id':ObjectId(str(myMainArgData['AuthKey'])), 
                           'LoginId': myMainArgData['LoginId'],'LoginType':myMainArgData['LoginType'],
                           'EntityId': myMainArgData['EntityId'],'EntityType':myMainArgData['EntityType'],
                           'DeviceType': myMainArgData['DeviceType'],'DeviceOs':myMainArgData['DeviceOs'],
                           'MacAddress': myMainArgData['MacAddress'],'AppVer':myMainArgData['AppVer'] }
            myProjection = {'_id':1}
            #print('criteria',myCriteria)
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, myCriteria, myProjection,False)
            myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
           
            '''if argkey passed and argkey from db is not matching return False '''
            #print('valid auth key',myResultsData,myMainArgData['AuthKey'])
            if myResultsData and ('_id' in myResultsData) and (str(myMainArgData['AuthKey']) == str(myResultsData['_id'])):
                return True
            else:
                return False

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __isValidLogin(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':''}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','Password']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' Retrieving/preparing  value for login id/password'''
            
            myLoginId = myMainArgData['LoginId']
            myPasswordText = str(myMainArgData['Password'])
            myLoginArgData = {'LoginId':myLoginId}
            myLoginCriteria = {'_id':myLoginId}
            myLoginInfo = self.__getLoginInfo(myLoginArgData)
            myValidLoginRetVal = 0

            if myLoginInfo:
                myMainArgData.update({'EntityId':myLoginInfo['EntityId']})
                myMainArgData.update({'EntityType':myLoginInfo['EntityType']})
            #fi

            if myLoginInfo and myLoginInfo.get('AccountStatus') == 'Open':
                myStoredHashPassword = myLoginInfo.get('Password')
                #print (myPasswordText,myStoredHashPassword)

                if myStoredHashPassword == None:
                    myValidLoginRetVal = "LoginError-001" 

                    ''' recording activity'''
                    self.activityInstance._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globalInstance._Global__Internal, 
                             'Activity':' Invalid loginid [{entity}]'.
                                        format(entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                             'Auth': myMainArgData})

                elif checkpw(str(myPasswordText), str(myStoredHashPassword)):
                    ''' we got valid login we need to create authentication'''
                    myValidLoginRetVal = "Success" 

                    ''' recording activity'''
                    ''' recording activity'''
                    self.activityInstance._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globalInstance._Global__Internal, 
                             'Activity':'Invalid loginid [{entity}]'.
                                        format(entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                             'Auth': myMainArgData})
                else:
                    myValidLoginRetVal = "LoginError-002"                     
                    ''' we got invalid password, lets increase the invalid count by 1 '''            
                    myDbResults = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__loginColl, myLoginCriteria, {'PasswordRetryCount':1}, 'inc')
                    myLoginInfo = self.__getLoginInfo(myLoginArgData)

                    ''' recording activity'''
                    self.activityInstance._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globalInstance._Global__Internal, 
                             'Activity':'Invalid password for Login [{login}] !!! Maximum password try count; current value [{current}] '.
                                    format(login=myMainArgData['LoginId'], current=myLoginInfo.get('PasswordRetryCount')),
                             'Auth': myMainArgData})

                    if myLoginInfo.get('PasswordRetryCount') >= 3:
                        myDbResults = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__loginColl, myLoginCriteria, {'AccountStatus':'Locked'}, 'set')
                        # expire all authentication
                        self.__expireAllAuthentication(myMainArgData)

                        ''' recording activity'''
                        self.activityInstance._Activity__logActivity(
                                {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                                 'ActivityType':self.globalInstance._Global__Internal, 
                                 'Activity':'Account is locked for [{login}] !!! Expiring all valid authentication '.
                                        format(login=myMainArgData['LoginId']),
                                 'Auth': myMainArgData})
                    #fi
                #fi
            elif myLoginInfo and myLoginInfo.get('AccountStatus') == 'Locked':
                myValidLoginRetVal = "LoginError-003"                     

                ''' recording activity'''
                ''' recording activity'''
                self.activityInstance._Activity__logActivity(
                        {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                         'ActivityType':self.globalInstance._Global__Internal, 
                         'Activity':'Password verification attempt, account is locked for [{login}] !!!'.
                                format(login=myMainArgData['LoginId']),
                         'Auth': myMainArgData})
            else:
                myValidLoginRetVal = "LoginError-001"                     
            #fi
            return myValidLoginRetVal

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def registerEntity(self, argRequestDict):
        '''
            argRequestDict = ['EntityType','MainArg']
        '''
        
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['MainArg']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            print(myArgValidationResults)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            print(myArgValidation)            
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))

            ''' extract entity type form mainArgument '''
            if ('EntityType' in myMainArgData['MainArg']['Auth']):
                '''Register entity '''
                if myMainArgData['MainArg']['Auth']['EntityType'] == self.globalInstance._Global__member:
                    myEntityData = self.registerMember(argRequestDict['MainArg'])
                elif myMainArgData['MainArg']['Auth']['EntityType'] == self.globalInstance._Global__vendor:
                    myMemberData = self.registerVendor(argRequestDict)
                else:
                    raise com.uconnect.core.error.InvalidEntity('Invalid entity passed during registration [{entity}]'.format(entity=myMainArgData['EntityType'])) 
                #fi    
            else:
                raise com.uconnect.core.error.MissingArgumentValues('Key [EntityType] is missing from main argument arg[{arg}]'.format(arg=myMainArgData['MainArg']))
            #fi
            return myEntityData

        except com.uconnect.core.error.InvalidEntity as error:
            myModuleLogger.exception('InvalidEntity: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def registerMember(self,argRequestDict):
        ''' 
            Description:    Register a new member;
                            1.) Create a new Member
                            2.) Create a new Login
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            ['LoginId':'','Password':'', 'LoginType':'', 'DeviceType':'', 'DeviceOs':'', 'MacAddress':'','SessionId':'','AppVer':'',
                              'Main':{},'Address':{},'Contact':{}]
            usage:          <createAMember(<argReqRequestDict>)
            Return:         Json object
        '''
        try:
            ''' importing MemberBPS module here to avoid the error (importing module from each other) '''
            from com.uconnect.bps.memberBPS import MemberBPS
            memberBPSInstance = MemberBPS.Instance()

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            ''' declaring variables '''

            myArgKey = myMainArgKey = myAddressArgKey = myContactArgKey = []
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myAuthKey = ''
            myMemberId = ''

            ''' preparing arg key for validation'''
            myArgKey = ['Auth','Main','Address','Contact']
            myMainArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Main')
            myAddressArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Address')

            ''' we dont need validation for contact, yet TBD ''
            myContactArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Contact')
            self.utilityInstance.removeKeyFromList([])
            '''
            myAuthArgKey = self.utilityInstance.buildKeysFromTemplate('Auth')

            ''' encrypt password '''
            myMainArgData['Auth']['Password'] = self.__genHashPassword({'Password':myMainArgData['Auth']['Password']})            

            ''' validating arguments '''
            # Main Arg validation

            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # Member Main arg validation
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myMainArgKey, 'NickName')
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg [Member.Main] validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # Member Address arg validation
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Address'], myAddressArgKey, ['Street','City','State','Country'])
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg [Member.Address] validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # Member Contact arg validation
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Contact'], myContactArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg [Member.Contact] validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            # Auth arg validation
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Auth'], myAuthArgKey, ['ExpiryDate','AuthKey','EntityId','_id'])
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Autharg validation error; auth arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Check if this login is already in use '''
            myLoginArgData = {'LoginId':myMainArgData['Auth']['LoginId'],'ResponseMode':self.globalInstance._Global__InternalRequest}
            myLoginInUseResult = self.isLoginInUse(myLoginArgData)
            #print()
            if myLoginInUseResult['Status'] == self.globalInstance._Global__True:
                raise com.uconnect.core.error.InvalidLogin("Requested login [{login}] is already in use".format(login=myMainArgData['Auth']['LoginId']))
            #fi

            ''' create a member '''
            myMemberData = {'Main':myMainArgData['Main'], 'Address':myMainArgData['Address'], 'Contact':myMainArgData['Contact']}
            myMemberId = memberBPSInstance._MemberBPS__createAMember(myMemberData)
            myMainArgData['Auth'].update({'EntityId':myMemberId})
            myMainArgData['Auth'].update({'EntityType':self.globalInstance._Global__member})

            ''' building auth dictionary '''
            myMainAuthArgData = {'Auth':self.utilityInstance.getCopy(myMainArgData['Auth'])}

            ''' recording activity '''
            self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(
                myMemberId,self.globalInstance._Global__member,self.globalInstance._Global__Internal,'Member [{member}] created'.
                format(member=myMemberId), myMainAuthArgData))

            ''' create login for this member '''
            myAuthKey = self.__createLogin(myMainAuthArgData)

            ''' Building response
            we got Auth key, we need to inject it to get this memeber information from database '''

            myMainAuthArgData['Auth'].update({'AuthKey':myAuthKey})

            self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(
                myMemberId,self.globalInstance._Global__member, 'Internal','LoginId [{login}] and AuthKey [{authKey}] created for Member [{member}]'.
                format(login=myMainAuthArgData['Auth']['LoginId'], member=myMemberId, authKey= myAuthKey),myMainAuthArgData))

            ''' getting member information from database '''
            myMemberData = memberBPSInstance.getAMemberDetail(
                {'Auth':myMainAuthArgData['Auth'],'ResponseMode':self.globalInstance._Global__InternalRequest})
            
            #print(self.utilityInstance.extr1stDocFromResultSets(myMemberData))
            
            if myMemberData:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(
                    self.globalInstance._Global__UnSuccess, "Could not find member {member} information".format(member=myMemberId))
            #fi            

            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberData )
            myResponse['Response']['Header']['Auth']['AuthKey'] = myAuthKey
            return myResponse

        except com.uconnect.core.error.InvalidLogin as error:
            myModuleLogger.exception('InvalidLogin: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find')
            return myResponse            
            #raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find')
            return myResponse            
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            # undo all the work
            if myMemberId:
                self.mongoDbInstance.DeleteDoc(self.globalInstance._Global__memberColl,{'_id':myMemberId} )
            if myAuthKey:
                self.mongoDbInstance.DeleteDoc(self.globalInstance._Global__authColl,{'_id':ObjectId(str(myAuthKey))} )

            self.mongoDbInstance.DeleteDoc(self.globalInstance._Global__loginColl, {'_id':myMainArgData['Auth']['LoginId']} )    
           
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find')
            return myResponse            

    def validateCredential(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':'', 'LoginType':'','DeviceOs':'','SessionId'}
            This method is called externally
            Questions: EntityId and EntityType is passed, do we need this, should we send the entityid and entityype back???
              we need to clarify link here ? should we expect the entityid and entitytype to be passed
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myArgKey = ['ResponseMode','Auth']
            myResponseData = {}
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myMainAuthArgData = self.utilityInstance.getCopy(myMainArgData)['Auth'] 
            myAuthArgKey = self.utilityInstance.buildKeysFromTemplate('Auth')

            '''we need either LoginId/Auth's required argument '''
            if 'LoginId' in myMainAuthArgData and 'Password' in myMainAuthArgData:

                ''' validating auth arguments '''
                myArgValidationResults = self.utilityInstance.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','AuthKey'])
                myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues('Autharg validation error; auth arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
                #fi

                myValidateLoginStatus = self.__isValidLogin(myMainAuthArgData)

                if myValidateLoginStatus == self.globalInstance._Global__Success:
                    ''' we need to check if this device is 1st time used, if yes, we would need security code validation '''
                    ''' we need to return newAuthKey, EntityId and EntityType for this loginId '''
                    myLoginInfo = self.__getLoginInfo({'LoginId':myMainAuthArgData['LoginId']})

                    ''' injecting entitytype and entityid '''
                    myMainAuthArgData.update({'EntityId':myLoginInfo.get('EntityId')})
                    myMainAuthArgData.update({'EntityType':myLoginInfo.get('EntityType')})

                    myAuthKey = self.__createAuthentication(myMainAuthArgData)
                    myResponseData = {'EntityId':myLoginInfo.get('EntityId'),'EntityType':myLoginInfo.get('EntityType'),'AuthKey':myAuthKey}
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                else:
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myValidateLoginStatus + ' ' + self.utilityInstance.getErrorCodeDescription(myValidateLoginStatus))
                #fi
            elif 'AuthKey' in myMainAuthArgData: 

                ''' validating auth arguments '''
                myArgValidationResults = self.utilityInstance.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','EntityType','LoginId','Password'])
                myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues('Autharg validation error; auth arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
                #fi

                ''' perform authkey validation '''
                if self.__isValidAuthentication(myMainAuthArgData):
                    ''' we need to retrieve entityid and entitytype from Auth collection '''
                    myAuthResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, {'_id':ObjectId(str(myMainAuthArgData['AuthKey']))},{},True)
                    myAuthData =  self.utilityInstance.extr1stDocFromResultSets(myAuthResults)
                    myResponseData = {'EntityId':myAuthData.get('EntityId'),'EntityType':myAuthData.get('EntityType'),'AuthKey':str(myAuthData.get('_id'))}
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                else:
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Invalid LoginId/Password')                    
                #fi
            else:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, argument must be [{login}] or [{auth}]'.
                    formmat(login='[LoginID,Password,DeviceOs,DeviceType,SessionId,MacAddress,AppVer]',
                            auth='[AuthKey,DeviceOs,DeviceType,SessionId,MacAddress,AppVer]'))                
            #fi
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find',myResponseData)
            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse

    def isLoginInUse(self, argRequestDict):
        '''
            argRequestDict = {'LoginId'}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            ''' declaring/initializing variables '''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgKey = ['LoginId','ResponseMode']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Preparing value for login id'''
            myCriteria = {'_id': myMainArgData['LoginId']}
            myProjection = {'_id':1}

            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__loginColl, myCriteria, myProjection, True)
            #print(myResults)
            myLoginData = self.utilityInstance.extr1stDocFromResultSets(myResults)
            #print('login',myLoginData, myCriteria)

            if myLoginData and '_id' in myLoginData and (not (myLoginData['_id'] == None)) :
                # loginid found, its in use
                myRequestStatus = self.utilityInstance.getRequestStatus(
                    self.globalInstance._Global__UnSuccess,'Login [{login}] is already in use'.
                                        format(login=myMainArgData['LoginId']))
                myRequestStatus.update({'Status':self.globalInstance._Global__True})
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                myRequestStatus.update({'Status':self.globalInstance._Global__False})
                myRequestStatus.update({'Message':'Login [{login}] is not in use'.format(login=myMainArgData['LoginId'])})
            #fi

            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            myRequestStatus.update({'Status':self.globalInstance._Global__True})
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
            myRequestStatus.update({'Status':self.globalInstance._Global__True})
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse
