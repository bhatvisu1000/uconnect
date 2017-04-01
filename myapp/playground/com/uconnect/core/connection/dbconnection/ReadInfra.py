import json, os
from globalSetting import GlobalSetting

#myEnvFile = "C:/Users/anil.singh/Documents/uConnect/myapp/com/uconnect/core/connection/interface/infra.json"
#myGlobalFile = "C:/Users/anil.singh/Documents/uConnect/myapp/com/uconnect/core/connection/interface/globals.json"

#if (os.path.isfile(myEnvFile)):
#    print "Environment file [%s" % myEnvFile, "] is missing, aborting !!!"
#    raise ValueError

#if (os.path.isfile(myGlobalFile)):
#    print "Global file [%s" % myGlobalFile, "] is missing, aborting !!!"
#    raise ValueError

#myEnvDetailResult = {}
#myInfra = json.loads(open(myEnvFile).read())
#globalSettings = json.loads(open(myGlobalFile).read())

class __init__:
  pass

class Environment:

  def __init__(self):
    #self.myGlobalFile = "C:/Users/anil.singh/Documents/uConnect/myapp/com/uconnect/core/connection/interface/globals.json"
    self.myGlobalFile = "globals.json"
    self.globalSettings = json.loads(open(self.myGlobalFile).read())
    self.globalFileAbsPath = os.path.abspath(self.myGlobalFile)
    print self.globalFileAbsPath    
    self.myHomePath = self.globalSettings['uConnectHomePath'] 
    self.myInfraPath = self.globalSettings['InfraPath']
    self.myInfraFile = self.globalSettings['Infra']
    #self.myEnvFile = self.globalSettings['InfraPath']
    self.myInfraFileWAbsPath = self.myHomePath + self.myInfraPath + self.myInfraFile
    self.myEnvDetailResult = {}

    self.myInfra = json.loads(open(self.myInfraFileWAbsPath).read())
    
    # check if myInfra dict is empty, raise error
    if not self.myInfra: 
       print "Bootstrap [Environment] could not be loaded, aborting !!!"

  def getEnvironmentDetails(self,envType):
    #print "in getEnvironmentDetails"
    #print myInfra
    #print myEnvDetailResult
    #print globalSettings
    self.myEnvDetailResult = self.globalSettings
    for myEnvDetails in self.myInfra['Environment']:
      #print myEnvDetails
      if (myEnvDetails['type'] == envType):
        #print "found env", myEnvDetailResult, "my type is ", type(myEnvDetailResult)
        #print self.myEnvDetailResult
        self.myEnvDetailResult.update(myEnvDetails['Details'])
        #print myEnvDetailResult
        #print myEnvDetails['Details']['DBType']
        #print myEnvDetails['Details']['DBHost']
    return self.myEnvDetailResult

if __name__ == "__main__":
  print "Reading global settings"
  #execfile('globalSetting.py')
  #globalFile ='globals.json'
  #myGlobal = GlobalSetting()
  #myGlobal.getGlobalSetting(globalFile)
  #myEnvironment = myGlobal.myEnvironment
  #print "global setting" , myGlobal.globalSettings
  #myGlobal = GlobalSetting()
  #myGlobal.getGlobalSetting(args.global_file)
  #print myGlobal.globalPath
  #print myGlobal.myEnvironment

  myEnv = Environment()
  #print globalSettings['Environment']
  myEnvDetails = myEnv.getEnvironmentDetails(myEnv.globalSettings['Environment'])
  print myEnvDetails




#for devDetails in myInfra['Environment']:
  #print devDetails
  #if ( devDetails['type'] == 'Dev' ):
    #for x in devDetails['Details']:
    #print devDetails['Details']['DBType']
    #print devDetails['Details']['DBHost']