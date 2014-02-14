#!usr/bin/python
import zmq
from common import Song
from common import ClientData
import pickle
from mutagenx.easyid3 import EasyID3
import sys

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555



SERVER_STREAM_PORT = 5556

context = zmq.Context()
myClientData = ClientData(input('Nickname: '))

socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (SERVER_IP, SERVER_PORT))
socket.send(pickle.dumps(myClientData))
myPort = pickle.loads(socket.recv())
socket.close()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://%s:%s" %(SERVER_IP, myPort))

def sendMessage(data):
	socket.send(pickle.dumps(data)) 

q = []
while True:
	title = input('Song: ')
	if title == 'q':
		break
	else:
		mp3 = EasyID3(title)
		song = Song(mp3["title"][0],mp3["artist"][0])
		print (song)
		q.append(song)
		sendMessage(q)
		try:
			f = open(title , "rb")
			if f.readable():
				print('the song is readable')
				bytez = f.read()
				sendMessage((song,bytez))
				print('successfully read file')
		finally:
			f.close()
