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

        ### Invitee --> to whom invitation has been sent to
        ### Requestor --> Member who has sent the invitation
        ### Initial connection status of invitee in requestor doc.
        self.__Initial_Req_MemConnectionStatus = 'Awaiting Response'   
        ### Initial connection status of requestor in invitee doc. 
        self.__Initial_Inv_MemConnectionStatus = 'Pending'
        ### connection status of invitee in requestor doc, after invitee accepted invitation. 
        self.__Accepted_Req_MemConnectionStatus = 'Accepted'
        ### connection status of requestor in invitee doc, after invitee accepted invitation. 
        self.__Accepted_Inv_MemConnectionStatus = 'Valid'
        ''' MemberConnectin = {'Event':{'Record Exists':{'ActionBy':'Requestor/Invitee'}} 
        this is to find the next status 
        '''
        self.__MemberConnectionStatus = {
                'New Connection':{'Requestor':'Awaiting Response','Invitee':'Pending'},
                'Accept Connection':{'Requestor':'Accepted','Invitee':'Valid'},
                'Reject Connection':{'Requestor':'Rejected','Invitee':'Invalid'}
                 }
        self.__RequestStatus = {'Status':'','Message':''}
        self.__ArgIsAValidMember = {"MemberId":"","AuthKey":"","EntityId":"","EntityType":""}
        self.__Connection_Action = ['Accept','Reject','Remove']
        self.__Connection_Action_Accepted = 'Accept'
        self.__Connection_Action_Rejected = 'Reject'
        self.__Connection_Action_Removed = 'Remove'
