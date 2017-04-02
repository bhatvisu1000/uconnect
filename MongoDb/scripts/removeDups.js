var duplicates = [];

db.runCommand(
  {aggregate: "YOURCOLLECTION",
    pipeline: [
      { $group: { _id: { DUPEFIELD: "$DUPEFIELD"}, dups: { "$addToSet": "$_id" }, count: { "$sum": 1 } }},
      { $match: { count: { "$gt": 1 }}}
    ],
    allowDiskUse: true }
)
.result
.forEach(function(doc) {
    doc.dups.shift();
    doc.dups.forEach(function(dupId){ duplicates.push(dupId); })
})
printjson(duplicates); //optional print the list of duplicates to be removed

db.YOURCOLLECTION.remove({_id:{$in:duplicates}});