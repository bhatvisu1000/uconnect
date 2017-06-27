import threading, time

class AsyncWrite(threading.Thread):
    def __init__(self, text, out):
        threading.Thread.__init__(self)
        self.text = text
        self.out = out

    def run(self):
        f = open(self.out, 'a')
        f.write(self.text + "\n")
        f.close()
        time.sleep(1)
        print ("Finished writing to file {file}".format(file=self.out))

def Main():
    message = raw_input('Enter your message to be stored:')
    worker = AsyncWrite(message, 'myfile.out')
    worker.start()
    print ('Worker process started, will move on')
    # wait for worker process to finish
    worker.join()

if __name__ == "__main__":
    Main()
