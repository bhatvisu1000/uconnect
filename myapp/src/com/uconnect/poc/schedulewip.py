# Converting string to datetime format
def isDate(dateArg):
    try:
        if datetime.datetime.strptime(dateArg,'%Y/%m/%d %H:%M:%S'):
            return True
    except ValueError as err:
        print(sys.exc_info())
        raise ValueError('Invalid Date Format')
    except Exception as err:
        print(sys.exc_info())
        return False

def returnTimeZone(tz):
    try:
        timeZone = timezone(tz)
        return timeZone
    except Excpetion as err:
        return None

def formatDate(dateArg, tz='US/Eastern'):
    try:
        if isDate(dateArg):
            myTimeZone = returnTimeZone(tz)
            if not myTimeZone:
                myTimeZone = timezone('US/Easter')
            return (datetime.datetime.strptime(dateArg,'%Y/%m/%d %H:%M:%S')).replace(tzinfo=myTimeZone)
        else:
            return None
    except ValueError as err:
        print(sys.exc_info())
        raise ValueError('Invalid Date Format')
    except Exception as err:
        print(sys.exc_info())

myDate = formatDate('2017/10/28 10:00:00')



from pytz import all_timezones # this is to get all the timezones
from pytz import timezone
from com.uconnect.db.mongodb import MongoDB
mongoDB = MongoDB.Instance()
mongoDB.
mongoDbInstance.InsertOneDoc(self.globalInstance._Global__loginColl, myLoginCriteria, myProjection,True)