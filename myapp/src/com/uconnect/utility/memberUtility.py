import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security

myLogger = logging.getLogger('uConnect')

@Singleton
class MemberUtility(object):
    ''' 
    Member BPS class, called from factory method
    '''
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

    def __buildArg4IsAValidMember(self, argMemberId, argAuthKey, argEntityId, argEntityType):
        
        return {'MemberId':argMemberId, 'EntityId':argEntityId, 'EntityType': argEntityType, 'AuthKey':argAuthKey}

    def __buildInitMembderData(self, argRequestDict):

        #argMainDict,argAddressDict,argContactDict
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

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

            myInitMemberData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__member)
            #myModuleLogger.debug('Member template [{template}]'.format(template=myInitMemberData))        

            ''' Main '''
            if ( 'LastName' in myMainDict ):
                myInitMemberData['Main']['LastName'] = myMainDict['LastName']
            #fi
            if ( 'FirstName' in myMainDict ):
                myInitMemberData['Main']['FirstName'] = myMainDict['FirstName']
            #fi
            if ( 'NickName' in myMainDict ):
                myInitMemberData['Main']['NickName'] = myMainDict['NickName']
            #fi

            ''' Address '''            
            if ( 'Street' in myAddressDict ):
                myInitMemberData['Address']['Street'] = myAddressDict['Street']
            #fi
            if (not (myCity == None)) and (not(myState == None)): 
                myInitMemberData['Address']['City'] = myCity
                myInitMemberData['Address']['State'] = myState
                myInitMemberData['Address']['ZipCode'] = myZipCode
            else:
                myInitMemberData['Address']['ZipCode'] = myZipCode
            #fi

            ''' Contact '''
            if ( 'Mobile' in myContactDict ):
                myInitMemberData['Contact']['Mobile'] = myContactDict['Mobile']
            #fi
            if ( 'Email' in myContactDict ):
                myInitMemberData['Contact']['Email'] = myContactDict['Email']
            #fi

            ''' lets get the memberid for this member '''
            myMemberId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__memberColl)
            myInitMemberData['_id'] = myMemberId

            ''' build initial history data '''
            myInitMemberData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
            myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitMemberData))

            return myInitMemberData

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    #__buildInitMembderData Ends here

    def __buildGetAllConnPipeline(self, argRequestDict):
        #argMemberId, argConnectionType
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

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

            myModuleLogger.debug('Building pipeline for aggregate function')

            if myConnectionType == self.globalInstance._Global__memberColl:
                myFromCollection = self.globalInstance._Global__memberColl
                myPipeLine =  [ 
                        {"$match"  : {"_id":myMemberId}},
                        {"$unwind" : {"path":"$Connections","preserveNullAndEmptyArrays":True}},  
                        {"$match"  : { "$and": [{"Connections.Type":myConnectionType} ] } },
                        {"$lookup" :
                            {
                                "from":myFromCollection,
                                "localField":"Connections.MemberId",                  
                                "foreignField":"_id",                  
                                "as":"MyMemberConnections"
                            }      
                        },
                        {"$project": 
                            {
                                "_id":1,"Connections":1,
                                "MyMemberConnections.MemberId":1,
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
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    #__buildGetAllConnPipeline Ends here

    def __buildMyConnection(self, argRequestDict):
        #argConnectionType, argConnectionRawData):

        #argMemberId, argConnectionType
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

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

            myModuleLogger.debug('Building [{conn}] Connection '.format(conn=myConnectionType))

            if myConnectionType == self.globalInstance._Global__memberColl:
                myResultStatus = {"Success":myConnectionRawData['ok']}
                myMemberConnRawData =  myConnectionRawData['result']
                if (myMemberConnRawData): 
                    myMemberConnections = {"_id":myMemberConnRawData[0]['_id']}

                    myMemberConnections['Connections'] = []
                    for x in myMemberConnRawData:
                        x['MyMemberConnections'][0].update({'Favorite':x['Connections']['Favorite']})
                        x['MyMemberConnections'][0].update({'Blocked':x['Connections']['Blocked']})
                        x['MyMemberConnections'][0].update({'MemberId':x['Connections']['MemberId']})
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
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    #__buildMyConnection Ends here

    def __getMemberConnectionInfo(self, argRequestDict):
        '''
        Returns current Member connection status
        MemberId, ConnectMemberId, Auth
        '''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

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
            myCriteria = {'_id':myMainArgData['MemberId'], 'Connections.MemberId':myMainArgData['ConnectMemberId'], 'Connections.Type':'Member'}                
            myProjection = {'_id':1,'Connections':1}
            #print(myCriteria,myProjection)
            ''' Finding document '''
            myResult = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, True)
            #print(myResult)
            myMemberConnection = self.utilityInstance.extr1stDocFromResultSets(myResult)

            return myMemberConnection

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise
    #__getMemberConnectionInfo Ends here

    def __AddMember2MemberConnection(self, argRequestDict):
        ''' This mehtod is for building a fresh new connection
            usage:          <__AddMember2MemberConnection(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
            Return:         Success/UnSuccess
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
            isReqConnectionAdded = self.globalInstance._Global__False
            isInvConnectionAdded = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Auth','ResponseMode']

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

            ''' validating Member and Connect Memebr '''
            if myMainArgData['MemberId'] == myMainArgData['ConnectMemberId']:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Member [{member}] and it\'s Connection[{connect}] can not be same'.format(member=myMainArgData['MemberId'], connect=myMainArgData['ConnectMemberId'] ))                

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['MemberId']},'Auth':myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid MemberId [{member}]'.format(member=myMainArgData['MemberId'] ))
            #fi

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['ConnectMemberId']},'Auth':myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid Connect MemberId [{member}]'.format(member=myMainArgData['ConnectMemberId'] ))
            #fi

            ''' Preparing Requestor/Invitee member connection document '''
            myRequestorConn = self.utilityInstance.getConnTemplateCopy(self.globalInstance._Global__member)
            myInviteeConn = self.utilityInstance.getConnTemplateCopy(self.globalInstance._Global__member)

            ''' Requestor connection '''
            myRequestorCriteria = {'_id':myMainArgData['MemberId']}
            myRequestorConn['MemberId'] = myMainArgData['ConnectMemberId']
            myRequestorConn['Status'] = self.utilityInstance.getMemberConnStatus4Action('New Connection','Requestor')
            myRequestorConnData = {'Connections': myRequestorConn}

            ''' Invitee  (reverse connection)'''
            myInviteeCriteria = {'_id':myMainArgData['ConnectMemberId']}
            myInviteeConn['MemberId'] = myMainArgData['MemberId']
            myInviteeConn['Status'] = self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')
            myInviteeConnData = {'Connections': myInviteeConn}

            myModuleLogger.debug('Requestor [{requestor}] connection document [{doc}] prepared'.
                format(requestor=myMainArgData['MemberId'], doc=myRequestorConn))
            myModuleLogger.debug('Invitee [{invitee}] connection document [{doc}] prepared'.
                format(invitee=myMainArgData['ConnectMemberId'],doc=myInviteeConn))

            ''' persisiting connection data'''

            myReqConnectionResult = self.mongoDbInstance.UpdateDoc(
                self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'addToSet',False)
                
            if self.utilityInstance.getUpdateStatus(myReqConnectionResult) == self.globalInstance._Global__Success:
                
                myModuleLogger.debug('Requestor connection [{conn}] created successfully, result [{result}]'.
                    format(conn = str(myMainArgData['MemberId'])  + ' -> ' + str(myMainArgData['ConnectMemberId']), result=myReqConnectionResult))
                isReqConnectionAdded = self.globalInstance._Global__True

                ''' building invitee connection (revese of requestor)'''
                myInvConnectionResult =  self.mongoDbInstance.UpdateDoc(
                    self.globalInstance._Global__memberColl, myInviteeCriteria, myInviteeConnData, 'addToSet',False)

                if self.utilityInstance.getUpdateStatus(myInvConnectionResult) == self.globalInstance._Global__Success:

                    ''' invitee connection is successful '''
                    isInvConnectionAdded = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                else:                    
                    ''' invitee connection is not successful, remvoving requestor connection to maintain the data integrity '''
                    myModuleLogger.debug('Invitee connection [{conn}] creation unsuccessful, result [{result}]'.
                        format(conn = str(myMainArgData['ConnectMemberId'])  + ' -> ' + str(myMainArgData['MemberId']), result=myInvConnectionResult))

                    ''' rolling back previous Requestor connection'''
                    self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'pull',False)

                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not build Invitee [{inv}] while performing "Add Connection" task'.
                            format(inv=myMainArgData['ConnectMemberId']))
                #fi
            else:
                myModuleLogger.debug('Requestor connection [{conn}] creation unsuccesful, result [{result}]'.
                    format(conn = str(myMainArgData['MemberId'])  + ' -> ' + str(myMainArgData['ConnectMemberId']), result=myReqConnectionResult))
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not build Requestor [{req}] while performing "Add Connection" task'.
                            format(req=myMainArgData['MemberId']))
            #fi

            ''' Return RequestStatus'''
            return myRequestStatus

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isReqConnectionAdded and (not isInvConnectionAdded) and (not isCleanUpDone):
                #print(isReqConnectionAdded,isInvConnectionAdded,isCleanUpDone)
                self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'pull',False)                
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.message)            
            raise
    #__AddMember2MemberConnection Ends here

    def __acceptInvitation(self, argRequestDict):
        ''' This method is invoked by Invitee; update the status of connection status in each other (Requestor/Invitee)'s connection list 
            usage:          <__AcceptInvitation(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
                                <Invitee => MemberId, Requestor => ConnectMemberId>
            Return:         Success/UnSuccess
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
            isReqConnectionAdded = self.globalInstance._Global__False
            isInvConnectionAdded = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Auth']

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

            ''' validating Member and Connect Memebr '''            
            if myMainArgData['MemberId'] == myMainArgData['ConnectMemberId']:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Member [{member}] and it\'s Connection[{connect}] can not be same'.format(member=myMainArgData['MemberId'], connect=myMainArgData['ConnectMemberId'] ))                

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['MemberId']}, 'Auth': myMainArgData['Auth'] } )):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid MemberId [{member}]'.format(member=myMainArgData['MemberId'] ))
            #fi

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['ConnectMemberId']}, 'Auth': myMainArgData['Auth'] } )):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid Connect MemberId [{member}]'.format(member=myMainArgData['ConnectMemberId'] ))
            #fi

            ''' Building Invitee (reverse connection) connection data'''
            myInviteeCriteria = {'_id':myMainArgData['MemberId'],'Connections.MemberId':myMainArgData['ConnectMemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}
            myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getMemberConnStatus4Action('Accept Connection','Invitee')}

            ''' Building Requestor connection data '''
            myRequestorCriteria = {'_id':myMainArgData['ConnectMemberId'], 'Connections.MemberId':myMainArgData['MemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('New Connection','Requestor')}
            myRequestorConnData = {'Connections.$.Status':self.utilityInstance.getMemberConnStatus4Action('Accept Connection','Requestor')}

            ''' persisitng changes in database '''

            ''' Updating invitee's connection status '''
            myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, myInviteeConnData, 'set',False)

            myModuleLogger.debug('Invitee connection status updated, [{conn}], result [{result}] '.
                format(conn = str(myMainArgData['MemberId'])  + ' -> ' + str(myMainArgData['ConnectMemberId']), result=myConnectionResult))

            if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                isInvConnStatusUpdated = self.globalInstance._Global__True

                ''' Invitee connection update is successful, persisiting Requestor's connection status update'''
                myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'set',False)

                myModuleLogger.debug('Requestor connection status updated, [{conn}], result [{result}] '.
                    format(conn = str(myMainArgData['ConnectMemberId'])  + ' -> ' + str(myMainArgData['MemberId']), result=myConnectionResult))

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                    ''' Requestor connection update is successful, undo Invitee connection change '''
                    isInvConnStatusUpdated = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                else:
                    ''' Requestor connection update is not successful, undo Invitee connection change '''
                    myModuleLogger.debug('Requestor [{req}] connection update unsuccessful, results [{result}]'.
                        format(req=myMainArgData['ConnectMemberId'], result=myReqConnResults ))

                    myInviteeCriteria = {'_id':myMainArgData['MemberId'],'Connections.MemberId':myMainArgData['ConnectMemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}
                    myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}
                    myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, myInviteeConnData, 'set',False)
                
                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not update Requestor [{req}] connection status to [{status}] while performing "Accpetance Connection" task'.
                                        format(req=myMainArgData['ConnectMemberId'], status=self.globalInstance._Global__Accepted_Req_MemConnectionStatus))
                    myModuleLogger.debug('undo changes to Invitee\'s connection successful, result [{result}]'.format(result=myReqConnResults))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not update Invitee [{inv}] connection status to [{status}] while performaing "Accpetance Connection" task'.
                                    format(inv=myMainArgData['MemberId'], status=self.globalInstance._Global__Accepted_Inv_MemConnectionStatus))
            #fi

            return myRequestStatus

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))

            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            
            if isInvConnStatusUpdated and (not isReqConnStatusUpdated) and (not isCleanUpDone):
            
                myInviteeCriteria = {'_id':myMainArgData['MemberId'],'Connections.MemberId':myMainArgData['ConnectMemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('Accept Connection','Invitee')}
                myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}
                myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, myInviteeConnData, 'set',False)
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, error.message)
            raise
    #__AcceptInvitation Ends here

    def __rejectInvitation(self, argRequestDict):
        ''' This method is invoked by Invitee; remove the connection from each other (Requestor/Invitee)'s connection list 
            usage:          <__rejectInvitation(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
                                <Invitee => MemberId, Requestor => ConnectMemberId>
            Return:         Success/UnSuccess
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
            isReqConnectionAdded = self.globalInstance._Global__False
            isInvConnectionAdded = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','Auth']

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

            ''' validating Member and Connect Memebr '''
            if myMainArgData['MemberId'] == myMainArgData['ConnectMemberId']:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Member [{member}] and it\'s Connection[{connect}] can not be same'.format(member=myMainArgData['MemberId'], connect=myMainArgData['ConnectMemberId'] ))                

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['MemberId']}, 'Auth': myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid MemberId [{member}]'.format(member=myMainArgData['MemberId'] ))
            #fi

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['ConnectMemberId']}, 'Auth': myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid Connect MemberId [{member}]'.format(member=myMainArgData['ConnectMemberId'] ))
            #fi

            ''' Building Invitee (reverse connection) connection data'''
            myInviteeCriteria = {'_id':myMainArgData['MemberId'],'Connections.MemberId':myMainArgData['ConnectMemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}
            myInviteeConnData = {'Connections':{'MemberId': myMainArgData['ConnectMemberId'],'Status':self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')}}

            ''' Building Requestor connection data '''
            myRequestorCriteria = {'_id':myMainArgData['ConnectMemberId'], 'Connections.MemberId':myMainArgData['MemberId'], 'Connections.Status': self.utilityInstance.getMemberConnStatus4Action('New Connection','Requestor')}
            myRequestorConnData = {'Connections':{'MemberId': myMainArgData['MemberId'],'Status':self.utilityInstance.getMemberConnStatus4Action('New Connection','Requestor')}}

            ''' persisitng changes in database '''
            ''' removing connections '''
            myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, myInviteeConnData, 'pull',False)
            myModuleLogger.debug('Invitee connection removed, [{conn}], result [{result}] '.
                format(conn = str(myMainArgData['MemberId'])  + ' -> ' + str(myMainArgData['ConnectMemberId']), result=myConnectionResult))

            if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:
                
                isInvConnRemoved = self.globalInstance._Global__True

                ''' Invitee connection removed, removing requestors connection'''                
                myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'pull',False)

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:
                    ''' Requestor connection update is successful '''
                    isReqConnRemoved = self.globalInstance._Global__True
                    myModuleLogger.debug('Requestor [{req}] connection remove successful, results [{result}]'.
                        format(req=myMainArgData['ConnectMemberId'], result=myConnectionResult ))

                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                else:
                    ''' Requestor connection update is not successful, undo Invitee connection removal (adding a new connection to invitees list)'''
                    myModuleLogger.debug('Requestor [{req}] connection remove unsuccessful, results [{result}]'.
                        format(req=myMainArgData['ConnectMemberId'], result=myConnectionResult ))

                    myInviteeCriteria = {'_id':myMainArgData['MemberId']}
                    myInviteeConn['MemberId'] = myMainArgData['ConnectMemberId']
                    myInviteeConn['Status'] = self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')                    
                    myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, {'Connections':myInviteeConn}, 'addToSet',False)
                    
                    isCleanUpDone = self.globalInstance._Global__True
                    myModuleLogger.debug('undo changes to Invitee\'s connection successful, result [{result}]'.format(result=myReqConnResults))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not remove invitee [{inv}]\'s connection while performing Reject task'.
                                    format(inv=myMainArgData['MemberId'])) 
            #fi

            return myRequestStatus

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isInvConnRemoved (not isReqConnRemoved) and (not isCleanUpDone):
                myInviteeCriteria = {'_id':myMainArgData['MemberId']}
                myInviteeConn['MemberId'] = myMainArgData['ConnectMemberId']
                myInviteeConn['Status'] = self.utilityInstance.getMemberConnStatus4Action('New Connection','Invitee')                    
                myConnectionResult = self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInviteeCriteria, {'Connections':myInviteeConn}, 'addToSet',False)
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, error.message)
            raise
    #__rejectInvitation end here

    def __removeConnection(self, argRequestDict):
        ''' This method will remove connection from each other (Requestor/Invitee)'s connection list 
            usage:          <___remAMemConnFromMember(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
            Return:         Success/UnSuccess
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
            isMemberConnRemoved = self.globalInstance._Global__False
            isConnectMemberConnRemoved = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False
            #arg4IsAValidMember = {}
            myArgKey = ['MemberId','ConnectMemberId','Auth']

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

            ''' validating Member and Connect Memebr '''
            if myMainArgData['MemberId'] == myMainArgData['ConnectMemberId']:
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Member [{member}] and it\'s Connection[{connect}] can not be same'.format(member=myMainArgData['MemberId'], connect=myMainArgData['ConnectMemberId'] ))                

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['MemberId']},'Auth':myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid MemberId [{member}]'.format(member=myMainArgData['MemberId'] ))
            #fi

            if (not self.isAValidMember({'Main':{'MemberId':myMainArgData['ConnectMemberId']},'Auth':myMainArgData['Auth']})):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid Connect MemberId [{member}]'.format(member=myMainArgData['ConnectMemberId'] ))
            #fi

            ''' preparing document for removing connections '''
            myReqCriteria = {'_id':myMainArgData['MemberId']}
            myReqConnections = {'MemberId': myMainArgData['ConnectMemberId'],'Type':self.globalInstance._Global__member}
            myReqConnectionData = {'Connections':myReqConnections}            

            ''' backing up exisiting connection '''
            myMemberConnection = self.__getMemberConnectionInfo({'MemberId':myMainArgData['MemberId'],'ConnectMemberId':myMainArgData['ConnectMemberId'],'Auth':myMainArgData['Auth']})
            if myMemberConnection and 'Connections' in myMemberConnection:
                myReqMemberConnection = myMemberConnection['Connections'][0]
            else:
                raise com.uconnect.core.error.DBError("Failed to backup Member connection, Db criteria{criteria} ".format(criteria={'MemberId':myMainArgData['MemberId'],'ConnectMemberId':myMainArgData['ConnectMemberId']}))
            #fi
            ''' removing connection '''
            myReqConnectionResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl,myReqCriteria, myReqConnectionData, 'pull',True)

            if self.utilityInstance.getUpdateStatus(myReqConnectionResult) == self.globalInstance._Global__Success:
                
                isMemberConnRemoved = self.globalInstance._Global__True
                myModuleLogger.debug('Connection between [{member}] and [{connectMember}] removed, result [{result}]'.
                    format(member=myMainArgData['MemberId'], connectMember=myMainArgData['ConnectMemberId'], result=myReqConnectionResult))

                ''' preparing doc for deleting reverse connections '''
                myInvCriteria = {'_id':myMainArgData['ConnectMemberId']}
                myInvConnections = {'MemberId': myMainArgData['MemberId'],'Type':self.globalInstance._Global__member}
                myInvConnectionData = {'Connections':myInvConnections}            
                
                ''' deleting reverse connection '''
                myInvConnectionResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myInvCriteria, myInvConnectionData, 'pull',True)

                if self.utilityInstance.getUpdateStatus(myInvConnectionResult) == self.globalInstance._Global__Success: 

                    ''' reverse connection removal is successful '''
                    isConnectMemberConnRemoved = self.globalInstance._Global__True
                    myModuleLogger.debug('Connection between [{member}] and [{connectMember}] removed, result [{result}]'.
                        format(member=myMainArgData['ConnectMemberId'], connectMember=myMainArgData['MemberId'], result=myReqConnectionResult))
                else:
                    ''' rollback previous deletion of connection '''
                    self.mongoDbInstance.UpdateDoc(
                        self.globalInstance._Global__memberColl,{'_id':myMainArgData['MemberId']} , {'Connections':myReqMemberConnection}, 'addToSet',False)

                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not remove rever connection for member [{member}]'.
                                        format(member=myMainArgData['ConnectMemberId']))
                    isCleanUpDone = self.globalInstance._Global__True
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not remove member [{member}]\'s connection'.
                                    format(member=myMainArgData['MemberId']))
            #fi

            return myRequestStatus

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except com.uconnect.core.error.DBError as error:
            myModuleLogger.exception('DBError: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
            return myRequestStatus

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            if isMemberConnRemoved and (not isConnectMemberConnRemoved) and (not isCleanUpDone):
                ''' rollback previous deletion of member connection '''
                self.mongoDbInstance.UpdateDoc(
                    self.globalInstance._Global__memberColl,{'_id':myMainArgData['MemberId']},{'Connections':myReqMemberConnection}, 'addToSet',False)
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, error.message)
            raise   
    #__remAMemConnFromMember Ends here

    def isAValidMember(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MemnberId':'','Auth':''}
            usage:          <getAGroupDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            isValidMember = self.globalInstance._Global__False 
            myArgKey = ['Main','Auth']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myArgKey = ['MemberId']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData['Main'].keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member 
            commenting below statement, this will be done by BPS processes
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(myMainArgData.get('Auth'),'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})
            '''
            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

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
    # isAValidMember Ends here