import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
myPort = 1000
myServer = 'localhost'
server_address = (myServer, myPort)
print >>sys.stderr, 'connecting to %s port %s' % server_address
try:
    sock.connect(server_address)
except Exception as err:
    print('Error connecting to server, Pls make sure server [{server}] is listening on port [{port}]'.\
        format(server=myServer, port=myPort))
    sys.exit(-1)
#After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in the server.

try:
    
    # Send data
    #message = 'This is the message.  It will be repeated.'
    message = 'STOP'
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    print('received, expected',amount_received,amount_expected)
    while amount_received < amount_expected:
        print('in while')
        data = sock.recv(1024)
        print('Data',data)
        amount_received += len(data)
        print('Amount Received',amount_received,len(data))
        print ('received "%s"' % data)
        break
finally:
    print('closing socket')
    #sock.shutdown(socket.SHUT_WR)
    sock.close()