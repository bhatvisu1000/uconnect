#pip install persist-queue

# File Based Queue ....

#from persistqueue import Queue
#q = Queue("mypath")
#q.put('a')
#q.put('b')
#q.put('c')
#q.get()
#'a'
#q.task_done()

#Close the python console, and then we restart the queue from the same path,

#from persistqueue import Queue
#q = Queue('mypath')
#q.get()
#'b'
#q.task_done()

# SqlLiteQueue
import persistqueue, time
q = persistqueue.SQLiteQueue('c:\uconnect_logs')
# get the queue size
print('Queue sizre is {size}'.format(size=q.qsize()))
q.put({'Priority':1,'Time':time.ctime()})
q.put({'Priority':2,'Time':time.ctime()})
q.put({'Priority':3,'Time':time.ctime()})
q.get()

del q

import persistqueue
q = persistqueue.SQLiteQueue('c:\uconnect_logs')
q.get()

# Multithread
#Example usage with multi-thread
from persistqueue import Queue

q = Queue()

def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()

for i in range(num_worker_threads):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

for item in source():
    q.put(item)

q.join()  

#Example usage for SQLite3 based queue

def worker():
    while True:
        item = q.get()
        print(item)

q = FIFOSQLiteQueue(path='c:\uconnect_logs', multithreading=True)
items=[{'Item':1},{'Item':2},{'Item':3},{'Item':4},{'Item':5}]
num_worker_threads=3

for i in range(num_worker_threads):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

for item in items:
    q.put(item)

q.join()

from persistqueue import FIFOSQLiteQueue
from threading import Thread
import time

# locking to ensure it doesnt get modified by multiple thread at same time
print_lock=threading.Lock()

def exampleJob(worker):
    time.sleep(1)
    #with print_lock:
    #    print(threading.current_thread().name,worker,'Thread count', threading.active_count())
    #print(threading.current_thread().name,worker)

def threader():
    while True:
        worker = q.get()
        exampleJob(worker)
        q.task_done()

if (__name__ == "__main__"):
    q = FIFOSQLiteQueue(path='c:\uconnect_logs', multithreading=True)
    # creating thread to perform the task
    for x in range(3):
        t = threading.Thread(target = threader)
        t.daemon = True
        t.start()

    start = time.time()

    # creating task which need to be threaded
    for worker in range(30):
        q.put({'Item':worker,'Time':time.ctime()})

    q.join()

    print('Took',time.time()-start)
