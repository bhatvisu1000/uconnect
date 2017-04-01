import logging, json, logging.config

class ucLogging:
  def __init__(self):
    with open('loggingConfig.json', 'rt') as f:
      loggingConfig = json.load(f)
#print loggingConfig
    logging.config.dictConfig(loggingConfig)
#for key,elem in loggingConfig.items():
#    print key, ":", elem
'''
loggingConfig = dict(
    version = 1,
    formatters = {
        'f': {'format':'%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
              'datefmt': '%Y-%m-%d %H:%M:%S'}
        },
    handlers = {
        'console': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG},
        'file': {'class': 'logging.handlers.RotatingFileHandler',
              'formatter': 'f',
              'filename' : 'uConnect.log',
              'maxBytes' : 1024,
              'backupCount' : 2,
              'level': logging.DEBUG}        },
    loggers = {
       'root' : {'handlers': ['console'],'level': logging.DEBUG},
       'test' : {'handlers': ['file'],'level': logging.DEBUG}
       }
)
'''
#print loggingConfig
#logging.config.dictConfig(loggingConfig)
#logging.config.fileConfig('logging_config.json')

# create logger
#print "config completed"
#logger = logging.getLogger('myConsole')
'''
def myFunc():
  print(__name__)
  logger = logging.getLogger(__name__)
  logger.info("This is info")

myFunc()
'''

logger = logging.getLogger("uConnect."+str(__name__))
print(logger)
logger.info("This is info")
