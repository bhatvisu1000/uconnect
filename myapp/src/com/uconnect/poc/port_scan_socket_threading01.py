# threading

import socket
import threading
from Queue import Queue

print_lock = threading.Lock()

server = '127.0.0.1'

def portscan(port):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        mySocket.timeout(1)
        myConnection = mySocket.connect((server,port))
        with print_lock:
            print('port',port,'is open')
        myConnection.close()
    except Exception as e:
        with print_lock:
            print('port',port,'is npt open')
def threader():
    while True:
        worker = q.get()
        portscan(worker)
        q.task_done()
q = Queue()

for x in range(30):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()

for worker in range(1,9010):
    q.put(worker)

q.join()
#https://www.youtube.com/watch?v=icE6PR19C0Y
