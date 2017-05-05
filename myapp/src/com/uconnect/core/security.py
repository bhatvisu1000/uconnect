import json, os, sys, logging, copy, datetime, com.uconnect.utility.ucLogging, com.uconnect.core.error

from bcrypt import hashpw, checkpw, gensalt
from bson.objectid import ObjectId

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.infra import Environment
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.globals import Global

@Singleton
class Security(object):
    def __init__(self):
        self.mongoDbInstance = MongoDB.Instance()
        self.envInstance = Environment.Instance()
        self.utilityInstance = Utility.Instance()
        self.globalInstance = Global.Instance()

        self.myClass = self.__class__.__name__

    def __genHashPassword(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['Password']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            myPasswordText = str(myMainArgData['Password']) 
            hashPassword = hashpw(myPasswordText, gensalt(rounds=8, prefix='2b'))
            print('hash:' + ':' + myPasswordText + ':' + hashPassword)
            return  hashPassword

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __getLoginPassword(self, argRequestDict):

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myArgKey))

            myLoginCriteria = {'_id':myMainArgData['LoginId']}
            myProjection = {'Password':1}
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__loginColl, myLoginCriteria, myProjection,True)
            #print ('LoginId,Proj,Pass',argLoginId,myLoginCriteria,myProjection,myLoginPassword['Data'][0]['Password'])
        
            if self.utilityInstance.extrStatusFromResultSets(myResults) == self.globalInstance._Global__OkStatus:
                myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
            
            if not(myResultsData == None) and self.utilityInstance.isKeyInDict(myResultsData,'Password'):
                return myResultsData['Password']
            else:
                return None

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def __getEntity4Login(self, argRequestDict):
        ''' internal method, will be called by validateAuthentication'''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId','Password']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myArgKey))

            myLoginCriteria = {'_id':myMainArgData['LoginId']}
            myProjection = {'Password':1,'EntityType':1,'EntityId':1}
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__loginColl, myLoginCriteria, myProjection,True)

            if self.utilityInstance.extrStatusFromResultSets(myResults) == self.globalInstance._Global__OkStatus:
                # we got password, lets authenticate the passwords
                if self.__isValidLogin(myMainArgData):
                    myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
                #fi
            #fi

            if not(myResultsData == None):
                myResultsData.pop('Password')
                return myResultsData
            else:
                return None

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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

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
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId','Password','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','EntityType','EntityId','AppVer']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            ''' This is to ensure if password is encrypted. Do we need this ?'''
            #if not(len(myMainArgData['Password']) == 60 and myMainArgData['Password'].startswith('$2b$')):
            #    myMainArgData['Password'] = self.__genHashPassword({'Password':myMainArgData['Password']})

            ''' Buildkng LoginInfo document'''
            myLoginData = self.__buildInitLoginData(myMainArgData)
            myDbResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__loginColl, myLoginData)

            ''' if login creation is successful, create authentication and return Auth Id'''
            if myDbResult[self.globalInstance._Global__StatusKey] == self.globalInstance._Global__TrueStatus:
                myAuthKey = self.__createAuthentication(argRequestDict)
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

            myArgKey =  ['LoginId','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','AppVer']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            '''Retrieving all Authentication and mark it as expired  '''
            myAllAuthKey = self.__getAuthKey(myMainArgData)
            if myAllAuthKey:
                for myAuthKey in myAllAuthKey:
                    myExpireResult = self.__expireAuthentication({'AuthKey':myAuthKey['_id']})
                    print(myExpireResult)
                    if myExpireResult['deleted'] == 0:
                        raise com.uconnect.core.error.DBError('Failed to expire auth document AuthKey[{authKey}]'.format(authKey=myAuthKey))
                    #fi
                #end for loop
            #fi
            '''Preparing/Creating new Auth Doc '''
            myModuleLogger.debug('Argument validated, preparing Auth document')
            myAuthDoc = self.__buildInitAuthData(myMainArgData)
            myAuthResult = self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__authColl, myAuthDoc)
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
    
    def __expireAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':''}
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['AuthKey']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

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

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityId','AppVer']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            '''Preparing value '''
            myCriteria = {'LoginId':myMainArgData['LoginId'], 
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'SessionId':myMainArgData['SessionId'],
                          'EntityId':myMainArgData['EntityId'],
                          'EntityType':myMainArgData['EntityType'],
                          'AppVer':myMainArgData['AppVer']}
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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

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

    def __isValAuthKeyInternal(self, argRequestDict):
        '''
            argRequestDict = {'AuthKey':'','EntityId':'','EntityType':''}
        '''

        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myAuthArgKey = ['AuthKey','EntityId','EntityType']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myAuthArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' we also need to check if caller is internal, if not return auth key is invalid
            if caller class name and module file is not in list, return Invalid Auth Key
            '''

            '''Preparing value '''
            myCriteria = { '_id':ObjectId(str(myMainArgData['AuthKey'])), 'EntityId': myMainArgData['EntityId'],'EntityType':myMainArgData['EntityType']}
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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            ''' Retrieving/preparing  value for login id/password'''
            myLoginId = myMainArgData['LoginId']
            myPasswordText = str(myMainArgData['Password'])
            myLoginIdCriteria = {'LoginId':myLoginId}
            myStoredHashPassword = str(self.__getLoginPassword(myLoginIdCriteria))
            print (myPasswordText,myStoredHashPassword)

            if myStoredHashPassword == None:
                myValidLogin = False
            elif checkpw(myPasswordText, myStoredHashPassword):
                ''' we got valid login we need to create authentication'''
                myValidLogin = True
            else:
                myValidLogin = False

            return myValidLogin

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
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))


            ''' extract entity type form mainArgument '''
            if ('EntityType' in myMainArgData['MainArg']):
                '''Register entity '''
                if myMainArgData['MainArg']['EntityType'] == self.globalInstance._Global__member:
                    myEntityData = self.registerMember(argRequestDict['MainArg'])
                elif myMainArgData['MainArg']['EntityType'] == self.globalInstance._Global__vendor:
                    myMemberData = self.registerVendor(argRequestDict)
                else:
                    raise com.uconnect.core.error.InvalidEntity('Invalid entity passed during registration [{entity}]'.format(entity=myMainArgData['EntityType'])) 
            else:
                raise com.uconnect.core.error.MissingArgumentValues('Key [EntityType] is missing from main argument arg[{arg}]'.format(arg=myMainArgData['MainArg']))

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
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            ''' preparing arg key for validation'''
            myArgKey = ['Auth','Main','Address','Contact']
            myMainArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Main')
            myAddressArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Address')

            ''' we dont need validation for contact, yet TBD ''
            myContactArgKey = self.utilityInstance.buildKeysFromTemplate('Member','Contact')
            self.utilityInstance.removeKeyFromList([])
            '''
            myAuthArgKey = self.utilityInstance.buildKeysFromTemplate('Auth')

            ''' validating arguments '''
            # Main Arg validation
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData, key=myArgKey))
            #fi

            # Member Main arg validation
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myMainArgKey, 'NickName')
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData['Main'], key=myMainArgKey))
            #fi

            # Member Address arg validation
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData['Address'], myAddressArgKey, ['Street','City','State'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData['Address'], key=myAddressArgKey))
            #fi

            # Member Contact arg validation
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData['Contact'], myContactArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData['Contact'], key=myContactArgKey))
            #fi

            # Auth arg validation
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData['Auth'], myAuthArgKey, ['ExpiryDate','AuthKey','EntityId','_id'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData['Auth'], key=myAuthArgKey))

            ''' Check if this login is already in use '''
            myLoginArgData = {'LoginId':myMainArgData['Auth']['LoginId'],'ResponseMode':self.globalInstance._Global__InternalRequest}
            myLoginInUseResult = self.isLoginInUse(myLoginArgData)
            #print()
            if myLoginInUseResult['Status'] == self.globalInstance._Global__UnSuccess:
                raise com.uconnect.core.error.InvalidLogin("Requested login [{login}] is already in use".format(login=myMainArgData['Auth']['LoginId']))
            #fi

            ''' create a member '''
            myMemberData = {'Main':myMainArgData['Main'], 'Address':myMainArgData['Address'], 'Contact':myMainArgData['Contact']}
            myMemberId = memberBPSInstance._MemberBPS__createAMember(myMemberData)
            myMainArgData['Auth'].update({'EntityId':myMemberId})

            ''' create login, encrypt password '''
            myMainArgData['Auth']['Password'] = self.__genHashPassword({'Password':myMainArgData['Auth']['Password']})            
            myAuthKey = self.__createLogin(myMainArgData['Auth'])
            #print('MyAuthKey',myAuthKey)

            ''' Building response
            we got Auth key, we need to inject it to get this memeber information from database '''

            myMainArgData['Auth'].update({'AuthKey':myAuthKey})

            ''' getting member information from database '''
            myMemberData = memberBPSInstance.getAMemberDetail(
                {'MemberId':myMemberId,'Auth':myMainArgData['Auth'],'ResponseMode':self.globalInstance._Global__InternalRequest})
            
            print(self.utilityInstance.extr1stDocFromResultSets(myMemberData))
            
            if myMemberData:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(
                    self.globalInstance._Global__UnSuccess, "Could not find member {member} information".format(member=myMemberId))
            #fi            

            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberData )

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
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myArgKey))

            myMainAuthArgData = self.utilityInstance.getCopy(myMainArgData)['Auth'] 
            myAuthArgKey = self.utilityInstance.buildKeysFromTemplate('Auth')
            myArgValidation = self.utilityInstance.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','EntityType'])

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainAuthArgData, key=myAuthArgKey))

            ''' Validate login id,if successful, create authentication'''
            ''' we should check to see if authentication already exists and its valid, if its valid, mark it as expired and create new one '''
            if self.__isValidLogin(myMainAuthArgData):
                # now we need EntityId and EntityType for which we need to create authentication
                myAuthKey = {'AuthKey':self.__createAuthentication(myMainAuthArgData)}
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Invalid Credential for login [{login}] !!!'.format(login=myMainAuthArgData['LoginId']))                
                myAuthKey = {'AuthKey':''}
            #fi

            #myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find',)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find',myAuthKey)
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

    def isValidAuthentication(self, argRequestDict):
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
            myAuthArgKeys = self.utilityInstance.buildKeysFromTemplate('Auth').append('ResponseMode').append('AuthKey')
            #myAuthArgKey.append('ResponseMode')
            #myAuthArgKey.append('AuthKey')

            ''' validating arguments '''
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myAuthArgKeys,['ExpiryDate','_id'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myAuthArgKeys))

            '''Preparing value '''
            myCriteria = {'_id':ObjectId(str(myMainArgData['AuthKey'])),
                          'LoginId':myMainArgData['LoginId'], 
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'SessionId':myMainArgData['SessionId'],
                          'EntityId':myMainArgData['EntityId'],
                          'EntityType':myMainArgData['EntityType'],
                          'ExpiryDate':{'$gte': datetime.datetime.utcnow()},
                          'AppVer':myMainArgData['AppVer']}
            myProjection = {'_id':1}
            #print('criteria',myCriteria)
            myResults = self.mongoDbInstance.findDocument(self.globalInstance._Global__authColl, myCriteria, myProjection,False)
            myResultsData = self.utilityInstance.extr1stDocFromResultSets(myResults)
            '''if argkey passed and argkey from db is not matching return False '''
            #print('valid auth key',myResultsData,myMainArgData['AuthKey'])
            if myResultsData and ('_id' in myResultsData) and (str(myMainArgData['AuthKey']) == str(myResultsData['_id'])):
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success) 
                #return True
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, "Invalid Authentication !!!") 
                #return False
            #fi
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find')
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

            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData.keys(), key=myArgKey))

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
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            #fi

            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find')

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
