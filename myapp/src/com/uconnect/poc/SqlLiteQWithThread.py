#python c:\app\uconnect\myapp\src\com\uconnect\poc\SqlLiteQWithThread.py
# pip install APPScheduler

from persistqueue import FIFOSQLiteQueue
from threading import Thread
import time, threading

# locking to ensure it doesnt get modified by multiple thread at same time
print_lock=threading.Lock()

def exampleJob(worker):
    #time.sleep(1)
    with print_lock:
        print(threading.current_thread().name,worker,'Thread count', threading.active_count())
    #print(threading.current_thread().name,worker)

def threader():
    while True:
        #if not (q.tran_lock.locked_lock):
        #q.tran_lock.acqure(True)
        worker = q.get()
        if worker:
            if 'Message' in worker and worker['Message'] == 'STOP':
                break
            else:
                exampleJob(worker)
        #q.tran_lock.release()            
        #q.task_done()

if (__name__ == "__main__"):
    q = FIFOSQLiteQueue(path='c:\\uconnect_logs', multithreading=True)
    # creating thread to perform the task
    start = time.time()
    while True:
        #if q.qsize() > 0: 
        #    print('Queue size is ', q.qsize())
        for x in range(3):
            t = threading.Thread(target = threader)
            t.daemon = True
            t.start()

        #if time.time()-start > 300:
        t.join()
        break

    print('Took',time.time()-start)

# creating task which need to be threaded
#
#q = FIFOSQLiteQueue(path='c:\\uconnect_logs', multithreading=True)
#for worker in range(30):
#    q.put({'Message':worker,'Time':time.ctime()})
#
#q.put({'Message':'STOP'})

#print('Took',time.time()-start)

# call from another python 
#   p = os.popen('python c:\\app\\uconnect\\myapp\\src\\com\\uconnect\\poc\\SqlLiteQWithThread.py')
#   p._proc.pid

#   import signal
#   '''need to understand appropriate signal needed to kill processes''' 
#   os.kill(<pid from anbove>,9)
#
# check if pid exist
# ??