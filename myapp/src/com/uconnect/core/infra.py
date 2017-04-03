from com.uconnect.core.singleton import Singleton
import json, os, sys, logging
import com.uconnect.utility.ucLogging
import com.uconnect.core.error

myLogger = logging.getLogger('uConnect')

@Singleton
class Environment(object):
  '''
  This is initialization class, this is the first class excuted during initialization process
  '''
  def __init__(self):
    ''' 
        Description:    Initialize/read/populates following components
                        1. Global Setting
                        2. Specific Environment Setting
                        3. Facroty Metadata
                        4. Zipcode
                        5. Defaults value
        argEnvType:     N/A
        usage:          <called internally during instantiation process>
        Return:         <N/A>
    '''
    ''' Initializing variables '''

    self.globalSettings = {}
    self.envDetailResult = {}
    self.infra = {}
    self.factoryMetaData = {}
    self.zipCodeData = {}
    self.defaultsData = {}

    ''' building core path - globals.json'''
    
    myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')

    myModuleLogger.info("Initializing Environment ...")

    self.uconnectHome = os.environ['UCONNECT_HOME']
    self.configLoc = os.path.join(self.uconnectHome,'config')
    self.myGlobalFile = os.path.join(self.configLoc,'globals.json')

    ''' Global Settings - globals.json'''
    try:
      # ensure config file exists
      # globals.json
      myModuleLogger.info("Initializing Global settings ....")      
      if not (os.path.isfile(self.myGlobalFile)):
        raise com.uconnect.core.error.MissingConfigFile("GlobalFile [{globalFile}] is missing !!!".format(globalFile=self.myGlobalFile))

      myModuleLogger.info("Reading global configuration file [{globalFile}] ".format(globalFile=self.myGlobalFile))
      self.globalSettings = json.loads(open(self.myGlobalFile).read())

      # ensure globalsetting has value
      if not self.globalSettings: 
        raise com.uconnect.core.error.BootStrapError("GlobalSettings dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading global file [{globalFile}] (value error) ".format(globalFile=self.myGlobalFile))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise error

    ''' Building Infra/FactoryMetadata file with path '''

    self.infraFile = self.globalSettings['Infra']
    self.factoryMetaFile = self.globalSettings['Factory']
    self.zipCodeFile = self.globalSettings['ZipCode']
    self.defaultsFile = self.globalSettings['Defaults']

    self.infraFilewPath = os.path.join(self.configLoc,self.infraFile)
    self.factoryMetaFilewPath = os.path.join(self.configLoc,self.factoryMetaFile)
    self.zipCodeFileWPath = os.path.join(self.configLoc,self.zipCodeFile)
    self.defaultsFileWPath = os.path.join(self.configLoc,self.defaultsFile)
    
    ''' Infra settings - infra.json '''
    try:
      # ensure config file exists
      # infra.json
      myModuleLogger.info("Initializing Infra ....")      
      if not (os.path.isfile(self.infraFilewPath)):
        raise com.uconnect.core.error.MissingConfigFile("Infra file [{infraFile}] is missing !!!".format(infraFile=self.infraFilewPath))

      ''' Reading infra file '''
      myModuleLogger.info("Reading infra config file [{infraFile}] ".format(infraFile=self.infraFilewPath)) 
      self.infra = json.loads(open(self.infraFilewPath).read())
    
      # check if Infra dictionary is empty, raise error

      if not self.infra: 
        raise com.uconnect.core.error.BootStrapError("InfraSetting dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Infra file [{infraFile}] (value error) ".format(infraFile=self.infraFile))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise error

    ''' factory metadata '''

    try:
      # ensure config file exists
      # FactoryMetadata.json

      myModuleLogger.info("Initializing Factory Metadata ....")

      if not (os.path.isfile(self.factoryMetaFilewPath)):
        raise com.uconnect.core.error.MissingConfigFile("FactoryMetada File [{factoryFile}] is missing !!!".format(factoryFile=self.factoryMetaFilewPath))

      myModuleLogger.info("Reading factory json file [{factoryFile}] ".format(factoryFile=self.factoryMetaFilewPath)) 
      self.factoryMetaData = json.loads(open(self.factoryMetaFilewPath).read())
    
      # check if factory metadata dictionary is empty after loading data, raise error

      if not self.factoryMetaData: 
        raise com.uconnect.core.error.BootStrapError("FactoryMetada dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Factory Metadata file [{factoryFile}] (value error) ".format(factoryFile=self.factoryMetaFilewPath))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise error

    ''' Loading zipcode '''
    try:
      # ensure config file exists
      # zipcode.json
      myModuleLogger.info("Initializing zipcode ....")

      if not (os.path.isfile(self.zipCodeFileWPath)):
        raise com.uconnect.core.error.MissingConfigFile("Zipcode File [{zipCodeFile}] is missing !!!".format(zipCodeFile=self.zipCodeFileWPath))

      myModuleLogger.info("Reading zipcode json file [{myZipFile}] ".format(myZipFile=self.zipCodeFileWPath))
      self.zipCodeData = json.loads(open(self.zipCodeFileWPath).read())
    
      # check if zipcode dictionary is empty after loading data, raise error

      if not self.zipCodeData: 
        raise com.uconnect.core.error.BootStrapError("ZipCode dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Zipcode file [{zipcCodeFile}] (value error) ".format(zipcCodeFile=self.zipCodeFileWPath))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise

    ''' Loading Defaults value from defaults.json '''
    try:
      # ensure config file exists
      # defaults.json.json
      if not (os.path.isfile(self.defaultsFileWPath)):
        raise com.uconnect.core.error.MissingConfigFile("Defaults File [{defaultsFile}] is missing !!!".format(defaultsFile=self.defaultsFileWPath))

      myModuleLogger.info("Reading defaults json file [{defaultsFile}] ".format(defaultsFile=self.defaultsFileWPath))
      self.defaultsData = json.loads(open(self.defaultsFileWPath).read())
      #print(self.defaultsData)
      # check if defaults dictionary is empty after loading data, raise error

      if not self.defaultsData: 
        raise com.uconnect.core.error.BootStrapError("Defaults dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Defaults file [{defaultsFile}] (value error) ".format(defaultsFile=self.defaultsFileWPath))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise

    ''' initializing other variables '''

    self.maxPageSize = int(self.globalSettings['maxPageSize'])

  def getEnvironmentDetails(self, argEnvType):
    ''' 
        Description:    Returns environment details for a given environment 'Dev/Prod'
        argEnvType:     Environment type 
        usage:          <getEnvironmentDetails(<envrionment type>)
        Return:         Dictonary
    '''
    myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')

    ''' will build dictionary from globals and infra dictionary for a given env type '''
    
    self.envDetailResult = self.globalSettings

    myModuleLogger.info("Preparing environment details for [{myEnvironment}] ".format(myEnvironment=argEnvType)) 
    
    self.envDetailResult.update(self.infra[argEnvType])

    myModuleLogger.debug("Environent details for [{myEnvironment}] is [{myEnvDetails}] ".format(myEnvironment=argEnvType, myEnvDetails=self.envDetailResult)) 
    
    return self.envDetailResult


'''
if __name__ == "__main__":
  print "Reading global settings"
  
  myEnv = Environment()
  #print globalSettings['Environment']
  myEnvDetails = myEnv.getEnvironmentDetails(myEnv.globalSettings['Environment'])
  print myEnvDetails
'''