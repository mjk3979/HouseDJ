#!usr/bin/python
import zmq
from common import Song
import pickle
from mutagenx.easyid3 import EasyID3
import sys



mp3 = EasyID3(sys.argv[1])
print(type(mp3["title"]))
print(mp3["title"])
song = Song(mp3["title"][0],mp3["artist"][0])
	
#song = Song("Beast and the Harlot", "A7X")

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (SERVER_IP, SERVER_PORT))
socket.send(pickle.dumps(song))
