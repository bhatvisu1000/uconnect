import json, os, sys
from globalSetting import GlobalSetting

class __init__:
  pass

class Environment:

  def __init__(self):

    ''' building core path - globals.json'''
    self.uconnectHome = os.environ['UCONNECT_HOME']
    self.configLoc = os.path.join(self.uconnectHome,'config')
    self.myGlobalFile = os.path.join(self.configLoc,'globals.json')

    #print self.myGlobalFile ## for debug only

    if not (os.path.isfile(self.myGlobalFile)):
       print "Global file ", self.myGlobalFile, " is missing !!!"
       exit(1) ## which code we should return back ???

    self.globalSettings = json.loads(open(self.myGlobalFile).read())

    if not self.globalSettings: 
       print "Bootstrap [Environment(globalSettings)] could not be loaded, aborting !!!"
       exit(1) ## which code we should return back ???

    ''' infra.json'''

    self.infraFile = self.globalSettings['Infra']
    self.myInfraFile = os.path.join(self.configLoc,self.infraFile)
    self.myEnvDetailResult = {}

    self.myInfra = json.loads(open(self.myInfraFile).read())
    
    # check if myInfra dict is empty, raise error
    if not self.myInfra: 
       print "Bootstrap [Environment(infra)] could not be loaded, aborting !!!"
       exit(1) ## which code we should return back ???

    ## extract all variable here
    self.maxPageSize = int(self.globalSettings['maxPageSize'])
    #print myEnvDetails['logCfg']
    #print os.path.join(myEnvironment.configLoc, myEnvDetails['logCfg'])

  def getEnvironmentDetails(self,envType):
    ''' will build dict from globals and infra dict for a given env type '''
    
    self.myEnvDetailResult = self.globalSettings

    for myEnvDetails in self.myInfra['Environment']:
      if (myEnvDetails['type'] == envType):
        self.myEnvDetailResult.update(myEnvDetails['Details'])

    return self.myEnvDetailResult

  def __del__(self):
    pass

if __name__ == "__main__":
  print "Reading global settings"
  
  myEnv = Environment()
  #print globalSettings['Environment']
  myEnvDetails = myEnv.getEnvironmentDetails(myEnv.globalSettings['Environment'])
  print myEnvDetails
