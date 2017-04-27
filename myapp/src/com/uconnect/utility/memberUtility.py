import datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.bps.factory import Factory
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
        self.factoryInstance = Factory.Instance()
        self.utilityInstance = Utility.Instance()
        self.mongoDbInstance = MongoDB.Instance()
        self.dbutilityInstance = DBUtility.Instance()
        self.globalInstance = Global.Instance()
        self.securityInstance = Security.Instance()

        self.myClass = self.__class__.__name__

    def __buildInitMembderData(self,argMainDict,argAddressDict,argContactDict):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{Main}], [{Address}], [{Contact}] received'.
            format(Main=argMainDict,Address=argAddressDict,Contact=argContactDict))

        myZipCode = argAddressDict['ZipCode']
        myCityNState = self.envInstance.getAddressCityState(myZipCode)
        myCity = myCityNState[0]
        myState = myCityNState[1]

        myInitMemberData = self.envInstance.getTemplateCopy(self.globalInstance._Global__member)
        myModuleLogger.debug('Member template [{template}]'.format(template=myInitMemberData))        

        ''' Main '''
        if ( 'LastName' in argMainDict ):
            myInitMemberData['Main']['LastName'] = argMainDict['LastName']
        if ( 'FirstName' in argMainDict ):
            myInitMemberData['Main']['FirstName'] = argMainDict['FirstName']
        if ( 'NickName' in argMainDict ):
            myInitMemberData['Main']['NickName'] = argMainDict['NickName']
        if ( 'Street' in argAddressDict ):
            myInitMemberData['Address']['Street'] = argAddressDict['Street']

        ''' Address '''
        if (not (myCity == None)) and (not(myState == None)): 
            myInitMemberData['Address']['City'] = myCity
            myInitMemberData['Address']['State'] = myState
            myInitMemberData['Address']['ZipCode'] = myZipCode
        else:
            myInitMemberData['Address']['ZipCode'] = myZipCode

        ''' Contact '''
        if ( 'Mobile' in argContactDict ):
            myInitMemberData['Contact']['Mobile'] = argContactDict['Mobile']
        if ( 'Email' in argContactDict ):
            myInitMemberData['Contact']['Email'] = argContactDict['Email']

        ''' lets get the memberid for this member '''
        myMemberId = self.mongoDbInstance.genKeyForCollection(self.globalInstance._Global__memberColl)
        myInitMemberData['_id'] = myMemberId

        ''' build initial history data '''
        myInitMemberData[self.globalInstance._Global__HistoryColumn] = self.utilityInstance.buildInitHistData() 
        myModuleLogger.info('Data [{arg}] returned'.format(arg=myInitMemberData))

        return myInitMemberData

    def __buildGetAllConnPipeline(self, argMemberId, argConnectionType):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{member}], [{conntype}]  received'.format(member=argMemberId,conntype=argConnectionType))
        myModuleLogger.debug('Building pipeline for aggregate function')

        #if argConnectionType == 'member':
        #    myFromCollection = self.memberColl
        if argConnectionType == self.globalInstance._Global__memberColl:
            myFromCollection = self.globalInstance._Global__memberColl
            myPipeLine =  [ 
                    {"$match"  : {"_id":argMemberId}},
                    {"$unwind" : {"path":"$Connections","preserveNullAndEmptyArrays":True}},  
                    {"$match"  : { "$and": [{"Connections.Type":argConnectionType} ] } },
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

        return myPipeLine

    def __buildMyConnection(self, argConnectionType, argConnectionRawData):

        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
        myModuleLogger.debug('Argument [{conn}], [{data}] received'.format(conn=argConnectionType, data=argConnectionRawData))
        myModuleLogger.debug('Building [{conn}] Connection '.format(conn=argConnectionType))

        myConnectionRawData = argConnectionRawData

        if argConnectionType == self.globalInstance._Global__memberColl:
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
            #print json.dumps(myMemberConnections, sort_keys=True)
            #print myMemberConnections

        return myConnection

    def __ConnectAMemebr2Member(self, argRequestDict):
        ''' This is being called for invitation status will be as "Pending
            usage:          <__linkAMember2Member(<argReqJsonDict>)
                            MainArg['MemberId','ConnectMemberId','ConnectionStatus','Auth']
            Return:         Json object
        '''
        try:
            
            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            
            myConnectionResult = self.globalInstance._Global__False
            myArgKey = ['MemberId','ConnectMemberId','ConnectionStatus','Auth','ResponseMode']
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.format(arg=myMainArgData, key=myAuthArgKey))

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            ''' Preparing member connection document '''
            myConnections = self.envInstance.getConnTemplateCopy(self.globalInstance._Global__member)
            myCriteria = {'_id':myMainArgData['MemberId']}
            myConnections['MemberId'] = myMainArgData['MemberId']
            myConnections['Status'] = myMainArgData['ConnectionStatus']
            ''' we need to add connection as block to add this connection to Connection array '''
            myConnectionData = {'Connections':myConnections}            

            myModuleLogger.debug('Connection document [{doc}] prepared'.format(doc=myConnectionData))

            ''' Persisting data in database '''

            myConnectionResult =  self.mongoDbInstance.UpdateDoc(self.globalInstance._Global__memberColl, myCriteria, myConnectionData, 'addToSet',False)
            myModuleLogger.debug('Connection [{conn}] creation result [{result}]'.
                format(conn = myMainArgData['MemberId']  + ' -> ' myMainArgData['ConnectMemberId'], result=myConnectionResult))

            '''
            if (myConnectionStatus) and ('modified' in myConnectionStatus) and myConnectionStatus['modified'] > 0 :
                myConnectionResult = self.globalInstance._Global__True
            '''
            return myConnectionResult

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise

            ''' Build response data 
            myResponseRequest = self.utilityInstance.builInternalRequestDict({'Data':{'MemberId':myMainArgData['MemberId'],'ConnectionType':'Member'}})
            myResponseData = self.getAMemberConnections(myResponseRequest)
            myResponse = self.utilityInstance.buildResponseData(
                argRequestDict['Request']['Header']['ScreenId'],myBuildConnectStatus,'Update',myResponseData)

            return myResponse
            '''

    def __acceptInvitation(self, argRequestDict):
        pass
    def __rejectInvitation(self, argRequestDict):
        pass
    def isAValidMember(self,argRequestDict):
        ''' 
            Description:    Find a member details
            argRequestDict: Json/Dict; Following key name is expected in this dict/json object
                            {'MemnberId':'','AuthId':''}
            usage:          <getAGroupDetail(<argReqJsonDict>)
            Return:         Json object
        '''
        try:

            myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)['MainArg']
            myModuleLogger.debug('Argument [{arg}] received'.format(arg=myMainArgData))
            
            myArgKey = ['MemberId','Auth','ResponseMode']
            isValidMember = False 
            myArgValidation = self.utilityInstance.valRequiredArg(myMainArgData, myArgKey)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues('Arg validation error arg[{arg}], key[{key}]'.
                    format(arg=myMainArgData, key=myArgKey))

            ''' will overwrite EntityType and EntityId if passed in Auth dictionary. This is to ensure that Auth key must belong to this Member '''
            myMainArgData['Auth'] = self.securityInstance._Security__updateAuthEntity(
                {'Auth':myMainArgData['Auth'],'EntityType':self.globalInstance._Global__member,'EntityId':myMainArgData['MemberId']})

            ''' Validate auth key for this request'''
            if not (self.securityInstance.isValidAuthentication(myMainArgData['Auth'])):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.utilityInstance.whoAmI()))

            myCriteria = {'_id':myMainArgData['MemberId']}
            myProjection={'_id':1}
            myFindOne = True

            myMemberData = self.mongoDbInstance.findDocument(self.globalInstance._Global__memberColl, myCriteria, myProjection, myFindOne)
            myMemberId = self.utilityInstance.extr1stDocFromResultSets(myMemberData)['_id'] 

            if myMemberId and (myMemberId == myMainArgData['MemberId']):
                  isValidMember = True 

            ''' build response data '''            
            return isValidMember

        except com.uconnect.core.error.InvalidAuthKey as error:
            myModuleLogger.exception('InvalidAuthKey: error [{error}]'.format(error=error.errorMsg))
            raise
        except com.uconnect.core.error.MissingArgumentValues as error:
            myModuleLogger.exception('MissingArgumentValues: error [{error}]'.format(error=error.errorMsg))
            raise
        except Exception as error:
            myModuleLogger.exception('Error [{error}]'.format(error=error.message))
            raise
