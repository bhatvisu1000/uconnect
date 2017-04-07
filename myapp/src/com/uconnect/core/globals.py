import copy

from com.uconnect.core.singleton import Singleton
### We need Json Path to validate the data structure for MainArg in request json data
@Singleton
class Global(object):
    def __init__(self):

        self.__Success = "Success"
        self.__UnSuccess = "UnSuccess"
        self.__Error = "Error"
        self.__InternalScreenId='Internal'
        self.__InternalActionId='Internal'
        self.__InternalPage=99999
        self.__ResponseTemplate="Response"
        self.__RequestTemplate="Request"
        self.__HistoryTemplate="History"