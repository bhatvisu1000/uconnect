# print all args passed and its value
def a(p,q,r):
   a = vars()
   for x in a:
     print(a[x])
# Checking if an argument passed has null/none value

def checkArgs(*arg):
  print(len(arg))
  print(arg)
  for x in arg:
    print x
  print(all (arg))
  print ( not all (arg))

checkArgs(1,None,2)

def isAllArgumentsValid(*args):
    ''' 
        Description:    Checks if any argument passed to this function has Null/None/Empty/Zero value
        *args:          All argumnet seperated by comma, any # of arguments can be passed
        usage:          ( isAllArgumentsValid(<*args>)
        Return:         Return True if all argument passed does not contain any not null value (this includes 
                             empty and zero value), False if any argument passed contains Null/None/Empty/Zero value
    '''
    return (all (args))
