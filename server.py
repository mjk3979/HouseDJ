import zmq
import pickle
from common import Song
from threading import Thread
from threading import Lock
import time
import pygame
from pydub import AudioSegment
from io import BytesIO
import sys
from MasterQueue import *
from copy import deepcopy

SERVER_IP = '127.0.0.1'
clients = {}
currentIndex = 0
masterQueue = MasterQueue()
socket = None
songMap = {}
queueLock = Lock()
publishLock = Lock()


PUBLISH_PORT = 5556


contextPub = zmq.Context()
socketPub = contextPub.socket(zmq.PUB)
socketPub.bind("tcp://*:%s" % (PUBLISH_PORT,))

def playerLoop():
	global currentIndex, masterQueue, songMap
	pygame.mixer.init(44100)
	while True:
		if masterQueue.peek() != None and masterQueue.peek()[1] in songMap and not(pygame.mixer.get_busy()):
			print("HERE")
			cli, song = masterQueue.pop()
			publishQueue()
			songdata = songMap[song]
			print("CONVERTING")
			aseg = AudioSegment.from_file(BytesIO(songdata))
			songdata = BytesIO()
			aseg.export(songdata, format="wav", bitrate="44.1k")
			print("ABOUT TO PLAY")
			songdata.seek(0)
			songdata = songdata.read()
			song = pygame.mixer.Sound(songdata)
			song.play()
			print("STARTED")

		else:
			time.sleep(.1)

def publishQueue():
	global socketPub, publishLock
	publishLock.acquire()
	socketPub.send(pickle.dumps(masterQueue.toList()))
	publishLock.release()

class Client():
	__slots__=('clientdata', 'queue', 'port', 'lock')

	def __init__(self, clientdata, port):
		self.clientdata = clientdata
		self.queue = []
		self.port = port
		self.lock = Lock()

	def handleMessage(self, message):
		# Queue update
		if (type(message) is Song):
			self.lock.acquire()
			self.queue.append(message)
			self.lock.release()
			publishQueue()
		else:
			self.lock.acquire()
			songMap[message[0]] = message[1]
			self.lock.release()

	def run(self):
		context = zmq.Context()
		mysock = context.socket(zmq.PAIR)
		mysock.bind("tcp://*:%s" % (self.port,))
		while True:
			data = pickle.loads(mysock.recv())
			self.handleMessage(data)

	def __deepcopy__(self, memo):
		copy = Client(deepcopy(self.clientdata, memo), self.port)
		copy.queue = [deepcopy(s, memo) for s in self.queue]
		return copy

def listenNewPort():
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	port = socket.bind_to_random_port('tcp://%s' % SERVER_IP,5555,7000,100)
	print ('BINDING CLIENT SOCKET ON ' + str(port))
	return port
	
def clientLoop():
	global socket, clients
	while True:
		raw = socket.recv()
		clientdata = pickle.loads(raw)
		if not clientdata in clients:
			newClient = Client(clientdata,listenNewPort())
			clients[clientdata] = newClient
			masterQueue.addClient(newClient)
			Thread(target=clients[clientdata].run).start()
		socket.send(pickle.dumps((clients[clientdata].port,PUBLISH_PORT)))

def main(port):
	global socket
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % (port,))
	Thread(target=playerLoop).start()
	# Loop to recieve clients
	clientLoop()

if __name__ == '__main__':
	main(sys.argv[1])
