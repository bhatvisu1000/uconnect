import threading
import time

timerLock = threading.Lock()
def timer(name,delay,repeat):
    with timerLock:
        #timerLock.acquire()
        while repeat > 0:
            time.sleep(delay)
            print('Thread: {thread}, time: {time} '.format(thread=name, time=str(time.ctime(time.time()))) )
            repeat -= 1
            #time.sleep(1)
        #timerLock.release()
    print('Thread: {thread} completed'.format(thread=name))

def Main():
    thread1 = threading.Thread(target=timer, args=('Timer1',1,3))
    thread2 = threading.Thread(target=timer, args=('Timer2',1,3))
    thread1.start()
    thread2.start()

    print ("Process completed")

if __name__ == "__main__":
    Main()