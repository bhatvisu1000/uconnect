import sys, datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security

myLogger = logging.getLogger('uConnect')

@Singleton
class Member(object):

    def __init__(self):
        ''' 
            Description:    Initialization internal method, called internally
            usage:          Called internally
            Return:         N/A
        '''        
        self.envInstance = Environment.Instance()
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.dbutilityInstance = DBUtility.Instance()
        self.globalInstance = Global.Instance()
        self.securityInstance = Security.Instance()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def __buildArg4IsAValidMember(self, argMemberId, argAuthKey, argEntityId, argEntityType):
        
        return {'MemberId':argMemberId, 'EntityId':argEntityId, 'EntityType': argEntityType, 'AuthKey':argAuthKey}

    def __updateMemberTag(self, argRequestDict):
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['_id']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' preparing pipeline for aggregate function '''
            myAggregateColl = self.globalInstance._Global__memberColl
            #myPipeLine=[{"$match":{"_id":myMainArgData['_id']}},{"$unwind":"$Contact"},{"$addFields": { "Tag": { "$concat":["$Main.LastName", " , ", "$Main.FirstName"," , ","$Address.City"," ", "$Address.State", " , ", "$Contact.Value"] }}},{"$project": { "Tag":1, "_id":0 }}]
            # tag filed is Main.LastName, Main.FirstName, Address.City/State, Contact.Email 
            myPipeLine=[{"$match":{"_id":myMainArgData['_id']}},{"$addFields": { "Tag": { "$concat":["$Main.LastName", " , ", "$Main.FirstName"," , ","$Address.City"," ", "$Address.State", " , ", "$Contact.Email"] }}},{"$project": { "Tag":1, "_id":0 }}]            
            myAggregateCommand = {"aggregate":myAggregateColl, "pipeline":myPipeLine}

            self.myModuleLogger.debug('pipeline [{pipeline}] will be used to build Tag for member [{member}]'.format(pipeline=myPipeLine, member=myMainArgData['_id']))

            ''' executing aggregate command to get Tag information '''
            myTagResult = self.mongoDbInstance.ExecCommand(myAggregateCommand)

            self.myModuleLogger.debug('Tag [{tag}] built'.format(tag=myTagResult))
            print('tag result:',myTagResult)

            if 'result' in myTagResult:
                myTagData = [tag.upper() for tag in [myTagResult['result'][0]['Tag']]]
                #print('tag:',myTagData[0],tuple(myTagData))
                myTagUpdateData = {'Tag':myTagData}
                myTagUpdateResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myMainArgData, myTagUpdateData,'set')
                if self.utilityInstance.getUpdateStatus(myTagUpdateResult) == self.globalInstance._Global__Success:
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                else:
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess)
                #fi                    
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess)
                self.myModuleLogger.exception('Could not build tag for this member, Error [{myerror}]'.format(myerror='result key is missing'+myTagResult))
            #fi
        except Exception as error:
            myErrorMessage = error.errorMsg            
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)
        finally:
            return myRequestStatus

    def __buildInitMembderData(self, argRequestDict):

        #argMainDict,argAddressDict,argContactDict
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['Main','Address','Contact']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myMainDict = myMainArgData['Main']
            myAddressDict = myMainArgData['Address']
            myContactDict = myMainArgData['Contact']

            myZipCode = myAddressDict['ZipCode']
            myCityNState = self.utilityInstance.getAddressCityState(myZipCode)
            myCity = myCityNState[0]
            myState = myCityNState[1]
            myMemberTag = []
            myInitMemberData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__member)
            #myModuleLogger.debug('Member template [{template}]'.format(template=myInitMemberData))        

            ''' Main '''
            if ( 'LastName' in myMainDict ):
                myInitMemberData['Main']['LastName'] = myMainDict['LastName']
                myMemberTag.append(myMainDict['LastName'])
            #fi
            if ( 'FirstName' in myMainDict ):
                myInitMemberData['Main']['FirstName'] = myMainDict['FirstName']
                myMemberTag.append(myMainDict['FirstName'])
            #fi
            if ( 'NickName' in myMainDict ):
                myInitMemberData['Main']['NickName'] = myMainDict['NickName']
                myMemberTag.append(myMainDict['NickName'])
            #fi
            if ( 'Type' in myMainDict) :
                myInitMemberData['Main']['Type'] = myMainDict['Type']
            else:
                myInitMemberData['Main']['Type'] = self.globalInstance._Global__Participant                            
            #fi

            ''' Address '''            
            if ( 'Street' in myAddressDict ):
                myInitMemberData['Address']['Street'] = myAddressDict['Street']
                #myMemberTag.append(myAddressDict['Street'])
            #fi
            if (not (myCity == None)) and (not(myState == None)): 
                myInitMemberData['Address']['City'] = myCity
                myInitMemberData['Address']['State'] = myState
                myInitMemberData['Address']['ZipCode'] = myZipCode
                #myMemberTag.extend([myCity,myState])
            else:
                myInitMemberData['Address']['ZipCode'] = myZipCode
            #fi

            ''' Contact, ''' 
            if ( 'Mobile' in myContactDict ):
                ''' commenting following code, will go back to original way to store the contact data 
                myInitMemberData['Contact'].append({'Method':'Mobile','Value': myContactDict['Mobile']})
                '''
                myInitMemberData['Contact']['Mobile'] = myContactDict['Mobile']
                #myMemberTag.append(myContactDict['Mobile'])
            #fi
            if ( 'Email' in myContactDict ):
                ''' commenting following code, will go back to original way to store the contact data 
                myInitMemberData['Contact'].append({'Method':'Email','Value': myContactDict['Email']})
                '''
                myInitMemberData['Contact']['Email'] = myContactDict['Email']
                #myMemberTag.append(myContactDict['Email'])
            #fi

            # building tag
            #myMemberTag = self.utilityInstance.removeEmptyValueFromList(myMemberTag)
            #myInitMemberData['Tag'].extend(myMemberTag)

            ''' lets get the memberid for this member '''
            myMemberId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__memberColl)
            myInitMemberData['_id'] = myMemberId

            ''' build initial history data '''
            myInitMemberData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
            self.myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitMemberData))

            return myInitMemberData

        except Exception as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise

    #__buildInitMembderData Ends here

    def __createAMember(self,argRequestDict):
        ''' 
            Description:    Create a member
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {<Member data 'Main','Address','Contact'>}}
                            }
                            We will add 'BusyHours', BusyDays' block from default value
            usage:          <createAMember(<argReqJsonDict>)
            Return:         Json object

            Collection:     Member: Insert a record in Member collection
        '''
        try:
            ## we need to check who called this function, must be from register
            #print(self.utilityInstance.whoAmi())
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))

            myArgKey = ['Main','Address','Contact']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=myMainArgData))

            ''' Preparing value to create a new member build initial data '''
            myMemberData = self.__buildInitMembderData({'Main':myMainArgData['Main'],'Address':myMainArgData['Address'],'Contact':myMainArgData['Contact']})
            myMemberId = myMemberData['_id'] 

            ''' Creating a member '''
            self.myModuleLogger.info('Creating new member, data [{doc}]'.format(doc=myMemberData))
            
            myMemberResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global__memberColl, myMemberData)
            myTagUpdateResult = self.__updateMemberTag({'_id':myMemberId})

            self.myModuleLogger.info('Member [{id}] created, result[{result}]'.format(id=myMemberId, result=myMemberResult))
            self.myModuleLogger.info('Tag updated, result[{result}]'.format(result=myTagUpdateResult))

            ''' Building response data, we can not retrieve member information because we dont have Auth ket yet, will return member id created'''

            '''
            myRequestDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myMemberId}})
            myRequestDict = self.getAMemberDetail(myResponseDataDict)
            myResponse = self.utilityInstance.buildResponseData(self.globalInstance._Global__InternalRequest,myMemberResult,'Insert',myResponseData)
            '''
            myResponse = myMemberResult['_id']

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            raise
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise


    def __buildGetAllConnPipeline(self, argRequestDict):
        #argMemberId, argConnectionType
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['MemberId','ConnectionType']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myConnectionType = myMainArgData['ConnectionType']
            myMemberId = myMainArgData['MemberId']

            self.myModuleLogger.debug('Building pipeline for aggregate function')

            if myConnectionType == self.globalInstance._Global__memberColl:
                myFromCollection = self.globalInstance._Global__memberColl
                myPipeLine =  [ 
                        {"$match"  : {"_id":myMemberId}},
                        {"$unwind" : {"path":"$Connections","preserveNullAndEmptyArrays":True}},  
                        {"$match"  : { "$and": [{"Connections.Type":myConnectionType} ] } },
                        {"$lookup" :
                            {
                                "from":myFromCollection,
                                "localField":"Connections.Id",                  
                                "foreignField":"_id",                  
                                "as":"MyMemberConnections"
                            }      
                        },
                        {"$project": 
                            {
                                "_id":1,"Connections":1,
                                "MyMemberConnections.Id":1,
                                "MyMemberConnections.Main":1,"MyMemberConnections.Address":1,"MyMemberConnections.Contact":1
                            }
                        },
                        {
                            "$sort" :
                                {
                                    "MyMemberConnections.Main.LastName":1
                                }
                        }
                    ]
            #fi
            return myPipeLine

        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise

    #__buildGetAllConnPipeline Ends here

    def __buildMyConnection(self, argRequestDict):
        #argConnectionType, argConnectionRawData):

        #argMemberId, argConnectionType
        try:
            #self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['ConnectionType','ConnectionRawData']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myConnectionType = myMainArgData['ConnectionType']
            myConnectionRawData = myMainArgData['ConnectionRawData']

            self.myModuleLogger.debug('Building [{conn}] Connection '.format(conn=myConnectionType))

            if myConnectionType == self.globalInstance._Global__memberColl:
                myResultStatus = {"Success":myConnectionRawData['ok']}
                myMemberConnRawData =  myConnectionRawData['result']
                if (myMemberConnRawData): 
                    myMemberConnections = {"_id":myMemberConnRawData[0]['_id']}

                    myMemberConnections['Connections'] = []
                    for x in myMemberConnRawData:
                        x['MyMemberConnections'][0].update({'Favorite':x['Connections']['Favorite']})
                        x['MyMemberConnections'][0].update({'Blocked':x['Connections']['Blocked']})
                        x['MyMemberConnections'][0].update({'Id':x['Connections']['Id']})
                        x['MyMemberConnections'][0].update({'Type':x['Connections']['Type']})
                        x['MyMemberConnections'][0].update({'Status':x['Connections']['Status']})
                        myMemberConnections['Connections'].append(x['MyMemberConnections'][0])

                    # sorting now
                    #myConnection = json.dumps(myMemberConnections, sort_keys=True)    
                    myConnection = myMemberConnections    
                else:
                    myConnection = {}
                #fi

                #print json.dumps(myMemberConnections, sort_keys=True)
                #print myMemberConnections

            return myConnection

        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])            
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise

    #__buildMyConnection Ends here

    def __getMemberConnectionInfo(self, argRequestDict):
        '''
        Returns current Member connection status
        MemberId, ConnectMemberId, Auth
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myArgKey = ['MemberId', 'ConnectMemberId', 'Auth']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
            #fi
            
            ''' Preparing '''
            myCriteria = {'_id':myMainArgData['MemberId'], 'Connections.Id':myMainArgData['ConnectMemberId'], 'Connections.Type':'Member'}                
            myProjection = {'_id':1,'Connections':1}
            
            #print(myCriteria,myProjection)
            ''' Finding document '''
            myResult = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, True)
            #print(myResult)
            myMemberConnection = self.utilityInstance.extr1stDocFromResultSets(myResult)

            return myMemberConnection

        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            raise
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            raise
    #__getMemberConnectionInfo Ends here

    def __updateMemberMain(self,argRequestDict):
        ''' 
            We need to combine all update of a Member
            Description:    Update Member's Main information (LastName,FirstName,NickName,Sex)
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Main':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Main':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            ''' validating arguments '''
            myArgKey = ['Auth','Main']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi
            # validating security, this has already been validated by BPS process ???
            '''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))
            #fi
            '''
            ''' Preparing document:    '''
            # removing key(s) if it has any empty values
            myMainUpdateData = self.utilityInstance.removeEmptyValueKeyFromDict({'Main':myMainArgData['Main']})

            # building update data, find all key informarion which need to be changed 
            myAllMainKey = self.utilityInstance.getAllKeysFromDict(myMainUpdateData['Main'])
            myMainUpdateData= {}
            for key in myAllMainKey:
                myMainUpdateData.update({'Main.'+key : myMainArgData['Main'][key]})
            #

            myMemberId = myMainArgData['Auth']['EntityId']
            myCriteria = {'_id':myMemberId}
            self.myModuleLogger.info('Updating Member [{member}]\'s [{main}]' .format(member=myMemberId, main=myMainUpdateData))

            ''' Executing document update '''
            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myMainUpdateData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Update',myResult) 
            #return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise error
            #fi
            
    def __updateMemberAddress(self,argRequestDict):
        ''' 
            Description:    Update Member's Address
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Address':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Contact':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''

        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            ''' validating arguments '''
            myArgKey = ['Auth','Address']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' preparing document '''
            myMemberId = myMainArgData['Auth']['EntityId']
            myCriteria = {'_id':myMemberId}
            myAddressUpdateData= {}

            # removing key(s) if it has any empty values
            myAddressData = self.utilityInstance.removeEmptyValueKeyFromDict({'Address':myMainArgData['Address']})
            print('AddressData',myAddressData)
            # building update data, find all key informarion which need to be changed 
            myAllAddressKey = self.utilityInstance.getAllKeysFromDict(myAddressData['Address'])

            # would not change city/state, this shold be change by changing the ZipCode
            if 'City' in myAllAddressKey:
                myAllAddressKey.remove('City')
            #fi
            if 'State' in myAllAddressKey:
                myAllAddressKey.remove('State')
            #fi                
            print('Removed City/State,addressData:',myAddressData, myAllAddressKey)
            for key in myAllAddressKey:
                myAddressUpdateData.update({'Address.'+key : myAddressData['Address'][key]})
            #
            print('Created address update data', myAddressUpdateData)
            # will add matching the City/State, if ZipCode is passed
            if 'ZipCode' in myAllAddressKey:
                myCityNState = self.utilityInstance.getAddressCityState(myAddressData['Address']['ZipCode'])
                myAddressUpdateData.update({'Address.City':myCityNState[0]})
                myAddressUpdateData.update({'Address.State':myCityNState[1]})
            #fi                

            self.myModuleLogger.info('Updating Member [{member}]\'s address [{address}]' .format(member=myMemberId, address=myAddressUpdateData))

            ''' Executing document update '''
            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myAddressUpdateData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Update',myResult)           
            #return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise error
            #fi

    def __updateMemberContact(self,argRequestDict):
        ''' 
            Description:    Update Member's contact 
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'MemberId':'','Contact':[{'Key':'Value'},...]
                            }
            usage:          <addMember2Favorite(<argReqJsonDict>)
                            MainArg{'MemberId':'','Contact':[{Key':'', 'Value':''}]}
            Return:         Json object
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            ''' validating arguments '''
            myArgKey = ['Auth','Contact']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' preparing document '''
            # removing key(s) if it has any empty values
            myContactData = self.utilityInstance.removeEmptyValueKeyFromDict({'Contact':myMainArgData['Contact']})
            myMemberId = myMainArgData['Auth']['EntityId']
            myCriteria = {'_id':myMemberId}

            # building update data, find all key informarion which need to be changed 
            myAllContactKey = self.utilityInstance.getAllKeysFromDict(myContactData['Contact'])
            myContactUpdateData= {}
            for key in myAllContactKey:
                myContactUpdateData.update({'Contact.'+key : myMainArgData['Contact'][key]})
            #
            self.myModuleLogger.info('Updating Member [{member}]\'s Contact [{contact}]' .format(member=myMemberId, contact=myContactUpdateData))

            ''' Executing document update '''
            myResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myContactUpdateData, 'set',False)

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Update',myResult)           
            #return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
            #return myResponse
        finally:
            if 'myResponse' in locals():
                return myResponse
            else:
                raise error
            #fi

    def __isAValidMember(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MemnberId':'','Auth':''}
            usage:          <__isAValidMember(<argReqJsonDict>)
            Return:         Json object
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            isValidMember = self.globalInstance._Global__False 
            #myArgKey = ['Member','Auth']

            ''' validating arguments '''
            myArgKey = ['Member','ResponseMode']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myArgKey = ['_id']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Member'], myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData['Member'].keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' commenting out this block, this will be internal call 
            #Validate auth key for this request
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi
            '''
            myCriteria = {'_id':myMainArgData['Member']['_id'], 'Main.Type':self.globalInstance._Global__member}
            myMemberDataCount = self.mongoDbInstance.findTotDocuments(self.globalInstance._Global__memberColl, myCriteria)

            #print(myCriteria,myProjection,myMemberData)
            if myMemberDataCount > 0:
                isValidMember = self.globalInstance._Global__True 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                isValidMember = self.globalInstance._Global__False 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'MemberID [{member}] does not exist'.format(member=str(myMainArgData['Member']['_id'])))                
            #fi
            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',isValidMember)
            #return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('InvalidAuthKey: error [{myerror}]'.format(myerror=myErrorMessage))
            isValidMember = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            #return myResponse
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            isValidMember = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            #return myResponse
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            isValidMember = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)
        finally:
            if 'myResponse' in locals():            
                return myResponse
            else:
                raise
    # __isAValidMember Ends here