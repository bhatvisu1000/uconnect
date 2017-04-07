import importlib,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton


#from com.uconnect.bps.scheduleBPS import Schedule

myLogger = logging.getLogger('uConnect')

@Singleton
class Factory(object):
    '''
    This is Factory class, this will execute a BO process as mapped in config/FactoryMetadata.json
    '''
    def __init__(self):
       self.utilityInstance = Utility.Instance()
       self.envInstance = Environment.Instance()
    
    def processRequest(self, argReqJsonDict):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <processRequest(argScreenId, argActionId, argReqJsonDict)
        '''
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
        myModuleLogger.debug("arg received [{args}]".format(args=argReqJsonDict))

        ''' Validating argumemt received '''
        self.utilityInstance.valBPSArguments(argReqJsonDict)
        myArgValidation = self.utilityInstance.valBPSArguments(argReqJsonDict)

        if not (myArgValidation):
            raise com.uconnect.core.error.MissingArgumentValues("Arg validation error {arg}".format(arg=argReqJsonDict))

        bpsProcessVal = self.__findBPSProcess (argReqJsonDict['Request']['Header']['ScreenId'],argReqJsonDict['Request']['Header']['ActionId'])
        # extracting tuple value returned from above method
        myLibrary, myClass, myMethod = bpsProcessVal
        #myArg.append(argReqJsonDict)
        myModuleLogger.debug("found, bps process [{bpsprocVal}]".format(bpsprocVal=bpsProcessVal))
        #argReqJsonDict.update({'Projection':myProjection})
        respJsonDictVal = self.__executeBPSPRocess(myLibrary, myClass, myMethod, argReqJsonDict) 

        myModuleLogger.debug("return value from bps process [{responseVal}]".format(responseVal=respJsonDictVal))
        return respJsonDictVal

    def __findBPSProcess(self, argScreenId, argActionId):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <__updateKeyValue(<coll>,<DictDocument>)
            Return:         library, class, method
        '''
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
        myModuleLogger.debug("arg received [{screen},{action}]".format(screen=argScreenId, action=argActionId))

        try:
            myLibClassMethod = self.envInstance.getModuleClassMethod(argScreenId, argActionId)
            if not( myLibClassMethod[0] == None):
                myLibrary = myLibClassMethod[0]
                myClass   = myLibClassMethod[1]
                myMethod  = myLibClassMethod[2]
            else:
                raise KeyError
        except KeyError as error:
            print(error)
            myModuleLogger.error("KeyError while navigating in Factory data, error[{err}]".format(err=error.message))
            raise
        except Exception as Error:
            myModuleLogger.error("Error occurred while extracting module/class/method [{err}]".format(err=error.message))
            raise Error

        return myLibrary, myClass, myMethod

    def __executeBPSPRocess(self, argLibrary, argClass, argMethod, argReqJsonDict):
        ''' 
            Description:    Update key in dictDocument for a given collection, this is a private method
            argCollection:  Collection name
            argDictDocument:Dict documents
            usage:          <__updateKeyValue(<coll>,<DictDocument>)
            Return:         Return value from called objects
        '''     
        myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
        myModuleLogger.debug("arg received [{lib},{cls},{method},{args}]".format(lib=argLibrary,cls=argClass,method=argMethod,args=argReqJsonDict))

        myModule = importlib.import_module(argLibrary)
        myClass = getattr(myModule, argClass)
        # if singleton, get an instance else instantiate the class
        if hasattr(myModule,'Singleton') and hasattr(myClass,'Instance') :
            myCallableClass = myClass.Instance()
        else:
            myCallableClass = myClass()

        # get the method from this class
        myMethod = getattr(myCallableClass,argMethod)
        # execute the method
        myRetval = myMethod(argReqJsonDict)

        return (myRetval)

