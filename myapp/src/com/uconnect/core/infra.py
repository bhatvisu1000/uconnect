from com.uconnect.core.singleton import Singleton
import json, os, sys, logging, copy
import com.uconnect.utility.ucLogging
import com.uconnect.core.error
from com.uconnect.core.globals import Global

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
                        5. Template value
        argEnvType:     N/A
        usage:          <called internally during instantiation process>
        Return:         <N/A>
    '''
    ''' Initializing variables '''

    self._globalSettings = {}
    self.__infra = {}
    self.__factoryMetaData = {}
    self.__zipCodeData = {}
    self.__templateData = {}

    self.globalInstance = Global.Instance()

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
      self.__globalSettings = json.loads(open(self.myGlobalFile).read())

      # ensure globalsetting has value
      if not self.__globalSettings: 
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

    self.infraFile = self.__globalSettings['Infra']
    self.factoryMetaFile = self.__globalSettings['Factory']
    self.zipCodeFile = self.__globalSettings['ZipCode']
    self.templateFile = self.__globalSettings['Template']
    self.errorCodesFile = self.__globalSettings['ErrorCodes']
    self.exclColl4Id = self.__globalSettings['ExclColl4Id']
    self.AuthValidDuration = self.__globalSettings['AuthValidDuration']
    self.SecurityCodeLength = self.__globalSettings['SecurityCodeLength']
    print('Infra SecCode Length',self.SecurityCodeLength)
    self.infraFilewPath = os.path.join(self.configLoc,self.infraFile)
    self.factoryMetaFilewPath = os.path.join(self.configLoc,self.factoryMetaFile)
    self.zipCodeFileWPath = os.path.join(self.configLoc,self.zipCodeFile)
    self.templateFileWPath = os.path.join(self.configLoc,self.templateFile)
    self.errorCodesFileWPath = os.path.join(self.configLoc,self.errorCodesFile)

    '''    
    print ("InfraFile:",self.infraFile)
    print ("FactoryFile:",self.factoryMetaFile)
    print ("ZipCodeFile:",self.zipCodeFile)
    print ("TemplateFile:",self.templateFile)
    '''
    ''' Infra settings - infra.json '''
    try:
      # ensure config file exists
      # infra.json
      myModuleLogger.info("Initializing Infra ....")      
      if not (os.path.isfile(self.infraFilewPath)):
        raise com.uconnect.core.error.MissingConfigFile("Infra file [{infraFile}] is missing !!!".format(infraFile=self.infraFilewPath))

      ''' Reading infra file '''
      myModuleLogger.info("Reading infra config file [{infraFile}] ".format(infraFile=self.infraFilewPath)) 
      self.__infra = json.loads(open(self.infraFilewPath).read())
    
      # check if Infra dictionary is empty, raise error

      if not self.__infra: 
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
      self.__factoryMetaData = json.loads(open(self.factoryMetaFilewPath).read())
    
      # check if factory metadata dictionary is empty after loading data, raise error

      if not self.__factoryMetaData: 
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
      self.__zipCodeData = json.loads(open(self.zipCodeFileWPath).read())
    
      # check if zipcode dictionary is empty after loading data, raise error

      if not self.__zipCodeData: 
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

    ''' Loading Template value from template.json '''
    try:
      # ensure config file exists
      # template.json
      if not (os.path.isfile(self.templateFileWPath)):
        raise com.uconnect.core.error.MissingConfigFile("Template File [{templateFile}] is missing !!!".format(templateFile=self.templateFileWPath))

      myModuleLogger.info("Reading template json file [{templateFile}] ".format(templateFile=self.templateFileWPath))
      self.__templateData = json.loads(open(self.templateFileWPath).read())
      # check if template dictionary is empty after loading data, raise error

      if not self.__templateData: 
        raise com.uconnect.core.error.BootStrapError("Template dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Template file [{templateFile}] (value error) ".format(templateFile=self.templateFileWPath))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise

    ''' Loading Error codes from errorCodes.json '''
    try:
      # ensure config file exists
      # errorCodes.json
      if not (os.path.isfile(self.errorCodesFileWPath)):
        raise com.uconnect.core.error.MissingConfigFile("Error code File [{errorCodesFile}] is missing !!!".format(errorCodesFile=self.templateFileWPath))

      myModuleLogger.info("Reading error codes json file [{errorCodesFile}] ".format(errorCodesFile=self.errorCodesFileWPath))
      self.__errorCodesData = json.loads(open(self.errorCodesFileWPath).read())
      # check if error codes dictionary is empty after loading data, raise error

      if not self.__errorCodesData: 
        raise com.uconnect.core.error.BootStrapError("Error Code dictionary is empty")

    except com.uconnect.core.error.MissingConfigFile as error:
        myModuleLogger.error("MissingConfigFile Error, [{error}]".format(error=error.errorMsg))
        raise error 
    except com.uconnect.core.error.BootStrapError as error:
        myModuleLogger.error("BootStrapError, [{error}]".format(error=error.errorMsg))
        raise error     
    except ValueError as error:
       myModuleLogger.error("Error, loading Error code file [{errorCodesFile}] (value error) ".format(errorCodesFile=self.errorCodesFileWPath))
       raise error
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise

    ''' initializing other variables '''

    self.maxPageSize = int(self.__globalSettings['maxPageSize'])

  def getCurrentEnvironment(self):
    ''' 
        Description:    Returns current environment
        usage:          <getCurrentEnvironment()
        Return:         String <envrionment type>
    '''
    myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')

    myEnvironment = self.__globalSettings["Environment"]
    myModuleLogger.info("Current envrionment [{env}] ".format(env=myEnvironment)) 
    
    return myEnvironment 

  def getEnvironmentDetails(self, argEnvType):
    ''' 
        Description:    Returns environment details for a given environment 'Dev/Prod'
        argEnvType:     Environment type 
        usage:          <getEnvironmentDetails(<envrionment type>)
        Return:         Dictonary
    '''
    myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')
    myModuleLogger.debug("Argument [{arg}] received ".format(arg=argEnvType))

    ''' will build dictionary from globals and infra dictionary for a given env type '''

    myenvDetailResult = copy.deepcopy(self.__globalSettings)
    myModuleLogger.info("Preparing environment details for [{myEnvironment}] ".format(myEnvironment=argEnvType)) 
    myenvDetailResult.update(self.__infra[argEnvType])
    myModuleLogger.debug("Environent details for [{myEnvironment}] is [{myEnvDetails}] ".format(myEnvironment=argEnvType, myEnvDetails=myenvDetailResult)) 
    
    return myenvDetailResult


  def getConnTemplateCopy1(self, argConnectionType):
    ''' Returns a copy of Member template from template.json '''

    myModuleLogger = logging.getLogger('uConnect.'+__name__+'.Environment')
    myModuleLogger.debug("Argument [{arg}] received ".format(arg=argConnectionType))

    try:
      if argConnectionType in self.__templateData['Connections']:
        return copy.deepcopy(self.__templateData['Connections'][argConnectionType])
      else:
        raise com.uconnect.core.error.InvalidConnectionType('Connection type [{connType}] is missing in template repository !!! '.format(connType=argConnectionType))

    except com.uconnect.core.error.InvalidConnectionType as error:
        myModuleLogger.error("InvalidConnectionTypeError, [{error}]".format(error=error.errorMsg))
        raise error     
    except Exception as error:
       myModuleLogger.error("Error, an error occurred [{error}]".format(error=error.message))
       raise


'''
if __name__ == "__main__":
  print "Reading global settings"
  
  myEnv = Environment()
  #print globalSettings['Environment']
  myEnvDetails = myEnv.getEnvironmentDetails(myEnv.globalSettings['Environment'])
  print myEnvDetails
'''