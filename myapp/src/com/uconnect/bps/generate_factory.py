from pymongo import MongoClient
import json os
from bson.json_util import dumps
from bson import json_util

db = "test"
collection="Member"
criteria = {"_id":"MEM192551"}
projection = {"_id":"aaaa"}
mongoUri="mongodb://localhost:27017/test?connectTimeoutMS=300000&maxPoolSize=100&minPoolSize=10&w=1"
conn = MongoClient(mongoUri)
conn1 = conn.get_database(db)
fileName = 'test.json'

with open(fileName, "w") as f:
    #truncate the data
    f.truncate()
    l = list(conn1.Member.find().limit(100))    
    mystring = json.dumps(l, ensure_ascii=False, default=json_util.default, indent = 4)
    if os.path.isfile(fileName):
        f.truncate()
    f.write(mystring)



    json.dump(mystring,f)
    json.dump(json.dumps(l, ensure_ascii=False, default=json_util.default, separators=(',',':')),f,indent = 4)
    json.dump(list(conn1.Member.find().limit(1)), f)  
    l = conn1.Member.find().limit(1)
    print (l)
    #for x in (conn1.Member.find().limit(1)):
    for x in l:
        print(x)
        f.write(x)
        #json.dumps(x,f,indent = 4)
    json.dump(json.dumps(l,default=json_util.default, separators=(',',':')),f,indent = 4)



call("mongoexport --db test --collection url_db --query '{\"state\": \"processed\"}' --out " + outfile, shell=True)