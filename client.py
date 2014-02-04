import socket

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555
BUFFER_SIZE = 20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((SERVER_IP,SERVER_PORT))
s.send(bytes(input(), 'UTF-8'))
print (s.recv(1024))
s.close()
