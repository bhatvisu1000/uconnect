//CopyDataToDiffColl
db.Member.aggregate({$match:{'_id':314290}}, {$out:"MemberTransaction"})
