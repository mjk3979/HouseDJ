import zmq
import pickle
from common import Song
from threading import Thread
from threading import Lock
import time
import pygame
from pydub import AudioSegment
from io import BytesIO

SERVER_IP = '127.0.0.1'
clients = {}
currentIndex = 0
masterQueue = None
socket = None
songMap = {}
queueLock = Lock()

def playerLoop():
	pygame.mixer.init(44100)
	while True:
		if masterQueue != None and len(masterQueue) != 0 and masterQueue[0] in songMap and not(pygame.mixer.get_busy()):
			song = masterQueue.pop(0)
			songdata = songMap[song]
			print("CONVERTING")
			aseg = AudioSegment.from_file(BytesIO(songdata))
			aseg = aseg.reverse()
			songdata = BytesIO()
			aseg.export(songdata, format="wav", bitrate="44.1k")
			print("ABOUT TO PLAY")
			songdata.seek(0)
			songdata = songdata.read()
			song = pygame.mixer.Sound(songdata)
			song.play()
			print("STARTED")

		else:
			time.sleep(.05)

def getNewIndex():
	if len(clients) == 0:
		return 0
	return max(c.index for c in clients.values()) + 1

def updateMasterQueue():
	global masterQueue, currentIndex, clients, queueLock
	queueLock.acquire()
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
	queueLock.release()

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
