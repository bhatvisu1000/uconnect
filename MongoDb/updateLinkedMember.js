// $ne = not equal
//$eq = equal

// db.Member.find({Main:{$exists:false}},{_id:true,Main:true})
// db.Member.remove({_id:{ $in:["MEM70766","MEM70781"]}})
// Or db.Member.remove({Main:{$exists:false}})

//Loop thru documents and update the same document
var MemberSet = new Array
var LinkedMemberInfo = new Array
//db.Member.find({"LinkedMember.MemberId":{$eq:null}},{_id:true}).limit(2).forEach( function(memberInfo) { 
db.Member.find({},{_id:true,"Main":true}).forEach( function(memberInfo) { 
//db.Member.find({},{_id:true,Main:true}).forEach( function(memberInfo) {
	print( "MemberId: " + memberInfo._id + "before finding 10 member to be lnked");
	// Find 10 member, except the member found in above find
	MemberSet = db.Member.find({_id:{$ne : memberInfo._id},"Main.LastName":{$ne: memberInfo.Main.LastName}},{_id:true,"Main":true}).limit(10).toArray();
	totLinkedMemberInfo = MemberSet.length;
	print( "MemberId: " + memberInfo._id + "before going in loop" + totLinkedMemberInfo);
	//print("Total Member"+ totLinkedMemberInfo);
	for (var x=0; x < totLinkedMemberInfo; x++){
		//print("_id:"+MemberSet[x]._id);
		//print("Last Name:"+MemberSet[x].Main.LastName);	
		//print("Current Element:" + x);	
		LinkedMemberInfo[x] = 
			{"MemberId":MemberSet[x]._id,"LastName":MemberSet[x].Main.LastName,"FirstName":MemberSet[x].Main.FirstName,
			 "Sex":MemberSet[x].Main.Sex,"IsFavorite":true,"StartDt": new Date(),"EndDt":""};
			//{"MemberId":"MEM10001","LastName":"Smith","FirstName":"Dianna","Sex":"Male","IsFavorite":"true",
			//"StartDt":"01/01/2016","EndDt":"01/30/2020"},		
	}
    //db.Member.update({"_id":memberInfo._id},{"LinkedMember":[]});
    db.Member.update({"_id":memberInfo._id},{$addToSet:{"LinkedMember":{$each:LinkedMemberInfo}}});
    // $push
    MemberSet = [];
});



// Example of addToSet
//> db.Test1.update({_id:'1001'},  { $set : {myArray:[]}})
//WriteResult({ "nMatched" : 1, "nUpserted" : 0, "nModified" : 1 })
//> db.Test1.find()
//{ "_id" : "1001", "myArray" : [ ] }
//> print(a.length)
//3
//> db.Test1.update({_id:'1001'},  { $addToSet : {myArray:{$each:a}}})
//WriteResult({ "nMatched" : 1, "nUpserted" : 0, "nModified" : 1 })
//> db.Test1.find()
//{ "_id" : "1001", "myArray" : [ { "MyId" : "Id10001" }, { "MyId" : "Id10002" }, { "MyId" : "Id10003" } ] }
//>
//db.collecyion.findAndModify and $push
// 