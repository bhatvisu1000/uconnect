import multiprocessing
import threading
import socket

class Server(object):
    def handle(self, connection, address):
        print("OK...connected...")
        try:
            while True:
                data = connection.recv(1024)
                if data == "":
                    break
                connection.sendall(data)
        except Exception as e:
           print(e)
        finally:
            connection.close()
            print("Connection closed")
    def accept_forever(self):
        while True:
            # Accept a connection on the bound socket and fork a child process
            # to handle it.
            print("Waiting for connection...")
            conn, address = self.socket.accept()
            process = multiprocessing.Process(
                target=self.handle, args=(conn, address))
            process.daemon = True
            process.start()
            # Close the connection fd in the parent, since the child process
            # has its own reference.
            conn.close()
    def __init__(self, port, ip):
        self.port = port
        self.ip = ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)
        # Spin up an acceptor thread
        self.worker = threading.Thread(target=self.accept_forever)
        self.worker.daemon = True
        self.worker.start()
    def join(self):
        # threading.Thread.join() is not interruptible, so tight loop
        # in a sleep-based join
        while self.worker.is_alive():
            self.worker.join(0.5)

# Create two servers that run in the background
s1 = Server(9001,"127.0.0.1")
s2 = Server(9002,"127.0.0.1")

# Wait for servers to shutdown
s1.join()
s2.join()