import os,sys,json, copy, random, datetime
from com.uconnect.bps.factory import Factory
from com.uconnect.db.mongodb import MongoDB

class loadTestData(object):
    def __init__(self):

        print('initializing')

        testDataFile = 'c:\\app\\uconnect\\MongoDb\\json\\MemberTestData.json'
        templateFile = os.path.join(os.getenv('UCONNECT_CONFIG'),'template.json')
        self.myRegScreen = 'Registration'
        self.myRegAction = 'RegisterEntity'
        self.myGenSecAction = 'GenerateSecCode'
        self.mySecValidateAction = 'ValidateSecCode'
        self.testData = []
        self.template = {}

        self.factory = Factory()
        self.mongo = MongoDB()
        
        self.testData = self.__loadJsonFile(testDataFile)
        self.template = self.__loadJsonFile(templateFile)
        self.requestTemplate = self.template['Request']

    def removCollData(self):
        print('dropping collection...')
        self.mongo.conn.drop_collection('Member')
        self.mongo.conn.drop_collection('LoginInfo')
        self.mongo.conn.drop_collection('Auth')
        self.mongo.conn.drop_collection('Schedule')
        print('collection dropped, proceeding with data load',)
    def __loadJsonFile(self, dataFile):
        if not os.path.isfile(dataFile):
            print("Data file {file} is missing, exiting !!!".format(file=dataFile))
            sys.exit(-1)
        #print ('loading test data file in memory')
        try:
            if os.path.getsize(dataFile) == 0:
                print('Data file {file} is empty, exiting !!!'.format(file=dataFile))
                sys.exit(-1)
            else:
                myData = json.loads(open(dataFile).read())
            if len(myData) == 0:
                print('Data object is empty after loading from file, exiting !!!')
                sys.exit(-1)
            return myData
        #print ('Data file is loaded in memory')
        except Exception as error:
            print('Error [{err}] occurred while loading file {file} in memory'.format(err=sys.exc_info(), file=dataFile))
            sys.exit(-1)

    def loadMemberData (self):
        print('Loading Member Data ....')
        totalSuccess = totalFailure = 0
        #creatign member
        test = []
        for member in self.testData:
        #for member in test:
            try:

                #Create Member
                print('Registering Member ...')
                myRequest = self.buildFactoryRequest(member,self.myRegScreen, self.myRegAction)
                myAuth = myRequest['Request']['MainArg']['Auth']
                memberData = self.factory.processRequest(myRequest)
                memStatus, memMessage = self.parseResult(memberData)
                #print(memberData)
                if memStatus == 'UnSuccess':
                    print('Error {error} occurred, skiping'.format(error=memMessage))
                else:    
                    myMemberId = memberData['MyResponse']['Data'][0]['_id'] 
                    print('member id [{memberid}] registered'.format(memberid = myMemberId))
                
                    # Generate Security Code
                    mySecData = {'LoginId': myAuth['LoginId']}
                    myRequest = self.buildFactoryRequest(mySecData,self.myRegScreen, self.myGenSecAction)
                    #print(myRequest)
                    myGenSecResult = self.factory.processRequest(myRequest)
                    myGenSecStatus, myGenSecMessage = self.parseResult(myGenSecResult)

                    if myGenSecStatus == 'Success':
                        myDBCriteria = {'LoginId':mySecData['LoginId']}
                        myDBProjection = {'_id':0,'SecurityCode':1}
                        mySecurityCode = self.mongo.findDocument('SecurityCode',myDBCriteria,myDBProjection,True)['Data'][0]['SecurityCode']
                        print('sec code [{code}] generated'.format(code=mySecurityCode))
    
                        mySecValData = {'LoginId':myAuth['LoginId'], 'SecurityCode':mySecurityCode}
                        myRequest = self.buildFactoryRequest(mySecValData, self.myRegScreen, self.mySecValidateAction)
                        #print('Sec validation request >>>',myRequest)
                        myValSecResult = self.factory.processRequest(myRequest)
                        myValSecStatus, myValSecMessage = self.parseResult(myValSecResult)
                        if myValSecStatus == 'Success':
                            print('Security code {code} validated successfuly'.format(code=mySecurityCode))
                            print('Member {member} created successfuly'.\
                                format(member=''.join([str(myMemberId), '-', myAuth['LoginId'] ] )))
                            totalSuccess+=1
                        else:
                            print('Security code {code} could not be validated, message {message}'.format(code=mySecurityCode, message = myValSecMessage))
                    else:
                        print('sec code could not be generated, message {result}'.format(message=myGenSecMessage))
                        print('skipping security code generation/validation')
                    # validate security code
            except Exception as error:
                print('Error {err} occured, skipping '.format(err=sys.exc_info()[0:]))
                totalFailure+=1
                #raise error
        print('Status {success} out of {total}'.format(success=totalSuccess, total=len(self.testData)))

        #creating 5 connection for this member
        print('creating connection ....')
        print('creating 5 connection for all members')

        allLoginList = self.mongo.findDocument('LoginInfo',\
            {'AccountStatus':'Open','EntityType':'Member'},{'_id':1,'LoginType':1, 'EntityType':1, 'EntityId':1})['Data']
        myRequest = {}
        print('Total Login found in Open status >>> {cnt}'.format(cnt=len(allLoginList)))
        #input("Press Enter to Continue ...")

        for login in allLoginList:
            # get the auth for this member, we need to validate login id
            myMember = self.mongo.findDocument('Member',{'_id':login['EntityId']},{},True)['Data'][0]
            print('Adding connection for memebr {member}'.format(member=myMember['_id']))
            myAuth = self.mongo.findDocument('Auth',{'EntityId':myMember['_id'], 'ExpiryDate': {'$gt' : datetime.datetime.now()}},{},True)['Data'][0]
            myAuth.update({'AuthKey':myAuth['_id']})

            #get 5 member fromt this database except this member            
            myResult = self.mongo.ExecCommand({'find':'Member',
                'filter':{'_id': {'$nin':[login['EntityId']]}}, 
                'projection':{'_id':1}, '$sample' : {'size':5}, 'limit':5})
            myMemberConnList = myResult['cursor']['firstBatch']
            print("Connection count:",len(myMemberConnList))
            #print(myResult)

            for conn in myMemberConnList:
                myRequest = self.buildFactoryRequest({'ConnMemberId':conn['_id'],'Action':'Invite','Auth':myAuth}, 'Member', 'UpdateConnectionDetails')
                myResult = self.factory.processRequest(myRequest)
                myResultStatus, myResultMessage = self.parseResult(myResult)
                if myResultStatus == 'Success':
                    print('Connection {member} --> {conn} request is Successful '.format(member = myAuth['EntityId'], conn = conn['_id']))
                else:
                    print('Connection {member} --> {conn} request is Unsuccessful, message >> {msg} '.format(member = myAuth['EntityId'], conn = conn['_id'], msg = myResultMessage))
                print('Connection {conn} added to member {member}'.format(conn=conn['_id'], member=myAuth['EntityId']))
            # last connection to be accepted by invitee
            
            myInvitee = myRequest['Request']['MainArg']['UpdateConnections'][0]['Id']
            myAuth = self.mongo.findDocument('Auth',{'EntityId':myInvitee, 'ExpiryDate': {'$gt' : datetime.datetime.now()}},{},True)['Data'][0]
            myAuth.update({'AuthKey':myAuth['_id']})
            myRequest = self.buildFactoryRequest({'ConnMemberId':myMember['_id'],'Action':'Accept','Auth':myAuth}, 'Member', 'UpdateConnectionDetails')
            myResult = self.factory.processRequest(myRequest)
            if myResultStatus == 'Success':
                print('Connection [{member}] --> [{conn}] is Successful'.format(member = myMember['_id'], conn = myInvitee))
            else:
                print('Connection [{member}] --> [{conn}] is Unsuccessful, message >> {msg}'.format(member = myMember['_id'], conn = myInvitee, msg = myResultMessage))

        # we need to build some schedule data
    #def getStartTime()

    def loadSchedules(self):
        allLoginList = self.mongo.findDocument('LoginInfo',\
            {'AccountStatus':'Open','EntityType':'Member'},{'_id':1,'LoginType':1, 'EntityType':1, 'EntityId':1})['Data']
        myRequest = {}
        print('Total Login found in Open status >>> {cnt}'.format(cnt=len(allLoginList)))
        print('Creating schedule for all the open accounts')

        for login in allLoginList:
            myMember = self.mongo.findDocument('Member',{'_id':login['EntityId']},{},True)['Data'][0]
            print('creating schedule for memebr {member}'.format(member=myMember['_id']))
            myAuth = self.mongo.findDocument('Auth',{'EntityId':myMember['_id'], 'ExpiryDate': {'$gt' : datetime.datetime.now()}},{},True)['Data'][0]
            myAuth.update({'AuthKey':myAuth['_id']})

            #get 5 member fromt this database except this member            
            myAllInvitee = self.mongo.ExecCommand({'find':'Member',
                'filter':{'_id': {'$nin':[login['EntityId']]}}, 
                'projection':{'_id':1}, '$sample' : {'size':5}, 'limit':5})['cursor']['firstBatch']
            
            print("Invitee count:",len(myAllInvitee))

            schedDetails = [
                {"Description":"Business discussion", "Place": "Starbucks","StartTime":"2017-12-12 09:00:00"},
                {"Description":"Movie", "Place": "Starbucks","StartTime":"2017-12-28 10:00:00"},
                {"Description":"Cricket Trounament", "Place": "Starbucks","StartTime":"2018-01-10 11:00:00"},
                {"Description":"Shopping", "Place": "Starbucks","StartTime":"2018-01-15 18:00:00"},
                {"Description":"Lunch", "Place": "Starbucks","StartTime":"2018-01-19 16:00:00"}
            ]

            for seq, invitee in enumerate(myAllInvitee):
                #print(seq,invitee)
                # build schedule data
                schedData = {
                    "ScheduleDetails" : {
                        "Description"   : schedDetails[seq]["Description"],
                        "Place"         : schedDetails[seq]["Place"],
                        "StartTime"     : schedDetails[seq]["StartTime"],
                        "DurationMins"  : 30
                    },
                    "Invitee" : [
                        {"Id" : invitee['_id'], "Type":"Member", "IsOwner":"N"}
                    ],
                    "ShareWith":[{"MemberId" : "<Family memberid"}],
                    "Tasks": [],
                    "WaitList" : [], 
                    "Repeat": {
                        "RepeatSchedule": "Every Day/Date of Week/Month/Year",
                        "StartDate": "Repeat Start Date",
                        "EndDate": "Repeat End Date"
                    },
                    "Auth" :{
                        "AuthKey" : myAuth["AuthKey"],
                        "LoginId" : myAuth["LoginId"],
                        "LoginType" : myAuth["LoginType"],
                        "DeviceType" : myAuth["DeviceType"],
                        "DeviceOs" : myAuth["DeviceOs"],
                        "MacAddress" : myAuth["MacAddress"],
                        "SessionId" : myAuth["SessionId"],
                        "EntityType" : myAuth["EntityType"],
                        "EntityId" : myAuth["EntityId"],
                        "AppVer" : myAuth["AppVer"]
                    }
                }
                myRequest = self.buildFactoryRequest(schedData,'Schedule','NewSchedule')
                # we need to get diff timing for each of the schdule
                myResult = self.factory.processRequest(myRequest)
                #print(myResult)
                myResultStatus, myResultMessage = self.parseResult(myResult)
                if myResultStatus == 'Success':
                    print('Schedule between {member} and {inv} creatino was successful '.format(member = myAuth['EntityId'], inv = invitee['_id']))
                else:
                    print('Schedule between {member} and {inv} creation was unsuccessful** '.format(member = myAuth['EntityId'], inv = invitee['_id']))
                    print('Error',myResult)
                
                #print(schedData)

    def parseResult(self, argResult):
        return argResult['MyResponse']['Header']['Status'], argResult['MyResponse']['Header']['Message']

    def buildFactoryRequest(self, data, argScreenId, argActionId):
        myRequest = copy.deepcopy(self.requestTemplate)
        #print(myRequest)
        myRequest['Request']['Header'] = {'ScreenId' : argScreenId, 'ActionId' : argActionId, 'Page':None}
        #print('build',myRequest)
        if argScreenId == self.myRegScreen:

            if argActionId == self.myRegAction:
                myRequest['Request']['MainArg'] = {
                    'Main' : {
                        'LastName': data['Main']['LastName'],
                        'FirstName':data['Main']['FirstName'], 
                        'NickName': ''.join([data['Main']['FirstName'][0],data['Main']['LastName'][0]]) },
                    'Address' : {'ZipCode':data['Address']['ZipCode']},
                    'Contact' : {'Email':data['Contact']['Email']},
                    'Auth': {
                        'LoginId':data['Contact']['Email'],
                        'LoginType':'Web',
                        'Password':data['Main']['FirstName'],
                        'DeviceType': 'OS2',
                        'DeviceOs': 'Web',
                        #'MacAddress' : ''.join([data['Main']['FirstName'],data['Main']['LastName'],data['Contact']['Email']]),
                        'MacAddress' : 'MACADDRESS:001',
                        'EntityType': 'Member',
                        'AppVer' : '1.0',
                        'SessionId' : str(random.random())
                    }
                }
                #print('in build factory',myRequest)
            elif argActionId == self.myGenSecAction:
                # must pass the auth dict which was used to create the member
                myRequest['Request']['MainArg'] = {'SecurityCode':{'LoginId': data['LoginId'], 'DeliveryMethod': 'Email', 'DeliverTo': data['LoginId']}}
            elif argActionId == self.mySecValidateAction:
                myRequest['Request']['MainArg'] = {'SecurityCode':{'LoginId': data['LoginId'], 'SecurityCode': data['SecurityCode']}}
        elif argScreenId == 'Login':
            if argActionId == 'Authenticate':
                myRequest['Request']['MainArg'] = {
                    'Auth':{
                        'LoginId'    : data['Auth']['LoginId'],
                        'Password'   : data['Password'],
                        'LoginType'  : data['Auth']['LoginType'],
                        'DeviceOs'   : data['Auth']['DeviceOs'],
                        'DeviceType' : data['Auth']['DeviceType'],
                        'MacAddress' : data['Auth']['MacAddress'],
                        'EntityType' : data['Auth']['EntityType'],
                        'AppVer'     : data['Auth']['AppVer'],
                        'SessionId'  : data['Auth']['SessionId']  
                    }
                }
            #print(myRequest)
        elif argScreenId == 'Member':
            if argActionId == 'UpdateConnectionDetails':
                myRequest['Request']['MainArg'] = {
                    "UpdateConnections":[{"Id":data['ConnMemberId'],"Type":"Member","Action":data["Action"]}],
                    "Auth" : data['Auth']
                }
                #print('conn',myRequest)
        elif argScreenId == 'Schedule':
            if argActionId == 'NewSchedule':
                #print(data)
                myRequest['Request']['MainArg'] = {
                    "ScheduleDetails" : {
                        "Description"   : data["ScheduleDetails"]["Description"],
                        "Place"         : data["ScheduleDetails"]["Place"],
                        "StartTime"     : data["ScheduleDetails"]["StartTime"],
                        "DurationMins"  : data["ScheduleDetails"]["DurationMins"]
                    },
                    "Invitee" : [],
                    "ShareWith":[{"MemberId" : "<Family memberid"}],
                    "Tasks": [],
                    "WaitList" : [], 
                    "Repeat": {
                        "RepeatSchedule": "Every Day/Date of Week/Month/Year",
                        "StartDate": "Repeat Start Date",
                        "EndDate": "Repeat End Date"
                    },
                    "Auth" :{
                        "AuthKey" : data["Auth"]["AuthKey"],
                        "LoginId" : data["Auth"]["LoginId"],
                        "LoginType" : data["Auth"]["LoginType"],
                        "DeviceType" : data["Auth"]["DeviceType"],
                        "DeviceOs" : data["Auth"]["DeviceOs"],
                        "MacAddress" : data["Auth"]["MacAddress"],
                        "SessionId" : data["Auth"]["SessionId"],
                        "EntityType" : data["Auth"]["EntityType"],
                        "EntityId" : data["Auth"]["EntityId"],
                        "AppVer" : data["Auth"]["AppVer"]
                    }
                }

                for inv in data['Invitee']:
                    myRequest['Request']['MainArg']['Invitee'].append(
                        {"Id" : inv["Id"] , "Type" : inv["Type"], "IsOwner" : inv["IsOwner"]})

        return myRequest


if __name__ == "__main__":
    while True:
        userResponse = input('Proceed with test data load, exisitng data will be remove (Y/N): ')
        if userResponse not in ['Y','N']:
            print('Invalid response, Pls enter Y/N :')
            continue
        else:
            break

    if userResponse == 'Y':
        print('User entered \'Y\', proceeding with test data load')
        load = loadTestData()
        load.removCollData()
        load.loadMemberData()
        load.loadSchedules()

        print('completed')
    else:
        print('User entered \'N\', aborting test data load')
