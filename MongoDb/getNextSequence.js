//function to ge the next sequence for Member/Group/Vendor/VendorLoc/Schedue/Activity

function getNextSequence(DbConn, CollName) {
   DbConnCounters = DbConn.getCollection('counters')
   DbConnColl = DbConn.getCollection(CollName)
    var KeyId = DbConnCounters.findAndModify(
           {
             query: { _id: name },
             update: { $inc: { seq: 1 } },
             new: true
           });
     if ( dbConnCol.find({"_id":KeyId.seq}).count() > 0 ) {
        break;
     }
    return KeyId.seq;
}

function getNextKeyValue( argCollName) {

  //var DbConn = connect(argDbConn)
  //DbConnCntrs = DbConn.getCollection('counters');
  //DbConnColl = DbConn.getCollection(argCollName);  
  DbConnCntrs = db.getCollection('counters');
  DbConnColl = db.getCollection(argCollName);  
  
  var NextKeyValue = '';

  var Key = DbConnCntrs.findAndModify
  (
    { query: { _id: argCollName }, update: { $inc: { seq: 1 } },  new: true }, {write_concern: {w:"majority", wtimelut: 1000}}
  );
  // need to find if generated keyvalue already exists in collection
  NextKeyValue = Key.seq;
  if ( DbConnColl.find({"_id":NextKeyValue}).count() > 0 ) {
    // keyvalue already exists in collection, lets get the maxvalue from collection and update same value in counters
    // collection

    var MaxKeyValue = DbConnColl.find({},{_id:1}).sort({_id:-1}).limit(1);
    print (MaxKeyValue[0]._id);
    NextKeyValue = NumberLong ((MaxKeyValue[0]._id).replace (/[^0-9]/g,"") )+1;

    DbConnCntrs.update({"_id":argCollName}, { $set: { seq: NextKeyValue } });
  }

  return NextKeyValue;
}

// Following will save the Js function in system collection.
db.system.js.save(
   {
     _id: "getNextSequence",
     value : function getNextKeyValue(argCollName) {

              //var DbConn = connect(argDbConn)
              DbConnCntrs = db.getCollection('counters');
              DbConnColl = db.getCollection(argCollName);  
              var NextKeyValue = '';

              var Key = DbConnCntrs.findAndModify
              (
                { query: { _id: argCollName }, update: { $inc: { seq: 1 } },  new: true }, {write_concern: {w:"majority", wtimelut: 1000}}
              );
              // need to find if generated keyvalue already exists in collection
              NextKeyValue = Key.seq;
              if ( DbConnColl.find({"_id":NextKeyValue}).count() > 0 ) {
                // keyvalue already exists in collection, lets get the maxvalue from collection and update same value in counters
                // collection

                var MaxKeyValue = DbConnColl.find({},{_id:1}).sort({_id:-1}).limit(1);
                print (MaxKeyValue[0]._id);
                NextKeyValue = NumberLong ((MaxKeyValue[0]._id).replace (/[^0-9]/g,"") )+1;

                DbConnCntrs.update({"_id":argCollName}, { $set: { seq: NextKeyValue } });
              }

              return NextKeyValue;
            }
    });


// Load the function for current database.
db.loadServerScripts();





function getNextSequence(name) {
   var ret = db.counters.findAndModify(
          {
            query: { _id: name },
            update: { $inc: { seq: 1 } },
            new: true
          }
   );
   return ret.seq;
}



function getNextSequence(name) {
   var ret = db.counters.findAndModify(
          {
            query: { _id: name },
            update: { $inc: { seq: 1 } },
            new: true
          }
   );
   return ret.seq;
}

## To display the Family GroupId owned by this Member, would need an indicator of Family Group in Member documents
function getGroupId(ownerMemberId) {
   var ret = db.Member.find( {"_id": ownerMemberId, "LinkedGroup.GroupType":"Private"},{"_id":false,"LinkedGroup.GroupId":true});
   print (ret)
   return ret;
}
