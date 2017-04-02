// hint
//The following example returns all documents in the collection named users using the index on the age field.

db.users.find().hint( { age: 1 } )

// You can also specify the index using the index name:

db.users.find().hint( "age_1" )