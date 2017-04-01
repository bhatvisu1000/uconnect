from ReadInfra import Environment

if __name__ == "__main__":
  print "Reading global settings"
  myEnv = Environment()
  myEnvDetails = myEnv.getEnvironmentDetails(myEnv.globalSettings['Environment'])
  print myEnvDetails

