import os, sys, json,datetime
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
        '''
        print ("Global Success:",self.globalInstance._Global__Success)
        print ("Global UnSuccess:",self.globalInstance._Global__UnSuccess)
        print ("Global Error:",self.globalInstance._Global__Error)
        print ("Global Screen:",self.globalInstance._Global__InternalScreenId)
        print ("Global Action:",self.globalInstance._Global__InternalActionId)
        '''
    def isDict(self, argDict):
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
        print(type(argRequest))
        print(argRequest)

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

        if argCreateResult["_id"]:
            return self.globalInstance._Global__Success
        else:
            return self.globalInstance._Global__UnSuccess

    def getUpdateStatus(self,argUdateResult):

        if (int(argUdateResult['modified'])) > 0:
            return self.globalInstance._Global__Success
        else:
            return self.globalInstance._Global__UnSuccess

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
        myRequestData = { "Request" :self.envInstance.getTemplateCopy(self.globalInstance._Global__RequestTemplate) }
        print ('Request:', myRequestData)
        print ('Internal Scr:', self.globalInstance._Global__InternalScreenId)
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

    def buildResponseData(self, argScreenId, argResult, argResultType, argResultData = None):
       
        ''' if this is internal request, we should not built the response, response will be built by mehtod whcih
        was called externally     '''

        if (argScreenId == self.globalInstance._Global__InternalScreenId):
            return argResult

        #myResponseData = self.envInstance.getTemplateCopy(self.globalInstance._ResponseTemplate)
        myResponseData = {"Response": self.envInstance.getTemplateCopy(self.globalInstance._Global__ResponseTemplate) }
        print("Response",myResponseData)
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
            print("Success",self.globalInstance._Global__Success)

            myResponseData['Response']['Header']['Status'] = self.globalInstance._Global__Success
            myResponseData['Response']['Header']['Message'] = self.globalInstance._Global__Success
            myData = argResult

        #end if
        #print("build response:",myData)
        #print("is Dict:",(self.isDict(myData['Data'])))
        #print('Data' in myData)

        #if (myData) and '''(self.isDict(myData['Data'])) and''' ('Data' in myData) and (myData['Data']):
        if (myData) and ('Data' in myData) and (myData['Data']):
            myResponseData['Response']['Data'] = myData['Data']
            if ('Summary' in myData) and (myData['Summary']):
                myResponseData['Response']['Header']['Summary']= myData['Summary']    
        
        return myResponseData 


''' Pop dict items
>>> for x in a.keys():
...   if not a[x]:
...     a.pop(x)
'''