import sys, datetime, json,logging, com.uconnect.utility.ucLogging, com.uconnect.core.error

from com.uconnect.core.infra import Environment
from com.uconnect.core.singleton import Singleton
from com.uconnect.core.globals import Global
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.db.dbutility import DBUtility
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.security import Security
from com.uconnect.core.member import Member

myLogger = logging.getLogger('uConnect')

#@Singleton
class Schedule(object, metaclass=Singleton):
    def __init__(self):
        self.globaL = Global()
        self.mongo = MongoDB()
        self.util = Utility()
        self.member = Member()
        self.globaL = Global()

        self.myClass = self.__class__.__name__
        self.myModuleLogger = logging.getLogger('uConnect.' +str(__name__) + '.' + self.myClass)

    def isTimeSlotOpen(self, argFor, argWho, argWhen, argDurationMins):
        '''
        Description: Return True/False if timeslot is available for Member/Vendor
        argFor  : Member/Vandor
        argWho  : MemberId/AgentId 
                [Vendor must have an agent, all schedule belongs to an agent. In future we can accept Vendor id then we 
                 would need to join vendor collection to get all the agent and its availability, may be create another wrapper for 
                Venodr]
        argWhen             : DateTime string (format = 'YYYY-MM-DD HH:MI:SS')
        argDurationMins     : Duration in minutes

        e.g. isTimeSlotOpen('Member',999999999999999,'2010-01-01 10:00:00',30)
                [Above example will find if timeslot (10-10:30 am) is open for member id 999999999999999]
        '''
        self.myModuleLogger.debug('Argument(s) received {arg}'.format(arg=(argFor,argWho,argWhen, argDurationMins)))

        # validating arguments

        if argFor == self.globaL._Global__member:
            myMemberValArg = {'_id':argWho, 'ResponseMode':self.globaL._Global__InternalRequest}
            self.myModuleLogger.debug(myMemberValArg)
            if not(self.member._Member__isAValidMember(myMemberValArg)):
                raise com.uconnect.core.error.MissingArgumentValues(\
                    'Invalid member [{member}]'.format(member=myParticipant['_id']))
            #myScheduleOwner = self.globaL._Global__member 
        else:
            pass
        
        # formating date/time
        if not isinstance(argWhen, datetime.datetime):
            myStartTime = self.util.convertStr2Date(argWhen,self.globaL._Global__defaultDateFormat,self.globaL._Global__currentTZ)
        else:
            myStartTime = argWhen
        
        myEndTime = self.util.addTime2Date(myStartTime,0,argDurationMins,0)
        
        #building criteria for db operation
        #myCriteria = {
        #    "$and" : [
        #        {"$or": [
        #            {"$and" : 
        #                [
        #                    {"Invitee.Type"   : argFor},
        #                    {"Invitee.Id"     : argWho}
        #                ]
        #            },
        #            {"$and" : 
        #                [
        #                    {"ShareWith.Type" : argFor}, 
        #                    {"ShareWith.Id"   : argWho}
        #                ]
        #            }
        #        ]},
        #       {"$or": [
        #            {"$and": 
        #                [
        #                    {'ScheduleDetails.StartTime' : {"$gte" : myStartTime}},
        #                    {"$or":[
        #                        {'ScheduleDetails.EndTime'    : {"$lte" : myEndTime}},
        #                        {'ScheduleDetails.StartTime'  : {"$lt" : myEndTime}} ]
        #                    }
        #                ]
        #            },
        #            {"$and": 
        #                [
        #                    {'ScheduleDetails.StartTime' : {"$lte" : myStartTime }},
        #                    {'ScheduleDetails.EndTime'   : {"$gt"  : myStartTime }}, 
        #                    {'ScheduleDetails.EndTime'   : {"$lt"  : myEndTime }}, 
        #                ]
        #            }
        #        ]}
        #    ]
        #}

        myCriteria = {
            "$and" : [
                {"$or": [
                            {"Invitee.Type"   : argFor, "Invitee.Id"     : argWho},
                            {"ShareWith.Type" : argFor,"ShareWith.Id"   : argWho}
                        ]
                },
                {"$or": 
                    [
                        {
                            "ScheduleDetails.StartTime" : {"$gte" : myStartTime},
                            "$or": 
                                [
                                    {"ScheduleDetails.EndTime"    : {"$lte" : myEndTime}},
                                    {"ScheduleDetails.StartTime"  : {"$lt" : myEndTime}} 
                                ]
                        },
                        {
                            "ScheduleDetails.StartTime" : {"$lte" : myStartTime },
                            "ScheduleDetails.EndTime"   : {"$gt"  : myStartTime }, 
                            "ScheduleDetails.EndTime"   : {"$lt"  : myEndTime }
                        } 
                    ]
                }
            ]
        }

        #print(self.globaL._Global__scheduleColl, myCriteria)
        #print(myCriteria)
        myTotalSchedules = self.mongo.findTotDocuments(self.globaL._Global__scheduleColl,myCriteria)
        data = self.mongo.findDocument(self.globaL._Global__scheduleColl, myCriteria)
        #print('data',data)
        #print('total doc [{doc}] found for this timeslot'.format(doc=myTotalSchedules))

        #print(myTotalSchedules)
        if myTotalSchedules == 0:
            return True
        else:
            return False
        # 10 to 10:30, 11 to 11:30 is working but 09:59 ,30 minutes is not working

    def getAllScheduleFor(self, argFor, argWho):
        '''
        Description: Return All schedules in descending order (latest schedule will be displayed first)
        argFor      : Member/Vandor
        argWho      : MemberId/AgentId 
                    [Vendor must have an agent, all schedule belongs to an agent. In future we can accept Vendor id then we 
                     would need to join vendor collection to get all the agent and its availability, may be create another wrapper for Venodr]

        e.g. getAllScheduleFor('Member',999999999999999) 
                [Above example will return all schedule for member id 999999999999999]
        '''
        try:
            self.myModuleLogger.debug('Argument(s) received {arg}'.format(arg=(argType,argId,argWhen, argDurationMins)))

            # validating arguments
            if argFor == self.globaL._Global__member:
                myMemberValArg = {'_id':argId, 'ResponseMode':self.globaL._Global__InternalRequest}
                self.myModuleLogger.debug(myMemberValArg)
                if not(self.member._Member__isAValidMember(myMemberValArg)):
                    raise com.uconnect.core.error.MissingArgumentValues(\
                        'Invalid member [{member}]'.format(member=myParticipant['_id']))
            else:
                pass
            myCriteria = {'Invitee.Type' : argFor, 'Invitee.Id' : argWho}
            myProjection = {"ScheduleDetails":1, "Invitee":1, "ShareWith" : 1, "Tasks":1, "RepeatSchedule" : 1}
            mySort = {'ScheduleDetails.StartTime': -1}
            myAllSchedules = mongo.findAllDocuments4Page(self.globaL_Global__scheduleColl, myCriteria, myProjection, None, mySort)
            return myAllSchedules

        except Exception as error:
            raise error

    def isValidSchedule(self, argScheduleId):
        '''
        Description: Return if scheduled is valid (exists in repository)
        argScheduleId   : ScheduleId

        e.g. isValidSchedule(123456789)
                [Above example will check if schedule id 123456789 exists in repository, returns True if exist, False if does not exist]
        '''

        myCriteria = {'_id': argScheduleId}
        isValidSchedule = True
        mySchedCount = self.mongo.findTotDocuments(self.globaL._Global__scheduleColl,myCriteria)
        
        if mySchedCount == 0:
            isValidSchedule = False

        return isValidSchedule

    def isValidScheduleFor(self, argScheduleId, argFor, argWho):
        '''
        Description     : Check if this schedule exists for this requestor in repository)
        argScheduleId   : ScheduleId
        argRequestorType: Requestor Type
        argRequestorId  : Requestor Id

        e.g. isValidRequestorSchedule(123456789, 'Member', 1234)
                [Above example will check if schedule id 123456789 belongs to Requestor(Member: 1234)
        Following is commented out becauze requestor/invitee is part of invitee list
        myCriteria = {
            '_id': argScheduleId, '$or': [{
                'ScheduleDetails.Requestor' : argRequestorType, 'ScheduleDetails.RequestorId' : argRequestorId
            },
            {
                'Invitee.Type' : argRequestorType, 'Invitee.Id' : argRequestorId
            }]
        }
        '''
        myCriteria = {'_id': argScheduleId, 'Invitee.Type' : argFor, 'Invitee.Id' : argWho}

        isValidSchedule = True
        mySchedCount = self.mongo.findTotDocuments(self.globaL._Global__scheduleColl, myCriteria)
        
        if mySchedCount == 0:
            isValidSchedule = False

        return isValidSchedule

    def isValidInviteeInSchedule(self, argScheduleId, argInviteeType, argInviteeId):
        '''
        Description     : Check if Invitee is part of a schedule
        argScheduleId   : ScheduleId

        e.g. isValidInviteeInSchedule(123456789)
                [Above example will check if schedule id 123456789 exists in repository, returns True if exist, False if does not exist]
        '''

        myCriteria = {'_id': argScheduleId, 'Invitee.Type' : argInviteeType, 'Invitee.Id' : argInviteeId}
        isValidSchedule = True
        mySchedCount = self.mongo.findTotDocuments(self.globaL__Global__scheduleColl,myCriteria)
        
        if mySchedCount == 0:
            isValidSchedule = False

        return isValidSchedule

    def __getMyAllSchedules(self, argRequestDict):
        '''
        Description: Return a schedules details 
        argRequestDict   : For, Who, ResponseMode

        e.g. __getMyAllSchedules({For:Member, Who: 12345, ResponseMode : I})
                [Above example will find all schedules & its details for Member 12345
        '''
        try:
            self.myModuleLogger.debug('Argument(s) received {arg}'.format(arg=(argRequestDict)))
            myMainArgData = self.util.getCopy(argRequestDict)

            # validating arguments, checking if schedule is a valid schedule
            myArgKey = ['ScheduleFor','ScheduleForWho','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)

            myScheduleFor = myMainArgData['ScheduleFor']
            myScheduleForWho = myMainArgData['ScheduleForWho']
            myResponseMode = myMainArgData['ResponseMode']
            if myScheduleFor == self.globaL._Global__member:
                myCriteria = {'Invitee.Type': myScheduleFor, 'Invitee.Id' : myScheduleForWho} 
                myProjection = {"ScheduleDetails":1, "Invitee":1, "ShareWith" : 1, "Tasks":1, "RepeatSchedule" : 1}
                mySort = [('ScheduleDetails.StartTime', -1)]
                
                myAllSchedules = self.mongo.findDocument(self.globaL._Global__scheduleColl, myCriteria, myProjection, False, mySort)
                
                if myAllSchedules:
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                else:
                    myRequestStatus = self.util.getRequestStatus(
                        self.globaL._Global__UnSuccess, "Could not find schedule {member} details".format(schedule=myScheduleId))
            else:
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess, "Schedule {schedule} does not exist ".format(schedule=myMemberId))
            myResponse = self.util.buildResponseData(self.globaL._Global__InternalRequest, myRequestStatus, 'Find', myAllSchedules )
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def __getAScheduleDetail(self, argRequestDict):
        '''
        Description: Return a schedules details 
        argRequestDict   : ScheduleId, ResponseMode

        e.g. __getAScheduleDetail({ScheduleId:12312, ResponseMode : I})
                [Above example will find a schedule details
        '''
        try:
            self.myModuleLogger.debug('Argument(s) received {arg}'.format(arg=(argRequestDict)))
            myMainArgData = self.util.getCopy(argRequestDict)

            # validating arguments, checking if schedule is a valid schedule
            myArgKey = ['ScheduleId','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)

            myScheduleId = myMainArgData['ScheduleId']
            if self.isValidSchedule(myScheduleId):
                myCriteria = {'_id':myScheduleId}
                myProjection = {"ScheduleDetails":1, "Invitee":1, "ShareWith" : 1, "Tasks":1, "RepeatSchedule" : 1}
                #mySort = {'ScheduleDetails.StartTime': -1}
                myAllSchedules = self.mongo.findDocument(self.globaL._Global__scheduleColl, myCriteria, myProjection, True)
                if myAllSchedules:
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                else:
                    myRequestStatus = self.util.getRequestStatus(
                        self.globaL._Global__UnSuccess, "Could not find schedule {member} details".format(schedule=myScheduleId))
            else:
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess, "Schedule {schedule} does not exist ".format(schedule=myMemberId))
            myResponse = self.util.buildResponseData(self.globaL._Global__InternalRequest, myRequestStatus, 'Find', myAllSchedules )
            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def __createASchedule(self, argRequestDict):
        '''
        Description     : Create a schedule 
        argScheduleId   : argRequestDict
            argRequestDict: {
                'MainArg': {
                  'ScheduleDetails': {
                    'Description'   : '<Subjet/brief description of meeting',
                    'Requestor'     : 'Member/Venodr',
                    'RequestorId'   : 'MemberId/AgentId',
                    'Place'         : 'Schedule Place',
                    'StartTime'     : 'Start Date and time of meeting',
                    'EndTime'       : 'Start Date and time of meeting',
                    'Duration'      : '<in minutes, default 30 minutes for Member, for Vendor it should come from their setting>',
                    'Status'        : 'Draft/Waiting/WaitLiist (meeting with vendor)/Confirmed 
                                        (atleast 1 invitee confirms the meeting, will also so n/<total invitee>'
                  },
                  'Invitee': [
                    {
                      'Type'    : '<Vendor/Member>',
                      'Id'      : 'InviteeId',
                      'IsOwner' : 'Y/N',
                      'Status'  : '<Pending/Accepted/Rejected/Proposed New Time>'
                    }
                  ],
                  'ShareWith':[
                    {
                      'MemberId' : '<Member Id whose calendar will be shown as busy for this scheduled slot time, this will be family member'
                    }
                  ],
                  'Tasks': [],
                  'WaitList' : [], 
                  'Repeat': {
                    'RepeatSchedule': 'Every Day/Date of Week/Month/Year',
                    'StartDate': 'Repeat Start Date',
                    'EndDate': 'Repeat End Date'
                  }
                }
                'Auth': {'<Auth object>'}
            }

        e.g. createASchedule(argRequestDict)

                [Above example will create a scheudle as per the information provided in this object, Pls see above for details of this object]
        '''
        try:
            self.myModuleLogger.debug('Argument(s) received {arg}'.format(arg=(argRequestDict)))
            myMainArgData = self.util.getCopy(argRequestDict)
            myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)

            # build inti schedule data
            myScheduleData = self.__buildInitScheduleData(myMainArgData)
            self.myModuleLogger.info('Intial schedule data [{data}] built, persisting data'.format(data=myScheduleData))
            
            # validate new schedule content
            myValidateResponse = self.__validateNewScheduleContents(myScheduleData)
            #print(myValidateResponse)
            if myValidateResponse['Status'] == self.globaL._Global__Success:
                myScheduleResult = self.mongo.InsertOneDoc(self.globaL._Global__scheduleColl, myScheduleData)

                if myScheduleResult['Status']:
                    myScheduleId = myScheduleResult['_id']
                    self.myModuleLogger.info('Schedule [{id}] created, result[{result}]'.format(id=myScheduleId, result=myScheduleResult))
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success, self.globaL._Global__Success,{'_id':myScheduleId})
                    print(myRequestStatus)
                else:
                    myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess, 'error, persisiting data')
            else:
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess, myValidateResponse['Message'])
            
            return myRequestStatus

        except Exception as err:
            myErrRequestStatus = self.util.extractLogError()
            return myErrRequestStatus

    def __validateNewScheduleContents(self, argScheduleData):
        myRequestStatus = self.util.getCopy(self.globaL._Global__RequestStatus)        
        try:
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success,self.globaL._Global__Success)

            # checking if time slot is open
            if not self.isTimeSlotOpen(\
                argScheduleData['ScheduleDetails']['Requestor'], argScheduleData['ScheduleDetails']['Requestor'], 
                argScheduleData['ScheduleDetails']['StartTime'],argScheduleData['ScheduleDetails']['DurationMins']):

                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__UnSuccess,'Requested time slot is already in use')
            
            return myRequestStatus

        except Exception as err:
            myErrRequestStatus = self.util.extractLogError()
            return myErrRequestStatus

    def __buildInitScheduleData(self, argRequestDict):
        '''
            Build initial schedule data for a new schedule
        '''
        try:
            self.myModuleLogger.debug('Argument [{arg}] received'.format(arg=argRequestDict))
            myMainArgData = self.util.getCopy(argRequestDict)

            #Validatring Arguments
            myArgKey = ['ScheduleDetails','Invitee']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey, ['ShareWith','Task','Tasks','WaitList','Repeat','Auth'])

            myArgKey = ['Description','Requestor','RequestorId','Place','StartTime','Duration']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData['ScheduleDetails'], myArgKey, ['Status','EndTime'])

            # validating start date
            if self.util.isValidDate(myMainArgData['ScheduleDetails']['StartTime'],self.globaL._Global__defaultDateFormat):
                mySchedStartTimeISO = self.util.convertStr2Date(\
                    myMainArgData['ScheduleDetails']['StartTime'],
                    self.globaL._Global__defaultDateFormat, 
                    self.globaL._Global__currentTZ, 
                    self.globaL._Global__utcTZ)
            else:
                print('Invalid Date',myMainArgData['ScheduleDetails']['StartTime'],self.globaL._Global__defaultDateFormat)
            # get GEO Code for the place of meeting
            try:
                myMeetingPlaceGeoLoc = self.util.getGeoLocation(myMainArgData['ScheduleDetails']['Place'])
            except:
                # we could not interpre the meeting place to a valid GEO location
                myMeetingPlaceGeoLoc = None
            # 
            #print(myMainArgData['ScheduleDetails']['Place'],myMeetingPlaceGeoLoc)
            # building ScheduleDetails
            myInitScheduleData = self.util.getTemplateCopy(self.globaL._Global__schedule)
            myInitScheduleData['ScheduleDetails'].update(myMainArgData['ScheduleDetails'])
            myInitScheduleData['ScheduleDetails']['StartTime'] = mySchedStartTimeISO
            #self.util.copyKeyValuesFromTo(['Description','Requestor','RequestorId','Place','StartTime','Duration'], myMainArgData['ScheduleDetails'],mySchedDict['ScheduleDetails'] )
            myInitScheduleData['ScheduleDetails']['PlaceGeo'] = myMeetingPlaceGeoLoc
            myInitScheduleData['ScheduleDetails']['EndTime'] = self.util.addTime2Date(mySchedStartTimeISO,0,myInitScheduleData['ScheduleDetails']['DurationMins'],0)

            # building invitee
            myInitScheduleData['Invitee'] = myMainArgData['Invitee']
            for seq, invitee in  enumerate(myInitScheduleData['Invitee']):
                myIsOwner = 'N'
                if invitee['Id'] == myMainArgData['ScheduleDetails']['RequestorId']:
                    myIsOwner = 'Y'
                myInitScheduleData['Invitee'][seq].update({'Status':'Pending','IsOwner':myIsOwner})
                # we need to validate if this invitee is a connection (must be an accepted connection)
            # adding requestor in invitee list as owner in the begining of the list (0 position)
            myInitScheduleData['Invitee'].insert(0,\
                {
                    'Id': myMainArgData['ScheduleDetails']['RequestorId'], 
                    'Type': myMainArgData['ScheduleDetails']['Requestor'],
                    'IsOwner' : 'Y',
                    'Status' : 'Owner'
                })
            #determining status of schedule
            myInitScheduleData['ScheduleDetails']['Status'] = self.util.getScheduleStatus(myInitScheduleData['ScheduleDetails']['Status'], myInitScheduleData['Invitee'])

            #Tasks, we need a seperate method to format this
            if 'Tasks' in myMainArgData:
                myInitScheduleData['Tasks'] = myMainArgData['Tasks']

            #ShareWith, we need a seperate method to format this
            if 'SbhareWith' in myMainArgData:
                myInitScheduleData['ShareWith'] = myMainArgData['ShareWith']

            #Repeat, we need a seperate method to format this
            if 'Repeat' in myMainArgData:
                myInitScheduleData['Repeat'] = myMainArgData['Repeat']

            #building history
            myInitScheduleData[self.globaL._Global__HistoryColumn] = self.util.buildInitHistData() 

            # get new schedule id for this schedule
            myScheduleId = self.mongo.genKeyForCollection(self.globaL._Global__scheduleColl)
            myInitScheduleData.update({'_id':myScheduleId})

            return myInitScheduleData

        except Exception as err:
            myError = self.util.extractLogError()
            self.myModuleLogger.error('error {error} occurred during creating a new schedule'.format(error=myError))
            raise err

    def AcceptSchedule(self, argScheduleId):
        pass

    def rejectSchedule(self, argScheduleId):
        pass

    def updateScheduleTask(self, argScheduleId, argTaskId, argTaskText):
        pass



'''
from datetime import datetime
import sys

def isValidDate(dateArg, formatArg):
    try:
        if datetime.strptime(dateArg,formatArg):
            return True
    except ValueError as err:
        print(sys.exc_info())
        raise ValueError('Invalid Date Format')
    except Exception as err:
        print(sys.exc_info())
        return False

def getTimeZone(tz):
    try:
        if isValidTZ(tz):
            timeZone = pytz.timezone(tz)
            return timeZone
        else:
            return None
    except Exception as err:
        return None

def isValidTZ(argTZ):
    return argTZ in pytz.all_timezones

def getAllValidTimeZone():
    return pytz.all_timezones

def convertStr2Date(dateStrArg, dateStrFormat, sourceTZ, targetTZ='UTC'):
    try:
        #myDateFormat = '%Y-%m-%d %H:%M:%S'
        if isValidDate(dateStrArg,dateStrFormat):
            mySourceTimeZone = getTimeZone(sourceTZ)
            myTargetTimeZone = getTimeZone(targetTZ)
            #print(mySourceTimeZone, myTargetTimeZone)
            myDate = datetime.strptime(dateStrArg,dateStrFormat)
            myDateSrcTZ = datetime.astimezone(myDate,mySourceTimeZone)
            mydateTrgTZ =  datetime.astimezone(myDate,myTargetTimeZone)
            #print(myDateSrcTZ, mydateTrgTZ)            
            #print('Date: {date}, timezone: {tz}'.format(date=mydate,tz=mydate.tzname()))
            return mydateTrgTZ
        else:
            return None
    except ValueError as err:
        print(sys.exc_info())
        raise ValueError('Invalid Date Format')
    except Exception as err:
        print(sys.exc_info())

def getTimeFromDate(dateArg):
    return dateArg.time()

def addTime2Date(dateArg, secsArg, minsArg, daysArg)
    return dateArg + datetime.timedelta(days = daysArg, seconds = secsArg, minutes = minutesArg)

print(convertStr2Date('2017/10/28 10:00:00','%Y-%m-%d %H:%M:%S','US/Eastern','UTC'))

print(myDate, myDate.tzname(), myDate.time(), myDate.timetz())
print('TZ class: ', myDate.tzinfo)
print('ISO Year, week#, weekday: ', myDate.isocalendar)
print('ISO day of week: ', myDate.isoweekday())
print('Ctime: ',myDate.ctime())
print('Day of month: ',myDate.day)
print('day of week : ', myDate.weekday())
print('year, month, day: ', myDate.year, myDate.month, myDate.day)
print('hour, minute, second: ', myDate.hour, myDate.minute, myDate.second)

#https://www.saltycrane.com/blog/2008/11/python-datetime-time-conversions/

from com.uconnect.db.mongodb import MongoDB
mongo = MongoDB()
totDoc = mongo.findTotDocuments('Schedule',
    {'ScheduleDetails.Owner':'Member',
    'ScheduleDetails.OwnerId':314333,
    'ScheduleDetails.StartTime' : {"$gte" : convertStr2Date('2017-12-01 10:00:00','%Y-%m-%d %H:%M:%S','US/Eastern')}, 
    'ScheduleDetails.EndTime':{"$lte" : convertStr2Date('2017-12-01 10:30:00','%Y-%m-%d %H:%M:%S','UTC')}
    })

# db.Schedule.find({'ScheduleDetails.Owner':'Member','ScheduleDetails.OwnerId':314333,'ScheduleDetails.StartTime' : {$gte : new Date('2017-12-01T10:00:00')}, 'ScheduleDetails.EndTime':{$lte : new Date('2017-12-01T10:30:00')}},{'ScheduleDetails.StartTime':1,'ScheduleDetails.EndTime':1})

db.Schedule.
'''