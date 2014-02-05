#!usr/bin/python
import zmq
from common import Song
from common import ClientData
import pickle
from mutagenx.easyid3 import EasyID3
import sys

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555

context = zmq.Context()
myClientData = ClientData(input('Nickname: '))

def sendMessage(data):
    socket.send(pickle.dumps((myClientData, data)))

socket = context.socket(zmq.PAIR)
socket.connect("tcp://%s:%s" % (SERVER_IP, SERVER_PORT))

q = []
while True:
    mp3 = EasyID3(input('Song: '))
    song = Song(mp3["title"][0],mp3["artist"][0])
    print (song)
    q.append(song)
            
    sendMessage(q)
