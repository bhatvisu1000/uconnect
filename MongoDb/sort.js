// Sort
db.orders.find().sort( { amount: -1 } )

//Queries that include a sort by $natural order do not use indexes to fulfill the query predicate //with the following exception

db.trees.find().sort( { $natural: 1 } )

