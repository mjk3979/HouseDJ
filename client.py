import socket

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555
BUFFER_SIZE = 20

s = socket.socket()

s.connect((SERVER_IP,SERVER_PORT))
print s.recv(1024)
s.close()
