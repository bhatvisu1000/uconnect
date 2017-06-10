import socket

# Instantiate object for TCP/IP socket

mySocket = socket.socket(scket.AF_INET, socket.SOCK_STREAM)
myServer = 'localhost'
myPort = 3800
myServerIpAdd = socket.gethostbyname(myServer)

myRequest = ''
mySocket.connet(myServer, myPort)
mySocket.send(myRequest.encode())

# get the result
while (len(myResult) > 0):
    myResult = mySocket.receive(1024)


# checking if port is open

import socket

# Instantiate object for TCP/IP socket

def portScan(argPort):
    try:
        mySocket = socket.socket(scket.AF_INET, socket.SOCK_STREAM)
        myServer = 'localhost'
        mySocket.connet(myServer, argPort)
        return True
    except Exception as e:
        return False

for x in range(1,26):
    if pscan(x):
        print('Port',x, 'is open')
    else:
        print('Port',x, 'is not open')        
    #fi
#end for

# threading

import socket
import threading
from queue import queue

print_lock = threading.lock()

target= 'pythonprogramming.net'

https://www.youtube.com/watch?v=icE6PR19C0Y