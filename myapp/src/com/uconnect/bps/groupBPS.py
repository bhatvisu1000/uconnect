    '''
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    GGGGGGGGGGGGG       RRRRRRRRRRR          OOOOOOOOOOOO       UU          UU      PPPPPPPPPPPP
    GG                  RR       RR         OO          OO      UU          UU      PP         PP
    GG                  RR       RR         OO          OO      UU          UU      PP         PP
    GG    GGGGGGG       RRRRRRRRRRR         OO          OO      UU          UU      PPPPPPPPPPPP
    GG         GG       RR        RR        OO          OO      UU          UU      PP
    GG         GG       RR         RR       OO          OO      UU          UU      PP
    GGGGGGGGGGGGG       RR          RR       OOOOOOOOOOOO       UUUUUUUUUUUUUU      PP
    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    '''

    def __buildInitGroupData(self, argRequestDict):

        #argMainDict,argAddressDict,argContactDict
        try:
            # Preparing document:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))

            myMainArgData = self.utilityInstance.getCopy(argRequestDict)            
            myArgKey = ['GroupName','MemberId']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myInitGroupData = self.utilityInstance.getTemplateCopy(self.globalInstance._Global__member)
            myInitGroupData['GroupName'] = myMainArgData['GroupName']
            myInitGroupData['MemberId'] = myMainArgData['MemberId']
            myGroupId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__groupColl)
            myInitMemberData['_id'] = myMemberId

            ''' build initial history data '''
            myInitGroupData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
            myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitGroupData))

            return myInitGroupData

        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    #__buildInitGroupData Ends here

    def isAMemberGroupNameInUse(self, argRequestDict):
        ''' check if the group name is already in use for this member'''
        try:
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            isGroupNameInUse = self.globalInstance._Global__False 
            myArgKey = ['Main','Auth']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            myArgKey = ['GroupName','MemberId']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData['Main'], myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData['Main'].keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            myCriteria = {'Main.MemberId':myMainArgData['Main']['MemberId'],'Main.GroupName':myMainArgData['Main']['GroupName']}
            myProjection={'_id':1}
            myFindOne = True

            myGroupData = self.mongoDbInstance.findDocument(self.globalInstance._Global__groupColl, myCriteria, myProjection, myFindOne)

            ''' we need to make sure if "Data" key is in Result set from above find, it must not be empty and must have "_id" key in it'''
            if 'Data' in myGroupData and myGroupData.get('Data') and '_id' in myGroupData.get('Data')[0]:
                myGroupId = self.utilityInstance.extr1stDocFromResultSets(myGroupData)['_id'] 
            else:
                myGroupId = None
            #fi
            if myGroupId:
                isGroupNameInUse = self.globalInstance._Global__True 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
            else:
                isGroupNameInUse = self.globalInstance._Global__False 
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'GroupName [{group}] is not in use'.format(group=str(myMainArgData['Main']['GroupName'])))                
            #fi

            ''' build response data '''
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find',isGroupNameInUse)
            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{errmsg}]'.format(errmsg=error.errorMsg))
            isGroupNameInUse = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Invalid Auth Key; error [{errmsg}] occurred'.format(errmsg=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            return myResponse
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{errmsg}]'.format(error=error.errorMsg))
            isGroupNameInUse = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Arg validation error; error [{errmsg}] occurred'.format(errmsg=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isGroupNameInUse)            
            return myResponse
        except Exception as error:
            myModuleLogger.exception('Error [{errmsg}]'.format(errmsg=error.message))
            isGroupNameInUse = self.globalInstance._Global__Error
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'An error [{errmsg}] occurred'.format(errmsg=error.message))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error',isValidMember)            
            return myResponse

    def createAMemGroup(self,argRequestDict):
        ''' 
            Description:    Create a Member's group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MainArg': {'GroupName':'<GroupName>','MeberId':'<owner of group>'}}
            usage:          <createAMemGroup(<argRequestDict>)
            Return:         Json object
            Collection:     Group: Insert a record in Group collection
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else
                myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            #fi

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgKey = ['GroupName','Auth','ResponseMode']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            # validating group name
            myGroupNameValArg = {'Main':{'GroupName':myMainArgData['GroupName'], 'MemberId': myMainArgData['MemberId']}}
            if self.isAMemberGroupNameInUse(myGroupNameValArg):
                raise com.uConnect.core.error.DuplicateGroup('Duplicate group Name [{group}]'.format(group=myMainArgData['GroupName']))
            #fi

            # Preparing document:
            myGroupData = self.__buildInitGroupData(myMainArgData['Main'])
            myModuleLogger.info('Creating new Group, data [{doc}]'.format(doc=myGroupData))

            #creating a member group
            myGroupResult =  self.mongoDbInstance.InsertOneDoc(self.globalInstance._Global_groupColl, myGroupData)
            myGroupId = myGroupResult['_id']
            myGroupResultStatus = self.utilityInstance.getCreateStatus(myGroupResult)

            if myGroupResultStatus == self.globalInstance._Global__Success:
                # Building response data
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)
                myGroupArg = {'Main':{'ResponseMode':self.globalInstance._Global__Internal, '_id':myGroupId}}
                myGroupDetail = self.getAGroupDetail(myGroupArg)
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find', myGroupDetail)
            else:
                myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess)                
                myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Find')
            #fi
            
            ''' dont need information to be saved in Member collection, 
            if
                myGroupId = myGroupResult['_id'] 
                myMainArgData.update({'GroupId':myGroupId})
                myLogger.info('Group [{group}] creation is successful, now linking to member[{member}]'.
                    format(group=myGroupId, member=myGroupData['Main']['MemberId']))
                
                myLinkedResult = self.linkAMember2Group(myLinkedData)
                myLinkedResultStatus = self.utilityInstance.getUpdateStatus(myLinkedResult)
                
                if myLinkedResultStatus == self.globalInstance._Global__UnSuccess:
                    #Link was unsuccessful, need to clean up the data (delete group collection just got inserted)
                    myLogger.info('Linking group [{group}] to member[{member}] is unsuccessful, removing group'.
                        format(group=myGroupId, member=myGroupData['Main']['MemberId']))
                    myDeleteResult = self.mongoDbInstance.DeleteDoc(self.globalInstance._Global_groupColl,{'_id':myGroupId})
                else:
                    myLogger.info('Linking group [{group}] to member[{member}] is successful'.
                        format(group=myGroupId, member=myGroupData['Main']['MemberId']))

                    # Building response data

                    myResponseDataDict = self.utilityInstance.builInternalRequestDict({'Data':{'_id':myGroupId}})
                    myResponseData = self.getAGroupDetail(myResponseDataDict)
                    #print('response data',myResponseData)
                    myResponse = self.utilityInstance.buildResponseData(argRequestDict['Request']['Header']['ScreenId'],myGroupResult,'Insert', myResponseData)

                    return myResponse
                #end if
            
            else:
                # Creation of group was unsuccessful, no need to send the data back
                # Build response data
                myResponse = self.utilityInstance.buildResponseData(
                    argRequestDict['Request']['Header']['ScreenId'],myGroupResult,'Insert')
                return myResponse
            #end if
            '''

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except com.uConnect.core.error.DuplicateGroup as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.errorMsg))
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            myRequestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Error [{err}] occurred'.format(err=error.message)) 
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myRequestStatus,'Error')
        finally:
            return myResponse

    def getGroupDetails4AMember(self,argRequestDict):
        ''' 
            Description:    Find all group member participates and all participating member
            argRequestDict:     Json/Dict; Following key name is expected in this dict/json object
            usage:          <getGroupDetails4AMember(<argReqJsonDict>)
            Return:         Json object
        '''
        # we need to check which arguments are passed; valid argument is Phone/Email/LastName + FirstName

        #print (argRequestDict)

        # raise an user defined exception here
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            if 'MainArg' in argRequestDict:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            else:
                myMainArgData = self.utilityInstance.getCopy(argRequestDict['MainArg'])
            #fi

            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            myRequestStatus = self.utilityInstance.getCopy(self.globalInstance._Global__RequestStatus)
            myArgKey = ['Auth','ResponseMode']

            ''' validating arguments '''
            myArgValidationResults = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)
            myArgValidation = self.utilityInstance.extractValFromTuple(myArgValidationResults,0)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Mainarg validation error; main arg(s)[{arg}], missing/empty key(s)[{key}]'.format(arg=myMainArgData.keys(), key=self.utilityInstance.extractValFromTuple(myArgValidationResults,1)))
            #fi

            ''' Validate auth key for this request'''
            if not (self.securityInstance._Security__isValAuthKeyInternal(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['AuthKey'], me=self.utilityInstance.whoAmI()))
            #fi

            myModuleLogger.info('Finding a group details [{arg}]'.format(arg=myMainArgData))

            myCriteria = {'_id':myMainArgData['GroupId']}
            myProjection={'Main':1,'Address':1,'Contact':1}
            myFindOne = True

            myGroupData = self.mongoDbInstance.findDocument(self.globalInstance._Global__groupColl, myCriteria,myProjection,myFindOne)
            
            ''' build response data '''            
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'],myGroupData,'Find')

            return myResponse

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

    def linkAMember2Group(self,argRequestDict):
        ''' 
            Description:    Linke a member 2 a Group
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'Request': 
                                {'Header':{ScreenId':'','ActionId':'',Page:},
                                {'MainArg': {'GroupId':'','MemberId'}}
                            }
            usage:          <linkAMember2Member(<argReqJsonDict>)
                            MainArg{'GroupId':'','MemberId':''}
            Return:         Json object
        '''
        try:
            
            ''' Initialization & Validation '''

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg = argRequestDict))
            myLinkedData = {}

            myArgValidation = self.utilityInstance.valBPSArguments(argRequestDict)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error {arg}'.format(arg=argRequestDict))

            ''' Extracting MainArg from data from Request '''            
            myMainArgData = self.utilityInstance.extMainArgFromReq(argRequestDict)

            ''' Preparing document:    '''

            myLinkedData = {'LinkedBy':{'GroupId':myMainArgData['GroupId']}}
            myMemberId = myMainArgData['MemberId']
            myGroupId = myMainArgData['GroupId']
            myCriteria = {'_id':myMemberId}
            myModuleLogger.info('Adding member to a group [{memberId} --> {groupId}]'.format(
                memberId=myMemberId, groupId=myGroupId))

            ''' Updating document (Group Collection, add participant) '''
            myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myLinkedData, 'addToSet',False)
            myUpdateStatus = self.utilityInstance.getUpdateStatus(myLinkedResult)
            
            ''' will link member to group in member collection, if member was associated '''

            if myUpdateStatus == self.globalInstance._Global__Success:
                myModuleLogger.info('Member -> Group connection successful, adding participant in group')

                ''' Adding participant in Group collection  '''
                myModuleLogger.info('Adding participant [{memberId}] to group [{groupId}]'.format(
                    memberId=myMemberId, groupId=myGroupId))

                ''' preparing document '''
                myParticipantdData = {'Participants':{'MemberId':myMemberId,'When':datetime.datetime.utcnow()}}
                myCriteria = {'_id':myGroupId}

                '''executing update document '''
                myLinkedResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global_groupColl, myCriteria, myParticipantdData, 'addToSet',False)

                myModuleLogger.info('Member [{memberId} linked to group {groupId}]'.format(
                    memberId=myMemberId, groupId=myGroupId))

            ''' Build response data '''
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myLinkedResult,'Update')

            return myResponse

        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise error
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise error

