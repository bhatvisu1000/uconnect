import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.

# Bind the socket to the port
myport = 1000
myHost = '' ## this is to get the local ip address
server_address = (myHost, myport)
#print >>sys.stderr, 'starting up on %s port %s' % server_address
print('starting up on {host} '.format(host=server_address))
sock.bind(server_address)
#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print ('waiting for a connection...')
    connection, client_address = sock.accept()
    try:
        #print >>sys.stderr, 'connection from', client_address
        print ('got connection from {client} '.format(client=client_address))
        # Receive the data in small chunks and retransmit it
        while True:
            myData = connection.recv(1024)
            print('data received',myData, type(myData))
    except Exception as err:
        print(err.message)
    finally:
            # Clean up the connection
            print('got data from client ... {data}'.format(data=myData),type(myData))
            connection.close()