// Store generated security code, secutity code must be deleted after its time to live has passed or code has been validated or
// next code is requested. Same data must be inserted in SecurityCodeLog table to maintain history of security code generation
// we need to cap this collection ???

db.createCollection('SecurityCode',{validator:{$or ....}})
db.SecurityCode.createIndex({"when":1},{expireAfterSeconds:300})
db.createCollection('SecurityCodeLog',{validator:{$or ....}})
// Sec code request: 
//      1. generate 6 digit code
//      2. Store the data in SecurityCode and SecurityCodLog table
//      3. Security code vaidation will occu on SecurityCode table
db.SecurityCode.insert({'DeviceType':'Mac',
    'DeviceMac':'0:AX:W98SFF:3244',
    'MemberId':'1220',
    'SecurityCode':'12345',
    'When': new Date() })

db.SecurityCodeLog.insert(
    {'DeviceType':'Mac',
     'Device':
        {
            'Mac':'0:AX:W98SFF:3244',
            'OS':'iOS'
        },
     'MemberId':'1220',
     'Security':
        {
            'Code':'12345',
            'CreationDate':new Date(),
            'SentTo':'',
            'SentDate':'',
            'ValidationDate':''
        }
    }
)

// Member Collection
//db.createCollection('Member',{validator:{$or ....}})
// Vendor Collection
//db.createCollection('Vendor',{validator:{$or ....}})
// Schedule Collection
//db.createCollection('Vendor',{validator:{$or ....}})
//db.createCollection('Location',{validator:{$or ....}})
//db.createCollection('Agent',{validator:{$or ....}})
//db.createCollection('Schedule',{validator:{$or ....}})
// Activity Collection
//db.createCollection('Activity',{validator:{$or ....}})
// Offers Collection
//db.createCollection('Offers',{validator:{$or ....}})
// Notification Collection
//db.createCollection('Notification',{validator:{$or ....}})

//uconnect db

db.createCollection('SecurityCode')
db.SecurityCode.createIndex({"when":1},{expireAfterSeconds:300})
db.createCollection('Auth')
db.createCollection('Member')
db.createCollection('Group')
db.createCollection('Vendor')
db.createCollection('Location')
db.createCollection('Agent')
db.createCollection('Schedule')
db.createCollection('Activity')
db.createCollection('Offers')
db.createCollection('Notification')
db.createCollection('AuthHistory')
db.createCollection('ActivityLog')

// Show all collections
// show all colectins and its indexes

db.getCollectionNames().forEach(function(collection) {
   indexes = db[collection].getIndexes();
   print("Indexes for " + collection + ":");
   printjson(indexes);
});


AllRequests
{
    "_id":"<RequestId>",
    "RequestType":"<SCHEDULE/INVITE/>"
    "From":{"Id":"1001","Type":"Member"},
    "For":{"Join Network"},
    "To"
}

Member requests another member for a connection
Member invites another Family member to join a family group
Member invites another Member to join a group
Member requests for an apppointment to Vendor
Venodr requests an appointment to member (recurring) 
    (Member must have an exisiting relationship. i.e. Member must have an appointment scheduled already with vendor)
    Vendor 
        Doctor
        Mechanic Shop
        Small Business Shop
        Event Organizer
        Schools


Vendor
{
    "_id":
    "Main":{"Name":"","Type":""},
    "Address":{"Street":"","City":"","State":"","ZipCode":"","Lattitude":"","Longitude":""},
    "Contact":{"Phone":"","URL":"","Email":""},
    "Metrics":{"Total Loctions":""}
}

Location
{
    "_id":
    "Main":
        {
            "Name":"","Type":"","Vendor":"",
            "AgentWorking":"Yes/No","IsWaitList":"YES/NO","WaitListQueueLength":0,
            "ServiceDuration","ServiceProvided":[],"IsOffHrs":""
        },
    "OffHrsService":{"OffHrsContact":"","OffHrsService":[]},
    "Address":{"Street":"","City":"","State":"","ZipCode":"","Lattitude":"","Longitude":""},
    "Contact":{"Phone":"","URL":"","Email":""},
    "Agent":
        [
            {"Id":"", "LastName":"","FirstName":"","Title":"", "WorkTitle":"","ServiceDuration":""}
        ]
}

LocationSettings:
{
    "_id":"LocationId",
    "WorkHours":
        [
            {"Week":"*","Days":"0","StartHours":"","EndHours":""},
            {"Week":"*","Days":"1","StartHours":"","EndHours":""},
            {"Week":"*","Days":"2","StartHours":"","EndHours":""},
            {"Week":"*","Days":"3","StartHours":"","EndHours":""},
            {"Week":"*","Days":"4","StartHours":"","EndHours":""},
            {"Week":"*","Days":"5","StartHours":"","EndHours":""},
            {"Week":"*","Days":"6","StartHours":"","EndHours":""}
        ]
}

AgentSettings:
{
    "_id":"AgentId",
    "WorkHours":
        [
            {"Week":"*","Days":"0","StartHours":"","EndHours":""},
            {"Week":"*","Days":"1","StartHours":"","EndHours":""},
            {"Week":"*","Days":"2","StartHours":"","EndHours":""},
            {"Week":"*","Days":"3","StartHours":"","EndHours":""},
            {"Week":"*","Days":"4","StartHours":"","EndHours":""},
            {"Week":"*","Days":"5","StartHours":"","EndHours":""},
            {"Week":"*","Days":"6","StartHours":"","EndHours":""}
        ]
}
