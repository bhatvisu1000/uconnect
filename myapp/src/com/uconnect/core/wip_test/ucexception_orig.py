import sys, traceback, inspect
from functools import wraps
from com.uconnect.core.singleton import Singleton

#handle the exception in super class
#define allexception must be inherittance of super class which is sub class of exception
# we need to know the current function and or class name so this can be passed as an argument and should be recorded

@Singleton
class ucException(Exception):
    #print "Main Error"
    '''
    def __init__(self, errorCode, errorMessage):
        self.errorCode = errorCode
        self.errorMessage = errorMessage
        print "in 1st class " + self.message
    def setException(self,errorCode, errorMessage):
        self.errorCode = errorCode
        self.errorMessage = errorMessage

    def handleError(self, errMessage):
        print "Handling Error", errMessage
    '''
    pass
class MissingConfigFile(ucException):
    pass
class MissingArgumentValue(ucException):
    pass
class myError(ucException):
    '''
    def __init__(self, **kwargs):
        print kwargs
        self.handleError (kwargs)
        print "in my error"
        #self.expression = expression
        #self.message = message
        #print self.message, " ", self.message
    '''
    pass
    '''
class TransitionError(ucException):
    """Raised when an operation attempts a state
    transition that's not allowed.
    
    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific
                    transition is not allowed
    """
    
    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message       
        print self.previous, self.next, self.message
        self.handleError (self.message)

def callme():
    try:
        print 1/'a'
    except Exception as ex:
        myex = ucException()
        myex.errorCode=10
        raise myError
        

    try:
        #raise TransitionError(1,2,"Invalid Name")
        print 1/'a'
    except Exception as ex:
        raise
    finally:
        print "we are done here"
'''

if __name__ == "__main__":
    try:
        callme()
    except Exception as ex:
            print 'In Exception ', ex.message, 'type', type(ex), "length", len(ex.args)
            print "exception:" + ex.message
            print 'In Excepton, will now print all args'
            for x in ex:
                print x
            # 1st option,gives precise line# location where error occurred
            e = sys.exc_info()[1]
            print "sys.exc_info",e.args
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            print "trace back:",tbinfo
            # 2nd doesn't give precise line# location where error occurred
            #print "Error occurred in ", inspect.stack()[1][3], inspect.stack()[0][2], inspect.stack()[0][1]
            print "Error occurred in ", inspect.stack()
            #raise
#        else:
#            pass
    finally:
            pass

'''

from functools import wraps

def tmp_wrap(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        print func.__name__
        return func(*args, **kwargs)
    return tmp

@tmp_wrap
def my_funky_name():
    print "STUB"

my_funky_name()


import inspect
def bar():
    print "My name is", inspect.stack()[0][3]

'''