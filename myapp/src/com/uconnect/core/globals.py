import copy

from com.uconnect.core.singleton import Singleton
### We need Json Path to validate the data structure for MainArg in request json data
@Singleton
class Global(object):
    def __init__(self):

        self.__memberColl = self.__member = 'Member'
        self.__vendorColl = self.__vendor = 'Vendor'
        self.__vendorLocColl = self.__location = 'Location'
        self.__locAgentColl = self.__agent = 'Agent'
        self.__groupColl = self.__group = 'Group'
        self.__loginColl = self.__login = 'LoginInfo'
        self.__authColl = self.__auth = 'Auth'
        self.__authHistColl = self.__authHist = 'AuthHistory'

        self.__True = True
        self.__TrueStatus = True
        self.__False = False        
        self.__Success = "Success"
        self.__UnSuccess = "UnSuccess"
        self.__Error = "Error"
        self.__InternalScreenId='Internal'
        self.__InternalActionId='Internal'
        self.__InternalPage=99999
        self.__InternalRequest='I'
        self.__ExternalRequest='E'
        self.__ResponseTemplate="Response"
        self.__RequestTemplate="Request"
        self.__HistoryTemplate="History"
        self.__DataKey = 'Data'
        self.__SummaryKey = 'Summary'
        self.__StatusKey = 'Status'
        self.__OkStatus = 'OK'
        self.__hashPassPrefix='2b'
        self.__HistoryColumn='_History'
