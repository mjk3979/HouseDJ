import zmq
import pickle
from common import *
from threading import Thread
from threading import Lock
import time
import pygame
import sys
from MasterQueue import *
from copy import deepcopy
from io import BytesIO

SERVER_IP = '127.0.0.1'
clients = {}
currentIndex = 0
masterQueue = MasterQueue()
socket = None
songMap = {}
queueLock = Lock()
publishLock = Lock()
paused = False


PUBLISH_PORT = 5556


contextPub = zmq.Context()
socketPub = contextPub.socket(zmq.PUB)
socketPub.bind("tcp://*:%s" % (PUBLISH_PORT,))

def playerLoop():
	global currentIndex, masterQueue, songMap, paused
	pygame.mixer.init(44100)
	while True:
		if masterQueue.peek() != None and masterQueue.peek()[1] in songMap and not(pygame.mixer.music.get_busy()):
			print("HERE")
			cli, song = masterQueue.pop()
			publishQueue()
			songdata = BytesIO(songMap[song])
			del songMap[song]
			print("ABOUT TO PLAY")
			pygame.mixer.music.load(songdata)
			pygame.mixer.music.play()
			print("STARTED")

		else:
			time.sleep(.5)

def publishQueue():
	global socketPub, publishLock
	publishLock.acquire()
	socketPub.send(pickle.dumps(masterQueue.toList()))
	publishLock.release()

class Client():
	__slots__=('clientdata', 'queue', 'port', 'lock', 'sock')

	def __init__(self, clientdata, port):
		self.clientdata = clientdata
		self.queue = []
		self.port = port
		self.lock = Lock()

	def handleQueueUpdate(self, qupdate):
		com = qupdate.command
		if com == COMMAND_ADD:
			self.queue.append(qupdate.data)
		elif com == COMMAND_MOVE:
			song1, song2 = qupdate.data
			ind1, ind2 = self.queue.index(song1), self.queue.index(song2)
			self.queue[ind1], self.queue[ind2] = song2, song1
		elif com == COMMAND_DELETE:
			self.queue.pop(self.queue.index(qupdate.data))

	def handleMessage(self, message):
		global paused
		# Queue update
		if (type(message) is QueueUpdate):
			self.lock.acquire()
			self.handleQueueUpdate(message)
			self.lock.release()
			publishQueue()
		elif type(message) is tuple:
			print("got song data")
			self.lock.acquire()
			songMap[message[0]] = message[1]
			self.lock.release()
		elif message == None:
			self.lock.acquire()
			self.sock.send(pickle.dumps(self.queue))
			self.lock.release()
		elif type(message) == PlayerCommand:
			self.lock.acquire()
			if message.cmd == PLAYER_PAUSE:
				if paused:
					pygame.mixer.music.unpause()
					paused = False
				else:
					pygame.mixer.music.pause()
					paused = True
			elif message.cmd == PLAYER_VOLUME_UP:
				pygame.mixer.music.set_volume(min(pygame.mixer.music.get_volume() + 0.02, 1.0))
			elif message.cmd == PLAYER_VOLUME_DOWN:
				pygame.mixer.music.set_volume(max(pygame.mixer.music.get_volume() - 0.02, 0.0))
			self.lock.release()


	def run(self):
		context = zmq.Context()
		self.sock = context.socket(zmq.PAIR)
		self.sock.bind("tcp://*:%s" % (self.port,))
		while True:
			print("looping")
			data = pickle.loads(self.sock.recv())
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
		socket.send(pickle.dumps((clients[clientdata].port,PUBLISH_PORT,masterQueue.toList())))

def main():
	global socket
	argc = len(sys.argv)
	if (argc <= 1):
		port = 5555
	else:
		port = int(sys.argv[1])
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % (port,))
	Thread(target=playerLoop).start()
	# Loop to recieve clients
	clientLoop()

if __name__ == '__main__':
	main()
