#!usr/bin/python
import zmq
from common import Song
from common import ClientData
import pickle
from mutagenx.easyid3 import EasyID3
import sys
from threading import Thread
import time

masterQueue = []
qSocket = None
socket = None

def init(host,port):
	global qSocket, socket
	context = zmq.Context()
	myClientData = ClientData(input('Nickname: '))

	socket = context.socket(zmq.REQ)
	socket.connect("tcp://%s:%s" % (host, port))
	socket.send(pickle.dumps(myClientData))
	ports = pickle.loads(socket.recv())
	socket.close()
	socket = context.socket(zmq.PAIR)
	socket.connect("tcp://%s:%s" %(host, ports[0]))

	qContext = zmq.Context();
	qSocket = qContext.socket(zmq.SUB)
	qSocket.connect("tcp://%s:%s" % (host,ports[1])) 
	qSocket.setsockopt_string(zmq.SUBSCRIBE, '') 
	Thread(target=listenMasterQueue).start()

def listenMasterQueue():
		global qSocket, masterQueue
		while True:
			masterQueue = pickle.loads(qSocket.recv())

def sendMessage(data):
	socket.send(pickle.dumps(data)) 

def inputLoop():		
	q = []
	while True:
		title = input('Song: ')
		if title == 'q':
			break
		elif title == 'v':
				print("Master Queue:")
				for cli, song in masterQueue:
					print(cli.nickname + ": " + str(song))
		else:
			mp3 = EasyID3(title)
			song = Song(mp3["title"][0],mp3["artist"][0])
			sendMessage(song)
			try:
				f = open(title , "rb")
				if f.readable():
					print('the song is readable')
					bytez = f.read()
					sendMessage((song,bytez))
					print('successfully read file')
			finally:
				f.close()

def main(host,port):
	init(host,port)
	inputLoop()		

if __name__ == '__main__':
	main(sys.argv[1],sys.argv[2])
