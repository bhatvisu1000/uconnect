import logging, json, logging.config, os, sys

'''
  Logging utility, constructing dictionary object to be used by native logging module
'''

print ("Constructing logging utility foundation")

'''
Constructing  config file name and path
'''

logCfg = 'loggingConfig.json'
logPath = os.environ['UCONNECT_LOG']
logCfgPath = os.environ['UCONNECT_CONFIG']
logCfgFile = os.path.join(logCfgPath, logCfg) 

'''checking is confif file exists, if exists read the file and load it into a dictionary project '''

try:

  if not(os.path.isfile(logCfgFile)):
    raise com.uconnect.core.error.MissingConfigFile("Logging config file [{logFile}]".format(logFile=logCfgFile))

  with open(logCfgFile, 'rt') as f:
    loggingConfig = json.load(f)

  if not loggingConfig: 
    raise com.uconnect.core.error.BootStrapError("Logging config dict is empty")

except com.uconnect.core.error.MissingConfigFile as error:
  print (error.errorMsg)
  raise error
except com.uconnect.core.error.BootStrapError as error:
  print("BootStrapError, [{error}]".format(error=error.errorMsg))
  raise error     
except Exception as error:
  print (error.errorMsg)
  raise errror


'''
UCONNECT_LOG path for logfile takes precidence over the logfile name specified in logginfConfig.json file
overwriting the value of logging file path from UCONNECT_LOG environment variable. loggingConfigfile is 
'''

absLogFileName = os.path.basename(loggingConfig['handlers']['file']['filename'])
logFileName = os.path.join(logPath,absLogFileName)
loggingConfig['handlers']['file']['filename'] = logFileName

''' 
overwrite logging configuration with this configuration 
'''

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
