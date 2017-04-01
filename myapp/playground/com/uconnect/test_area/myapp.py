# myapp.py
import ucLogging, logging
# lets the parent logger from config file
myLogger = logging.getLogger('uConnect')
print myLogger.handlers
# lets try to get the child logger which doesnt exist, this will default to parent logger
myLogger1 = logging.getLogger('uConnect.'+__name__)
print myLogger1.handlers
# you must get parent logger which is already defined in config file and then get the module logger with defining "."

print myLogger1
for x in xrange(10):
    myLogger1.debug("this is my debug")
    myLogger1.info("this is my info")
    myLogger1.warning("this is my warning")
    myLogger1.error("this is my error")
    myLogger1.critical("this is critical error")
