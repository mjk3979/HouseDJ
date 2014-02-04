import zmq
import pickle
from common import Song

port = 5555

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % (port,))

data = socket.recv()
song = pickle.loads(data)
print(song)
