import importlib,os,sys,json
from com.uconnect.core.connection.singleton01 import Singleton

@Singleton
class Schedule(object):
    #@staticmethod
    def process(self,arg2Print1, arg2Print2):
        print arg2Print1 + arg2Print2
        return arg2Print1 , arg2Print2
