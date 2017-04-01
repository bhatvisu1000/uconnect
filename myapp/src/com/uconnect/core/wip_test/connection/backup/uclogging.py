import os, json, logging.config
from infra import Environment

class uclogging:
    def __init__(self):
        myEnvironment = Environment()
        myEnvDetails = myEnvironment.getEnvironmentDetails(myEnvironment.globalSettings['Environment'])
        #logCfgVal = myEnvDetails['logCfg']
        logCfgFile = myEnvDetails['logCfg']
        print "logCfgVal:", logCfgFile
        print "Env details:", myEnvDetails
        print "config Loc:", myEnvironment.configLoc
        #logCfgFile = os.path.join(myEnvironment.configLoc, myEnvDetails[logCfgVal])
 
        #if os.path.exists(logCfgFile):
        with open(logCfgFile, 'rt') as f:
            loggingConfig = json.load(f)
            logging.config.dictConfig(loggingConfig)
            print "config completed"
        #else:
            #logging.basicConfig(level=default_level)

    def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'):
        pass
    """Setup logging configuration

    """


if __name__ == "__main__":
    myLogging = uclogging()
    logger = myLogging.getLogger('my_module')
    print logger
    logger.info("This is info")

'''
    myEnvironment = Environment()
    myEnvDetails = myEnvironment.getEnvironmentDetails(myEnvironment.globalSettings['Environment'])
    print myEnvDetails
    print myEnvDetails['logCfg']
    print os.path.join(myEnvironment.configLoc, myEnvDetails['logCfg'])

import logging
loglevel="Debug"
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
    
logging.basicConfig(level=loglevel.upper(), file_name='ucConnect.log', filemode='w')
'''