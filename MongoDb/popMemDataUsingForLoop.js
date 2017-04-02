db = db.getSiblingDB('test');
db.loadServerScripts();
var MemberFirstNameList=["John","Dianna","Mark","Michele","Mark","Steve","David","Edward","Richard","Gio","Ramen","Willaim","James","Ethan","John"]	
var MemberLastNameList=["Smith","Jackson","Robinson","Seterburg","Markel","Jones","Euma","Brown","Miller","Thompson","Lopez","Lee","Harris","Gonzalez","Clark"]	
var StreetList=["Main Street","Pine Street","Lake Ave","River Road","Lake Ave","Ridge Street","Church Street","Willow Street","Sunset Ave","Mill Road","Jackson Street","Cherry Street","Center Street","Hillcrest Ave","Madison Ave"]
var CityList=[
	{"City":"Princeton","ZipCode":"08542"},
	{"City":"Plainsboro","ZipCode":"08536"},
	{"City":"Trenton","ZipCode":"08601"},
	{"City":"Roseland","ZipCode":"07068"},
	{"City":"Jersey City","ZipCode":"07097"},
	{"City":"Rutherford","ZipCode":"07070"},
	{"City":"Basking Ridge","ZipCode":"07920"},
	{"City":"Bridgewater","ZipCode":"08807"},
	{"City":"Bloomsbury","ZipCode":"08804"},
	{"City":"Franklin Park","ZipCode":"08823"},
	{"City":"Monmouth Junction","ZipCode":"08852"},
	{"City":"Iselin","ZipCode":"08830"},
	{"City":"South Amboy","ZipCode":"08879"},
	{"City":"Perth Amboy","ZipCode":"08861"},
	{"City":"New Brunswick","ZipCode":"08901"},
	{"City":"Lyndhurst","ZipCode":"07071"},
	{"City":"Lakewood","ZipCode":"08701"},
	{"City":"Somerville","ZipCode":"08876"} ]
var TotLNameCnt = TotFNameCnt = TotStreetCnt = TotCityCnt = 0
var vLastName = vFirstName = vStreet = vCity = vZipCode = vState = ""
TotLNameCnt = MemberLastNameList.length -1
TotFNameCnt = MemberFirstNameList.length -1
TotStreetCnt = StreetList.length -1
TotCityCnt = CityList.length -1
vState = "New Jersey"
var dataBlock = new Array
db.Member.remove({});
for (var curCityCnt = 0; curCityCnt <= TotCityCnt; curCityCnt ++) {
	for (var curStreetCnt = 0; curStreetCnt <= TotStreetCnt; curStreetCnt ++) {
		for (var curFNameCnt = 0; curFNameCnt <= TotFNameCnt; curFNameCnt++) {
			for (var curLNameCnt = 0; curLNameCnt <= TotLNameCnt; curLNameCnt++ ) {
				vLastName = MemberLastNameList[curLNameCnt];
				vFirstName = MemberFirstNameList[curFNameCnt];
				vStreet = StreetList[curStreetCnt];
				vCity = CityList[curCityCnt].City;
				vZipCode = CityList[curCityCnt].ZipCode;
				dataBlock[curCityCnt] = {"_id": "MEM" + getNextSequence("MemberId") ,
	  				"Auth":{"AuthType":""},
	  				"Main":{"LastName":vLastName,"FirstName":vFirstName,"Sex":"M"},
	  				"Address":{"Street": curCityCnt + " " + vStreet,"City":vCity,"State":vState,"Zip":vZipCode},
	  				"Contact":{"Mobile":"7325558273","Email":vLastName+"."+vFirstName+"@uconnect.com","Other":""},
	  				"LinkedMember":[],
	  				"LinkedGroup":[{"GroupId":"GRPFAM" + getNextSequence("GroupId") ,
	                  "GroupName":"MyFamily","IsOwner":true,"GroupType":"Private","StartDt": new Date() ,"EndDt":""}],
	  				"LinkedVendor":[],
	  				"BusyHours":[{"Week":"*","WeekDay":["MO","TU","WE","TH","FR"],"StartHours":"09:00","EndHours":"17:00"}],
	  				"BusyDays":[{"StartDate": new Date() ,"EndDate":"","CreatedDt": new Date() }],	                  
	  				"VacationDays":[],
	  				"MyFavorite":[],
	  				"MyBlocked":[]
				};
			}
			db.Member.insertMany(dataBlock,{ordered:false});
			dataBlock = [];
		}
	}
}

// Lets update the LinkedMember
// $ne = not equal
//$eq = equal

//Loop thru documents and update the same document
var MemberSet = new Array
var LinkedMemberInfo = new Array
//db.Member.find({"LinkedMember.MemberId":{$eq:null}},{_id:true}).limit(2).forEach( function(memberInfo) { 
db.Member.find({},{_id:true,Main:true}).forEach( function(memberInfo) { 
//db.Member.find({},{_id:true,Main:true}).forEach( function(memberInfo) {
	print( "MemberId: " + memberInfo._id );
	// Find 10 member, except the member found in above find
	MemberSet = db.Member.find({_id:{$ne : memberInfo._id},"Main.LastName":{$ne:memberInfo.Main.LastName}},{_id:true,"Main":true}).limit(10).toArray();
	totLinkedMemberInfo = MemberSet.length-1;
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
    db.Member.update({"_id":memberInfo._id},{"LinkedMember":[]});
    db.Member.update({"_id":memberInfo._id},{$addToSet:{"LinkedMember":{$each:LinkedMemberInfo}}});
    MemberSet = [];
});


// This is test

for (var curFNameCnt = 0; x <= TotFNameCnt; x++) {
	db.Test.insert({"_id": x, "MyText": "This is test for counter [" + x + "]" ,"City":City[curCity], "When": new Date() });
	curCity++;
	if ( curCity > 4 ) {
		curCity = 0
	} ;
}
