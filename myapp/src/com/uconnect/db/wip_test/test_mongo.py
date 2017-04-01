from pymongo import MongoClient

from pymongo import write_concern
from pymongo import results

db = "test"
collection="Member"
criteria = {"_id":"MEM192551"}
projection = {"_id":"aaaa"}
mongoUri="mongodb://localhost:27017/test?connectTimeoutMS=300000&maxPoolSize=100&minPoolSize=10&w=1"
conn = MongoClient(mongoUri)
conn1 = conn.get_database(db)

''' 
#find the results from insert one

myresults = conn1.test.insert_one({"_id":"id002","a":"10"})
print myresults.inserted_id
print myresults.acknowledged

'''

''' 
#testing call to js function stored in Mongo

conn2 = conn1[collection]
data = conn2.find(criteria,projection)
key = conn2.eval("getNextSequence",argCollection)
myKeyValue = int(conn1.system_js.getNextSequence(collection))

'''
# testing insert many doc in mongo

if type(data) == dict:
   print 'dict'
elif type(data) == 'mymongo.cursor.Cursor':
    print 'cursor'

data = conn1.collection_names()
print ('Member' in data)

'''