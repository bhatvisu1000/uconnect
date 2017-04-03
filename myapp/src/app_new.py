from flask import Flask, flash, session, redirect, url_for, escape, request, jsonify, json
from datetime import timedelta
from com.uconnect.core.singleton import Singleton
from com.uconnect.bps.factory import Factory
from com.uconnect.core.infra import Environment
from com.uconnect.db.mongodb import MongoDB
from com.uconnect.utility.ucUtility import Utility
from flask_cors import CORS

import logging, com.uconnect.utility.ucLogging

#'\x95\x8d\xe3\xab\x18\xc2\xc6\xeb\xd4+\x11H<\xdc\xd8m\xaf\xae0\xcfb\xdc\x84\x92\xc5\xb2\xado\x98\xc5\x08\xa9\xbb/\x95\xe9/\xda\x10\xaa\x1f\xb7k\x956SLCIj\r7v\xdbm\\\x1e\xdc\xf3M&$\xb0\xce\xdb\x18\xd6\xa3\x13\x85\xd0m\r\x1a]\xbe\xf8\xd8Q\xcf\xed\xaf\x0b\x827TB\xb7'
myLogger = logging.getLogger('uConnect')
utilityInstance = Utility.Instance()
myFactory = Factory.Instance()

app = Flask(__name__)
CORS(app)
app.secret_key = '\x95\x8d\xe3\xab\x18\xc2\xc6\xeb\xd4+\x11H<\xdc\xd8m\xaf\xae0\xcfb\xdc\x84\x92\xc5\xb2\xado\x98\xc5\x08\xa9\xbb/\x95\xe9/\xda\x10\xaa\x1f\xb7k\x956SLCIj\r7v\xdbm\\\x1e\xdc\xf3M&$\xb0\xce\xdb\x18\xd6\xa3\x13\x85\xd0m\r\x1a]\xbe\xf8\xd8Q\xcf\xed\xaf\x0b\x827TB\xb7'
#session = {}

@app.before_request
def make_session_permanent():
    myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
    myModuleLogger.debug("initializing session information ...")
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
@app.route('/uConnect', methods=['GET','POST'])
def uConnect():
  myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
  myModuleLogger.debug("uconnect main page")

  return jsonify("uConnect !!!")

@app.route('/login', methods=['GET','POST'])
def login():
  myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
  myModuleLogger.debug("initiating login page")

  if request.method == 'POST':
    myModuleLogger.debug("got a POST request, initiating login page")
    session['username'] = request.form['username']
    myModuleLogger.debug("user [{user}]".format(user=session['username']))    
    #flash('You were successfully logged in')
    return redirect(url_for('getAMember', memberId = 'MEM192551'))
    #return redirect(url_for('uConnect'))

  return '''
    <form method="post">
      <p><input type=text name=username>
      <p><input type=submit value=Login>
    </form>

  '''
@app.route('/insert')
def insert():
  Member = MongoDB.Instance()
  MemberData = Member.InsertOneDoc('Member',{ 'Main':{'FirstName':'Aditya','LastName':'Singh'},'Address':{'Street':'44 Helena Street','City':'East Brunswick','State':'NJ','ZipCode':'08816'}})
  return jsonify(MemberData)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flash('You were successfully logged out')
    session.pop('username', None)

    return redirect(url_for('login'))

@app.route('/processRequestOrig/<requestType>/<memberId>/<connType>' , methods=['GET','POST'])
def processRequestOrig(requestType,memberId,connType):
  #memberId='MEM192551'
  if (requestType == 'Find'):
    argRequests = {"Request":
                    {"Header":
                        {"ScreenId":"MEMBER_01","ActionId":"SearchMember_01","Page":None},
                     "MainArg":
                        {"Criteria":
                          {"_id":memberId},
                          "Projection":None,
                          "FindOne":True
                          }
                    }
                  }
  elif (requestType) == 'Insert':
    argRequests = {"Request":
                    {"Header":
                        {"ScreenId":"RegisterMember_01","ActionId":"CreateMember_01","Page":None},
                     "MainArg":
                        {"Main":{"LastName":"Bhatt","FirstName":"Vishal"},
                         "Address":{"ZipCode":"08820"},
                         "Contact":{"Mobile":"999-555-1212"}
                        }
                    }
                  }
  elif (requestType) == 'GetCollection':
    argRequests = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"GetMemberConnection","Page":None},
                     "MainArg":
                        {"Main":{"MemberId":memberId,"MemberConnection":connType}
                        }
                    }
                  }

  app.logger.debug('got a request [{request}]'.format(request=requestType))
  myFactory = Factory.Instance()
  
  ''' extrcat value from argument passed '''
  
  myArgumentTuple = utilityInstance.extractRequest(argRequests)
  myArgTupleStatus = myArgumentTuple[0]  
  myScreenId = myArgumentTuple[1]
  myActionId = myArgumentTuple[2]
  myArgumentData = myArgumentTuple[3]
  myResults = ''

  ''' if we can extract value passed as an argument, will proceed else will build the responseDict with empty dataset '''

  if myArgTupleStatus == 'Success':
    myResults = myFactory.processRequest(myScreenId,myActionId,myArgumentData)

  myResponseData = utilityInstance.buildResponseData(myResults,myArgTupleStatus,myArgTupleStatus)

  return jsonify(myResponseData)

#@app.route('/processRequest/<request>' , methods=['POST'])
#def processRequest(request):

@app.route('/request/<requestType>', methods=['POST'])
def request(requestType):
  #print(request.headers)
  #print(dict(request))
  #myRequest = eval(request)
  #313883
  #313884
  #313885
  #313886
  #313888 

  myMemberId = 314094
  print(requestType)
  if requestType == "GetConnection":
    myRequest = {"Request":
                      {"Header":
                          {"ScreenId":"MemberConnection","ActionId":"GetMemberConnection","Page":None},
                       "MainArg":
                          {"MemberId":myMemberId,"ConnectionType":'Member'}
                      }
                    }
  elif requestType == "MemberDetail":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"getAMemberDetail","Page":None},
                     "MainArg":
                        {"_id":myMemberId}
                    }
                  }
  elif requestType == "CreateAMember":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberRegistration","ActionId":"CreateMember","Page":None},
                     "MainArg":
                        {"Main":{"LastName":"Bhat","FirstName":"Vishal"},
                         "Address":{"ZipCode":"08820"},
                         "Contact":{"Mobile":"999-555-1212"}
                        }
                    }
                  }
  elif requestType == "LinkAMember":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"LinkMember2Member","Page":None},
                     "MainArg":
                        {"MemberId":myMemberId,"ConnectMemberId":313886}
                    }
                  }
  elif requestType == "MarkAMemberFavorite":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"MarkMemberFavorite","Page":None},
                     "MainArg":
                        {"MemberId":myMemberId,"FavoriteMemberId":313884}
                    }
                  }
  elif requestType == "GetAGroupDetail":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"getAMemberDetail","Page":None},
                     "MainArg":
                        {"_id":1001}
                    }
                  }
  elif requestType == "CreateGroup":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"getAMemberDetail","Page":None},
                     "MainArg":
                        {"_id":1001}
                    }
                  }
  elif requestType == "AddParticipant2Group":
    myRequest = {"Request":
                    {"Header":
                        {"ScreenId":"MemberConnection","ActionId":"getAMemberDetail","Page":None},
                     "MainArg":
                        {"_id":1001}
                    }
                  }
  else:
    return jsonify("Sorry !!!, Invalid Request")    

  #print(request, type(myRequest))

  #myRequest = json.dump(request)
  #print (myRequest)
  if not(utilityInstance.isDict(myRequest)):
    return jsonify({"Status":"Error","Message":"Invalid argument {arg} passed, argument must be type of dictionary !!!".format(arg=myRequest)})

  try:
    if ( "Request" not in myRequest ) or ("Header" not in myRequest['Request']) or ('MainArg' not in myRequest['Request']):
      return jsonify({"Status":"Error","Message":"Key error"})
  except Exception as error:
    return jsonify({"Status":"Error","Message":"error {error}".format(error=error.message)})

  app.logger.debug('got request {request}'.format(request=myRequest))
  myFactory = Factory.Instance()
  MemberData = myFactory.processRequest(myRequest)
  return jsonify(MemberData)

@app.route('/testFactory/<id>/<type>' , methods=['GET','POST'])
def getAMemberFactory(id,type):
  #print(type(type))
  if (type == "Member"):
    app.logger.debug('got a request to retrieve member details for [%s]',id )
    myArgRequest = {"Request":
                      {"Header":
                        {"ScreenId":"Member_Main_01","ActionId":"SearchMember","Page":""},
                        "MainArg": {"_id":int(id)},
                        "Auth":{}
                      }
                    }  
    myData = myFactory.processRequest(myArgRequest)
  elif (type == "Group"):
    app.logger.debug('got a request to retrieve Group details for [%s]',id )
    myArgRequest = {"Request":
                      {"Header":
                        {"ScreenId":"Group01","ActionId":"FindAGroupDetail","Page":""},
                        "MainArg": {"_id":int(id)},
                        "Auth":{}
                      }
                    }  
    myData = myFactory.processRequest(myArgRequest)

  return jsonify(myData)

@app.route('/getAMember/<memberId>' , methods=['GET','POST'])
def getAMember(memberId):
  print session
  if not('username' in session):
    print "forbidden"
    raise session_expired
  #app.logger.debug('MemberId [%d] passed as an arguments', memberId)
  else:
    app.logger.debug('got a request to retrieve member details for [%s]',memberId )
    Member = MongoDB.Instance()
    criteria={"_id":memberId}
    MemberData = Member.findDocument('Member',criteria,{},True)

    return jsonify(MemberData)

@app.route('/getAllMembers/<page>' , methods=['GET','POST'])
def getAllMembers(page):

  app.logger.debug('got a request to retrieve all member\'s details, page# [%s] ', page)
  Member = MongoDB.Instance()
  
  #if (page == "summary"):
  #  MemberData = Memebr.getAllMemberDetailsSummary('Summary')
  #else
  MemberData = Member.findAllDocuments4Page('Member',{},{},page)
  myResponseData = utilityInstance.buildResponseData(MemberData,0,'Success')
  #print MemberData.count()
  return jsonify(myResponseData)

if __name__ == "__main__":
  print "Initializing flask environment ..."

  envInstance = Environment.Instance()
  curEnvDetails = envInstance.getEnvironmentDetails(envInstance.globalSettings['Environment'])
  myFlaskHost = curEnvDetails['FlaskHost']
  myFlaskPort = int(curEnvDetails['FlaskPort'])

  print "found, flask host:port", myFlaskHost, ":", myFlaskPort

  app.run(debug=True, host=myFlaskHost, port=myFlaskPort, threaded=True)
  