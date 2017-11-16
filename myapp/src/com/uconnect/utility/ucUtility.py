import os,sys,traceback,json,datetime,copy,random, pytz, com.uconnect.core.error

from geopy.geocoders import Nominatim
from geopy.distance import *
from com.uconnect.core.singleton import Singleton
from com.uconnect.utility.ucLogging import logging
from com.uconnect.core.infra import Environment
from com.uconnect.core.globals import Global

myLogger = logging.getLogger('uConnect')

# Python 3:
#Removed dict.iteritems(), dict.iterkeys(), and dict.itervalues().
#Instead: use dict.items(), dict.keys(), and dict.values() respectively.@Singleton
#@Singleton
class Utility(object, metaclass=Singleton):

    def __init__(self):
        self.env = Environment()
        self.globaL = Global()
        self.geolocator = Nominatim()
        self.myClass = self.__class__.__name__
        self.myPythonFile = os.path.basename(__file__)

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def isDict(self, argDict):
        #print(self.myClass)
        #print(sys._getframe().f_code.co_name)
        #print(self.myPythonFile)

        try:
            if isinstance(argDict,dict): 
                return True
            else:
                return False
        except Exception as error:
            return False
        finally:
            pass
        '''
        another way to check if passed argument is dict
        if (type(argDict)) == type({})):
            return True
        else:
            reture False
        '''

    def isList(self, argValue):
        try:
            if isinstance(argValue,list): 
                return True
            else:
                return False
        except Exception as error:
            return False
        finally:
            pass

    def removeEmptyValueKeyFromDict(self, argDict):
        # removes key if it has empty or 0 value
        myMainArgData = self.getCopy(argDict)
        return dict([(key,value) for key,value in myMainArgData.items() if (value)])

    def removeEmptyValueFromList(self, argList):
        # removes key if it has empty or 0 value
        myMainArgData = self.getCopy(argList)
        return list([(value) for value in myMainArgData if (value)])

    def buildMemberTag(self, argList):
        myMainArgData = self.getCopy(argList)
        return removeEmptyValueFromList(myMainArgData)

    ''' ????, not sure if below code is needed '''
    def convList2Dict(self, argValueList):
        ''' Duplicate value will be removed if found in list '''
        myDict = {}
        for myList in argValueList:
            myDict.update({myList['Key'] : myList['Value']})

        return myDict

    def findKeyInListDict(self, argList, argKey, argVal):
        return [i for i, x in enumerate(argList) if (argKey in x) and ( x[argKey] == argVal ) ]

    def getAllKeysFromDict(self, argDict):
        myKeyList = []
        for key,value in argDict.items():
            myKeyList.append(key)
        return myKeyList

    def valBPSArguments(self, argRequest):
        ''' 
            Description:    Validate argument passed as json/dict to BPS processes, returns True or False
            argReuest:      Dictionary object must be in following format
                            {"Request":
                                {"Header":
                                    {"ScreenId":"2001","ActionId":"100","Page":""},
                                 "MainArg":
                                    {"MemberId":"100001"},
                                 "Auth":
                                    {}
                                }
                            }            
            usage:          ( valBPSArguments(<dictionary object>)
        '''
        #print(type(argRequest))
        #print(argRequest)

        ''' we should match the layout of the argument with template defined in globals.py '''

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')
        myModuleLogger.debug("validating dict [{dict}] argument ".format(dict=argRequest))
        if (len(argRequest['Request']['Header']) == 0 ):
            myModuleLogger.error("Header key is empty [{arg}], expecting screenid, acrtion id (page# optional) !!!".format(arg=argRequest))
            return False
        elif (len(argRequest['Request']['MainArg']) == 0 ):
            myModuleLogger.error("MainArg key is empty [{arg}], expecting nonempty value) !!!".format(arg=argRequest))
            return False
        elif (len(argRequest['Request']['MainArg']) == 0 ):
            myModuleLogger.error("Main argument [{arg}] is empty, expecting valid argumen !!!) [{arg}]".format(arg=argRequest))
            return False

        myModuleLogger.debug("Validation completed successfully")
        return True

    def valRequiredArg(self, argRequestDict, argKeyList, argIgnoreList = None):
        ''' 
            Description:    Validate argument, all argument listed in argKeyList must have a value in argRequest. This method is called internally
            argReuest:      Dictionary object must be in following format
            usage:          ( valRequiredArg(<dictionary object>, <keyList>)
        '''

        isValidArgument = False
        myMissingOrEmptyKeyList = []

        ''' lets remove the ignore key from argKeyList, if ignore list is passed '''
        myArgKeyList = copy.deepcopy(argKeyList)
        myIgnoredArgKeyList = copy.deepcopy(argIgnoreList)
        myMainArgData = copy.deepcopy(argRequestDict)
        myValidationMessage = ''

        # we need to remove all the argument which is not part of validation and if its passed
        myRemoveKey = list(set(myMainArgData.keys()) - set(myArgKeyList))
        self.removeKeyFromDict(myMainArgData, myRemoveKey)
        
        # we need to remove ignored keys from argRequestDict

        if not(myIgnoredArgKeyList == None):
            #print('IgnoredKeyList is not empty',myArgKeyList, myIgnoredArgKeyList)
            self.removeKeyFromList(myArgKeyList, myIgnoredArgKeyList)
            self.removeKeyFromDict(myMainArgData, myIgnoredArgKeyList)
            #print('IgnoredKeyList removed',myArgKeyList)
        #fi

        # check if all key in dictionary
        if all(key in myMainArgData for key in myArgKeyList):
            # check if any key in dict has None or empty value
            if myMainArgData == dict ((key, values) for key, values in myMainArgData.items() if values):
                isValidArgument = True
            else:
                for key,val in myMainArgData.items():
                    if not val:
                        myMissingOrEmptyKeyList.append(key)
                    #fi
                #end for loop
                myValidationMessage = 'Arg Validation; empty key(s) ' + str(myMissingOrEmptyKeyList)
            #fi
        else:
            #need to find out which key is missing
            for key in myArgKeyList:
                if not key in myMainArgData:
                    myMissingOrEmptyKeyList.append(key)
                #fi
            #end for loop
            myValidationMessage = 'Arg Validation; missing key(s) ' + str(myMissingOrEmptyKeyList)
        #fi
        # checking if responsemode key has valid value ('I','E')
        if isValidArgument and 'ResponseMode' in myMainArgData:
            if not(myMainArgData['ResponseMode'] in self.globaL._Global__ValidResponseModeLsit):
                isValidArgument = False
                myValidationMessage = 'Arg Validation; ResponseMode key has invalid value, expecting [' +\
                  str(self.globaL._Global__ValidResponseModeLsit) + ']'
        #fi
        return isValidArgument, myMissingOrEmptyKeyList, myValidationMessage 

    def valResponseMode(self, argResponseMode):
        if len(argResponseMode) == 1:
            return argResponseMode in self.globaL._Global__ValidResponseModeLsit
        else:
            return False

        
    def getCopy(self, argDictList):
        return copy.deepcopy(argDictList)

    def isAllArgumentsValid(self,*args):
        ''' 
            Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
            *args:          All argumnet seperated by comma, any # of arguments can be passed
            usage:          ( isAllArgumentsValid(<*args>)
        '''
        return (all (args))

    def extractLogError(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #myErrorMessage = repr(traceback.format_exception(exc_type, exc_value, exc_traceback,limit=1))
        #myErrorMessage = repr(exc_type, exc_value, exc_traceback)
        #myErrorMessage = traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        '''
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print("*** print_exception:")
        # exc_type below is ignored on 3.5 and later
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        print("*** print_exc:")
        traceback.print_exc(limit=2, file=sys.stdout)
        print("*** format_exc, first and last line:")
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[0])
        print(formatted_lines[-1])
        print("*** format_exception:")
        # exc_type below is ignored on 3.5 and later
        print(repr(traceback.format_exception(exc_type, exc_value,
                                              exc_traceback)))
        print("*** extract_tb:")
        print(repr(traceback.extract_tb(exc_traceback)))
        print("*** format_tb:")
        print(repr(traceback.format_tb(exc_traceback)))
        print("*** tb_lineno:", exc_traceback.tb_lineno)
        '''
        myErrorMessage = traceback.format_exc().splitlines()
        #myErrorMessage = traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2)
        #self.myModuleLogger.error('Error [{err}] occurred'.format(err=myErrorMessage))

        return self.getRequestStatus(\
                self.globaL._Global__UnSuccess, repr(exc_value), None, myErrorMessage)

    def isValidZipCode(self, argZipCode):
        ''' 
            Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
            Arguments:      Zipcode
            usage:          ( isValidZipCode(<zipciode>)
        '''
        return argZipCode in self.env._Environment__zipCodeData

    def findPagingValue(self, argTotDocuments, argPageSize, argRequestedPage = None):
        ''' 
            Description:    Build paging information needed for summary section of data being returned
            Arguments:      argTotDocuments:    Total docments
                            argPageSize:        Page size (total documents in a page)
                            argRequestedPage:   Requested Page
            usage:          ( findPagingValue(<argTotDocuments, argPageSize, argRequestedPage>)
        '''

        if argRequestedPage == None:
            argRequestedPage = 1

        if argTotDocuments <=  argPageSize:
            myTotPages = 1
        else:
            myTotPages = argTotDocuments / argPageSize 
             
        #if requested page is out of bound display message "out of bound"

        if ( argRequestedPage > myTotPages ):
            myStatus = "ERROR: Out of bound page request"
            #myDisplay = "0"
        else:
            myStatus = "OK"
            #myDisplay = str( (argRequestedPage * argPageSize) +1 ) + " to " + str(((argRequestedPage * argPageSize) + 1) + argPageSize)

        return myStatus, myTotPages

    def isKeyInDict(self, argDict, argKeyName):
        ''' 
            Description:    Find if a given key present in dictionary
            Arguments:      argDict:            Dcit in which key need to be searched for 
                                                    (if nested dict, pass the dict key value in which search need to be made)
                            argKeyName:        Key name which need to be searched in this dictionary
            usage:          ( isKeyInDict(<argDict, argKeyName>)
        '''
        return argKeyName in argDict

    def isEmptyKey(self, argDict, argKeyName):
        ''' 
            Description:    Check if a key in dict is empty
            Arguments:      argDict:            Dcit in which key need to be searched for 
                                                    (if nested dict, pass the dict key value in which search need to be made)
                            argKeyName:        Key name which need to be searched in this dictionary
            usage:          ( isKeyInDict(<argDict, argKeyName>)
        '''
        return (not argKeyName[argDict])

    def getCurrentIsoDate(self, argDict, argKeyName):
        myIsoDateString = request.GET.isoDateString
        myIsoDate = datetime.datetime.strptime(myIsoDateString, '%Y-%m-%dT%H:%M:%S.%fZ')

    def getCreateStatus(self,argCreateResult):
        myCreateStatus = self.globaL._Global__UnSuccess
        if argCreateResult and ('_id' in argCreateResult):
            myCreateStatus = self.globaL._Global__Success

        return myCreateStatus

    def getUpdateStatus(self,argUdateResult):
        myUpdateStatus = self.globaL._Global__UnSuccess
        if argUdateResult and ('modified' in argUdateResult) and (int(argUdateResult['modified'])) > 0:
            myUpdateStatus = self.globaL._Global__Success
        
        return myUpdateStatus

    def extractValFromTuple(self, argTuple, argPosition):
        if len(argTuple) >= int(argPosition):
            return argTuple[argPosition]
        else:
            return None
        #fi

    def extractAllFromReq(self, argRequestDict):
        ''' 
            Description:    Extracts all argument passed to request
            Arguments:      Request json dict data 
            usage:          ( extractRequest(<argRequestDict>)
        '''
        myStatus = myScreenId = myActionId = myRequestData = ''

        if self.isDict(argRequestDict):
            myStatus = self.globaL._Global__Success
            myScreenId = argRequestDict['Request']['Header']['ScreenId']
            myActionId = argRequestDict['Request']['Header']['ActionId']
            myRequestData = argRequestDict['Request']['MainArg']
        else:
            myStatus = self.globaL._Global__Error

        return myStatus, myScreenId, myActionId, myRequestData 

    def extMainArgFromReq(self, argRequestDict):
        ''' 
            Description:    Extracts Main Argument passed to request
            Arguments:      Request json dict data 
            usage:          ( extractRequest(<argRequestDict>)
        '''
        return self.extractAllFromReq(argRequestDict)[3]

    def builInternalRequestDict(self, argRequestDict):
        ''' 
            Description:    Build request data for internal purpose
            Arguments:      Request json dict data, will use screenId:99999, ActionId: 99999
            usage:          ( builRequestData(<argRequestDict>)
        '''
        myRequestData = self.getTemplateCopy(self.globaL._Global__RequestTemplate)
        #print ('Request:', myRequestData)
        #print ('Internal Scr:', self.globaL._Global__InternalScreenId)
        myRequestData["Request"]["Header"]["ScreenId"] = self.globaL._Global__InternalScreenId
        myRequestData["Request"]["Header"]["ActionId"] = self.globaL._Global__InternalActionId 
        myRequestData["Request"]["Header"]["Page"] = self.globaL._Global__InternalPage
        myRequestData["Request"]["MainArg"] = argRequestDict["Data"]

        return myRequestData

    def buildInitHistData(self):
        ''' building initial history data for a given collection '''
        #myHistoryData = self.env.defaultsData["History"]
        myHistoryData = self.getTemplateCopy(self.globaL._Global__HistoryTemplate)

        myHistoryData["InitChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["InitChange"]["Message"]="Initial creation"            
        myHistoryData["LastChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["LastChange"]["Message"]="Initial creation"            
        
        return myHistoryData

    def buildActivityArg(self,argEntityId, argEntityType, argActivityType, argActivity, argAuth=None):

        myActivityLogData = self.getTemplateCopy(self.globaL._Global__activityLogColl)

        myActivityLogData["EntityType"]=argEntityType
        myActivityLogData["EntityId"]=argEntityId            
        myActivityLogData["ActivityType"]=argActivityType
        myActivityLogData["Activity"]=argActivity
        myActivityLogData["Auth"]=argAuth            
        self.removeKeyFromDict(myActivityLogData, ['Acknowledged','ActivityDate'])
        return myActivityLogData

    def getRequestStatus(self, argStatus, argStatusMessage = None, argData = None, argTraceBack = None):
        myRequestStatus = self.getCopy(self.globaL._Global__RequestStatus)
        if argStatus:
            myRequestStatus.update({'Status' :argStatus})
        if argStatusMessage:
            myRequestStatus.update({'Message' : argStatusMessage})
        else:
            myRequestStatus.update({'Message' : argStatus})
        #fi
        if argData:
            myRequestStatus.update({'Data' : argData})
        #fi
        if argTraceBack:
            myRequestStatus.update({'Traceback' : argTraceBack}) 
        #fi
        return myRequestStatus

    def buildResponseData(self, argResponseMode, argResultStatus, argResultType, argResultData = None):
       
        ''' if this is internal request, we should not built the response, response will be built by mehtod whcih
        was called externally     '''

        if (argResponseMode == self.globaL._Global__InternalRequest):
            if argResultData:
                return argResultData
            else:
                return argResultStatus
            #fi
        #fi

        #myResponseData = self.env.getTemplateCopy(self.globaL._ResponseTemplate)
        myResponseData = self.getTemplateCopy(self.globaL._Global__ResponseTemplate)
        #print("Response",myResponseData)
        myData = argResultData

        if (argResultType == 'Update'):
            myResponseStatus = self.getUpdateStatus(argResultStatus)
            myResponseData['MyResponse']['Header']['Status'] = myResponseStatus
            myResponseData['MyResponse']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Insert'):
            myResponseStatus = self.getCreateStatus(argResultStatus)
            myResponseData['MyResponse']['Header']['Status'] = myResponseStatus
            myResponseData['MyResponse']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Find'):
            myResponseData['MyResponse']['Header']['Status'] = argResultStatus['Status']
            myResponseData['MyResponse']['Header']['Message'] = argResultStatus['Message']
            myResponseData['MyResponse']['Header']['Traceback'] = argResultStatus['Traceback']
            #myData = argResult
        elif (argResultType == 'Error'):
            #print("Success",self.globaL._Global__Success)
            myResponseData['MyResponse']['Header']['Status'] = argResultStatus['Status']
            myResponseData['MyResponse']['Header']['Message'] = argResultStatus['Message']
            myResponseData['MyResponse']['Header']['Traceback'] = argResultStatus['Traceback']
            myData = []

        #print('util 1',myResponseData)
        ''' if data element passed, we will copy the "Data" to "Data" section, "Data.Summary" to "Header.Summary" secton'''
        try:
            # if myData is not iterable, exception will be raised, will ignore the exception 
            if (myData) and (self.globaL._Global__DataKey in myData) and (myData[self.globaL._Global__DataKey]):
                myResponseData['MyResponse'][self.globaL._Global__DataKey] = myData[self.globaL._Global__DataKey]
                if (self.globaL._Global__SummaryKey in myData) and (myData[self.globaL._Global__SummaryKey]):
                    myResponseData['MyResponse']['Header'][self.globaL._Global__SummaryKey]= myData[self.globaL._Global__SummaryKey]    
            elif (myData) and (self.globaL._Global__DataKey not in myData):
                ''' we got data but "data" key is missing '''
                if self.isDict:
                    myResponseData['MyResponse'][self.globaL._Global__DataKey] = [myData]
                else:
                    myResponseData['MyResponse'][self.globaL._Global__DataKey] = myData
                #fi
            #fi                    
        except TypeError:
            pass
        #print('util 2',myResponseData)
        return myResponseData 

    def extrAllDocFromResultSets(self, argResultSets):
        if (self.globaL._Global__DataKey in argResultSets) and (argResultSets[self.globaL._Global__DataKey]):
            return argResultSets[self.globaL._Global__DataKey]
        else:
            return None

    def extr1stDocFromResultSets(self, argResultSets):
        if (self.globaL._Global__DataKey in argResultSets) and (argResultSets[self.globaL._Global__DataKey]):
            return argResultSets[self.globaL._Global__DataKey][0]
        else:
            return None

    def extrSummFromResultSets(self, argResultSets):
        if self.globaL._Global__SummaryKey in argResultSets:
            return argResultSets[self.globaL._Global__SummaryKey]
        else:
            return None

    def extrStatusFromResultSets(self, argResultSets):
        if (self.globaL._Global__StatusKey in argResultSets[self.globaL._Global__SummaryKey]):
            return argResultSets[self.globaL._Global__SummaryKey][self.globaL._Global__StatusKey]
        else:
            return None

    def whoAmI(self):
        ''' return callers method/function anme and from line# call is made'''
        caller = sys._getframe(1).f_code.co_name
        caller_linenum = sys._getframe(1).f_lineno
        return caller

    def buildKeysFromTemplate(self, argTemplateName, argBlockName = None):
        # get a templaye copy for a given collection
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')
            myEmptyTemplate = self.getTemplateCopy(argTemplateName)
            #print(myEmptyTemplate)
            if not (argBlockName == None) and argBlockName in myEmptyTemplate:
                myEmptyTemplate = myEmptyTemplate[argBlockName]
            
            ## lets build the keys
            myAllKeys = []
            for myKey in myEmptyTemplate:
                myAllKeys.append(myKey)

            return myAllKeys

        except Exception as error:
            myModuleLogger.exception('An error [{error}] occurred'.format(error=error.message))
            raise

    def buildAuth(self, argLoginId, argLoginType, argDeviceType, argDeviceOs, argMacAddress, argSessionId, argEntityType, argEntityId,argAppVer):
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')            
            myArgKey = ['LoginId','LoginType','DeviceType','DeviceOs','MacAddress','SessionId','EntityType','EntityId','AppVer']
            myFrame = inspect.currentframe()
            myAllArgs, _, _, myValues = inspect.getargvalues(myFrame)
            for myArg in myAllArgs:
                if self.isEmptyKey(myValues[myArg]):
                    raise com.uconnect.error.MissingArg('Argument [{arg}] is empty !!!'.format(arg=myArg))

            myAuth = {
                'LoginId':argLoginId,
                'LoginType':argLoginType,
                'DeviceType':argDeviceType,
                'DeviceOs':argDeviceOs,
                'MacAddress':argMacAddress,
                'SessionId':argSessionId,
                'EntityType':argEntityType,
                'EntityId':argEntityId,
                'AppVer':argAppVer}
            return myAuth
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise

    def getNonEmptyKeyFromDict(self, argRequestDict):
        ''' return all non empty key from dictionary, passed argument is not changed'''
        #return dict ((k,v) for k, v in argRequestDict.iteritems() if v) ### Iteritems has been changed to items
        return dict ((k,v) for k, v in argRequestDict.items() if v)
    def isAnyKeyInDict(self, argKeyList, argDict):
        # check if any of the key value from List present in keys in dictionnary
        return any(key in argKeyList for key in argDict.keys())

    def removeKeyFromList(self, argRequestList, argRemoveKeyList):
        ''' remove key(s) from list '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestList: 
                argRequestList.remove(myKey)

        return argRequestList

    def removeKeyFromDict(self, argRequestDict, argRemoveKeyList):
        ''' remove key(s) from Dict '''
        for myKey in argRemoveKeyList:
            if myKey in argRequestDict:
                del argRequestDict[myKey]

        return argRequestDict

    ''' Member Utility '''

    def getConnStatus4Action(self, argAction, argActionBy):
        '''
            we dont need auth validation since we dont have a way to find this request for which memberid
        '''

        myAllowedConnection = self.globaL._Global__ConnectionStatus.keys()

        ''' validating arguments '''
        if (not argAction) or (not argActionBy) :
            raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, got null expecting values arg[{arg}]'.
                format(arg=argAction + ',' + argActionBy))

        ''' we need to validate if right action and actionby key is passed'''
        if not(argAction in myAllowedConnection):
            raise com.uconnect.core.error.MissingArgumentValues('Action key must have either on of this value {expectVal}, got [{arg}] '.
                format(expectVal=myAllowedConnection, arg=argAction))

        if not(argActionBy in self.globaL._Global__ConnectionStatus.get(argAction).keys()):
            raise com.uconnect.core.error.MissingArgumentValues('ActionBy key must have either one of this value [{expectVal}], got [{arg}] '.
                format(expectVal=self.globaL._Global__ConnectionStatus.get(argAction).keys(),
                       arg=argActionBy))

        return self.globaL._Global__ConnectionStatus.get(argAction).get(argActionBy)


    def getErrorCodeDescription(self, argErrorCode):
        myErrorDescription = ''
        if argErrorCode in self.env._Environment__errorCodesData:
            myErrorDescription = self.env._Environment__errorCodesData.get(argErrorCode)    

        #print(argErrorCode,self.env._Environment__errorCodesData,myErrorDescription)
        return myErrorDescription
    ''' Security Utility '''

    def getTemplateCopy(self, argTemplate):
        ''' Returns a copy of a template for an entity defined in template.json; For e.g. Member/Group/Vendor/History '''

        myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')
        myModuleLogger.debug("Argument [{arg}] received ".format(arg=argTemplate))

        try:

          if argTemplate in self.env._Environment__templateData:
            return copy.deepcopy(self.env._Environment__templateData[argTemplate])
          else:
            raise com.uconnect.core.error.InvalidTemplate('Template [{template}] is missing in template repository !!! '.format(template=argTemplate))

        except com.uconnect.core.error.InvalidTemplate as error:
            myModuleLogger.error("InvalidTemplateError, [{error}]".format(error=error.errorMsg))
            raise error     
        except Exception as error:
           myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
           raise
    def getAuthValidDuration(self):
        return self.env.AuthValidDuration

    def getExclColl4Id(self):
        return self.env.exclColl4Id
    def getMaxPageSize(self):
        return self.env.maxPageSize

    def getAddressCityState(self,argZipCode):

        try:
            if argZipCode in self.env._Environment__zipCodeData:
                return self.env._Environment__zipCodeData[argZipCode]['City'], self.env._Environment__zipCodeData[argZipCode]['State'] 
            else:
                raise com.uconnect.core.error.InvalidZipCode('Invalid Zipcode {zipcode} !!!'.format(zipcode = argZipCode))
        except Exception as error:
            #myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
            raise

    def getModuleClassMethod(self,argScreenId, argActionId):
        try:
            #myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')
            #myModuleLogger.debug("Argument(s) [{arg}] received ".format(arg=(argScreenId + ',' + argActionId)))
            if (argScreenId in self.env._Environment__factoryMetaData) and (argActionId in self.env._Environment__factoryMetaData[argScreenId]):
                myLibrary = self.env._Environment__factoryMetaData[argScreenId][argActionId]['BPS']['Module']
                myClass   = self.env._Environment__factoryMetaData[argScreenId][argActionId]['BPS']['Class']
                myMethod  = self.env._Environment__factoryMetaData[argScreenId][argActionId]['BPS']['Method']
                return myLibrary, myClass, myMethod 
            else:
                raise com.uconnect.core.error.InvalidScreenAction('Invalid Screen/Action Id [{screen}],[{action}] !!!'.format(screen = argScreenId, action = argActionId))
        except Exception as error:
            #myModuleLogger.error('Error, an error occurred [{error}]'.format(error=error.message))
            raise

    def getConnTemplateCopy(self, argConnectionType):
        ''' Returns a copy of Member template from template.json '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')
            #myModuleLogger.debug("Argument [{arg}] received ".format(arg=argConnectionType))

            if argConnectionType in self.env._Environment__templateData['Connections']:
                return copy.deepcopy(self.env._Environment__templateData['Connections'][argConnectionType])
            else:
                raise com.uconnect.core.error.InvalidConnectionType('Connection type [{connType}] is missing in template repository !!! '.format(connType=argConnectionType))
        except Exception as error:
            #myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
            raise error

    # Security utility

    def getDefaultSecCodeLength(self):
        #print (self.env.SecurityCodeLength)
        return self.env.SecurityCodeLength

    def getRanddomNum(self, argNumLength):
        #print(argNumLength)
        if argNumLength == None: return None
        myLowerBound = 10**(argNumLength-1)
        myUpperBound = 10**argNumLength-1
        return random.randint(myLowerBound, myUpperBound)

    # Date time function utility

    def isValidDate(self, dateArg, formatArg):
        try:
            if isinstance(dateArg, datetime.datetime):
                return True
            if datetime.datetime.strptime(dateArg,formatArg):
                return True
        except ValueError as err:
            print(sys.exc_info())
            raise ValueError('Invalid Date Format')
        except Exception as err:
            print(sys.exc_info())
            return False

    def getTimeZone(self, argtz):
        try:
            if self.isValidTZ(argtz):
                timeZone = pytz.timezone(argtz)
                return timeZone
            else:
                return None
        except Exception as err:
            return None

    def isValidTZ(self, argTZ):
        return argTZ in pytz.all_timezones

    def getAllValidTimeZone(self):
        return pytz.all_timezones

    def convertStr2Date(self, dateStrArg, dateStrFormat, sourceTZ, targetTZ='UTC'):
        '''
        Description: Format date into a time zone, expected date format is 'YYYY-MM-DD HH24:MI:SS'
        '''
        try:
            #myDateFormat = '%Y-%m-%d %H:%M:%S'
            if isinstance(dateStrArg,str) and self.isValidDate(dateStrArg,dateStrFormat):
                mySourceTimeZone = self.getTimeZone(sourceTZ)
                myTargetTimeZone = self.getTimeZone(targetTZ)
                if mySourceTimeZone and myTargetTimeZone:
                    #print(mySourceTimeZone, myTargetTimeZone)
                    mydate = datetime.datetime.strptime(dateStrArg,dateStrFormat)
                    #converting date to source time zone
                    mySrcTZDate = mySourceTimeZone.localize(datetime.datetime.strptime(dateStrArg,dateStrFormat))
                    myTargetTZDate = mySrcTZDate.astimezone(myTargetTimeZone)
                    #myDateSrcTZ = pytz.datetime.datetime.astimezone(myDate,mySourceTimeZone)
                    #mydateTrgTZ =  datetime.datetime.astimezone(myDate,myTargetTimeZone)
                    #myDateSrcTZ = mySourceTimeZone.localize(myDate)
                    #myDateTrgTZ = myTargetTimeZone.localize(myDate)
                    #print(myDateSrcTZ, mydateTrgTZ)            
                    #print('Date: {date}, timezone: {tz}'.format(date=mydate,tz=mydate.tzname()))
                    return myTargetTZDate
                else:
                    return None
            else:
                return None
        except Exception as err:
            self.extractLogError()
            raise

    def getTimeFromDate(self, dateArg):
        '''
        return time in tuple format from a given date object
        '''
        return dateArg.time()
        
    def addTime2Date(self, dateArg, secsArg = 0, minutesArg = 0, daysArg = 0):
        '''
        Descrition: Add time to an existing date. date must be an object of datetime
        dateArg     : Date object of datetime
        secsArg     : Seconds to add to date, drfault is 0
        minsArg     : Minutes to add to date, drfault is 0
        daysArg     : Days to add to date, drfault is 0

        addTime2Date(date,10,5,1) --> Add 1 day, 5 minutes and 10 seconds to date

        '''
        if isinstance(dateArg, datetime.datetime):
            return dateArg + datetime.timedelta(days = daysArg, seconds = secsArg, minutes = minutesArg)
    '''
    def getCurrentDateTimeTZ(self, tzArg = self.globaL._Global__currentTZ):
        myCurrentDateTime = datetime.datetime.now()
        return myCurrentDateTime.astimezone(pytz.timezone(tzArg))
    '''
    def getCurrentDateTimeTZ(self):
        return datetime.datetime.now()

    ### Dictionary utils
    def copyKeyValuesFromTo(self, argKeyList, argSourceDict, argTargetDict):
        '''
        Copy Key value as stated in argKeyList from argSourceDict to argTargetDict
        '''
        for key in argKeyList:
            if key in argSourceDict:
                argTargetDict.update({key: argSourceDict[key]})

    def copyDictFromTo(self, argSourceDict, argTargetDict):
        '''
        Copy Key value as stated in argKeyList from argSourceDict to argTargetDict, if source has any nested dict/list that will be overwritten as well
        '''
        argTargetDict.update(argTargetDict)

    ### GEO ...
    def getGeoLocation(self,argPlace):
        '''
        will return address as a tuple of a given Place/Zipcode/Landmark/City
        '''
        location = self.geolocator.geocode(argPlace)
        #print(location,argPlace)
        if location:
            myAddress = location.address.split(',')
            return tuple(myAddress)
        else:
            raise ValueError('Invalid location [{place}]'.format(place = argPlace))

    def getGeoCodeForAnAddress(self, argAddress):
        '''
        will return GEO co ordinates of an address (address can be a valida street address or zipcode) a tuple of a given zipcode
        '''
        location = self.geolocator.geocode(argAddress)
        if location:
            return tuple([location.latitude, location.longitude])
        else:
            raise ValueError ('Address [{add}] not found'.format(add = argAddress))

    def getAddressForGeoCode(self, argLatitude, argLongitude):
        '''
        will return GEO co ordinates of an address (address can be a valida street address or zipcode) a tuple of a given zipcode
        '''
        # we need to pass longitude and latitude as a string seperated by comma as valid point
        location = self.geolocator.reverse(str(','.join([str(argLatitude),str(argLongitude)])))
        return tuple(location.address.split(','))

    def getDistBetweenAddress(self, argStartAddress, ArgEndAddress, argVincenty):
        '''
        Defualt to miles (unit value is 'km' or 'm')
        if argUnit not in ['m','km']:
            raise ValueError('argUnit must be in [\'km\',\'m\' ')
        '''
        if type(argVincenty) != bool:
            raise ValueError('argVincenty must be of type boolean ')

        myStartGeo = self.getGeoCodeForAnAddress(argStartAddress)
        myEndGeo = self.getGeoCodeForAnAddress(ArgEndAddress)
        return self.getDistBetweenGeo(myStartGeo,myEndGeo, argVincenty)
   
    def getDistBetweenGeo(self, argStartGeo, argEndGeo, argVincenty):
        if argVincenty:
            return vincenty(argStartGeo, argEndGeo).miles
        else:
            return great_circle(argStartGeo, argEndGeo).miles

    # Schedule utils
    def getScheduleStatus(self, argCurStatus, argInvitee):
        '''
        Return Schedule status, based upon Invitee list passed, if any of invitee status is 'Confirmed', Schedule status is Confirmed
        '''

        # if current schedule status is 'Draft', it will stay as 'Draft'
        if argCurStatus == self.globaL._Global__ScheduleDraftStaus:
            return self.globaL._Global__ScheduleDraftStaus

        myUniqStatus = set()
        # [myUniqStatus.add(inv['Status'] for inv in argInvitee) if 'Invitee' in inv] # One liner is returing None at the end of call, skipping one liner code
        for invitee in argInvitee:
            myUniqStatus.add(invitee['Status'])

        #here is the logic for schedule status
        #1, if we have only one distinct invitee status = 'Owner', status is confirmed
        #2, if we have more than one invitee status and if 'Confirmed' is in the list, status is 'Pending' 
        if len(myUniqStatus) == 1 and self.globaL._Global__ScheduleOwnerStatus in myUniqStatus:
            return self.globaL._Global__ScheduleConfirmedStatus

        if len(myUniqStatus) > 1 and self.globaL._Global__ScheduleConfirmedStatus in myUniqStatus:
            return self.globaL._Global__ScheduleConfirmedStatus
        
        if len(myUniqStatus) > 1 and self.globaL._Global__ScheduleConfirmedStatus not in myUniqStatus:
            return self.globaL._Global__ScheduleWaitingStatus


''' Pop dict items
>>> for x in a.keys():
...   if not a[x]:
...     a.pop(x)
'''