import socket
from common import Song
import pickle

song = Song("Beast and the Harlot", "A7X")

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555
BUFFER_SIZE = 100

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((SERVER_IP,SERVER_PORT))
s.send(pickle.dumps(song))
print (s.recv(1024))
s.close()
