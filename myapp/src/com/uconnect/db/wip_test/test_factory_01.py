class BaseBPS(object):
    #base bps
    def factory(argScreenid):
        # find the relevant json 
        myFactory = {'ScreenId':'SCHEDULE','Class':'ScheduleBps'}
        myFactory.append = {'ScreenId':'MEMBER','Class':'MemberBps'}
        myFactory.append = {'ScreenId':'VENDOR','Class':'VenodrBps'}

        #{'ScreenId':'SCHEDULE','Class':'Schedule'}
        if argScreenid == "SCHEDULE":
            return Schedule()
        if argScreenid == "MEMBER": 
            return Van()
        assert 0, "Bad car creation: " + type 
    factory = staticmethod(factory)

class ScheduleBPS(Process):
    def process(self,argScreenid, argActionId): 
        print("processing [{scrn}], [{action}]".format(scrn=argScreenid, action=argActionId))

class MemberBPS(Process):
    def process(self,argScreenid, argActionId): 
        print("processing [{scrn}], [{action}]".format(scrn=argScreenid, action=argActionId))

class VendorBPS(Process):
    def process(self,argScreenid, argActionId): 
        print("processing [{scrn}], [{action}]".format(scrn=argScreenid, action=argActionId))

# Create object using factory.


request = Process.factory("SCHEDULE")
request.process('SCHEDULE','ACTION1')




import importlib

module = importlib.import_module('my_package.my_module')
my_class = getattr(module, 'MyClass')
my_instance = my_class()

