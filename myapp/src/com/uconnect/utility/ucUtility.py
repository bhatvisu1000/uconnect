import os, sys, json,datetime, copy, com.uconnect.core.error

from com.uconnect.core.singleton import Singleton
from com.uconnect.utility.ucLogging import logging
from com.uconnect.core.infra import Environment
from com.uconnect.core.globals import Global

myLogger = logging.getLogger('uConnect')

@Singleton
class Utility(object):

    def __init__(self):
        self.envInstance = Environment.Instance()
        self.globalInstance = Global.Instance()
        self.myClass = self.__class__.__name__
        self.myPythonFile = os.path.basename(__file__)
        '''
        print ("Global Success:",self.globalInstance._Global__Success)
        print ("Global UnSuccess:",self.globalInstance._Global__UnSuccess)
        print ("Global Error:",self.globalInstance._Global__Error)
        print ("Global Screen:",self.globalInstance._Global__InternalScreenId)
        print ("Global Action:",self.globalInstance._Global__InternalActionId)
        '''
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
            
    def convList2Dict(self, argValueList):
        ''' Duplicate value will be removed if found in list '''
        myDict = {}
        for myList in argValueList:
            myDict.update({myList['Key'] : myList['Value']})

        return myDict

    def findKeyInListDict(self, argList, argKey, argVal):
        return [i for i, x in enumerate(argList) if (argKey in x) and ( x[argKey] == argVal ) ]

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

        #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.Utility')
        #myModuleLogger.debug("validating dict [{key}] in [{dict}] ".format(dict=argRequestDict, key=argKeyList))
        ''' another way to check if all key is found in dict '''
        isValidArgument = False

        ''' lets remove the ignore key from argKeyList, if ignore list is passed '''
        myArgKeyList = copy.deepcopy(argKeyList)
        myIgnoredArgKeyList = copy.deepcopy(argIgnoreList)
        myMainArgData = copy.deepcopy(argRequestDict)
        if not(myIgnoredArgKeyList == None):
            self.removeKeyFromList(myArgKeyList, myIgnoredArgKeyList)

        '''
        print('val',myArgKeyList)
        print('val',myIgnoredArgKeyList)
        print('val',myMainArgData)
        '''
        # check if all key in dictionary
        if all(key in myMainArgData for key in myArgKeyList):
            # check if any key in dict has None or empty value
            if myMainArgData == dict ((key, values) for key, values in myMainArgData.iteritems() if values):
                isValidArgument = True

        '''
        isValidArgument = True
        for key in argKeyList:
            if (not(key in myMainArgData ))  or (myMainArgData[key] == None ):
                isValidArgument = False
                break
        '''
        return isValidArgument

    def getCopy(self, argDictList):
        return copy.deepcopy(argDictList)

    def isAllArgumentsValid(self,*args):
        ''' 
            Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
            *args:          All argumnet seperated by comma, any # of arguments can be passed
            usage:          ( isAllArgumentsValid(<*args>)
        '''
        return (all (args))

    def isValidZipCode(self, argZipCode):
        ''' 
            Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
            Arguments:      Zipcode
            usage:          ( isValidZipCode(<zipciode>)
        '''
        return argZipCode in self.envInstance._Environment__zipCodeData

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
        myCreateStatus = self.globalInstance._Global__UnSuccess
        if argCreateResult and ('_id' in argCreateResult):
            myCreateStatus = self.globalInstance._Global__UnSuccess

        return myCreateStatus

    def getUpdateStatus(self,argUdateResult):
        myUpdateStatus = self.globalInstance._Global__UnSuccess
        if argUdateResult and ('modified' in argUdateResult) and (int(argUdateResult['modified'])) > 0:
            myUpdateStatus = self.globalInstance._Global__Success
        
        return myUpdateStatus

    def extractAllFromReq(self, argRequestDict):
        ''' 
            Description:    Extracts all argument passed to request
            Arguments:      Request json dict data 
            usage:          ( extractRequest(<argRequestDict>)
        '''
        myStatus = myScreenId = myActionId = myRequestData = ''

        if self.isDict(argRequestDict):
            myStatus = self.globalInstance._Global__Success
            myScreenId = argRequestDict['Request']['Header']['ScreenId']
            myActionId = argRequestDict['Request']['Header']['ActionId']
            myRequestData = argRequestDict['Request']['MainArg']
        else:
            myStatus = self.globalInstance._Global__Error

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
        myRequestData = self.envInstance.getTemplateCopy(self.globalInstance._Global__RequestTemplate)
        #print ('Request:', myRequestData)
        #print ('Internal Scr:', self.globalInstance._Global__InternalScreenId)
        myRequestData["Request"]["Header"]["ScreenId"] = self.globalInstance._Global__InternalScreenId
        myRequestData["Request"]["Header"]["ActionId"] = self.globalInstance._Global__InternalActionId 
        myRequestData["Request"]["Header"]["Page"] = self.globalInstance._Global__InternalPage
        myRequestData["Request"]["MainArg"] = argRequestDict["Data"]

        return myRequestData

    def buildInitHistData(self):
        ''' building initial history data for a given collection '''
        #myHistoryData = self.envInstance.defaultsData["History"]
        myHistoryData = self.envInstance.getTemplateCopy(self.globalInstance._Global__HistoryTemplate)

        myHistoryData["InitChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["InitChange"]["Message"]="Initial creation"            
        myHistoryData["LastChange"]["When"]=datetime.datetime.utcnow()
        myHistoryData["LastChange"]["Message"]="Initial creation"            
        
        return myHistoryData

    def buildActivityArg(self,argEntityId, argEntityType, argActivityType, argActivity, argAuth):

        myActivityLogData = self.envInstance.getTemplateCopy(self.globalInstance._Global__activityLogColl)

        myActivityLogData["EntityType"]=argEntityType
        myActivityLogData["EntityId"]=argEntityId            
        myActivityLogData["ActivityType"]=argActivityType
        myActivityLogData["Activity"]=argActivity           
        myActivityLogData["Auth"]=argAuth            
        self.removeKeyFromDict(myActivityLogData, ['Acknowledged','ActivityDate'])
        return myActivityLogData

    def getRequestStatus(self, argStatus, argStatusMessage = None, argData = None):
        myRequestStatus = self.getCopy(self.globalInstance._Global__RequestStatus)
        if argStatus:
            if argStatus == self.globalInstance._Global__Success:
                myRequestStatus.update({'Status' :self.globalInstance._Global__Success})
                myRequestStatus.update({'Message' : self.globalInstance._Global__Success})
                myRequestStatus.update({'Data' : argData})
            elif argStatus == self.globalInstance._Global__UnSuccess:
                myRequestStatus.update({'Status' : self.globalInstance._Global__UnSuccess})
                if argStatusMessage:
                    myRequestStatus.update({'Message' : argStatusMessage})
                #fi
            #fi
        #fi
        return myRequestStatus

    def buildResponseData(self, argResponseMode, argResultStatus, argResultType, argResultData = None):
       
        ''' if this is internal request, we should not built the response, response will be built by mehtod whcih
        was called externally     '''

        if (argResponseMode == self.globalInstance._Global__InternalRequest):
            if argResultData:
                return argResultData
            else:
                return argResultStatus
            #fi
        #fi

        #myResponseData = self.envInstance.getTemplateCopy(self.globalInstance._ResponseTemplate)
        myResponseData = self.envInstance.getTemplateCopy(self.globalInstance._Global__ResponseTemplate)
        #print("Response",myResponseData)
        myData = argResultData

        if (argResultType == 'Update'):
            myResponseStatus = self.getUpdateStatus(argResult)
            myResponseData['Response']['Header']['Status'] = myResponseStatus
            myResponseData['Response']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Insert'):
            myResponseStatus = self.getCreateStatus(argResult)
            myResponseData['Response']['Header']['Status'] = myResponseStatus
            myResponseData['Response']['Header']['Message'] = myResponseStatus
        elif (argResultType == 'Find'):
            myResponseData['Response']['Header']['Status'] = argResultStatus['Status']
            myResponseData['Response']['Header']['Message'] = argResultStatus['Message']
            #myData = argResult
        elif (argResultType == 'Error'):
            #print("Success",self.globalInstance._Global__Success)
            myResponseData['Response']['Header']['Status'] = argResultStatus['Status']
            myResponseData['Response']['Header']['Message'] = argResultStatus['Message']
            myData = []

        ''' if data element passed, we will copy the "Data" to "Data" section, "Data.Summary" to "Header.Summary" secton'''
        try:
            # if myData is not iterable, exception will be raised, will ignore the exception 
            if (myData) and (self.globalInstance._Global__DataKey in myData) and (myData[self.globalInstance._Global__DataKey]):
                myResponseData['Response'][self.globalInstance._Global__DataKey] = myData[self.globalInstance._Global__DataKey]
                if (self.globalInstance._Global__SummaryKey in myData) and (myData[self.globalInstance._Global__SummaryKey]):
                    myResponseData['Response']['Header'][self.globalInstance._Global__SummaryKey]= myData[self.globalInstance._Global__SummaryKey]    
            elif (myData) and (self.globalInstance._Global__DataKey not in myData):
                ''' we got data but "data" key is missing '''
                if self.isDict:
                    myResponseData['Response'][self.globalInstance._Global__DataKey] = [myData]
                else:
                    myResponseData['Response'][self.globalInstance._Global__DataKey] = myData
                #fi
            #fi                    
        except TypeError:
            pass

        return myResponseData 

    def extrAllDocFromResultSets(self, argResultSets):
        if (self.globalInstance._Global__DataKey in argResultSets) and (argResultSets[self.globalInstance._Global__DataKey]):
            return argResultSets[self.globalInstance._Global__DataKey]
        else:
            return None

    def extr1stDocFromResultSets(self, argResultSets):
        if (self.globalInstance._Global__DataKey in argResultSets) and (argResultSets[self.globalInstance._Global__DataKey]):
            return argResultSets[self.globalInstance._Global__DataKey][0]
        else:
            return None

    def extrSummFromResultSets(self, argResultSets):
        if self.globalInstance._Global__SummaryKey in argResultSets:
            return argResultSets[self.globalInstance._Global__SummaryKey]
        else:
            return None

    def extrStatusFromResultSets(self, argResultSets):
        if (self.globalInstance._Global__StatusKey in argResultSets[self.globalInstance._Global__SummaryKey]):
            return argResultSets[self.globalInstance._Global__SummaryKey][self.globalInstance._Global__StatusKey]
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
            myEmptyTemplate = self.envInstance.getTemplateCopy(argTemplateName)
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
        return dict ((k,v) for k, v in argRequestDict.iteritems() if v)

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

    def getMemberConnStatus4Action(self, argAction, argActionBy):
        '''
            we dont need auth validation since we dont have a way to find this request for which memberid
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argAction + ',' + argActionBy))

            myAllowedConnection = self.globalInstance._Global__MemberConnectionStatus.keys()

            ''' validating arguments '''
            if (not argAction) or (not argActionBy) :
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, got null expecting values arg[{arg}]'.
                    format(arg=argAction + ',' + argActionBy))

            ''' we need to validate if right action and actionby key is passed'''
            if not(argAction in myAllowedConnection):
                raise com.uconnect.core.error.MissingArgumentValues('Action key must have either on of this value {expectVal}, got [{arg}] '.
                    format(expectVal=myAllowedConnection, arg=argAction))

            if not(argActionBy in self.globalInstance._Global__MemberConnectionStatus.get(argAction).keys()):
                raise com.uconnect.core.error.MissingArgumentValues('ActionBy key must have either one of this value [{expectVal}], got [{arg}] '.
                    format(expectVal=self.globalInstance._Global__MemberConnectionStatus.get(argAction).keys(),
                           arg=argActionBy))

            return self.globalInstance._Global__MemberConnectionStatus.get(argAction).get(argActionBy)

        except Exception as error:
            raise

    def getErrorCodeDescription(self, argErrorCode):
        myErrorDescription = ''
        if argErrorCode in self.envInstance._Environment__errorCodesData:
            myErrorDescription = self.envInstance._Environment__errorCodesData.get(argErrorCode)    

        print(argErrorCode,self.envInstance._Environment__errorCodesData,myErrorDescription)
        return myErrorDescription
    ''' Security Utility '''

''' Pop dict items
>>> for x in a.keys():
...   if not a[x]:
...     a.pop(x)
'''