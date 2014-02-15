import zmq
import pickle
from common import Song
from threading import Thread
import time
import pygame

SERVER_IP = '127.0.0.1'
clients = {}
currentIndex = 0
masterQueue = None
socket = None
songMap = {}

def playerLoop():
	pygame.init()
	while True:
		if masterQueue != None and len(masterQueue) != 0 and masterQueue[0] in songMap and not(pygame.mixer.get_busy()):
			song = masterQueue.pop(0)
			songdata = songMap[song]
			print("ABOUT TO PLAY")
			print(type(songdata))
			song = pygame.mixer.Sound(array=songdata)
			song.play()
			print("STARTED")

		else:
			time.sleep(.05)

def getNewIndex():
	if len(clients) == 0:
		return 0
	return max(c.index for c in clients.values()) + 1

def updateMasterQueue():
	global masterQueue, currentIndex, clients
	masterQueue = []
	i = currentIndex
	songsFromEach = 0
	orderClients = [c for (i,c) in sorted((cli.index, cli) for cli in clients.values())]
	while songsFromEach < max(len(c.queue) for c in orderClients):
		songsFromEach += 1
		for ci in range(len(orderClients)):
			ind = (i + ci) % len(orderClients)
		if len(orderClients[ind].queue) >= songsFromEach:
			masterQueue.append(orderClients[ind].queue[songsFromEach - 1])

class Client():
	__slots__=('clientdata', 'queue', 'index', 'port')

	def __init__(self, clientdata, port):
		self.clientdata = clientdata
		self.queue = []
		self.index = getNewIndex()
		self.port = port

	def handleMessage(self, message):
		# Queue update
		if (type(message) is list):
					self.queue = message
					updateMasterQueue()
		else:
					songMap[message[0]] = message[1]

	def run(self):
		context = zmq.Context()
		mysock = context.socket(zmq.PAIR)
		mysock.bind("tcp://*:%s" % (self.port,))
		while True:
			data = pickle.loads(mysock.recv())
			self.handleMessage(data)

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
			Thread(target=clients[clientdata].run).start()
		socket.send(pickle.dumps(clients[clientdata].port))

def main():
	global socket
	port = 5555
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:%s" % (port,))
	Thread(target=playerLoop).start()
	# Loop to recieve clients
	clientLoop()

if __name__ == '__main__':
	main()
