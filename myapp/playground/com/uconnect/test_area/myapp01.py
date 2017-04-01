
# myapp.py
import ucLogging, logging

def main():
    print "in main"
    logger = logging.getLogger("uConnect." + __name__)
    print logger
    logger.info("This is information")      
    logger.debug("This is debug information")      

if __name__ == '__main___':
    print "in main"
    main()
'''
def __init__():
    print "initializing"
    print "   config started .."
    logging.basicConfig \
        (filename = 'myapp.log', \
         level = logging.INFO, \
         format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s", \
         datefmt = "%Y-%m-%d %H:%M:%S")
    print "   config completed"
    logging.info('Started')
    #mylib.do_something()
    #logging.info('Finished')
    print "initialization completed"
    
def main():
    mainLogger = logging.getLogger(__name__)
    mainLogger.info("This is info from main")

if __name__ == '__main__':
    main()
'''