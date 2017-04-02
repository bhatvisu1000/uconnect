// var newConn = new Mongo ('localhost:port')
newConnDb = server2.getDB('test')
newConnDbColl = newConn.getCollection('Member')
newConnDbColl.count()
