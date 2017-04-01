from pymongo import MongoClient
import sys

class InitMongoDb(object):
    def __init__(self):
        self.mongoDbUri = "128.0.0.1:27017"
        print "mongoDbUri", self.mongoDbUri
        self.maxSevSelDelay = 10
        try:
            ## following line is for test purpose only, to see what exception is raised
            #print 10/"a"

            self.client = MongoClient(self.mongoDbUri,serverSelectionTimeoutMS=self.maxSevSelDelay)
            self.client.server_info() # force connection on a request as the
                             # connect=True parameter of MongoClient seems
                             # to be useless here 
        except TypeError as err:
            print "TypeError:", err
        except "pymongo.errors.PyMongoError" as err:
                print "Error [", err , "] occurred while accessing mongoDb [", mongoDbUri , "]"
        except "pymongo.errors.ServerSelectionTimeoutError" as err:
                # log error, this should be noted as severity HIGH
                print "MongoDb server is not running", err
        except Exception as err:
            print "Excpetion", err , sys.exc_info()[0]
        finally:
            print "We are done with initialization"

if __name__ == "__main__":
    print ("initializing")
    init = InitMongoDb()