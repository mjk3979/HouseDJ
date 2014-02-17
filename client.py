#!usr/bin/python
import zmq
from common import *
import pickle
from mutagenx.easyid3 import EasyID3
import sys
from threading import Thread
import time
from pydub import AudioSegment
from io import BytesIO

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
		print('a: Add')
		print('d: Delete')
		print('m: Move')
		print('v: View Master Queue')
		print('q: Quit')
		com = input('Command: ').lower()
		if com == 'q':
			break
		elif com == 'v':
				print("Master Queue:")
				for cli, song in masterQueue:
					print(cli.nickname + ": " + str(song))
		elif com == 'a':
			title = input('File: ')
			mp3 = EasyID3(title)
			song = Song(mp3["title"][0],mp3["artist"][0])
			sendMessage(QueueUpdate(COMMAND_ADD,song))
			try:
				f = open(title , "rb")
				if f.readable():
					print('the song is readable')
					bytez = f.read()
					print("CONVERTING")
					aseg = AudioSegment.from_file(BytesIO(bytez))
					songdata = BytesIO()
					aseg.export(songdata, format="wav", bitrate="44.1k")
					songdata.seek(0)
					songdata = songdata.read()
					sendMessage((song,songdata))
					print('successfully read file')
			finally:
				f.close()
		elif com == 'd':
			sendMessage(None)
			myq = pickle.loads(socket.recv())
			i = 0
			for s in myq:
				print(str(i) + ": " + str(s))
				i+=1
			choice = int(input("Which one: "))
			sendMessage(QueueUpdate(COMMAND_DELETE, myq[choice]))
		elif com == 'm':
			sendMessage(None)
			myq = pickle.loads(socket.recv())
			i = 0
			for s in myq:
				print(str(i) + ": " + str(s))
				i+=1
			choice1 = int(input("Which one: "))
			choice2 = int(input("Which one: "))
			sendMessage(QueueUpdate(COMMAND_MOVE, (myq[choice1], myq[choice2])))

def main():
	argc = len(sys.argv)
	if (argc <= 1):
		host = "localhost"
	else:
		host = sys.argv[1]
	if (argc <= 2):
		port = 5555
	else:
		port = int(sys.argv[2])
	init(host,port)
	inputLoop()		

if __name__ == '__main__':
	main()
