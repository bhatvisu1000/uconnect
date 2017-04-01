from com.uconnect.core.singleton import Singleton
### We need Json Path to validate the data structure for MainArg in request json data
@Singleton
class Global(object):
    def __init__(self):
        self.responseTemplate = {"Response":
                                    {"Header":
                                        {"Status":"","Message":"",
                                         "Summary":{"TotalDocs":"","TotalPages":"","DocsPerPage":"","CurrentPage":""}},
                                    "Data":{}
                                    }
                                }

        self.requestTemplate = {"Request":
                                    {"Header":
                                        {"ScreenId":"","ActionId":"","Page":""},
                                     "MainArg": {},
                                     "Auth":{}
                                    }
                                }

        self.Success = "Success"
        self.UnSuccess = "UnSuccess"
        self.Error = "Error"
        self.InternalScreenId=99999
        self.InternalActionId=99999
        self.InternalPage=99999
