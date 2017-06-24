from multiprocessing import Process
import os, time

def info(title):
    time.sleep(1)
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getpid())
    print('process id:', os.getpid())

def f(name):
    time.sleep(5)
    info('function f')
    print('hello', name)

if __name__ == '__main__':
    p = Process(target=f, args=('bob',))
    p.start()
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()