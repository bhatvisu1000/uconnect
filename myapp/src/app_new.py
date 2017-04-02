from flask import Flask, flash, session, redirect, url_for, escape, request, jsonify
from datetime import timedelta
from com.uconnect.core.connection.singleton01 import Singleton

from com.uconnect.core.connection.infra import Environment
#from com.uconnect.member.db.member import MemberDB
from com.uconnect.member.db.mongodb import MongoDB
import logging, com.uconnect.utility.ucLogging

#'\x95\x8d\xe3\xab\x18\xc2\xc6\xeb\xd4+\x11H<\xdc\xd8m\xaf\xae0\xcfb\xdc\x84\x92\xc5\xb2\xado\x98\xc5\x08\xa9\xbb/\x95\xe9/\xda\x10\xaa\x1f\xb7k\x956SLCIj\r7v\xdbm\\\x1e\xdc\xf3M&$\xb0\xce\xdb\x18\xd6\xa3\x13\x85\xd0m\r\x1a]\xbe\xf8\xd8Q\xcf\xed\xaf\x0b\x827TB\xb7'
myLogger = logging.getLogger('uConnect')

app = Flask(__name__)
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

  print jsonify("uConnect !!!")
  return

@app.route('/login', methods=['GET','POST'])
def login():
  myModuleLogger = logging.getLogger('uConnect.' +str(__name__) )
  myModuleLogger.debug("initiating login page")

  if request.method == 'POST':
    myModuleLogger.debug("got a POST request, initiating login page")
    session['username'] = request.form['username']
    myModuleLogger.debug("user [{user}]".format(user=session['username']))    
    #flash('You were successfully logged in')
    return redirect(url_for('getAMember', memberId = 'MEM10151'))
    #return redirect(url_for('uConnect'))

  return '''
    <form method="post">
      <p><input type=text name=username>
      <p><input type=submit value=Login>
    </form>

  '''
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flash('You were successfully logged out')
    session.pop('username', None)

    return redirect(url_for('login'))

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
    #print MemberData
    #resultSets=[]
    #for x in MemberData:
    #  resultSets.append(x)				

    return jsonify(MemberData)

@app.route('/getAllMembers/<page>' , methods=['GET','POST'])
def getAllMembers(page):

  app.logger.debug('got a request to retrieve all member\'s details, page# [%s] ', page)
  Member = MongoDB.Instance()
  
  #if (page == "summary"):
  #  MemberData = Memebr.getAllMemberDetailsSummary('Summary')
  #else
  MemberData = Member.findAllDocuments4Page('Member',{},page)
  
  #print MemberData.count()
  return jsonify(MemberData)

if __name__ == "__main__":
  print "Initializing flask environment ..."

  curEnv = Environment.Instance()
  curEnvDetails = curEnv.getEnvironmentDetails(curEnv.globalSettings['Environment'])
  myFlaskHost = curEnvDetails['FlaskHost']
  myFlaskPort = int(curEnvDetails['FlaskPort'])

  print "found, flask host:port", myFlaskHost, ":", myFlaskPort

  app.run(debug=True, host=myFlaskHost, port=myFlaskPort, threaded=True)
  
