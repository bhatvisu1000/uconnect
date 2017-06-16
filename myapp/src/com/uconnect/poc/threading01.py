import threading
from Queue import Queue
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
    q = Queue()
    # creating thread to perform the task
    for x in range(1):
        t = threading.Thread(target = threader)
        t.daemon = True
        t.start()

    start = time.time()

    # creating task which need to be threaded
    for worker in range(30):
        q.put(worker)

    q.join()

    print('Took',time.time()-start)
