db.member.remove({})
db.grp.remove({})
db.vendor.remove({})

//vendor
    Main
    Address
    WWW
    TotalLocation
    Promotion: {Text, Start and End Date}
    Business :{Type, SubType}
    ServiceOffering

//Location
    Vendor: {id}
    Main:Name
    Address
    Contact
    Tag:
    ServiceOffering:
// Agent


//LocationHrs
//LocationSettings

db.vendor.insert({
    "_id":1001,
    "Main":{"Name":"Abc Automobile","Type":"","ServiceOffering":[]},
    "Location":[
        {
            "LocationId":1001,
            "Main":{"Name":"Edison","AcceptWaitList":0,"WaitQueueLength":6},
            "Address":{"Street":"1 Main Street", "City":"Edison","State":"NJ","ZipCode":08820},
            "Contact":{"Phone":"9085551212","Email":"abcAuto@uconnect.com","WWW":"http://uconnect.com/abcAutoMobile/Edison/Main.html"},
            "Agent":{}
        },
        {
            "LocationId":1002,
            "Main":{"Name":"Woodbridge","AcceptWaitList":0,"WaitQueueLength":6},
            "Address":{"Street":"1 Main Street", "City":"Woodbridge","State":"NJ","ZipCode":08828},
            "Contact":{"Phone":"9085551213","Email":"abcAuto@uconnect.com","WWW":"http://uconnect.com/abcAutoMobile/Edison/Main.html"},
            "Agent":{}
        }]
    }
)

db.member.insert(
    {"_id": 1001,
     "Main":{"LastName":"Smith","FirstName":"Michael","Sex":"M"},
     "Connections": [
        {"MemberId":1002,"Favorite":0,"Blocked":0,"Type":"Member"},
        {"MemberId":1003,"Favorite":0,"Blocked":0,"Type":"Member"},
        {"GroupId":1001,"Favorite":0,"Blocked":0,"Type":"Group"},
        {"LocationId":1001,"Favorite":0,"Blocked":0,"Type":"Vendor"}]
    }
)

db.member.insert(
    {"_id": 1002,
     "Main":{"LastName":"Smith","FirstName":"Erika","Sex":"F"},
     "Connections": [
        {"MemberId":1001,"Favorite":0,"Blocked":0,"Type":"Member"},
        {"GroupId":1001,"Favorite":0,"Blocked":0,"Type":"Group"}]
    }
)


db.member.insert(
    {"_id": 1003,
     "Main":{"LastName":"Debass","FirstName":"David","Sex":"M"},
     "Connections": [
        {"MemberId":1001,"Favorite":0,"Blocked":0,"Type":"Member"},
        {"LocationId":1001,"Favorite":0,"Blocked":0,"Type":"Location"}]
    }
)

//Member

db.member.aggregate([
    {$match: {"_id":1001}},
    {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
    {$match: { $and: [{"Connections.Type":"Member"} ] } },
    {$lookup:{
        from:"member",
        localField:"Connections.MemberId",                  
        foreignField:"_id",                  
        as:"MemberConnections"}      
    },
    {$project: 
        {
            "_id":1, "Main":1,"Connections":1,
            "MemberConnections.Main":1,"MemberConnections.Address":1,"MemberConnections.Contact":1                    
        }
     }],
   {allowDiskUse:true}
).toArray()
//Group
db.member.aggregate([
    {$match: {"_id":1001}},
    {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
    {$match: { $and: [{"Connections.Type":"Group"} ] } },
    {$lookup:{
        from:"grp",
        localField:"Connections.GroupId",                  
        foreignField:"_id",                  
        as:"GroupConnections"}      
    },
    {$project: 
        {
            "_id":1, "Main":1,"Connections":1,
            "GroupConnections.Main":1,"GroupConnections.Address":1,"GroupConnections.Contact":1                    
        }
     }],
   {allowDiskUse:true}
).toArray()

//Vendor

db.member.aggregate([
    {$match: {"_id":1001}},
    {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
    {$match: { "Connections.Type":"Vendor" } },
    {$lookup:{
        from:"grp",
        localField:"Connections.LocationId",                  
        foreignField:"_id",                  
        as:"VendorConnections"}      
    },
    {$project: 
        {
            "_id":1, "Main":1,"Connections":1,
            "VendorConnections.Main":1,"VendorConnections.Address":1,"VendorConnections.Contact":1                    
        }
     }],
   {allowDiskUse:true}
).toArray()


db.member.aggregate([
    {$match: {"_id":1001}},
    {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
    {$match: { $and: [  {"_id":1001}, {"Connections.Type":"Group"} ] } },
    {$lookup:{
        from:"member",
        localField:"Connections.MemberId",                  
        foreignField:"_id",                  
        as:"MyMemberConnections"}      
    },
    {$lookup:{
        from: "grp",
        localField:"Connections.GroupId",                  
        foreignField:"_id",                  
        as:"MyGroupConnections"}      
    },
    {$unwind : {path:"$vendor.Location",preserveNullAndEmptyArrays:true}},  
    {$lookup:{
        from: "vendor",
        localField:"Connections.LocationId",                  
        foreignField:"_id",                  
        as:"MyVendorConnections"}      
    },    
    {$project: 
        {
            "_id":1, "Main":1,"Favorite":"$Connections.Favorite", "ConnType":"$Connections.Type",
            "MyMemberConnections.Main":1,"MyMemberConnections.Address":1,"MyMemberConnections.Contact":1,
            "MyGroupConnections.Main":1,"MyGroupConnections.Participant":1,
            "MyVendorConnections.Main":1,"MyVendorConnections.Location":1,"MyVendorConnections.Contact":1                    
        }
     }],
   {allowDiskUse:true}
)

db.member.aggregate([
    {$match: {"_id":1001}},
    {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
    {$lookup:{
        from:"member",
        localField:"Connections.MemberId",                  
        foreignField:"_id",                  
        as:"MyMemberConnections"}      
    },
    {$lookup:{
        from: "grp",
        localField:"Connections.GroupId",                  
        foreignField:"_id",                  
        as:"MyGroupConnections"}      
    },
    {$unwind : {path:"$vendor.Location",preserveNullAndEmptyArrays:true}},  
    {$lookup:{
        from: "vendor",
        localField:"Connections.LocationId",                  
        foreignField:"_id",                  
        as:"MyVendorConnections"}      
    },    
    {$project: 
        {
            "_id":1, "Main":1,"Favorite":"$Connections.Favorite", "ConnType":"$Connections.Type",
            "MyMemberConnections.Main":1,"MyMemberConnections.Address":1,"MyMemberConnections.Contact":1,
            "MyGroupConnections.Main":1,"MyGroupConnections.Participant":1,
            "MyVendorConnections.Main":1,"MyVendorConnections.Location":1,"MyVendorConnections.Contact":1                    
        }
     }],
   {allowDiskUse:true}
)


from pymongo import MongoClient
import json
client = MongoClient('mongodb://localhost:27017/')
db=client['test']
pipeLine = [ 
   {"$match"  : {"_id":1001}},
   {"$unwind" : {"path":"$Connections","preserveNullAndEmptyArrays":True}},  
   {"$match"  : { "$and": [{"Connections.Type":"Member"} ] } },
   {"$lookup" :{
        "from":"member",
        "localField":"Connections.MemberId",                  
        "foreignField":"_id",                  
        "as":"MyMemberConnections"}      
    },
    {"$project": 
        {
            "_id":1, "Main":1,"Connections":1,
            "MyMemberConnections.MemberId":1,
            "MyMemberConnections.Main":1,"MyMemberConnections.Address":1,"MyMemberConnections.Contact":1
        }
     }
    ]

myConnectionRawData = db.command('aggregate','member',pipeline=pipeLine, allowDiskUse=True)

myResultStatus = {"Success":myConnectionRawData['ok']}
myMemberConnRawData = myConnectionRawData['result']
myMemberConnections = {"_id":myMemberConnRawData[0]['_id']}

myMemberConnections['Connections'] = []
for x in myMemberConnRawData:
    x['MyMemberConnections'][0].update({'Favorite':x['Connections']['Favorite']})
    x['MyMemberConnections'][0].update({'Blocked':x['Connections']['Blocked']})
    x['MyMemberConnections'][0].update({'MemberId':x['Connections']['MemberId']})
    myMemberConnections['Connections'].append(x['MyMemberConnections'][0])

# sorting now
myMemberConnections = json.dumps(myMemberConnections, sort_keys=True)    


print myMemberConnections

// Find Connections using $graphLookup

// Find linked member
//      db.temp.find({"Connections.Member.id":1001},{"_id":1,"Connections.Member.Favorite.$":1})
// Mark/UnMark Favorite
//      db.Member.update({'_id':313848,'LinkedBy.MemberId':313850},{ $set : {'LinkedBy.$.Favorite':1}})

//      db.temp1.find({"LinkedBy.MemberId":1001},{"_id":1,"LinkedBy.MemberId.$":1})

//db.test.aggregate({$match: {"LinkedBy.Member.id":1001}},
//                  {$unwind: $LinkedBy},
//                 {$match: {'LinkedBy.Member.id':1001}},
//                  {$group: {_id: $LinkedBy, LinkedBy: {$push :'$LinkedBy.Member.id'}}})

//db.test.find({list: {$elemMatch: {"LinkedBy.Member.id": 1001}}}, {'list.$': 1})




// aggregate $lookup, nned to unwind if value from array need to be used for matching
// This works
db.temp1.aggregate( 
    [
        {$match : {"_id":1008}},
        {$unwind : {path:"$Connections",preserveNullAndEmptyArrays:true}},  
        {$lookup:
            { from:"temp1",
              localField:"Connections.MemberId",                  
              foreignField:"_id",                  
              as:"MyConnections"     
            }      
        },
        {$unwind:{path:"$Favorite",preserveNullAndEmptyArrays:true}},
        {$lookup:
            { from:"temp1",
              localField:"Favorite.MemberId",                  
              foreignField:"_id",                  
              as:"MyFavorite"     
            }      
        },        
        {$unwind:{path:"$Blocked",preserveNullAndEmptyArrays:true}},
        {$lookup:
            { from:"temp1",
              localField:"Blocked.MemberId",                  
              foreignField:"_id",                  
              as:"MyBlocked"     
            }      
        },
        {$unwind:{path:"$Connections",preserveNullAndEmptyArrays:true}},
        {$lookup:
            { from:"Group",
              localField:"Connections.GroupId",                  
              foreignField:"_id",                  
              as:"MyGroup"     
            }      
        },
        {$project:
            {"_id":1,
             "MyConnections.Main":1,
             "MyConnections._id":1, 
             "MyFavorite._id":1,
             "MyFavorite.Main":1,
             "MyBlocked._id":1,
             "MyBlocked.Main":1,
             "Group":"$mMyGroup"
            }
         }
    ]
).pretty()


db.temp1.aggregate( 
    [
        {$match : {"_id":1001}},  
        {$lookup:
            { from:"temp1",
              localField:"_id",                  
              foreignField:"Connections.MemberId",                  
              as:"MyConnections"     
            }      
        },
        {$unwind: "$MyConnections" },
        {$lookup:
            from:temp1, localField:}
        {$project:{"MyConnections.Main":1,"MyConnections._id":1}}
    ]
).pretty()

// aggregate $graphlookup (if recursive is 0, then this is same as $lookup)

db.temp1.aggregate([
     {$match: {"_id":1008}},
     {$unwind: "$Connections"},
     {$graphLookup: 
        {from: "temp1",
         startWith: "$Connections.MemberId",
         connectFromField: "Connections.MemberId",
         connectToField: "_id",
         as: "MyConnections",
         maxDepth:0,
         depthField:"Depth",
         restrictSearchWithMatch:{"Connections.Type":"Member"}
     }
    },
    {$project:{"_id":1,"Main":1,"MyConnections.Main":1,"MyConnections._id":1,"Connections":1}}
    ]
).pretty()

db.temp1.aggregate([
     {$match: {"_id":1008}},
     {$graphLookup: 
        {from: "temp1",
         startWith: "$Connections.MemberId",
         connectFromField: "Connections.MemberId",
         connectToField: "_id",
         as: "myConnections",
         maxDepth:1,
         depthField:"Depth"
        }
     },
     {$unwind: "$Conections"},
     {$graphLookup:
        {from: "temp1",
         startWith: "$Connections.MemberId",
         connectFromField: "Connections.MemberId",
         connectToField: "_id",
         as: "myFavorite",
         maxDepth:1,
         depthField:"Depth",
         restrictSearchWithMatch:{"Connections.Favorite":1}
        }
     },
     {$project: 
           {"Main":"$Connections.Main",
            "Favorite":"$myFavorite.Main",
            "Depth":"$Connections.Depth" }
     }],
   {allowDiskUse:true}
)
