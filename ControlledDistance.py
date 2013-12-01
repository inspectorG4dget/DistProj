__author__ = 'ashwin'

from Message import *
from Network import *
from random import randint
from copy import deepcopy as clone

import logging

log = logging.getLogger("Controlled Distance")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s | %(levelname)-8s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
log.disabled = True

class CDMessage(Message):
	FORTH = 2
	BACK = 3
	LEFT = -1
	RIGHT = 1

	def __init__(self):
		super().__init__()
		self.dist = 0
		self.dir = 0  # back/forth
		self.fromDir = None  # this is travelling left/right

	def log(self):
		return "<ID%d, T%d, d%d, D%d>" % (self.id, self.type, self.dir, self.delay)


class CDNetwork(Network):
	def __init__(self, networkSize):
		super().__init__(networkSize, CDNode)

	def run(self):
		curr = self.initiator.right
		while curr != self.initiator:
			curr.begin()
			curr = curr.right
		super().run()


class CDNode(Node):
	minDelay = 2
	maxDelay = 10

	CANDIDATE = Node.AWAKE
	DEFEATED = 7

	def __init__(self):
		self.stage = 1
		self.count = 0
		super().__init__()

	def log(self):
		return "(%d, S%d, Q%d)" % (self.id, self.state, len(self.messageQueue))

	def sendMessage(self, m):
		m.fromDir = m.LEFT
		log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), m.log(), self.left.log()))
		self.sendLeft(m)
		m = clone(m)
		m.fromDir = m.RIGHT
		m.delay = randint(self.minDelay, self.maxDelay)
		log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), m.log(), self.right.log()))
		self.sendRight(m)

	def begin(self):
		self.state = self.INITIATOR
		m = CDMessage()
		m.id = self.id
		m.type = CDMessage.INFO
		m.dir = m.FORTH
		m.delay = randint(self.minDelay, self.maxDelay)
		self.sendMessage(m)
		self.state = self.CANDIDATE

	def processMessageQueue(self):
		if len(self.messageQueue) == 0:
			return

		for message in self.messageQueue:
			message.delay -= 1
		m = self.messageQueue[0]
		if m.delay <= 0:
			self.messageQueue.pop(0)
			self.processMessage(m)

	def PROCESS_MESSAGE(self, message:CDMessage):
		log.debug("Node %-17s | PROCESS  | %-17s" %(self.log(), message.log()))
		if message.dist <= 0:
			message.dir = message.BACK
			message.delay = randint(self.minDelay, self.maxDelay)
			if message.fromDir == message.LEFT:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" %(self.log(), message.log(), self.left.log()))
				self.sendLeft(message)
			else:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.right.log()))
				self.sendRight(message)
		else:
			message.delay = randint(self.minDelay, self.maxDelay)
			if message.fromDir == message.RIGHT:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.right.log()))
				self.sendRight(message)
			else:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.left.log()))
				self.sendLeft(message)

	def CHECK(self):
		self.count += 1
		if self.count == 1:
			self.count = 0
			dist = 2**self.stage
			self.stage += 1
			m = CDMessage()
			m.id = self.id
			m.dist = dist
			m.dir = m.FORTH
			m.type = m.INFO
			m.delay = randint(self.minDelay, self.maxDelay)
			self.sendMessage(m)

	def processMessage(self, message:CDMessage):
		log.debug("Node %-17s | SEE      | %-17s" % (self.log(), message.log()))  ##
		message.dist -= 1
		if self.state == self.SLEEPING:
			self.begin()
			self.state = self.CANDIDATE

			if message.dir == message.FORTH:
				if message.id < self.id:
					self.PROCESS_MESSAGE(message)
					self.state = self.DEFEATED
				else:
					self.begin()
					self.state = self.CANDIDATE

		elif self.state == self.CANDIDATE:
			if message.dir == message.FORTH:
				if message.id < self.id:
					self.PROCESS_MESSAGE(message)
					self.state = self.DEFEATED
				else:
					if message.id == self.id:
						self.state = self.LEADER
						message.type = message.LEADER
						log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.left.log()))
						self.sendLeft(message)

			elif message.dir == message.BACK:
				if message.id == self.id:
					self.CHECK()

			elif message.type == message.LEADER:
				self.state = self.FOLLOWER
				message.delay = randint(self.minDelay, self.maxDelay)
				if message.fromDir == message.LEFT:
					log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.left.log()))
					self.sendLeft(message)
				else:
					log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.right.log()))
					self.sendRight(message)

		elif self.state == self.DEFEATED:
			if message.type == message.LEADER:
				self.state = self.FOLLOWER

			message.delay = randint(self.minDelay, self.maxDelay)
			if message.fromDir == message.LEFT:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.right.log()))
				self.sendRight(message)
			else:
				log.debug("Node %-17s | TRANSMIT | %-17s | to node %-17s" % (self.log(), message.log(), self.left.log()))
				self.sendLeft(message)


if __name__ == "__main__":
	#print('starting')
	log.debug("Starting simulation")

	networkSize = 10
	net = CDNetwork(networkSize)
	net.setIds()
	net.showTopology()
	net.initiator.begin = CDNode.begin
	net.run()
	complexity = net.getcomplexity()
	log.debug("Complexity = %d" %complexity)
	log.debug("Simulation Complete")

	#print('done')