from common import *
from threading import Lock
from copy import deepcopy

class MasterQueue:
	__slots__ = ('clients', 'lock')
	def __init__(self):
		self.clients = []
		self.lock = Lock()

	def __acquireLocks__(self):
		for c in self.clients:
			c.lock.acquire()

	def __releaseLocks__(self):
		for c in self.clients:
			c.lock.release()

	def peek(self):
		self.lock.acquire()
		self.__acquireLocks__()
		retval = self.__peek__()
		self.__releaseLocks__()
		self.lock.release()
		return retval

	def __peek__(self):
		if len(self.clients) < 1:
			return None
		loopSafety = 0
		while len(self.clients[0].queue) < 1 and loopSafety < len(self.clients):
			loopSafety += 1
			self.clients = self.clients[1:] + [self.clients[0]]
		if loopSafety == len(self.clients):
			return None
		return (self.clients[0].clientdata, self.clients[0].queue[0])

	def pop(self):
		self.lock.acquire()
		self.__acquireLocks__()
		retval = self.__peek__()
		if retval != None:
			self.clients[0].queue.pop(0)
		self.clients = self.clients[1:] + [self.clients[0]]
		self.__releaseLocks__()
		self.lock.release()
		return retval

	def addClient(self, client):
		self.lock.acquire()
		self.clients.append(client)
		self.lock.release()

	def __deepcopy__(self, memo):
		copy = MasterQueue()
		copy.clients = [deepcopy(c, memo) for c in self.clients]
		return copy

	def toList(self):
		self.lock.acquire()
		temp = deepcopy(self)
		self.lock.release()
		retval = []
		while temp.__peek__() != None:
			retval.append(temp.pop())
		return retval
