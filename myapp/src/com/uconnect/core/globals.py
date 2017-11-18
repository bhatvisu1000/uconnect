import copy, tzlocal

from com.uconnect.core.singleton import Singleton

### We need Json Path to validate the data structure for MainArg in request json data
#@Singleton
class Global(object, metaclass=Singleton):
    def __init__(self):

        self.__memberColl = self.__member = 'Member'
        self.__vendorColl = self.__vendor = 'Vendor'
        self.__vendorLocColl = self.__location = 'Location'
        self.__locAgentColl = self.__agent = 'Agent'
        self.__groupColl = self.__group = 'Group'
        self.__loginColl = self.__login = 'LoginInfo'
        self.__authColl = self.__auth = 'Auth'
        self.__authHistColl = self.__authHist = 'AuthHistory'
        self.__activityLogColl = self.__activityLog = 'ActivityLog'
        self.__securityCodeColl = self.__securityCode = 'SecurityCode'
        self.__securityCodeColl_Hist = 'SecurityCodeHist'
        self.__scheduleColl = self.__schedule = 'Schedule'

        self.__True = True
        self.__TrueStatus = True
        self.__False = False        
        self.__Success = "Success"
        self.__UnSuccess = "UnSuccess"
        self.__Error = "Error"
        self.__InternalPage=99999
        self.__InternalRequest='I'
        self.__ExternalRequest='E'
        self.__ValidResponseModeLsit = [self.__InternalRequest, self.__ExternalRequest]
        self.__ResponseTemplate="Response"
        self.__RequestTemplate="Request"
        self.__HistoryTemplate="History"
        self.__DataKey = 'Data'
        self.__SummaryKey = 'Summary'
        self.__StatusKey = 'Status'
        self.__OkStatus = 'OK'
        self.__hashPassPrefix='2b'
        self.__HistoryColumn='_History'
        self.__Internal = "Internal"
        self.__External = "External"
        ## Login
        self.__LoginStatusOpen = 'Open'
        self.__LoginStatusLocked = 'Locked'
        self.__LoginStatusPending = 'Pending'

        self.__Participant = 'Participant'
        ### Invitee --> to whom invitation has been sent to
        ### Requestor --> Member who has sent the invitation
        ### Initial connection status of invitee in requestor doc.
        self.__Initial_Req_ConnectionStatus = 'Awaiting Response'   
        ### Initial connection status of requestor in invitee doc. 
        self.__Initial_Inv_ConnectionStatus = 'Pending'
        ### connection status of invitee in requestor doc, after invitee accepted invitation. 
        self.__Accepted_Req_ConnectionStatus = 'Accepted'
        ### connection status of requestor in invitee doc, after invitee accepted invitation. 
        self.__Accepted_Inv_ConnectionStatus = 'Valid'
        ''' MemberConnectin = {'Event':{'Record Exists':{'ActionBy':'Requestor/Invitee'}} 
        this is to find the next status 
        '''
        self.__ConnectionStatus = {
                'New Connection':{'Requestor':'Awaiting Response','Invitee':'Pending'},
                'Accept Connection':{'Requestor':'Accepted','Invitee':'Valid'},
                'Reject Connection':{'Requestor':'Rejected','Invitee':'Invalid'}
                 }
        self.__RequestStatus = {'Status':'','Message':'','data':'','Traceback':''}
        self.__ArgIsAValidMember = {"MemberId":"","AuthKey":"","EntityId":"","EntityType":""}
        self.__Connection_Action = ['Invite','Accept','Reject','Remove','Favorite','Blocked']
        self.__Connection_Action_Invite = 'Invite'
        self.__Connection_Action_Accepted = 'Accept'
        self.__Connection_Action_Rejected = 'Reject'
        self.__Connection_Action_Removed = 'Remove'
        self.__Connection_Action_Favorite = 'Favorite'
        self.__Connection_Action_Block = 'Blocked'
        #Schedule
        self.__defaultDateFormat = '%Y-%m-%d %H:%M:%S'
        self.__currentTZ = tzlocal.get_localzone().zone
        self.__utcTZ = 'UTC'
        self.__ScheduleDraftStaus = 'Draft'
        self.__ScheduleOwnerStaus = 'Owner'
        self.__SchedulePendingStaus = 'Pending'
        self.__ScheduleWaitingStaus = 'Waiting'
        self.__ScheduleConfirmedStaus = 'Confirmed'