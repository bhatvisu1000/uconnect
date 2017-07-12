from persistqueue import FIFOSQLiteQueue
from threading import Thread
q = FIFOSQLiteQueue(path="c:\\uconnect_logs", multithreading=True)

def worker():
    while True:
        print('QSize before get',q.size)
        #q.tran_lock.acquire()
        item = q.get()
        #q.tran_lock.release()
        print(item, 'current qsize', q.size)

if __name__ == "__main__":
    for item in range(30):
        q.put({'Item #':item})

    for i in range(3):
         t = Thread(target=worker)
         t.daemon = True
         t.start()

    t.join()