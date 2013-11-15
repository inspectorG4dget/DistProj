__author__ = 'ashwin'

from Network import *
from Node import *
from Message import *
from random import randint

import logging
log = logging.getLogger('As Far')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class AsFarMessage(Message):
	def __init__(self):
		self.id = None
		self.type = super().INFO

	def log(self):
		return "(ID%d, T%d, D%d)" %(self.id, self.type, self.delay)


class AsFarNetwork(Network):
	def __init__(self, networkSize):
		super().__init__(networkSize, AsFarNode)

	def run(self):
		curr = self.initiator.right
		while curr != self.initiator:
			curr.begin()
			curr = curr.right
		super().run()

class AsFarNode(Node):
	minDelay = 2
	maxDelay = 10
	def __init__(self):
		super().__init__()
		delattr(self, 'left')

	def log(self):
		return "(ID%d, S%d, Q%d)" %(self.id, self.state, len(self.messageQueue))

	def processMessage(self:Node, message:AsFarMessage):
		log.debug("Node %s is processing message %s" %(self.log(), message.log()))  ##
		if message.id == self.id:  # algorithm terminates
			if self.state != self.LEADER:
				if message.type != message.LEADER:
					self.state = self.LEADER
					self.messageQueue = []

					m = AsFarMessage()
					m.type = m.LEADER
					m.id = self.id
					m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
					log.info("Node %s transmits message %s to Node %d" % (self.log(), m.log(), self.right.id))  ##
					self.right.messageQueue.append(m)
					self.sentMessages += 1
				else:
					self.messageQueue = []

		elif message.type == message.LEADER:
			self.messageQueue = []
			self.state = self.FOLLOWER
			log.info("Node %s transmits message %s to Node %d" % (self.log(), message.log(), self.right.id))  ##
			self.right.messageQueue.append(message)
			self.sentMessages += 1

		elif message.id < self.id:
			message.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
			log.info("Node %s transmits message %s to Node %d" % (self.log(), message.log(), self.right.id))  ##
			self.right.messageQueue.append(message)
			self.sentMessages += 1

	def processMessageQueue(self:Node):
		if not self.messageQueue:
			return
		else:
			for m in self.messageQueue:
				m.delay -= 1
				log.debug("Node %s saw message %s" %(self.log(), m.log()))  ##

			m = self.messageQueue[0]
			if m.delay <= 0:
				m = self.messageQueue.pop(0)
				self.processMessage(m)

	def begin(self):
		self.state = self.INITIATOR
		m = AsFarMessage()
		m.id = self.id
		m.type = AsFarMessage.INFO
		m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
		log.info("Node %s transmits message %s to Node %d" % (self.log(), m.log(), self.right.id))  ##
		self.right.messageQueue.append(m)
		self.sentMessages += 1

if __name__ == "__main__":
	print("starting")

	N = AsFarNetwork
	networkSize = 10
	net = AsFarNetwork(networkSize)
	net.setIds()
	net.showTopology()
	net.initiator.begin = AsFarNode.begin
	net.run()
	print(net.getcomplexity())

	print("done")
