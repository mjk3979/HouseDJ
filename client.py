#!usr/bin/python
import zmq
from common import Song
from common import ClientData
import pickle
from mutagenx.easyid3 import EasyID3
import sys
from threading import Thread
import time

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555
SERVER_PUB_PORT = 5556


context = zmq.Context()
myClientData = ClientData(input('Nickname: '))

socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (SERVER_IP, SERVER_PORT))
socket.send(pickle.dumps(myClientData))
myPort = pickle.loads(socket.recv())
socket.close()
socket = context.socket(zmq.PAIR)
socket.connect("tcp://%s:%s" %(SERVER_IP, myPort))

masterQueue = []

qContext = zmq.Context();
qSocket = qContext.socket(zmq.SUB)
qSocket.connect("tcp://%s:%s" % (SERVER_IP,SERVER_PUB_PORT)) 
qSocket.setsockopt_string(zmq.SUBSCRIBE, '') 

def listenMasterQueue():
		global qSocket
		while True:
			masterQueue = pickle.loads(qSocket.recv())
			print("got new Master Queue")
			for song in masterQueue:
				print(song)

Thread(target=listenMasterQueue).start()


def sendMessage(data):
	socket.send(pickle.dumps(data)) 

		
q = []
while True:
	title = input('Song: ')
	if title == 'q':
		break
	elif title == 'v':
			print("Master Queue:")
			for songTitle in masterQueue:
				print(songTitle)	
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
