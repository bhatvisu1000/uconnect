import logging, json, logging.config, os, sys
#from com.uconnect.core.connection.infra import Environment

'''
  Logging utility, defined for application. Must import uclogging 
'''

# instantiate Environment class, we need information for logpath, logConfig file etc. from environment

print "Initializing log config"
'''
myEnvironment =  Environment()
myEnvDetails = myEnvironment.getEnvironmentDetails(myEnvironment.globalSettings['Environment'])

logCfg = myEnvDetails['logCfg']
logPath = myEnvDetails['logPath']
logCfgFile = os.path.join(myEnvironment.configLoc, logCfg)

# check if config file exists

if not(os.path.isfile(logCfgFile)):
  print "config file [%s] does not exist " % (logCfgFile)
  sys.exit(-1)

# read the json file to be used for logging
print logCfgFile
'''
logCfg = 'loggingConfig.json'
logPath = os.environ['UCONNECT_LOG']
logCfgPath = os.environ['UCONNECT_CONFIG']
logCfgFile = os.path.join(logCfgPath, logCfg) 

with open(logCfgFile, 'rt') as f:
    loggingConfig = json.load(f)

#print loggingConfig

# overwriting path of logging file from infra.json

for x in loggingConfig['handlers']:
  if 'filename' in loggingConfig['handlers'][x]:
    absLogFileName = os.path.basename(loggingConfig['handlers'][x]['filename'])
    logFileName = os.path.join(logPath,absLogFileName)
    # lets change the path for logging as read from infra.json
    
    loggingConfig['handlers'][x]['filename'] = logFileName 

# load the logging configuration
#print loggingConfig
logging.config.dictConfig(loggingConfig)

'''
Follwoing format can be used in logging.config

   %(name)s            Name of the logger (logging channel)
   %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                       WARNING, ERROR, CRITICAL)
   %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                       "WARNING", "ERROR", "CRITICAL")
   %(pathname)s        Full pathname of the source file where the logging
                       call was issued (if available)
   %(filename)s        Filename portion of pathname
   %(module)s          Module (name portion of filename)
   %(lineno)d          Source line number where the logging call was issued
                       (if available)
   %(funcName)s        Function name
   %(created)f         Time when the LogRecord was created (time.time()
                       return value)
   %(asctime)s         Textual time when the LogRecord was created
   %(msecs)d           Millisecond portion of the creation time
   %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                       relative to the time the logging module was loaded
                       (typically at application startup time)
   %(thread)d          Thread ID (if available)
   %(threadName)s      Thread name (if available)
   %(process)d         Process ID (if available)
   %(message)s         The result of record.getMessage(), computed just as
                       the record is emitted
'''
