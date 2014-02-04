import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5555
BUFFER_SIZE = 20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)

(conn, addr) = s.accept()
print ('Client connected:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print ('got data: ', data)
    conn.send(data)
conn.close()
