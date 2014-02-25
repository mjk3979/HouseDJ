#!usr/bin/python
import zmq
from common import *
import pickle
from mutagenx.easyid3 import EasyID3
import sys
from threading import Thread
from time import sleep
import time
from cmdline import *
from groovesharkplugin import GroovesharkPlugin
from pydub import AudioSegment
from io import BytesIO
from os import path

masterQueue = []
qSocket = None
socket = None
shouldHalt = False

def init(host,port):
	global qSocket, socket, masterQueue
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

	masterQueue = ports[2]

def listenMasterQueue():
		global shouldHalt, qSocket, masterQueue
		while not(shouldHalt):
			try:
				masterQueue = pickle.loads(qSocket.recv(flags=zmq.NOBLOCK))
			except zmq.ZMQError:
				sleep(.2)

def sendMessage(data):
	socket.send(pickle.dumps(data)) 

def inputLoop():		
	gplugin = GroovesharkPlugin()
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
			responseTuple = inputChoice(["From File", "Grooveshark"])
			if responseTuple == None:
				continue
			else:
				i,_ = responseTuple
			if i==0:
				title = input('File: ')
				mp3 = EasyID3(title)
				song = Song(mp3["title"][0],mp3["artist"][0])
				try:
					f = open(title , "rb")
					if f.readable():
						print('the song is readable')
						bytez = f.read()
						print('successfully read file')
				finally:
					f.close()
			elif i==1:
				song = gplugin.pickSong()
				if song == None:
					continue
				else:
					bytez = gplugin.getSongData(song)
			print("CONVERTING")
			aseg = AudioSegment.from_file(BytesIO(bytez))
			songdata = BytesIO()
			aseg.export(songdata, format="mp3")
			songdata.seek(0)
			songdata = songdata.read()
			print(len(songdata))
			sendMessage(QueueUpdate(COMMAND_ADD,song))
			sendMessage((song,songdata))
		elif com == 'd':
			sendMessage(None)
			myq = pickle.loads(socket.recv())
			if len(myq) == 0:
				print("Can't delete current song!")
				continue
			i = 0
			for s in myq:
				print(str(i) + ": " + str(s))
				i+=1
			choice = input("Which one: ")
			try:
				choice = int(choice)
				if choice > (i-1) or choice < 0:
					print("please enter a valid index")
				else:
					sendMessage(QueueUpdate(COMMAND_DELETE, myq[choice]))
			except ValueError:
				print("Please input an integer")
		elif com == 'm':
			sendMessage(None)
			myq = pickle.loads(socket.recv())
			if len(myq) == 0:
				print("Can't move song.  No songs in queue")
				continue
			i = 0
			for s in myq:
				print(str(i) + ": " + str(s))
				i+=1
			choice1 = input("Which one: ")
			try:
				choice1 = int(choice1)
				if choice1 > (i-1) or choice1 < 0:
					print("please enter a valid index")
				else:
					choice2 = input("Which one: ")
					try:
						choice2 = int(choice2)
						if choice2 > i or choice2 < 0:
							print("please enter a valid index")
						else:
							sendMessage(QueueUpdate(COMMAND_MOVE, (myq[choice1], myq[choice2])))
					except ValueError:
						print("Please input an integer")
			except ValueError:
				print("Please input an integer")

def checkDirExists(musicDir):
	if(path.exists(musicDir) and path.isdir(musicDir)):
		pass	

def main():
	global shouldHalt
	argc = len(sys.argv)
	if((argc < 2) or  (argc > 4)):
		print("USAGE: python3.3 client.py musicDir [host] [port]")
		exit(1)
	else:
		if(argc == 2):
			musicDir = sys.argv[1]
			host = "localhost"
			port = 5555
		if (argc == 3):
			musicDir = sys.argv[1]
			host = sys.argv[2]
			port = 5555
		if (argc == 4):
			musicDir = sys.argv[1]
			host = sys.argv[2]
			port = sys.argv[3]
		checkDirExists(musicDir)
	init(host,port)
	inputLoop()		
	shouldHalt = True

if __name__ == '__main__':
	main()
