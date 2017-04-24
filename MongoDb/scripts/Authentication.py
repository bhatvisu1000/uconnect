pip install bcrypt

from bcrypt import hashpw, gensalt
hashed = hashpw(plaintext_password, gensalt(rounds=8))
by default rounds=12
print hashed

hashed = hashpw('Temp', gensalt(rounds=8))
password_attempt='Temp'
if hashpw(password_attempt, hashed) == hashed:
    print "It matches"
else:
    print "It does not match"

from pymongo import MongoClient
from com.uconnect.core.infra import Environment
from com.uconnect.core.dbconnection import ConnectionBuilder
from bcrypt import hashpw, gensalt

def createUser(argUserid,argPassword):
    connectBuildInstance = ConnectionBuilder.Instance()
    connectionInstance = connectBuildInstance.buildConnection("MongoDB")
    envInstance = Environment.Instance()
    myConnectionInst = connectionInstance
    myDb = myConnectionInst['LoggingInfo']
    hashPassword = hashpw(argPassword, gensalt(rounds=8)) 
    myDb.insert_one({'_id':argUserid,'password':hashPassword})

def authUser(argUserid,argPassword):
    connectBuildInstance = ConnectionBuilder.Instance()
    connectionInstance = connectBuildInstance.buildConnection("MongoDB")
    envInstance = Environment.Instance()
    myConnectionInst = connectionInstance
    myDb = myConnectionInst['LoggingInfo']
    myHashPAssword = str(myDb.find_one({'_id':argUserid},{'_id':0,'password':1})['password'])
    #myHashPAssword = str(myHashPAsswordDict['password'])
    if hashpw(argPassword, myHashPAssword) == myHashPAssword:
        return "Matched"
    else:
        print "Did not match"

LoginInfo
{
    "_id":"<EntityId>",
    "LoginType":"Email/Mobile",
    "LoginId":"abc@xyz.com",
    "Password":"<encrypted>",
    "EntityType":"Member",
    "Acccess":
        [
            {"ScreenId":"","ActionId":""}
        ]
    "Authentication":
        [
            {
                "11111111111111":
                    {
                        "AuthMacAddress":"",
                        "DeviceType":"",
                        "DeviceOs":"",
                        "CreatedDate":"",
                        "ExpiredOn":"",
                        "uConenctAppVer":""
                    }
            }
        ],
    "_History":{}
}