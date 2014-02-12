import zmq
import pickle
from common import Song
from threading import Thread

clients = {}
currentIndex = 0
masterQueue = None
socket = None

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

class Client(Thread):
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

    def run():
        mysock = context.socket(zmq.PAIR)
        mysock.bind("tcp://*:%s" % (port,))
        while True:
            data = pickle.loads(zmq.recv())

def recieveMessage():
    global socket, masterQueue, clients
    raw = socket.recv()
    (clientdata, data) = pickle.loads(raw)
    if not clientdata in clients:
        newClient = Client(clientdata)
        clients[clientdata] = newClient
    clients[clientdata].recieveMessage(data)
    if masterQueue != None:
        print ("Master Queue:")
        for song in masterQueue:
            print(song)

def main():
    global socket
    port = 5555
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind("tcp://*:%s" % (port,))

    # Loop to recieve clients
    while True:
        recieveMessage()

if __name__ == '__main__':
    main()
