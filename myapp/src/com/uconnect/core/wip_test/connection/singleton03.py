import logging, com.uconnect.utility.ucLogging

myLogger = logging.getLogger('uConnect')

def singleton(cls):
    myModuleLogger = logging.getLogger('uConnect.'+__name__)
    myModuleLogger.debug("Initializing, current request for class {cls} to be singletong".format(cls=cls))
    instances = {}
    def getinstance():
        myModuleLogger = logging.getLogger('uConnect.'+__name__)
        myModuleLogger.debug("checking if instance of class {cls} is already initialized ".format(cls=cls))
        if cls not in instances:
            myModuleLogger.debug("class {cls} is not initialized ".format(cls=cls))
            instances[cls] = cls()
        else:
            myModuleLogger.debug("class {cls} is initialized, returning initiated class ".format(cls=cls))
        
        myModuleLogger.debug("All classe(s) [{inst}] initialized using singletong method ".format(inst=instances))
        return instances[cls]
    return getinstance