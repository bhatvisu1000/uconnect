import sys,datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
#from com.uconnect.core.security import Security
from com.uconnect.core.member import Member
from com.uconnect.core.activity import Activity

myLogger = logging.getLogger('uConnect')

@Singleton
class Connections(object):
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
        self.activityInstance = Activity.Instance()
        self.memberInstance = Member.Instance()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def __AddAConnection(self, argRequestDict):
        ''' This mehtod is for building a fresh new connection
            usage:          <__AddMember2MemberConnection(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','Auth']
            Return:         Success/UnSuccess
        '''
        try:            
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            ''' declaring/initializing variables '''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            isReqConnectionAdded = self.globalInstance._Global__False
            isInvConnectionAdded = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False
            myArgKey = ['_id','Type','ConnectionId','ConnectionType']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.\
                    format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' validating Requestor entity
            must be a valid id and its connection can not be same '''
            if myMainArgData['Type'] == self.globalInstance._Global__member:
                #validating
                if myMainArgData['_id'] == myMainArgData['ConnectionId']:
                    raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Member [{member}] and it\'s Connection[{connect}] can not be same'.format(member=myMainArgData['MemberId'], connect=myMainArgData['ConnectMemberId'] ))                
                #fi
                myMemberValidationData = {'Member':{'_id':myMainArgData['_id']},'ResponseMode':self.globalInstance._Global__InternalRequest}
                if (not self.memberInstance._Member__isAValidMember(myMemberValidationData)):
                    raise com.uconnect.core.error.MissingArgumentValues('Arg validation error, Invalid MemberId [{member}]'.format(member=myMainArgData['MemberId'] ))
                #fi
                myRequestorCollection = self.globalInstance._Global__memberColl
                # requestor is Member and it has been validated, preparing Invitee (revese)connection which will be a member
                # connection
                myInviteeCriteria = {'_id':myMainArgData['ConnectionId']}
                myInviteeConn = self.utilityInstance.getConnTemplateCopy(self.globalInstance._Global__member)
                myInviteeConn['Id'] = myMainArgData['_id']
                myInviteeConn['Status'] = self.utilityInstance.getConnStatus4Action('New Connection','Invitee')
                myInviteeConnData = {'Connections': myInviteeConn}

                self.myModuleLogger.debug('Invitee [{invitee}] connection document [{doc}] prepared'.
                    format(invitee=myMainArgData['ConnectionId'],doc=myInviteeConn))

            elif myMainArgData['Type'] == 'Agent':
                pass
            #fi

            #validating connection id
            if myMainArgData['ConnectionType'] == self.globalInstance._Global__member:
                # this is a member 2 member connection
                myMemberValidationData = {'Member':{'_id':myMainArgData['ConnectionId']},'ResponseMode':self.globalInstance._Global__InternalRequest}
                if (not self.memberInstance._Member__isAValidMember(myMemberValidationData)):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Arg validation error, Invalid Connect MemberId [{member}]'.format(member=myMainArgData['ConnectionId'] ))
                #fi
                myInviteeCollection = self.globalInstance._Global__memberColl
                # Preparing Requestor connection
                myRequestorCriteria = {'_id':myMainArgData['_id']}
                myRequestorConn = self.utilityInstance.getConnTemplateCopy(self.globalInstance._Global__member)
                myRequestorConn['Id'] = myMainArgData['ConnectionId']
                myRequestorConn['Status'] = self.utilityInstance.getConnStatus4Action('New Connection','Requestor')
                myRequestorConnData = {'Connections': myRequestorConn}

                self.myModuleLogger.debug('Requestor [{requestor}] connection document [{doc}] prepared'.
                    format(requestor=myMainArgData['_id'], doc=myRequestorConn))

            elif myMainArgData['ConnectionType'] == 'Agent':
                pass
            #fi

            #persisiting requestor connection data
            myReqConnectionResult = self.mongoDbInstance.UpdateDoc(myRequestorCollection, myRequestorCriteria, myRequestorConnData,'addToSet',False)
            if self.utilityInstance.getUpdateStatus(myReqConnectionResult) == self.globalInstance._Global__Success:
                # Requestor connection created successfully
                self.myModuleLogger.debug('Requestor connection [{conn}] created successfully, result [{result}]'.
                    format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + myMainArgData['ConnectionType']\
                            + ' ' + str(myMainArgData['ConnectionId']), result=myReqConnectionResult))

                isReqConnectionAdded = self.globalInstance._Global__True

                #building invitee connection (revese of requestor)
                myInvConnectionResult =  self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'addToSet',False)
                if self.utilityInstance.getUpdateStatus(myInvConnectionResult) == self.globalInstance._Global__Success:
                    #invitee connection created successful
                    isInvConnectionAdded = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                    # recording this successful activity; requestor
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg( \
                        myMainArgData['_id'], myRequestorCollection,self.globalInstance._Global__Internal,\
                        'Requestor Connection [{conn}] created successfully'.format(conn=myMainArgData['Type'] + ' ' + \
                        str(myMainArgData['_id']) + ' --> ' + myMainArgData['ConnectionType'] + ' ' + \
                        str(myMainArgData['ConnectionId'])) ))
                    #recording this successful activity; invitee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(\
                        myMainArgData['_id'],myInviteeCollection,self.globalInstance._Global__Internal,\
                        'Invitee Connection [{conn}] created successfully'.format(conn=myMainArgData['ConnectionType'] + ' ' + \
                        str(myMainArgData['ConnectionId']) + ' --> ' + myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])) ))
                else:                    
                    ''' invitee connection is not successful, remvoving requestor connection to maintain the data integrity '''
                    self.myModuleLogger.debug('Invitee connection [{conn}] creation unsuccessful, result [{result}]'.
                        format(conn = myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId'])  + ' -> ' + \
                                myMainArgData['Type'] + ' ' + str(myMainArgData['_id']), result=myInvConnectionResult))
                    ''' rolling back previous Requestor connection'''
                    self.mongoDbInstance.UpdateDoc(myInviteeCollection, myRequestorCriteria, myRequestorConnData, 'pull',False)
                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not build Invitee [{inv}] while performing "Add Connection" task'.
                            format(inv=myMainArgData['ConnectionId']))
                #fi
            else:
                self.myModuleLogger.debug('Requestor connection [{conn}] creation unsuccesful, result [{result}]'.
                    format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + myMainArgData['ConnectionType']\
                            + ' ' + str(myMainArgData['ConnectionId']), result=myReqConnectionResult))
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Could not build Requestor [{req}] while performing "Add Connection" task'.
                            format(req=myMainArgData['_id']))
            #fi
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isReqConnectionAdded and (not isInvConnectionAdded) and (not isCleanUpDone):
                #print(isReqConnectionAdded,isInvConnectionAdded,isCleanUpDone)
                self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myRequestorCriteria, myRequestorConnData, 'pull',False)                
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
        finally:            
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise 
    #__AddMember2MemberConnection Ends here

    def __acceptInvitation(self, argRequestDict):
        ''' This method is invoked by Invitee; update the status of connection status in each other (Requestor/Invitee)'s connection list 
            usage:          <__AcceptInvitation(<argReqJsonDict>)
                            MainArg['_id','Type','ConnectionId','ConnectionType','Auth']
            Return:         Success/UnSuccess
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            ''' declaring/initializing variables '''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            isReqConnectionAdded = self.globalInstance._Global__False
            isInvConnectionAdded = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False

            if myMainArgData['Type'] == self.globalInstance._Global__member:
                myInviteeCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['Type'] == self.globalInstance._Global__agent:
                myInviteeCollection = self.globalInstance._Global__agentColl
            #fi

            if myMainArgData['ConnectionType'] == self.globalInstance._Global__member:
                myRequestorCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['ConnectionType'] == self.globalInstance._Global__agent:
                myRequestorCollection = self.globalInstance._Global__agentColl
            #fi

            ''' validating arguments '''
            myArgKey = ['_id','Type','ConnectionId','ConnectionType']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request (we dont need auth val since it has been already performed by BPS process,
            we need to ensure that any call to this process is from BPS process '''
            
            ''' we need to check if this is a valid request; is this invitation pending for this id (id is invitee)'''
            myInviValCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'],\
                                'Connections.Type': myMainArgData['ConnectionType'],\
                                'Connections.Status':self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
            #print('Invitee validation',myInviValCriteria)
            if self.mongoDbInstance.findTotDocuments(myInviteeCollection, myInviValCriteria) == 0:
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Invalid Request, Invitee [{invitee}] does not have any connection pending from [{requestor}]'.\
                            format( invitee=myMainArgData['Type'] + str(myMainArgData['_id']),\
                                    requestor= myMainArgData['ConnectionType'] + str(myMainArgData['ConnectionId']) ))
            #fi

            ''' Building Invitee connection data'''
            myInviteeCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'], \
                                 'Connections.Type': myMainArgData['ConnectionType'],\
                                 'Connections.Status': self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
            myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getConnStatus4Action('Accept Connection','Invitee')}

            ''' Building Requestor connection data '''
            myRequestorCriteria = {'_id':myMainArgData['ConnectionId'], 'Connections.Id':myMainArgData['_id'],\
                                   'Connections.Type':myMainArgData['Type'],\
                                   'Connections.Status': self.utilityInstance.getConnStatus4Action('New Connection','Requestor')}
            myRequestorConnData = {'Connections.$.Status':self.utilityInstance.getConnStatus4Action('Accept Connection','Requestor')}

            ''' persisitng changes in database, Updating invitee's connection status '''
            myConnectionResult = self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'set',False)
            self.myModuleLogger.debug('Invitee connection status updated, [{conn}], result [{result}] '.
                format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + \
                              myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']),\
                              result=myConnectionResult))

            if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:
                # Invitee connection update is successful, persisiting Requestor's connection status update
                isInvConnStatusUpdated = self.globalInstance._Global__True
                myConnectionResult = self.mongoDbInstance.UpdateDoc(myRequestorCollection,myRequestorCriteria,myRequestorConnData,'set',False)
                self.myModuleLogger.debug('Requestor connection status updated, [{conn}], result [{result}] '.
                format(conn = myMainargData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId'])  + ' -> ' + \
                              myMainArgData['Type'] + ' ' + str(myMainArgData['_id']),\
                              result=myConnectionResult))

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:
                    ''' Requestor connection update is successful, undo Invitee connection change '''
                    isInvConnStatusUpdated = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                    # recording this successful activity; Invitee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg( \
                        myMainArgData['_id'], myRequestorCollection,self.globalInstance._Global__Internal,\
                        'Invitee accepted connection [{conn}] '.format(conn=myMainArgData['Type'] + ' ' + str(myMainArgData['_id']) + \
                        ' --> ' + myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId'])) ))
                    #recording this successful activity; invitee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(\
                        myMainArgData['_id'],myInviteeCollection,self.globalInstance._Global__Internal,\
                        'Requestor connection [{conn}] status updated'.format(conn=myMainArgData['ConnectionType'] + ' ' + \
                        str(myMainArgData['ConnectionId']) + ' --> ' + myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])) ))

                else:
                    ''' Requestor connection update is not successful, undo Invitee connection change '''
                    self.myModuleLogger.debug('Requestor [{req}] connection update unsuccessful, results [{result}]'.
                        format(req=myMainArgData['Connectiontype'] + ' ' + str(myMainArgData['ConnectionId']), result=myReqConnResults ))

                    myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
                    self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'set',False)
                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                        'Requestor [{req}] connection status [{status}] update unsuccessful'.\
                        format(req=myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']), \
                               status=self.globalInstance._Global__Accepted_Req_ConnectionStatus))
                    self.myModuleLogger.debug('undo changes to Invitee\'s connection successful, result [{result}]'.\
                        format(result=myReqConnResults))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                    'Invitee [{inv}] connection status [{status}] update unsuccessful'. \
                    format(inv= myMainArgData['Type'] + ' ' + str(myMainArgData['_id']), 
                            status=self.globalInstance._Global__Accepted_Inv_ConnectionStatus))
            #fi
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,error.errorMsg)
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isInvConnStatusUpdated and (not isReqConnStatusUpdated) and (not isCleanUpDone):
                myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
                self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'set',False)
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
        finally:
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise
            #fi
    #__AcceptInvitation Ends here

    def __rejectInvitation(self, argRequestDict):
        ''' This method is invoked by Invitee; remove the connection from each other (Requestor/Invitee)'s connection list 
            usage:          <__rejectInvitation(<argReqJsonDict>)
                            MainArg['_id','Type','ConnectionId','ConnectionType','Auth']
            Return:         Success/UnSuccess
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            ''' declaring/initializing variables '''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            isInvConnStatusRemoved = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False

            if myMainArgData['Type'] == self.globalInstance._Global__member:
                myInviteeCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['Type'] == self.globalInstance._Global__agent:
                myInviteeCollection = self.globalInstance._Global__agentColl
            #fi

            if myMainArgData['ConnectionType'] == self.globalInstance._Global__member:
                myRequestorCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['ConnectionType'] == self.globalInstance._Global__agent:
                myRequestorCollection = self.globalInstance._Global__agentColl
            #fi

            ''' validating arguments '''
            myArgKey = ['_id','Type','ConnectionId','ConnectionType']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request (we dont need auth val since it has been already performed by BPS process,
            we need to ensure that any call to this process is from BPS process '''
            
            ''' we need to check if this is a valid request; is this invitation pending for this id (id is invitee)'''
            myInviValCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'],\
                                'Connections.Type': myMainArgData['ConnectionType'],\
                                'Connections.Status':self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}

            #print('Invitee validation',myInviValCriteria)
            if self.mongoDbInstance.findTotDocuments(myInviteeCollection, myInviValCriteria) == 0:
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Invalid Request, Invitee [{invitee}] does not have pending connection from [{requestor}]'.\
                            format( invitee=myMainArgData['Type'] + str(myMainArgData['_id']),\
                                    requestor= myMainArgData['ConnectionType'] + str(myMainArgData['ConnectionId']) ))
            #fi
            ''' Building Invitee connection data to be removed'''
            myInviteeCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'], \
                                 'Connections.Type': myMainArgData['ConnectionType'],\
                                 'Connections.Status': self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
            myInviteeConnData = {'Connections':{'Id': myMainArgData['ConnectionId'],'Type': myMainArgData['ConnectionType'],\
                                                'Status' : self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}}

            ''' Building Requestor connection data to be removed'''
            myRequestorCriteria = {'_id':myMainArgData['ConnectionId'], 'Connections.Id':myMainArgData['_id'],\
                                   'Connections.Type':myMainArgData['Type'],\
                                   'Connections.Status': self.utilityInstance.getConnStatus4Action('New Connection','Requestor')}
            myRequestorConnData = {'Connections':\
                                        {'Id': myMainArgData['_id'],'Type': myMainArgData['Type'],\
                                         'Status' : self.utilityInstance.getConnStatus4Action('New Connection','Requestor')}}

            ''' building backup data '''
            myInviteeConnBkupData = self.utilityInstance.extr1stDocFromResultSets(\
                self.mongoDbInstance.findDocument(myInviteeCollection,myInviteeCriteria,{'_id':1,'Connections':1},True))
            myRequestorConnBkupData = self.utilityInstance.extr1stDocFromResultSets(\
                self.mongoDbInstance.findDocument(myRequestorCollection,myRequestorCriteria,{'_id':1,'Connections':1},True))

            ''' persisitng changes in database, removing invitee's connection '''
            myConnectionResult = self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'pull',False)

            self.myModuleLogger.debug('Invitee rejected request, connection [{conn}] removed, result [{result}] '.
                format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + \
                          myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']),\
                          result=myConnectionResult))

            if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                # Invitee's connection removed.  removing Requestor's connection 
                isInvConnStatusRemoved = self.globalInstance._Global__True
                myConnectionResult = self.mongoDbInstance.UpdateDoc(myRequestorCollection,myRequestorCriteria,myRequestorConnData,'pull',False)
                self.myModuleLogger.debug('Invitee rejected request, Requestor connection [{conn}] removed, result [{result}] '.
                    format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + \
                              myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']),\
                              result=myConnectionResult))

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                    # Requestor connection update is successful, undo Invitee connection change
                    isInvConnStatusRemoved = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                    # recording this successful activity; Invitee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg( \
                        myMainArgData['_id'], myRequestorCollection,self.globalInstance._Global__Internal,\
                        'Invitee rejected connection [{conn}], removing this connection '.format(conn=myMainArgData['Type'] + ' ' + str(myMainArgData['_id']) + \
                        ' --> ' + myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId'])) ))

                    #recording this successful activity; invitee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(\
                        myMainArgData['_id'],myInviteeCollection,self.globalInstance._Global__Internal,\
                        'Invitee rejected connection [{conn}], removing this connection'.format(conn=myMainArgData['ConnectionType'] + ' ' + \
                        str(myMainArgData['ConnectionId']) + ' --> ' + myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])) ))
                else:

                    ''' Requestor connection update is not successful, undo Invitee connection change '''
                    self.myModuleLogger.debug('Requestor [{req}] connection update unsuccessful, results [{result}]'.
                        format(req=myMainArgData['Connectiontype'] + ' ' + str(myMainArgData['ConnectionId']), result=myReqConnResults ))

                    self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, \
                        {'Connections':{myInviteeConnBkupData['Connections'][0]}}, 'addToSet',False)

                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                        'Requestor [{req}] connection restored'.format(req=myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']) ))

                    self.myModuleLogger.debug('undo changes to Invitee\'s connection successful, result [{result}]'.\
                        format(result=myReqConnResults))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                    'Invitee [{inv}] connection status [{status}] update unsuccessful'. \
                    format(inv= myMainArgData['Type'] + ' ' + str(myMainArgData['_id']), 
                            status=self.globalInstance._Global__Accepted_Inv_ConnectionStatus ))
            #fi
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isInvConnStatusRemoved and (not isReqConnStatusUpdated) and (not isCleanUpDone):
                myInviteeConnData = {'Connections.$.Status':self.utilityInstance.getConnStatus4Action('New Connection','Invitee')}
                self.mongoDbInstance.UpdateDoc(myInviteeCollection, myInviteeCriteria, myInviteeConnData, 'set',False)
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
        finally:
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise
            #fi
    #__rejectInvitation end here

    def __removeConnection(self, argRequestDict):
        ''' Removes the connection from each other (Requestor/Requestee)'s connection list 
            usage:          <__rejectInvitation(<argReqJsonDict>)
                            MainArg['_id','Type','ConnectionId','ConnectionType','Auth']
            Return:         Success/UnSuccess
            Requestor   --> who initiated the removal of a connection
            Requestee   --> whose connection to be removed from requestor
            Connection will be removed from Requestor/Requstee's conneciton list for each other 
        '''
        try:
            #myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            ''' declaring/initializing variables '''
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            isRequestorConnRemoved = self.globalInstance._Global__False
            isRequesteeConnRemoved = self.globalInstance._Global__False
            isCleanUpDone = self.globalInstance._Global__False

            if myMainArgData['Type'] == self.globalInstance._Global__member:
                myRequestorCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['Type'] == self.globalInstance._Global__agent:
                myRequestorCollection = self.globalInstance._Global__agentColl
            #fi

            if myMainArgData['ConnectionType'] == self.globalInstance._Global__member:
                myRequesteeCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['ConnectionType'] == self.globalInstance._Global__agent:
                myRequesteeCollection = self.globalInstance._Global__agentColl
            #fi

            ''' validating arguments '''
            myArgKey = ['_id','Type','ConnectionId','ConnectionType']
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request (we dont need auth val since it has been already performed by BPS process,
            we need to ensure that any call to this process is from BPS process '''
            
            ''' we need to check if this is a valid request; is this invitation pending for this id (id is invitee)'''
            myRequestorValCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'],\
                                'Connections.Type': myMainArgData['ConnectionType']}

            if self.mongoDbInstance.findTotDocuments(myRequestorCollection, myRequestorValCriteria) == 0:
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Invalid Request, Requestor [{requestor}] does not have any connection from [{requestee}] to be removed'.\
                            format( requestor=myMainArgData['Type'] + str(myMainArgData['_id']),\
                                    requestee= myMainArgData['ConnectionType'] + str(myMainArgData['ConnectionId']) ))
            #fi

            ''' Building Invitee connection data to be removed'''
            myRequestorCriteria = {'_id':myMainArgData['_id'],'Connections.Id':myMainArgData['ConnectionId'], \
                                 'Connections.Type': myMainArgData['ConnectionType']}
            myRequestorConnData = {'Connections':{'Id': myMainArgData['ConnectionId'],'Type': myMainArgData['ConnectionType']}}

            ''' Building Requestor connection data to be removed'''
            myRequesteeCriteria = {'_id':myMainArgData['ConnectionId'], 'Connections.Id':myMainArgData['_id'],\
                                   'Connections.Type':myMainArgData['Type']}
            myRequesteeConnData = {'Connections':{'Id': myMainArgData['_id'],'Type': myMainArgData['Type']}}

            ''' building backup data '''
            myRequestorConnBkupData = self.utilityInstance.extr1stDocFromResultSets(\
                self.mongoDbInstance.findDocument(myRequestorCollection,myRequestorCriteria,{'_id':1,'Connections':1},True))
            myRequesteeConnBkupData = self.utilityInstance.extr1stDocFromResultSets(\
                self.mongoDbInstance.findDocument(myRequesteeCollection,myRequesteeCriteria,{'_id':1,'Connections':1},True))

            ''' persisitng changes in database, removing invitee's connection '''
            myConnectionResult = self.mongoDbInstance.UpdateDoc(myRequestorCollection, myRequestorCriteria, myRequestorConnData, 'pull',False)
            
            self.myModuleLogger.debug('Requestor connection [{conn}] removed, result [{result}] '.
                format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + \
                          myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']),\
                          result=myConnectionResult))

            if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                # Requestor's connection removed.  removing Requestor's connection 
                isRequestorConnRemoved = self.globalInstance._Global__True
                myConnectionResult = self.mongoDbInstance.UpdateDoc(myRequesteeCollection,myRequesteeCriteria,myRequesteeConnData,'pull',False)

                self.myModuleLogger.debug('Requestee connection [{conn}] removed, result [{result}] '.
                    format(conn = myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])  + ' -> ' + \
                              myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']),\
                              result=myConnectionResult))

                if self.utilityInstance.getUpdateStatus(myConnectionResult) == self.globalInstance._Global__Success:

                    ''' Requestor connection update is successful, undo Requestor connection change '''
                    isRequesteeConnRemoved = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)

                    # recording this successful activity; Requestor
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg( \
                        myMainArgData['_id'], myRequestorCollection,self.globalInstance._Global__Internal,\
                        'Requestor [{req}] removed connection [{conn}]'.\
                            format(req=myMainArgData['Type'] + ' ' + str(myMainArgData['_id']),\
                                    conn=myMainArgData['Type'] + ' ' + str(myMainArgData['_id']) + ' --> ' + \
                                    myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId'])) ))

                    #recording this successful activity; Requestee
                    self.activityInstance._Activity__logActivity(self.utilityInstance.buildActivityArg(\
                        myMainArgData['_id'],myRequesteeCollection,self.globalInstance._Global__Internal,\
                        'Requestor [{req}] removed connection, removing connection [{conn}] from requestee'.\
                            format(req=myMainArgData['Type'] + ' ' + str(myMainArgData['_id']), \
                                conn=myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']) + ' --> ' + \
                                myMainArgData['Type'] + ' ' + str(myMainArgData['_id'])) ))
                else:
                    ''' Requestee connection update is not successful, undo Requestor connection change '''
                    self.myModuleLogger.debug('Requestee [{req}] connection update unsuccessful, results [{result}]'.
                        format(req=myMainArgData['Connectiontype'] + ' ' + str(myMainArgData['ConnectionId']), result=myReqConnResults ))

                    self.mongoDbInstance.UpdateDoc(myRequestorCollection, myRequestorCriteria, \
                        {'Connections':{myRequestorConnBkupData['Connections'][0]}}, 'addToSet',False)

                    isCleanUpDone = self.globalInstance._Global__True
                    myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                        'Requestor [{req}] connection restored'.format(req=myMainArgData['ConnectionType'] + ' ' + str(myMainArgData['ConnectionId']) ))
                    self.myModuleLogger.debug('undo changes to Requestor\'s connection successful, result [{result}]'.\
                        format(result=myReqConnResults))
                #fi
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                    'Requestor [{req}] connection status [{status}] update unsuccessful'. \
                    format(req= myMainArgData['Type'] + ' ' + str(myMainArgData['_id']), 
                            status=self.globalInstance._Global__Accepted_Inv_ConnectionStatus ))
            #fi
            return myRequestStatus
        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)
            #raise
        except Exception as error:
            myErrorMessage = repr(sys.exc_info()[1])
            #print('error',string(myErrorMessage))
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            ''' we need to ensure if cleanup is required should there be an issue during failure of Invitee connection '''
            if isRequestorConnRemoved and (not isRequesteeConnRemoved) and (not isCleanUpDone):
                self.mongoDbInstance.UpdateDoc(myRequestorCollection, myRequestorCriteria, \
                    {'Connections':{myRequestorConnBkupData['Connections'][0]}}, 'addToSet',False)
            #fi
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess, myErrorMessage)
            print(myRequestStatus)
            #raise
        finally:
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise
            #fi
        #__reoveConnection Ends here

    def __favoriteConnection(self,argRequestDict):
        ''' 
            Description:    Change favorite of a connection
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
            usage:          <__MarkConnectionFavorite(<argReqJsonDict>)
                            MainArg{'_id','Type','ConnectionId','ConnectionType','Favorite'}
            Return:         Json object
        '''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            # validating arguments
            myArgKey = ['_id','Type','ConnectionId','ConnectionType','Favorite']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), \
                        key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if myMainArgData['Favorite'] not in ["0","1"]:
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Expecting favorite value in ["0","1"], got [{favorite}]'.format(favorite=myMainArgData['Favorite']))
            #fi

            if myMainArgData['Type'] == self.globalInstance._Global__member:
                myCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['Type'] == self.globalInstance._Global__agent:
                myCollection = self.globalInstance._Global__agentColl
            #fi

            # validating this connection
            myValidConnectionArg = {'_id':myMainArgData['_id'], 'Connections.Id':myMainArgData['ConnectionId'], \
                                    'Connections.Type': myMainArgData['ConnectionType'],\
                                    'Connections.Status' :{'$in':['Accepted','Valid']}}
            if self.mongoDbInstance.findTotDocuments(myCollection,myValidConnectionArg) == 0:
                raise com.uconnect.core.error.MissingArgumentValues('No connection found for this request [{request}]'.\
                    format( request=myMainArgData['Type'] + str(myMainArgData['_id']) + ': Connection(' + \
                        myMainArgData['ConnectionType'] + str(myMainArgData['ConnectionId']) + ')' ))
            #fi

            ''' Preparing document:    '''
            myCriteria = {'_id':myMainArgData['_id'],'Connections.Id': myMainArgData['ConnectionId'], \
                            'Connections.Type':myMainArgData['ConnectionType']}
            myFavoriteData = {"Connections.$.Favorite":int(myMainArgData['Favorite'])}

            ##db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})
            myMarkFavoriteStatus =  self.mongoDbInstance.UpdateDoc(myCollection, myCriteria, myFavoriteData, 'set',False)
            print('Favorite Status:',myMarkFavoriteStatus)
            if self.utilityInstance.getUpdateStatus(myMarkFavoriteStatus) == self.globalInstance._Global__Success:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                    myMarkFavoriteStatus.get('Message'))
            #fi            

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)            
        except Exception as error:
            myErrorMessage = repr(sys.exc_info())
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)            
        finally:
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise
            #fi
        #__favoriteConnection Ends here

    def __blockConnection(self,argRequestDict):
        ''' 
            Description:    Change block of a connection
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
            usage:          <__blockConnection(<argReqJsonDict>)
                            MainArg{'_id','Type','ConnectionId','ConnectionType','Favorite'}
            Return:         Json object
        '''
        try:
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            # validating arguments
            myArgKey = ['_id','Type','ConnectionId','ConnectionType','Blocked']
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)            
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), \
                        key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            if myMainArgData['Blocked'] not in ["0","1"]:
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Expecting blocked value in ["0","1"], got [{block}]'.format(block=myMainArgData['Blocked']))
            #fi

            if myMainArgData['Type'] == self.globalInstance._Global__member:
                myCollection = self.globalInstance._Global__memberColl
            elif myMainArgData['Type'] == self.globalInstance._Global__agent:
                myCollection = self.globalInstance._Global__agentColl
            #fi

            # validating this connection
            myValidConnectionArg = {'_id':myMainArgData['_id'], 'Connections.Id':myMainArgData['ConnectionId'], \
                                    'Connections.Type': myMainArgData['ConnectionType'],\
                                    'Connections.Status' :{'$in':['Accepted','Valid']}}

            if self.mongoDbInstance.findTotDocuments(myCollection,myValidConnectionArg) == 0:
                raise com.uconnect.core.error.MissingArgumentValues('No connection found for this request [{request}]'.\
                    format( request=myMainArgData['Type'] + str(myMainArgData['_id']) + ': Connection(' + \
                        myMainArgData['ConnectionType'] + str(myMainArgData['ConnectionId']) + ')' ))
            #fi

            ''' Preparing document:    '''
            myCriteria = {'_id':myMainArgData['_id'],'Connections.Id': myMainArgData['ConnectionId'], \
                            'Connections.Type':myMainArgData['ConnectionType']}
            myFavoriteData = {"Connections.$.Blocked":int(myMainArgData['Blocked'])}

            ##db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})
            myBlockedStatus =  self.mongoDbInstance.UpdateDoc(myCollection, myCriteria, myFavoriteData, 'set',False)
            print('Blocked Status:',myBlockedStatus)
            if self.utilityInstance.getUpdateStatus(myBlockedStatus) == self.globalInstance._Global__Success:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,\
                    myBlockStatus.get('Message'))
            #fi            

        except com.uconnect.core.error.MissingArgumentValues as error:
            myErrorMessage = error.errorMsg
            self.myModuleLogger.exception('MissingArgumentValues: error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)            
        except Exception as error:
            myErrorMessage = repr(sys.exc_info())
            self.myModuleLogger.exception('Error [{myerror}]'.format(myerror=myErrorMessage))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,myErrorMessage)            
        finally:
            if 'myRequestStatus' in locals():
                return myRequestStatus
            else:
                raise
            #fi    
        #__blockConnection Ends here
