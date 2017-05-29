function updateMemberTag(argMemberId){
  db.Member.find().snapshot().forEach(
    function (tag) {
        db.person.update(
            {
                _id: elem._id
            },
            {
                $set: {
                    name: elem.firstname + ' ' + elem.lastname
                }
            }
        );
    }
);

db.Member.aggregate( [
   {$match:{_id:314278}},
   {$unwind:"$Contact"},
   {$addFields: { Tag: { $concat:[ "$Main.LastName", " ", "$Main.FirstName"," ","$Address.City"," ", "$Contact.Value"] }}},
   {$project: { "Tag":1, _id:0 }}
] )

from com.uconnect.db.mongodb import MongoDB
mydb = MongoDB.Instance()


myAggregate = 'Member'
myTagConcat = "$Main.FirstName"," ","$Main.LastName", " ", "$Main.NickName", " ", "$Address.City", " ", "$Address"
myPipeLine=[{"$match":{"_id":314278}},{"$unwind":"$Contact"},{"$addFields": { "Tag": { "$concat":myTagConcat }}},{"$project": { "Tag":1, "_id":0 }}]
myAggregateCommand = {"aggregate":myAggregate, "pipeline":myPipeLine}
result = mydb.ExecCommand(myAggregateCommand)

// updating all Tag information
db.Member.find( {},{'_id':1}).forEach(function(updateMemberTag) {
    mydb = db.getCollection('Member')
    var memberid = updateMemberTag._id;
    var myTagCur = mydb.aggregate( [
        {$match:{_id:memberid}},
        //{$unwind:"$Contact"},
        {$addFields: { "Tag": { $concat:[ "$Main.LastName", " , ", "$Main.FirstName",", ","$Address.City"," ", "$Address.State"," " , "$Contact.Value"] }}},
        {$project: { "Tag":1}}
        ] );
    while (myTagCur.hasNext()){
        myTag = myTagCur.next();
    };
    print('MemberId:'+memberid,"Tag:"+myTag);

    mydb.update( {'_id':memberid}, {$set : {'Tag':myTag.Tag}} );
});


// text search
db.Member.find({$text:{$search:"\"Edison\""}},{'_id':1,'Tag':1},{score:{$meta:"textScore"}})
db.Member.find({$text:{$search:"vishal bha"}},{'_id':1,'Tag':1,score:{$meta:"textScore"}}).sort({score:{$meta:"textScore"}})