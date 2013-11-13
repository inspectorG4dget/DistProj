__author__ = 'ashwin'

from Node import *

import random

class Network:
	def __init__(self, networkSize, cls):
		"""
			`cls` is the node class of the node we want
		"""

		self.size = networkSize
		self.initiator = cls()
		""":type : Node"""
		self.initiator.state = Node.INITIATOR

		curr = self.initiator
		for _ in range(networkSize - 1):
			n = cls()
			n.state = Node.SLEEPING
			curr.right = n
			n.left = curr

			curr = n

		curr.right = self.initiator
		self.initiator.left = curr

	def setAlgorithm(self, part, f):
		"""
			Set function `f` as the algorithm for `part` of the protocol.
			Ex: set `f` as the function to be executed when a message is received
		"""

		setattr(self.initiator, part, f)
		curr = self.initiator.right
		while curr != self.initiator:
			setattr(curr, part, f)
			curr = curr.right

	def setIds(self):
		ids = list(range(1,self.size+1))
		random.shuffle(ids)
		curr = self.initiator
		curr.id = ids.pop()
		curr = curr.right
		#print("setting ID %d" %curr.id)  ##
		while curr != self.initiator:
			curr.id = ids.pop()
			curr = curr.right
			#print("setting ID %d" %curr.id)  ##

	def isDone(self):
		curr = self. initiator
		if curr.messageQueue:
			return False
		curr = curr.right
		while curr != self.initiator:
			if curr.messageQueue:
				return False
			curr = curr.right

		return True

	def run(self):
		self.initiator.begin(self.initiator)

		curr = self.initiator.right
		while curr != self.initiator:
			curr.processMessageQueue()
			curr = curr.right

		while not self.isDone():
			curr = self.initiator
			curr.processMessageQueue()
			curr = curr.right
			while curr != self.initiator:
				curr.processMessageQueue()
				curr = curr.right

	def showTopology(self):
		ids = [self.initiator.id]
		curr = self.initiator.right
		while curr != self.initiator:
			ids.append(curr.id)
			curr = curr.right

		print(*ids)

	def getcomplexity(self):
		answer = 0

		curr = self.initiator
		answer += curr.sentMessages
		curr = curr.right
		while curr != self.initiator:
			answer += curr.sentMessages
			curr = curr.right

		return answer