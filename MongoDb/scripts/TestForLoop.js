print ("db is [" + db + " ]")
db = db.getSiblingDB('test')
var TotalCntr = 10000000
print ("Inserting [" + TotalCntr + " ] in db [" + db + "] ")
var curCity=0
var City = ["Edison","North Brunswick","South Brunswick","Newark","Jersey City","Princeton","Trenton"]
var totCurCityCnt=City.length
print ("starting data population @ " + new Date() )
var dataBlock = new Array
db.Test.remove({})
for (var x = 1; x <= TotalCntr; x++) {
	dataBlock[x] = {"_id":  x , "MyText": "This is test for counter [" + x + "]" ," City": City[curCity] , "When": new Date() };
	//}
	//dataBlock = dataBlock + ', {"_id":' + x + ', "MyText": "This is test for counter [" ' + x + '"]" ," City":' + City[curCity] + ', "When": new Date() }' ;
	if ( x % 1000 == 0 ) {
		//dataBlock = dataBlock + ' ] , {ordered:false}'; 
		//print (dataBlock);
		print ('Inserting 1000 documents');
		db.Test.insertMany(dataBlock,{ordered:false});
		print ('Inserted');
		dataBlock = [];
	}
	//db.Test.insert({"_id": x, "MyText": "This is test for counter [" + x + "]" ,"City":City[curCity], "When": new Date() });
	curCity++;
	if ( curCity > 4 ) {
		curCity = 0;
	} ;
	//print (dataBlock)
}




db.Test.insertMany(dataBlock);

print ("Completed ...")
print ("Total [" + db.Test.find().count() + "] documents in Test Collection")
print ("Completed data population @ " + new Date() )

db.Test.insertMany(
[ {"_id":1, "MyText": "This is test for counter [ 1]" ," City":"Edison", "When": new Date() }, {"_id":2, "MyText": "This is test for counter [ 2]" ," City":"North Brunswick", "When": new Date() } ])