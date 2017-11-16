import json, os, sys, logging, copy, datetime, com.uconnect.utility.ucLogging, com.uconnect.core.error

from bcrypt import hashpw, checkpw, gensalt
from bson.objectid import ObjectId

from com.uconnect.core.singleton import Singleton
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.globals import Global
from com.uconnect.core.activity import Activity

myLogger = logging.getLogger('uConnect')

#@Singleton
class Security(object, metaclass=Singleton):
    def __init__(self):
        self.mongo = MongoDB()
        self.util = Utility()
        self.globaL = Global()
        self.activity = Activity()
        #self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.__class__.__name__)

    def __genHashPassword(self, argRequestDict):

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['Password']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myPasswordText = str(myMainArgData['Password']).encode('utf-8') 
            #hashPassword = hashpw(myPasswordText, gensalt(rounds=8, prefix=b"2b"))
            hashPassword = hashpw(myPasswordText, gensalt(rounds=8, prefix=b"2b"))
            #print('hash:' + ':' + myPasswordText + ':' + hashPassword)
            return  hashPassword

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __getLoginInfo(self, argRequestDict):

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myLoginCriteria = {'_id':myMainArgData['LoginId']}
            myProjection = {}
            myResults = self.mongo.findDocument(self.globaL._Global__loginColl, myLoginCriteria, myProjection,True)
            self.myModuleLogger.debug('got login information from repository [{result}] '.format(result=myResults))

            #print ('LoginId,Proj,Pass',argLoginId,myLoginCriteria,myProjection,myLoginPassword['Data'][0]['Password'])
        
            if self.util.extrStatusFromResultSets(myResults) == self.globaL._Global__OkStatus:
                myResultsData = self.util.extr1stDocFromResultSets(myResults)
            #fi

            if not(myResultsData == None):
                return myResultsData
            else:
                return None
            #fi

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __buildInitLoginData(self, argRequestDict):

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','EntityType','EntityId','Password']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # retrieve the template 
            myInitLoginInfoData = self.util.getTemplateCopy(self.globaL._Global__loginColl)
            self.myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitLoginInfoData))        

            myInitLoginInfoData['_id'] = myMainArgData['LoginId']
            myInitLoginInfoData['LoginType'] = myMainArgData['LoginType']
            myInitLoginInfoData['Password'] = myMainArgData['Password']
            myInitLoginInfoData['EntityId'] = myMainArgData['EntityId']
            myInitLoginInfoData['EntityType'] = myMainArgData['EntityType']

            ''' build initial history data '''
            myInitLoginInfoData['_History'] = self.util.buildInitHistData() 
            #print('initlogininfo',myInitLoginInfoData)
            self.myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitLoginInfoData))

            return myInitLoginInfoData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __buildInitAuthData(self, argRequestDict):

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityId','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # retrieve the template 
            myInitAuthData = self.util.getTemplateCopy(self.globaL._Global__authColl)
            #print(myInitAuthData, myMainArgData)
            self.myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitAuthData))        

            myInitAuthData['LoginId'] = myMainArgData['LoginId']
            myInitAuthData['LoginType'] = myMainArgData['LoginType']
            myInitAuthData['DeviceType'] = myMainArgData['DeviceType']
            myInitAuthData['DeviceOs'] = myMainArgData['DeviceOs']
            myInitAuthData['MacAddress'] = myMainArgData['MacAddress']
            myInitAuthData['SessionId'] = myMainArgData['SessionId']
            myInitAuthData['ExpiryDate'] = datetime.datetime.utcnow() + datetime.timedelta(days=self.util.getAuthValidDuration())
            myInitAuthData['EntityId'] = myMainArgData['EntityId']
            myInitAuthData['EntityType'] = myMainArgData['EntityType']
            myInitAuthData['AppVer'] = myMainArgData['AppVer']

            ''' build initial history data '''
            myInitAuthData['_History'] = self.util.buildInitHistData() 
            self.myModuleLogger.debug('Data [{arg}] returned'.format(arg=myInitAuthData))

            return myInitAuthData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __buildInitAuthHistData(self, argRequestDict):

        try:
            
            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['_id','LoginId','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','ExpiryDate','EntityId','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # retrieve the template 
            myInitAuthHistData = self.util.getTemplateCopy(self.globaL._Global__authHistColl)
            self.myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitAuthHistData))        

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
            myInitAuthHistData['_History'] = self.util.buildInitHistData() 
            self.myModuleLogger.debug('Data [{arg}] returned'.format(arg=myInitAuthHistData))

            return myInitAuthHistData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __buildInitSecurityCodeData(self, argRequestDict):

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','SecurityCode','DeliveryMethod','DeliverTo']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # retrieve the template 
            myInitSecurityCodeData = self.util.getTemplateCopy(self.globaL._Global__securityCodeColl)
            self.myModuleLogger.debug('LoginInfo template [{template}]'.format(template=myInitSecurityCodeData))
            myInitSecurityCodeData['LoginId'] = myMainArgData['LoginId']
            myInitSecurityCodeData['DeliveryMethod'] = myMainArgData['DeliveryMethod']
            myInitSecurityCodeData['DeliverTo'] = myMainArgData['DeliverTo']
            myInitSecurityCodeData['CreateDate'] = datetime.datetime.utcnow()
            myInitSecurityCodeData['SecurityCode'] = myMainArgData['SecurityCode']
            '''we dont need to update deliver date, this need to be update when the security code is sent '''
            myInitSecurityCodeData['DeliverDate'] = datetime.datetime.utcnow()

            ''' build initial history data '''
            #myInitSecurityCodeData['_History'] = self.util.buildInitHistData() 
            #print('securitylogininfo',myInitSecurityCodeData)
            self.myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitSecurityCodeData))

            return myInitSecurityCodeData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __createLogin(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':''}
        '''
        
        try:
            
            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            myMainAuthArgData = self.util.getCopy(myMainArgData['Auth'])
            #print ('login',myMainArgData)
            #print ('login',myMainAuthArgData)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['Auth']
            myAuthArgKey =  ['LoginId','Password','LoginType','DeviceOs','DeviceType','MacAddress','SessionId','EntityType','EntityId','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' validating Auth arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainAuthArgData, myAuthArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' This is to ensure if password is encrypted. Do we need this ?'''
            #if not(len(myMainArgData['Password']) == 60 and myMainArgData['Password'].startswith('$2b$')):
            #    myMainArgData['Password'] = self.__genHashPassword({'Password':myMainArgData['Password']})

            ''' Buildkng LoginInfo document'''
            myLoginData = self.__buildInitLoginData(myMainAuthArgData)
            myDbResult = self.mongo.InsertOneDoc(self.globaL._Global__loginColl, myLoginData)

            ''' if login creation is successful, create authentication and return Auth Id'''
            if myDbResult[self.globaL._Global__StatusKey] == self.globaL._Global__TrueStatus:
                myAuthKey = self.__createAuthentication(myMainAuthArgData)
            else:
                raise com.connect.core.error.DBError('Login creation failed loginifo[{login}]'.format(login=myLoginData))

            return myAuthKey

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __createAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':'','LoginId':'', 'LoginType':'','DeviceOs':'','SessionId'}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey =  ['LoginId','LoginType','EntityType','EntityId','DeviceOs','DeviceType','MacAddress','SessionId','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

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
            self.myModuleLogger.debug('Argument validated, preparing Auth document')
            myAuthDoc = self.__buildInitAuthData(myMainArgData)
            myAuthResult = self.mongo.InsertOneDoc(self.globaL._Global__authColl, myAuthDoc)
            
            ''' recording activity'''
            self.activity._Activity__logActivity(
                {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                 'ActivityType':self.globaL._Global__Internal, 
                 'Activity':'Generating new Auth key [{auth}] for [{entity}]'.
                        format(auth=str(myAuthResult['_id']),
                                entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                 'Auth': myMainArgData})

            ''' we need to return string value of object_id '''
            return str(myAuthResult['_id'])

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise
    
    def __expireAllAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':''}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','EntityId','EntityType']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

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
        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __expireAuthentication(self,argRequestDict):
        '''
            argRequestDict = {'AuthKey':''}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['AuthKey']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # checking if Authkey passed is a valid type of object id
            if not (ObjectId.is_valid(myMainArgData['AuthKey'])):
                raise com.uconnect.error.InvalidAuthKey('Invalid Auth key [{auth}]'.format (auth=myMainArgData['AuthKey']))

            ''' Finding Auth document '''
            myCriteria = {'_id':ObjectId(str(myMainArgData['AuthKey']))}
            myProjection = {}
            myResult = self.mongo.findDocument(self.globaL._Global__authColl, myCriteria, {}, True)
            self.myModuleLogger.debug('Results [{resuts}], after looking for Auth Document'.format (resuts=myResult))
            
            if self.util.extrStatusFromResultSets(myResult) == self.globaL._Global__OkStatus:

                '''Auth Document found, will archive before expiring this auth document, preparing AuthHistory document '''
                myAuthData = self.util.extr1stDocFromResultSets(myResult)
                myAuthHistData = self.__buildInitAuthHistData(myAuthData)   
                self.myModuleLogger.debug('Auth history document [{authhist}] prepared'.format (authhist=myAuthHistData))

                '''Moving Auth document to History collection, before removing from Auth collection '''
                myAuthHistResult = self.mongo.InsertOneDoc(self.globaL._Global__authHistColl, myAuthHistData)
                #print(myDbResult)
                if myAuthHistResult[self.globaL._Global__StatusKey] == self.globaL._Global__TrueStatus:
                    self.myModuleLogger.debug('Auth Key [{AuthKey}]; history document created, deleting Auth document '.format(AuthKey=myMainArgData['AuthKey']))
                    myAuthDelResult = self.mongo.DeleteDoc(self.globaL._Global__authColl, myCriteria)
                else:
                    self.myModuleLogger.debug('Auth history document creation failed, aborting operation (expiring Auth document)')
                    raise com.uconnect.core.error.DBError("Error moving Auth data to AuthHistory container AuthKey [{authkey}]".format(authkey=myAuthData['_id']))
            else:
                raise com.uconnect.core.error.DBError("Error while looking for AuthKey [{authkey}]".format(authkey=myAuthData['_id']))                

            return myAuthDelResult

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __getAuthKey(self, argRequestDict):
        '''
            argRequestDict = {'AuthKey':'','LoginId':'', 'LoginType':'','DeviceOs':'','SessionId'}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityId','EntityType','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            '''Preparing value '''
            myCriteria = {'LoginId':myMainArgData['LoginId'],
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'EntityId':myMainArgData['EntityId'],
                          'EntityType':myMainArgData['EntityType']}
            myProjection = {'_id':1}

            myAuthResults = self.mongo.findDocument(self.globaL._Global__authColl, myCriteria, myProjection,False)
            myAuthData = self.util.extrAllDocFromResultSets(myAuthResults)

            return myAuthData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __updateAuthEntity(self, argRequestDict):
        '''
            argRequestDict = {'Auth':'','EntityType':'', 'EntityId':''}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['Auth','EntityType','EntityId']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' lets inject EntityType and EnttyId in Auth Dict'''

            myMainArgData['Auth']['EntityType'] = myMainArgData['EntityType']
            myMainArgData['Auth']['EntityId'] = myMainArgData['EntityId']

            return myMainArgData['Auth']

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __isValidAuthentication(self, argRequestDict):
        '''
            argRequestDict = ['ResponseMode','Auth':[]]
               auth:[Key','LoginId','LoginType','DeviceOs','MacAddress','SessionId','AppVer']
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)            
            myAuthArgKeys = self.util.buildKeysFromTemplate('Auth')
            myAuthArgKeys.append('AuthKey')

            ''' validating arguments '''
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData, myAuthArgKeys,['ExpiryDate','_id'])
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myAuthArgKeys,['ExpiryDate','_id'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' making sure entitytype and entityid is passed in AUTH '''

            # checking if Authkey passed is a valid type of object id
            if not (ObjectId.is_valid(myMainArgData['AuthKey'])):
                raise com.uconnect.error.InvalidAuthKey('Invalid Auth key [{auth}]'.format (auth=myMainArgData['AuthKey']))
            #fi

            if not({'EntityType','EntityId','AuthKey','DeviceType','DeviceOs','MacAddress','AppVer'} <= set(myMainArgData)):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg Auth validation error; Auth dict must have [EntityType,EntityId,AuthKey]')
            #fi

            '''Preparing value '''
            myCriteria = {'_id':ObjectId(str(myMainArgData['AuthKey'])),
                          'LoginType':myMainArgData['LoginType'], 
                          'DeviceType':myMainArgData['DeviceType'],
                          'DeviceOs':myMainArgData['DeviceOs'],
                          'MacAddress':myMainArgData['MacAddress'],
                          'SessionId':myMainArgData['SessionId'],
                          'EntityId':myMainArgData['EntityId'], 
                          'EntityType':myMainArgData['EntityType'], 
                          'ExpiryDate':{'$gte': datetime.datetime.utcnow()},
                          'AppVer':myMainArgData['AppVer']}
            myProjection = {}
            #print('criteria',myCriteria)
            myResults = self.mongo.findDocument(self.globaL._Global__authColl, myCriteria, myProjection,False)
            myResultsData = self.util.extr1stDocFromResultSets(myResults)
            '''if argkey passed and argkey from db is not matching return False '''

            if myResultsData and ('_id' in myResultsData) and (str(myMainArgData['AuthKey']) == str(myResultsData['_id'])):
                return True
            else:
                return False

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            return False

    def __isValAuthKeyInternal(self, argRequestDict):
        '''
            argRequestDict = {All authentication information}
        '''

        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myAuthArgKey = ['AuthKey','LoginId','LoginType','EntityId','EntityType','DeviceOs','DeviceType','MacAddress','SessionId','AppVer']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myAuthArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' we also need to check if caller is internal, if not return auth key is invalid
            if caller class name and module file is not in list, return Invalid Auth Key
            '''
            # checking if Authkey passed is a valid type of object id
            if not (ObjectId.is_valid(myMainArgData['AuthKey'])):
                raise com.uconnect.error.InvalidAuthKey('Invalid Auth key [{auth}]'.format (auth=myMainArgData['AuthKey']))

            '''Preparing value '''
            myCriteria = { '_id':ObjectId(str(myMainArgData['AuthKey'])), 
                           'LoginId': myMainArgData['LoginId'],'LoginType':myMainArgData['LoginType'],
                           'EntityId': myMainArgData['EntityId'],'EntityType':myMainArgData['EntityType'],
                           'DeviceType': myMainArgData['DeviceType'],'DeviceOs':myMainArgData['DeviceOs'],
                           'MacAddress': myMainArgData['MacAddress'],'AppVer':myMainArgData['AppVer'] }
            myProjection = {'_id':1}
            #print('criteria',myCriteria)
            myResults = self.mongo.findDocument(self.globaL._Global__authColl, myCriteria, myProjection,False)
            myResultsData = self.util.extr1stDocFromResultSets(myResults)
           
            '''if argkey passed and argkey from db is not matching return False '''
            #print('valid auth key',myResultsData,myMainArgData['AuthKey'])
            if myResultsData and ('_id' in myResultsData) and (str(myMainArgData['AuthKey']) == str(myResultsData['_id'])):
                return True
            else:
                return False

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def __isValidLogin(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':''}       
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['LoginId','Password']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

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

            if myLoginInfo and myLoginInfo.get('AccountStatus') == self.globaL._Global__LoginStatusOpen:
                myStoredHashPassword = myLoginInfo.get('Password')
                #print (myPasswordText,myStoredHashPassword)

                if myStoredHashPassword == None:
                    myValidLoginRetVal = "LoginError-001" 

                    ''' recording activity'''
                    self.activity._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globaL._Global__Internal, 
                             'Activity':' Invalid loginid [{entity}]'.
                                        format(entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                             'Auth': myMainArgData})

                #elif checkpw(myPasswordText.encode('utf8'), myStoredHashPassword.encode('utf-8')):
                elif checkpw(myPasswordText.encode('utf-8'), myStoredHashPassword):
                    ''' we got valid login we need to create authentication'''
                    myValidLoginRetVal = "Success" 

                    ''' recording activity'''
                    ''' recording activity'''
                    self.activity._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globaL._Global__Internal, 
                             'Activity':'Invalid loginid [{entity}]'.
                                        format(entity=myMainArgData['EntityType'] + ' - ' + str(myMainArgData['EntityId'])),
                             'Auth': myMainArgData})
                else:
                    myValidLoginRetVal = "LoginError-002"                     
                    ''' we got invalid password, lets increase the invalid count by 1 '''            
                    myDbResults = self.mongo.UpdateDoc(self.globaL._Global__loginColl, myLoginCriteria, {'PasswordRetryCount':1}, 'inc')
                    myLoginInfo = self.__getLoginInfo(myLoginArgData)

                    ''' recording activity'''
                    self.activity._Activity__logActivity(
                            {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                             'ActivityType':self.globaL._Global__Internal, 
                             'Activity':'Invalid password for Login [{login}] !!! Maximum password try count; current value [{current}] '.
                                    format(login=myMainArgData['LoginId'], current=myLoginInfo.get('PasswordRetryCount')),
                             'Auth': myMainArgData})

                    if myLoginInfo.get('PasswordRetryCount') >= 3:
                        myDbResults = self.mongo.UpdateDoc(self.globaL._Global__loginColl, myLoginCriteria, {'AccountStatus':'Locked'}, 'set')
                        # expire all authentication
                        self.__expireAllAuthentication(myMainArgData)

                        ''' recording activity'''
                        self.activity._Activity__logActivity(
                                {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                                 'ActivityType':self.globaL._Global__Internal, 
                                 'Activity':'Account is locked for [{login}] !!! Expiring all valid authentication '.
                                        format(login=myMainArgData['LoginId']),
                                 'Auth': myMainArgData})
                    #fi
                #fi
            elif myLoginInfo and myLoginInfo.get('AccountStatus') == self.globaL._Global__LoginStatusLocked:
                myValidLoginRetVal = "LoginError-003"                     

                ''' recording activity'''
                ''' recording activity'''
                self.activity._Activity__logActivity(
                        {'EntityId':myMainArgData['EntityId'], 'EntityType':myMainArgData['EntityType'], 
                         'ActivityType':self.globaL._Global__Internal, 
                         'Activity':'Password verification attempt, account is locked for [{login}] !!!'.
                                format(login=myMainArgData['LoginId']),
                         'Auth': myMainArgData})
            elif myLoginInfo and myLoginInfo.get('AccountStatus') == self.globaL._Global__LoginStatusPending:
                myValidLoginRetVal = "LoginError-004"                     
            else:
                myValidLoginRetVal = "LoginError-002" 
                ''' recording activity'''
                self.activity._Activity__logActivity(
                        {'EntityId':myLoginId, 'EntityType': 'Login', 
                         'ActivityType':self.globaL._Global__Internal, 
                         'Activity':' Invalid loginid [{entity}]'.
                                    format(entity=myLoginId),
                         'Auth': myMainArgData})
            #fi
            return myValidLoginRetVal

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def registerEntity(self, argRequestDict):
        '''
            argRequestDict = ['EntityType','MainArg']
        '''
        
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            myArgKey = ['MainArg']
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' extract entity type form mainArgument '''
            if ('EntityType' in myMainArgData['MainArg']['Auth']):
                '''Register entity '''
                if myMainArgData['MainArg']['Auth']['EntityType'] == self.globaL._Global__member:
                    # injecting type, this memebr type will be a member
                    myMainArgData['MainArg']['Main'].update({'Type':self.globaL._Global__member})
                    myEntityData = self.registerMember(myMainArgData['MainArg'])
                elif myMainArgData['MainArg']['Auth']['EntityType'] == self.globaL._Global__vendor:
                    myMemberData = self.registerVendor(myMainArgData)
                else:
                    raise com.uconnect.core.error.InvalidEntity('Invalid entity passed during registration [{entity}]'.format(entity=myMainArgData['EntityType'])) 
                #fi    
            else:
                raise com.uconnect.core.error.MissingArgumentValues('Key [EntityType] is missing from main argument arg[{arg}]'.format(arg=myMainArgData['MainArg']))
            #fi
            return myEntityData

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def registerMember(self,argRequestDict):
        ''' 
            Description:    Register a new member;
                            1.) Create a new Member
                            2.) Create a new Login
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            ['LoginId':'','Password':'', 'LoginType':'', 'DeviceType':'', 'DeviceOs':'', 'MacAddress':'','SessionId':'','AppVer':'',
                              'Main':{},'Address':{},'Contact':{}]
            usage:          <registerMember(<argReqRequestDict>)
            Return:         Json object
        '''
        try:
            ''' importing MemberBPS module here to avoid the error (importing module from each other) '''
            from com.uconnect.core.member import Member
            from com.uconnect.bps.memberBPS import MemberBPS
            memberBPS = MemberBPS()
            member = Member()

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.util.getCopy(argRequestDict)

            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))

            ''' declaring variables '''

            myArgKey = myMainArgKey = myAddressArgKey = myContactArgKey = []
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myAuthKey = ''
            myMemberId = ''

            ''' preparing arg key for validation'''
            myArgKey = ['Auth','Main','Address','Contact']
            myMainArgKey = self.util.buildKeysFromTemplate('Member','Main')
            myAddressArgKey = self.util.buildKeysFromTemplate('Member','Address')
            myAuthArgKey = self.util.buildKeysFromTemplate('Auth')
            ''' encrypt password '''
            myMainArgData['Auth']['Password'] = self.__genHashPassword({'Password':myMainArgData['Auth']['Password']})            
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' we dont need validation for contact, yet TBD ''
            myContactArgKey = self.util.buildKeysFromTemplate('Member','Contact')
            self.util.removeKeyFromList([])
            '''
            ''' validating arguments '''
            # Main Arg validation

            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # Member Main arg validation
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData['Main'], myMainArgKey, ['NickName'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # Member Address arg validation
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData['Address'], myAddressArgKey, ['Street','City','State','Country'])
            myArgValidation, myMissingKeys, myArgValMessage\
                    = self.util.valRequiredArg(myMainArgData['Address'], myAddressArgKey, \
                        ['Street','City','State','Country'])
            #print('Addres Validation',myArgValidation, myMissingKeys, myArgValMessage )
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # Member Contact arg validation
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData['Contact'], myContactArgKey)
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData['Contact'], myContactArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            # Auth arg validation
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData['Auth'], myAuthArgKey, ['ExpiryDate','AuthKey','EntityId','_id'])
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData['Auth'], myAuthArgKey, \
                        ['ExpiryDate','AuthKey','EntityId','_id'])
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Check if this login is already in use '''
            myLoginArgData = {'Auth':{'LoginId':myMainArgData['Auth']['LoginId']},'ResponseMode':self.globaL._Global__InternalRequest}
            myLoginInUseResult = self.isLoginInUse(myLoginArgData)
            #print('LoginStatus',myLoginInUseResult)
            if myLoginInUseResult['Status'] == self.globaL._Global__True:
                raise com.uconnect.core.error.InvalidLogin("Requested login [{login}] is already in use".\
                    format(login=myMainArgData['Auth']['LoginId']))
            elif myLoginInUseResult['Status'] == self.globaL._Global__Error:
                raise com.uconnect.core.error.InvalidLogin("An error [{loginerror}] occurred while validating login".\
                    format(loginerror=myLoginInUseResult))
            #fi

            ''' create a member '''
            myMemberData = {'Main':myMainArgData['Main'], 'Address':myMainArgData['Address'], 'Contact':myMainArgData['Contact']}
            myMemberData['Main'].update({'Type':'Member'})
            myMemberId = member._Member__createAMember(myMemberData)
            myMainArgData['Auth'].update({'EntityId':myMemberId})
            myMainArgData['Auth'].update({'EntityType':self.globaL._Global__member})

            ''' building auth dictionary '''
            myMainAuthArgData = {'Auth':self.util.getCopy(myMainArgData['Auth'])}

            ''' recording activity '''
            self.activity._Activity__logActivity(self.util.buildActivityArg(
                myMemberId,self.globaL._Global__member,self.globaL._Global__Internal,'Member [{member}] created'.
                format(member=myMemberId), myMainAuthArgData))

            ''' create login for this member '''
            myAuthKey = self.__createLogin(myMainAuthArgData)

            ''' Building response
            we got Auth key, we need to inject it to get this memeber information from database '''

            myMainAuthArgData['Auth'].update({'AuthKey':myAuthKey})

            self.activity._Activity__logActivity(self.util.buildActivityArg(
                myMemberId,self.globaL._Global__member, 'Internal',\
                'LoginId [{login}] and AuthKey [{authKey}] created for Member [{member}]'.\
                format(login=myMainAuthArgData['Auth']['LoginId'], member=myMemberId, authKey= myAuthKey),myMainAuthArgData))

            ''' getting member information from database '''
            myMemberData = memberBPS.getAMemberDetail(
                {'Auth':myMainAuthArgData['Auth'],'ResponseMode':self.globaL._Global__InternalRequest})
            
            #print(self.util.extr1stDocFromResultSets(myMemberData))
            
            if myMemberData:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            else:
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess, "Could not find member {member} information".format(member=myMemberId))
            #fi            

            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myMemberData )
            #myResponse['MyResponse']['Header']['Auth']['AuthKey'] = myAuthKey
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            if 'myMemberId' in locals():
                self.mongo.DeleteDoc(self.globaL._Global__memberColl,{'_id':myMemberId} )
            if 'myAuthKey' in locals() and myAuthKey:
                #print('myAuthKey',myAuthKey)
                self.mongo.DeleteDoc(self.globaL._Global__authColl,{'_id':ObjectId(str(myAuthKey))} )
            if 'myMainArgData' in locals():
                self.mongo.DeleteDoc(self.globaL._Global__loginColl, {'_id':myMainArgData['Auth']['LoginId']} )    
            #
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def validateCredential(self, argRequestDict):
        '''
            argRequestDict = {'LoginId':'','Password':'', 'LoginType':'','DeviceOs':'','SessionId'}
            This method is called externally
            Questions: EntityId and EntityType is passed, do we need this, should we send the entityid and entityype back???
              we need to clarify link here ? should we expect the entityid and entitytype to be passed
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi

            myArgKey = ['ResponseMode','Auth']
            myResponseData = {}
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)            

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            myMainAuthArgData = self.util.getCopy(myMainArgData)['Auth'] 
            myAuthArgKey = self.util.buildKeysFromTemplate('Auth')

            '''we need either LoginId/Auth's required argument '''
            if 'LoginId' in myMainAuthArgData and 'Password' in myMainAuthArgData:

                ''' validating auth arguments '''
                #myArgValidationResults = self.util.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','AuthKey'])
                myArgValidation, myMissingKeys, myArgValMessage = \
                        self.util.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','AuthKey'])
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
                #fi

                myValidateLoginStatus = self.__isValidLogin(myMainAuthArgData)

                if myValidateLoginStatus == self.globaL._Global__Success:
                    ''' we need to check if this device is 1st time used, if yes, we would need security code validation '''
                    ''' we need to return newAuthKey, EntityId and EntityType for this loginId '''
                    myLoginInfo = self.__getLoginInfo({'LoginId':myMainAuthArgData['LoginId']})

                    ''' injecting entitytype and entityid '''
                    myMainAuthArgData.update({'EntityId':myLoginInfo.get('EntityId')})
                    myMainAuthArgData.update({'EntityType':myLoginInfo.get('EntityType')})

                    myAuthKey = self.__createAuthentication(myMainAuthArgData)
                    myResponseData = {'AuthResponse':{'EntityId':myLoginInfo.get('EntityId'),'EntityType':myLoginInfo.get('EntityType'),'AuthKey':myAuthKey}}
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                else:
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess, myValidateLoginStatus + '; ' + self.util.getErrorCodeDescription(myValidateLoginStatus))
                #fi
            elif 'AuthKey' in myMainAuthArgData: 

                ''' validating auth arguments '''
                #myArgValidationResults = self.util.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','EntityType','LoginId','Password'])
                myArgValidation, myMissingKeys, myArgValMessage = \
                        self.util.valRequiredArg(myMainAuthArgData, myAuthArgKey,['ExpiryDate','EntityId','EntityType','LoginId','Password'])
                if not (myArgValidation):
                    raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
                #fi

                # checking if Authkey passed is a valid type of object id
                if not (ObjectId.is_valid(myMainArgData['AuthKey'])):
                    raise com.uconnect.error.InvalidAuthKey('Invalid Auth key [{auth}]'.format (auth=myMainArgData['AuthKey']))

                ''' perform authkey validation '''
                if self.__isValidAuthentication(myMainAuthArgData):
                    ''' we need to retrieve entityid and entitytype from Auth collection '''
                    myAuthResults = self.mongo.findDocument(self.globaL._Global__authColl, {'_id':ObjectId(str(myMainAuthArgData['AuthKey']))},{},True)
                    myAuthData =  self.util.extr1stDocFromResultSets(myAuthResults)
                    myResponseData = {'AuthResponse':{'EntityId':myAuthData.get('EntityId'),'EntityType':myAuthData.get('EntityType'),'AuthKey':str(myAuthData.get('_id'))}}
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                else:
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess,'Invalid LoginId/Password')                    
                #fi
            else:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, argument must be [{login}] or [{auth}]'.
                    formmat(login='[LoginID,Password,DeviceOs,DeviceType,SessionId,MacAddress,AppVer]',
                            auth='[AuthKey,DeviceOs,DeviceType,SessionId,MacAddress,AppVer]'))                
            #fi
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find',myResponseData)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse

    def isLoginInUse(self, argRequestDict):
        '''
            argRequestDict = {'LoginId'}
        '''
        try:

            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            ''' declaring/initializing variables '''
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myArgKey = ['Auth','ResponseMode']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' validating arguments '''
            myArgKey = ['LoginId']
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData['Auth'], myArgKey)
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData['Auth'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' Preparing value for login id'''
            myCriteria = {'_id': myMainArgData['Auth']['LoginId']}
            myProjection = {'_id':1}

            myResults = self.mongo.findDocument(self.globaL._Global__loginColl, myCriteria, myProjection, True)
            #print(myResults)
            myLoginData = self.util.extr1stDocFromResultSets(myResults)
            #print('login',myLoginData, myCriteria)

            if myLoginData and '_id' in myLoginData and (not (myLoginData['_id'] == None)) :
                # loginid found, its in use
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess,'Login [{login}] is already in use'.
                                        format(login=myMainArgData['Auth']['LoginId']))
                myRequestStatus.update({'Status':self.globaL._Global__True})
            else:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                myRequestStatus.update({'Status':self.globaL._Global__False})
                myRequestStatus.update({'Message':'Login [{login}] is not in use'.format(login=myMainArgData['Auth']['LoginId'])})
                #print('Login',myRequestStatus)
            #fi

            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find')
            #print('Login Response',myResponse)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myRequestStatus.update({'Status':self.globaL._Global__Error})
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse

    def __isValidSecDeliveryOptions(self, argRequestDict):
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            ''' declaring/initializing variables '''
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)
            myArgKey = ['ResponseMode','LoginId','DeliverTo','DeliveryMethod']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' get the entity id for this login '''
            myCriteria = {'_id':myMainArgData['LoginId']}
            myProjection = {'EntityType':1, 'EntityId':1}
            myEntityResult = self.mongo.findDocument(self.globaL._Global__loginColl, myCriteria, myProjection, True)

            ''' preparing the document for validation '''
            myEntityData = self.util.extr1stDocFromResultSets(myEntityResult)
            myEntityId = myEntityData['EntityId'] 
            myEntityType = myEntityData['EntityType'] 

            myCriteria = {'_id': myEntityId,'Contact.Method':myMainArgData['DeliveryMethod'], 'Contact.Value':myMainArgData['DeliverTo']}
            myProjection = {'Contact':1}
            if myEntityType == self.globaL._Global__member:
                myCollection = self.globaL._Global__memberColl
            else:
                pass
            #fi
            myContactResults = self.mongo.findDocument(myCollection, myCriteria, myProjection, True)
            myContactData = self.util.extr1stDocFromResultSets(myContactResults)
            #print('myContactData',myContactData)
            if myContactData:
                myValidDeliveryOptions = True
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            else:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess, 'Invalid Contact method options provided for security code delivery')
                myValidDeliveryOptions = False
            #fi             
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find',myValidDeliveryOptions)
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myRequestStatus.update({'Status':self.globaL._Global__Error})
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')
            return myResponse

    def __generateNewSecCode(self):
        return self.util.getRanddomNum(self.util.getDefaultSecCodeLength())

    def __persistNewSecCode(self, argRequestDict):
        
        try:
            mySecurityCodeData = self.util.getCopy(argRequestDict)
            # Need to delete old security code
            myDbResults = self.mongo.DeleteDoc(self.globaL._Global__securityCodeColl, {'LoginId':mySecurityCodeData['LoginId']})
            # Persist new security code
            #History
            myHistDbResults = self.mongo.InsertOneDoc(self.globaL._Global__securityCodeColl_Hist, mySecurityCodeData)                

            if myHistDbResults[self.globaL._Global__StatusKey] == self.globaL._Global__TrueStatus:
                # we need to inject _id for sec code hist collection into securitycode collection
                mySecCodeHistId = myHistDbResults['_id']
                mySecurityCodeData.update({'SecurityCodeHistId':mySecCodeHistId})
                myDbResults = self.mongo.InsertOneDoc(self.globaL._Global__securityCodeColl, mySecurityCodeData)
                # checking if previous db call was successful
                if not(myDbResults[self.globaL._Global__StatusKey] == self.globaL._Global__TrueStatus):
                    #rolling back security log generation
                    self.mongo.DeleteDoc(self.globaL._Global__securityCodeColl,{'_id':myDbResults['_id']})
                    self.mongo.DeleteDoc(self.globaL._Global__securityCodeColl_Hist,{'_id':mySecCodeHistId})
                #fi
            #fi                
            return myDbResults
        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            raise

    def genSecurityCode(self, argRequestDict):
        '''
            argRequestDict = {'LoginId'}
        '''
        try:
            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            #print('genSecurityCode', argRequestDict)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.util.getCopy(argRequestDict['Main'])
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            ''' declaring/initializing variables '''
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            myArgKey = ['SecurityCode','ResponseMode']

            ''' validating arguments '''
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' vlaidating main arguments '''
            myArgKey = ['LoginId','DeliveryMethod','DeliverTo']
            myArgValidationResults = self.util.valRequiredArg(myMainArgData['SecurityCode'], myArgKey)
            myArgValidation = self.util.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.util.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' checking if delivery options are valid for this request '''

            ''' Preparing value for Security code'''
            myDeliveryOptiosnArg = self.util.getCopy(myMainArgData['SecurityCode'])
            myDeliveryOptiosnArg['ResponseMode'] = self.globaL._Global__InternalRequest
            #if not (self.__isValidSecDeliveryOptions(myDeliveryOptiosnArg['SecurityCode'])):
            if not (self.__isValidSecDeliveryOptions(myDeliveryOptiosnArg)):
                raise com.uconnect.core.error.InvalidSecCodeDeliveryOptions('Delivery options [{delivery}] is not valid for login [{login}]'.
                    format(delivery=myMainArgData['SecurityCode']['DeliveryMethod'] + ' , ' + myMainArgData['SecurityCode']['DeliverTo'],
                           login=myMainArgData['SecurityCode']['LoginId']))
            #fi

            mySecurityCode = self.__generateNewSecCode()

            myInitSecurityArg = {
                        'LoginId':myMainArgData['SecurityCode']['LoginId'],
                        'SecurityCode':mySecurityCode,
                        'DeliveryMethod':myMainArgData['SecurityCode']['DeliveryMethod'],
                        'DeliverTo':myMainArgData['SecurityCode']['DeliverTo'] }

            mySecurityCodeData = self.__buildInitSecurityCodeData(myInitSecurityArg)
            myDbResults = self.__persistNewSecCode(mySecurityCodeData)
            #print('dbresult',myDbResults)
            if myDbResults[self.globaL._Global__StatusKey] == self.globaL._Global__TrueStatus:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                #logging activity
                self.activity._Activity__logActivity(
                    {'EntityId':mySecurityCodeData['LoginId'], 'EntityType':'LoginId', 
                     'ActivityType':self.globaL._Global__Internal, 
                     'Activity':'Generating new security code [{sec}]'.format(sec=mySecurityCodeData['SecurityCode'])})
            else:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess)
                #raise com.connect.core.error.DBError('Security code creation failed !!')
            #fi

            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myDbResults,'Insert')
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse

    def validateSecurityCode(self, argRequestDict):
        '''
            Validate security code, security code must be in security code collection and it must have status 'Pending'
            if sec code is not found, either its expired or it doesnt exists. Check in hist collection to see if
            it exists this means it expired, if not found in hist coll, its invalid security code 
        '''
        try:
            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.util.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.util.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            ''' declaring/initializing variables '''
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            ''' validating arguments '''
            myArgKey = ['SecurityCode','ResponseMode']
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation, myMissingKeys, myArgValMessage = self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' validating argument passed in 'Main'dict '''
            myArgKey = ['LoginId','SecurityCode']
            #myArgValidationResults = self.util.valRequiredArg(myMainArgData['SecurityCode'], myArgKey)
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData['SecurityCode'], myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi

            ''' validating if security code belongs to this login is still valid '''
            #print('myMainArgData',myMainArgData)
            myCriteria = {'LoginId':myMainArgData['SecurityCode']['LoginId'], \
                            'SecurityCode': int(myMainArgData['SecurityCode']['SecurityCode'])}
            myProjection = {'SecurityCode':1} 
            mySecCodeValResults = self.mongo.findDocument(\
                        self.globaL._Global__securityCodeColl,myCriteria, myProjection, True)
            if self.util.extrStatusFromResultSets(mySecCodeValResults) == self.globaL._Global__OkStatus:
                mySecCodeValData = self.util.extr1stDocFromResultSets(mySecCodeValResults)
            else:
                mySecCodeValData = ''
            #fi
            #print('val sec',mySecCodeValResults)

            if not(mySecCodeValData):
                raise com.uconnect.core.error.InvalidSecurityCode('Security code [{seccode}] is invalid for login [{login}]'.
                    format(seccode=myMainArgData['SecurityCode']['SecurityCode'], login=myMainArgData['SecurityCode']['LoginId']))
            #fi

            ''' we got valid security code, will update the login status as 'Open' and update the status as this security 
            code validated '''

            #updating login account status to Open
            myLoginCriteria = {'_id': myMainArgData['SecurityCode']['LoginId']}
            myLoginUpdateData = {'AccountStatus':self.globaL._Global__LoginStatusOpen}
            self.mongo.UpdateDoc(self.globaL._Global__loginColl, myLoginCriteria, myLoginUpdateData, 'set' )

            # updating SecurityCodeHist, we need to have _id from history to be populate in security code collection

            #get the securityhistory code _id 
            myCriteria = {'LoginId':myMainArgData['SecurityCode']['LoginId']}
            myProjection = {'SecurityCodeHistId':1}            
            mySecurityCodeResults = self.mongo.findDocument(\
                                        self.globaL._Global__securityCodeColl,myCriteria,myProjection,True)
            mySecurityCodeHistId = self.util.extr1stDocFromResultSets(mySecurityCodeResults)
            
            # update sec code hist collection as validated
            myCriteria={'_id':mySecurityCodeHistId['SecurityCodeHistId']}
            mySecCodeHistUpdateData = {'Status':'Validated','ValidateDate':datetime.datetime.utcnow()}
            self.mongo.UpdateDoc(\
                self.globaL._Global__securityCodeColl_Hist, myCriteria, mySecCodeHistUpdateData, 'set' )

            # Delete data from Sec code coll
            myCriteria = {'LoginId': myMainArgData['SecurityCode']['LoginId'], }
            self.mongo.DeleteDoc(self.globaL._Global__securityCodeColl, myCriteria)

            self.activity._Activity__logActivity(
                {'EntityId':myMainArgData['SecurityCode']['LoginId'], 'EntityType':'LoginId', 
                 'ActivityType':self.globaL._Global__Internal,                 
                 'Activity':'Ssecurity code [{sec}] validated'.format(sec=myMainArgData['SecurityCode']['SecurityCode'])})

            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Find')
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus,'Error')            
            return myResponse
