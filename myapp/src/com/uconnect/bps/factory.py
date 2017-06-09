import importlib,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global


#from com.uconnect.bps.scheduleBPS import Schedule

myLogger = logging.getLogger('uConnect')

@Singleton
class Factory(object):
    '''
    This is Factory class, this will execute a BO process as mapped in config/FactoryMetadata.json
    '''
    def __init__(self):
        self.utilityInstance = Utility.Instance()
        self.globalInstance = Global.Instance()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def processRequest(self, argRequestDict):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <processRequest(argRequestDict)
        '''
        try:

            self.myModuleLogger.debug("arg received [{args}]".format(args=argRequestDict))
            myMainArgData = self.utilityInstance.getCopy(argRequestDict)

            ''' Validating argumemt received '''
            self.utilityInstance.valBPSArguments(myMainArgData)
            myArgValidation = self.utilityInstance.valBPSArguments(myMainArgData)

            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues("Arg validation error {arg}".format(arg=myMainArgData))
            #fi

            myScreenId = myMainArgData['Request']['Header']['ScreenId']
            myActionId = myMainArgData['Request']['Header']['ActionId']

            bpsProcessVal = self.__findBPSProcess (myScreenId, myActionId)

            # extracting tuple value returned from above method

            myLibrary, myClass, myMethod = bpsProcessVal
            if myLibrary and myClass and myMethod:
                myModuleLogger.debug("found, bps process [{bpsprocVal}]".format(bpsprocVal=bpsProcessVal))
                myResponse = self.__executeBPSPRocess(myLibrary, myClass, myMethod, myMainArgData) 
                myRquestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__Success)            
            else:
                self.myModuleLogger.debug("did not find mapped bps process, value from navigating factoty data [{bpsprocVal}]".format(bpsprocVal=bpsProcessVal))
                myRquestStatus = self.utilityInstance.getRequestStatus(self.globalInstance._Global__UnSuccess,'Invalid Screen [{screen}] Action [{action}]'.
                                    format(screen=myScreenId, action=myActionId))            
                myResponse = self.utilityInstance.buildResponseData('E',myRquestStatus,'Error')
            #fi

            self.myModuleLogger.debug("return value from bps process [{responseVal}]".format(responseVal=myResponse))

            return myResponse

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def __findBPSProcess(self, argScreenId, argActionId):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <__updateKeyValue(<coll>,<DictDocument>)
            Return:         library, class, method
        '''
        try:

            self.myModuleLogger.debug("arg received [{screen},{action}]".format(screen=argScreenId, action=argActionId))

            myLibrary = myClass = myMethod  = ''

            myLibClassMethod = self.utilityInstance.getModuleClassMethod(argScreenId, argActionId)
            if not( myLibClassMethod[0] == None):
                myLibrary = myLibClassMethod[0]
                myClass   = myLibClassMethod[1]
                myMethod  = myLibClassMethod[2]
            else:
                return None
            #fi
            return myLibrary, myClass, myMethod

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            #myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            raise

    def __executeBPSPRocess(self, argLibrary, argClass, argMethod, argReqJsonDict):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <__updateKeyValue(<coll>,<DictDocument>)
            Return:         Return value from called objects
        '''  
        try:

            self.myModuleLogger.debug("arg received [{lib},{cls},{method},{args}]".format(lib=argLibrary,cls=argClass,method=argMethod,args=argReqJsonDict))

            myModule = importlib.import_module(argLibrary)
            myClass = getattr(myModule, argClass)
            # if singleton, get an instance else instantiate the class
            if hasattr(myModule,'Singleton') and hasattr(myClass,'Instance') :
                myCallableClass = myClass.Instance()
            else:
                myCallableClass = myClass()

            # get the method from this class
            myMethod = getattr(myCallableClass,argMethod)
            ''' Only MainArg need to be passed  '''
            myMainArg = {'MainArg':self.utilityInstance.extMainArgFromReq(argReqJsonDict)}
            ''' need to mark that this response is external '''
            myMainArg['MainArg'].update({'ResponseMode':self.globalInstance._Global__ExternalRequest})

            # execute the method
            myResults = myMethod(myMainArg)

            return (myResults)

        except Exception as err:
            myRequestStatus = self.utilityInstance.extractLogError()
            #myResponse = self.utilityInstance.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            raise