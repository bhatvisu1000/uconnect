import inspect
import sys

class myClass(object):
  def __init__(self):
   print self.__class__.__name__
   print "All inspect Stack: "
   print inspect.stack()
   print "Follwoing is method name"
   #print inspect.stack()[0][3] 
   print inspect.stack()
   print "Follwoing is current file name"
   print inspect.stack()[1][1] 
   print "Follwoing is current class"
   print inspect.stack()[1][4] 
   print inspect.currentframe()
   #print inspect.outerframes()
   #print inspect.innerframes()
   print "Current function:", sys._getframe(  ).f_code.co_name
   print "Who called me 1:", sys._getframe(1).f_code.co_name
   print "Who called me 2:", sys._getframe(2).f_code.co_name
   print "this_line_number:", sys._getframe(  ).f_lineno
   print "this_filename:", sys._getframe(  ).f_code.co_filename

if __name__ == "__main__":
  locMyClass = myClass()
