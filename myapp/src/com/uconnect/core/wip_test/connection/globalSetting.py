import sys, os, argparse, json

class GlobalSetting(object):

  def __init__(self):
    self.globalPath = ''
    self.myEnvironment = ''
    self.globalSettings = {}

  def getGlobalSetting(self,globalFile):

    if not(os.path.isfile(globalFile)):
        print "Invalid file ", globalFile
        sys.exit()

    self.globalSettings = json.loads(open(globalFile).read())
    self.myEnvironment = self.globalSettings['Environment']
    self.globalPath = self.globalSettings['uConnectHomePath']

'''
# Following code is for testing purpose only
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-global_file",help="Provide global file name")
    args = parser.parse_args()
    print args.global_file
    myGlobal = GlobalSetting()
    myGlobal.getGlobalSetting(args.global_file)
    print myGlobal.globalPath
    print myGlobal.myEnvironment
    print "global setting" , myGlobal.globalSettings
'''