import zmq
from common import Song
import pickle

song = Song("Beast and the Harlot", "A7X")

SERVER_IP= '127.0.0.1'
SERVER_PORT = 5555

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://%s:%s" % (SERVER_IP, SERVER_PORT))
socket.send(pickle.dumps(song))
