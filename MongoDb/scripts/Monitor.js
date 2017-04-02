var sleepTime = 5000 // in milliseconds, i.e. 5 seconds
var pauseCnt = TotalDocuments = CurTotalDoc = PrevTotalDoc = 0
var totalPauseCnt = 5
var myCondition = true
db = db.getSiblingDB('uconnect')
while (myCondition) {
    CurTotalDoc = TotalDocuments = db.Test.find().count();
    if (CurTotalDoc = PrevTotalDoc) {
    	PreTotalDoc = CurTotalDoc;
    	pauseCnt = 0; }
    else {
    	pauseCnt++;
    	if (pauseCnt < totalPauseCnt ) {
    		myCondition = false;
    		}
    }
	print(new Date() + " Total Documents " + db.Test.find().count()) ;
	sleep(5000);
}
