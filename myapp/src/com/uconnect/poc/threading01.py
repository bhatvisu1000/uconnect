import threading
from queue import Queue
import time

print_lock=threading.Lock()

def exampleJob(worker):
    time.sleep(0.5)

    with print_lock:
        print(threading.current_thread().name,worker)