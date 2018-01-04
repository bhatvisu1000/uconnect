import importlib,os,sys,json

from com.uconnect.core.singleton import Singleton
from com.uconnect.core.schedule import Schedule
from com.uconnect.core.security import Security
from com.uconnect.utility.ucUtility import Utility
from com.uconnect.core.error import *
from com.uconnect.core.globals import Global

class ScheduleBPS(object):
    def __init__(self):
        self.sched = Schedule()
        self.sec = Security()
        self.util = Utility()
        self.globaL = Global()
        self.myClass = self.__class__.__name__

    def CreateNewSchedule(self, argRequestDict):
        try:
            myMainArgData = self.util.getCopy(argRequestDict)['MainArg']

            #validating Auth
            myAuth = myMainArgData['Auth']
            if not (self.sec._Security__isValidAuthentication(myAuth)):
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))

            # updating argument(s)
            myMainArgData['ScheduleDetails'].update({'Requestor' : myMainArgData['Auth']['EntityType']})
            myMainArgData['ScheduleDetails'].update({'RequestorId' : myMainArgData['Auth']['EntityId']})

            myScheduleResults = self.sched._Schedule__createASchedule(myMainArgData)
            if myScheduleResults['Status'] == self.globaL._Global__Success:
                myScheduleId = myScheduleResults['Data']['_id']
                myScheduleData = self.sched._Schedule__getAScheduleDetail({'ScheduleId' : myScheduleId, 'ResponseMode':myMainArgData['ResponseMode']})
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                #print('Sched BPS',myMainArgData['ResponseMode'],myScheduleData)
                myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myScheduleData )

                #if 'Data' in myResponse['Response']:
                #    myResponse['Response']['Data'] = ['Schedules' :  myResponse['Response']['Data']]
                myResponse = {'Header' : myResponse['Header'], 'Data' : [{'Schedule':myResponse['Data']}]}

            else:
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess, myScheduleResults['Message'])
                myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
                return myResponse

            return myResponse
        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def GetMyAllSchedules(self, argRequestDict):
        try:
            myMainArgData = self.util.getCopy(argRequestDict)['MainArg']

            #validating Auth
            myAuth = myMainArgData['Auth']
            if not (self.sec._Security__isValidAuthentication(myAuth)): 
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))

            myScheduleFor = myMainArgData['Auth']['EntityType']
            myScheduleForWho = myMainArgData['Auth']['EntityId']
            myScheduleData = self.sched._Schedule__getMyAllSchedules({'ScheduleFor' : myScheduleFor, 'ScheduleForWho': myScheduleForWho, 'ResponseMode':myMainArgData['ResponseMode']})
            myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myScheduleData )

            #if 'Data' in myResponse['Response']:
            #    myResponse['Response']['Data'] = ['Schedules' :  myResponse['Response']['Data']]
            myResponse = {'Header' : myResponse['Header'], 'Data' : [{'Schedule':myResponse['Data']}]}

            return myResponse
        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

    def GetAScheduleDetail(self, argRequestDict):
        try:
            
            myMainArgData = self.util.getCopy(argRequestDict['MainArg'])

            #validating Auth

            myArgKey = ['Auth','ScheduleId','ResponseMode']
            myArgValidation, myMissingKeys, myArgValMessage = \
                    self.util.valRequiredArg(myMainArgData, myArgKey)
            if not (myArgValidation):
                raise com.uconnect.core.error.MissingArgumentValues(myArgValMessage)
            #fi
            myAuth = myMainArgData['Auth']
            if not (self.sec._Security__isValidAuthentication(myAuth)): 
                raise com.uconnect.core.error.InvalidAuthKey('Invalid Auth Key [{auth}] for this request [{me}]'.
                    format(auth=myMainArgData['Auth'], me=self.myClass+'.'+self.util.whoAmI()))

            myScheduleId = myMainArgData['ScheduleId']
            myScheduleFor = myMainArgData['Auth']['EntityType']
            myScheduleForWho = myMainArgData['Auth']['EntityId'] 
            if self.sched.isValidScheduleFor(myScheduleId, myScheduleFor, myScheduleForWho):
                myScheduleData = self.sched._Schedule__getAScheduleDetail({'ScheduleId' : myScheduleId, 'ResponseMode': myMainArgData['ResponseMode']})
                myRequestStatus = self.util.getRequestStatus(self.globaL._Global__Success)
                myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Find', myScheduleData )
    
                #if 'Data' in myResponse['Response']:
                #    myResponse['Response']['Data'] = ['Schedules' :  myResponse['Response']['Data']]
                myResponse = {'Header' : myResponse['Header'], 'Data' : [{'Schedule':myResponse['Data']}]}

            else:
                myRequestStatus = self.util.getRequestStatus(
                    self.globaL._Global__UnSuccess, "Schedule {sched} does not belong to {who} ".
                        format(sched=myScheduleId, who=(myScheduleFor,myScheduleForWho)))
                myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
                #return myResponse

            return myResponse

        except Exception as err:
            myRequestStatus = self.util.extractLogError()
            myResponse = self.util.buildResponseData(myMainArgData['ResponseMode'], myRequestStatus, 'Error')
            return myResponse

