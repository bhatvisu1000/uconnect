import json
from com.uconnect.bps.factory import Factory
from com.uconnect.core.infra import Environment
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.db.mongodb import MongoDB

myFactory = Factory.Instance()
utilityInstance = Utility.Instance()
mongodbInstance = MongoDB.Instance()

# load Member test data, you might consider emptying Member collection: db.Member.remov({})
MemberData = json.loads(open("c:\\app\\uconnect\\MongoDb\\json\\MemberTestData.json").read())
#MemberData = json.loads(open("c:\\app\\uconnect\\MongoDb\\json\\Temp.json").read())
for line in MemberData:
    #print (line['Main'],line['Address'],['Contact'])
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"Registration","ActionId":"RegisterEntity","Page":None},
                     "MainArg":
                        {
                            "Main":line['Main'],
                            "Address":{'ZipCode':str(line['Address']['ZipCode'])},
                            "Contact":{'Mobile':line['Contact']['Mobile'],'Email':line['Main']['FirstName'] + '.' + line['Main']['LastName'] + '@uconnect.com' },
                            "Auth":
                            {
                                "LoginId":line['Main']['FirstName'] + '.' + line['Main']['LastName'] + '@uconnect.com',
                                "LoginType":"Web",
                                "Password":line['Main']['FirstName'],
                                "DeviceOs":"Web",
                                "DeviceType":"OS2",
                                "MacAddress":"SDFSDKLGHASKLDFGHSAKLFG214ADFA",
                                "EntityType":"Member",
                                "AppVer":"1.0",
                                "SessionId":"TestSessionId" 
                            }
                        }
                    }
                  }
    if not(utilityInstance.isDict(myRequest)):
        jsonify({"Status":"Error","Message":"Invalid argument {arg} passed, argument must be type of dictionary !!!".format(arg=myRequest)})
    try:
        if ( "Request" not in myRequest ) or ("Header" not in myRequest['Request']) or ('MainArg' not in myRequest['Request']):
            jsonify({"Status":"Error","Message":"Key error"})
    except Exception as error:
        jsonify({"Status":"Error","Message":"error {error}".format(error=error.message)})
    myMember = myFactory.processRequest(myRequest)
    print(myMember)

# Create a oonnection
# getting 1st page of 10
myAllMembers1 = mongodbInstance.findAllDocuments4Page('Member',None,{"_id":1},1)['Data']
# getting 2nd page of 10
myAllMembers2 = mongodbInstance.findAllDocuments4Page('Member',None,{"_id":1},2)['Data']
myAllMembers = myAllMembers1 + myAllMembers2

myMemberId = myAllMembers[0]['_id']
print(myMemberId)
myAuthInfo = mongodbInstance.findDocument('Auth',{'EntityId':myMemberId},{},False)['Data'][0]
myAllMembers.pop(0)
for x in myAllMembers:
    myRequest = {"Request":
                    {"Header":
                        {
                            "ScreenId":"Member","ActionId":"UpdateConnectionDetails","Page":"None"
                        },
                     "MainArg":
                        {
                            "Connections":[{"Id":x['_id'],"Type":"Member","Action":"Invite"}],
                            "Auth":
                                {
                                    "AuthKey":str(myAuthInfo['_id']),
                                    "LoginType":myAuthInfo['LoginType'],
                                    "LoginId":myAuthInfo['LoginId'],
                                    "DeviceOs":myAuthInfo['DeviceOs'],
                                    "DeviceType":myAuthInfo['DeviceType'],
                                    "MacAddress":myAuthInfo['MacAddress'],
                                    "EntityType":myAuthInfo['EntityType'],
                                    "EntityId":myAuthInfo['EntityId'],
                                    "AppVer":myAuthInfo['AppVer'],
                                    "SessionId":myAuthInfo['SessionId']
                                }
                        }
                    }
                }
    print(myRequest)
    if not(utilityInstance.isDict(myRequest)):
        jsonify({"Status":"Error","Message":"Invalid argument {arg} passed, argument must be type of dictionary !!!".format(arg=myRequest)})
    try:
        if ( "Request" not in myRequest ) or ("Header" not in myRequest['Request']) or ('MainArg' not in myRequest['Request']):
            jsonify({"Status":"Error","Message":"Key error"})
    except Exception as error:
        jsonify({"Status":"Error","Message":"error {error}".format(error=error.message)})
    myConnections = myFactory.processRequest(myRequest)
    print(myConnections)

# Mark Few (5) member connections as a favorite
# we already have memberid,
for x in range(5):
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"MarkMemberFavorite","Page":None},
                     "MainArg":
                        {"MemberId":myMemberId,"FavoriteMemberId":myAllMembers[x]['_id']}
                    }
                  }
    #print(myRequest)
    if not(utilityInstance.isDict(myRequest)):
        jsonify({"Status":"Error","Message":"Invalid argument {arg} passed, argument must be type of dictionary !!!".format(arg=myRequest)})
    try:
        if ( "Request" not in myRequest ) or ("Header" not in myRequest['Request']) or ('MainArg' not in myRequest['Request']):
            jsonify({"Status":"Error","Message":"Key error"})
    except Exception as error:
        jsonify({"Status":"Error","Message":"error {error}".format(error=error.message)})
    MemberData = myFactory.processRequest(myRequest)
