import zmq
import pickle
from common import Song

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

class Client:
    __slots__=('clientdata', 'queue', 'index')

    def __init__(self, clientdata):
        self.clientdata = clientdata
        self.queue = []
        self.index = getNewIndex()

    def recieveMessage(self, message):
        # Queue update
        if (type(message) is list):
            self.queue = message
            updateMasterQueue()


def recieveMessage():
    raw = socket.recv()
    (clientdata, data) = pickle.loads(raw)
    if not clientdata in clients:
        newClient = Client(clientdata)
        clients[clientdata] = newClient
    clients[clientdata].recieveMessage(data)

def main():
    global socket
    port = 5555
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % (port,))

    # Loop to recieve clients
    while True:
        recieveMessage()

if __name__ == '__main__':
    main()
