// load Group Data
db.Group.remove({})
db.Group.insert({'_id':1001,'Main':{'GroupName':'Family Group','GroupOwnerMemberId':314103,'TotalParticipants':1},'Participants':[{'MemberId':314103,'IsOwner':1}]})
db.Group.update({'_id':1001},{$addToSet:{'Participants':{'MemberId':314102,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1001},{$addToSet:{'Participants':{'MemberId':314104,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1001},{$addToSet:{'Participants':{'MemberId':314105,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1001},{$addToSet:{'Participants':{'MemberId':314106,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1001},{$addToSet:{'Participants':{'MemberId':314107,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})

db.Group.insert({'_id':1002,'Main':{'GroupName':'Friends Group','GroupOwnerMemberId':314102,'TotalParticipants':1},'Participants':[{'MemberId':314102,'IsOwner':1}]})
db.Group.update({'_id':1002},{$addToSet:{'Participants':{'MemberId':314103,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1002},{$addToSet:{'Participants':{'MemberId':314104,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1002},{$addToSet:{'Participants':{'MemberId':314105,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1002},{$addToSet:{'Participants':{'MemberId':314106,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})
db.Group.update({'_id':1002},{$addToSet:{'Participants':{'MemberId':314107,'IsOwner':0}}},{$inc:{'Main.TotalParticipants':1}})

db.Group.aggregate([
    {$match: {"Participants.MemberId":314103} },
    {$unwind : {path:"$Participants",preserveNullAndEmptyArrays:true}},  
    {$lookup:{
        from:"Member",
        localField:"Participants.MemberId",                  
        foreignField:"_id",                  
        as:"MemberParticipants"}      
    },
    {$project: 
        {
            "_id":"$id", "Main":"$Main","Participants":"$Participants",
            "MemberParticipants.Main":1,"MemberParticipants.Address":1,"MemberParticipants.Contact":1                    
        }
     }],
   {allowDiskUse:true}
).toArray()

db.Group.aggregate([
    {$match: {"Participants.MemberId":314103} },
    {$unwind : {path:"$Participants",preserveNullAndEmptyArrays:true}},  
    {$lookup:{
        from:"Member",
        localField:"Participants.MemberId",                  
        foreignField:"_id",                  
        as:"MemberParticipants"}      
    },
    {$project: 
        {
            "_id":1, "Main":1,"Participants":1,
            "MemberParticipants.Main":1,"MemberParticipants.Address":1,"MemberParticipants.Contact":1                    
        }
     }],
   {allowDiskUse:true}
).toArray()