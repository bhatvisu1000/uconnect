// Find max value of a field in colleciton
db.colleciton.find({},{_id:1}).sort({_id:-1}).limit(1).pretty()
db.collection.findOne({$query:{},$orderby:{_id:-1}})

db.myCollection.aggregate({ $group: { _id: '', last: { $max: "$_id" }} });