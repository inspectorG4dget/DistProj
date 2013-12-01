__author__ = 'ashwin'

from Network import *
from Node import *
from Message import *
from random import randint

import logging

log = logging.getLogger("All The Way")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s | %(levelname)-8s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
log.disabled = True

class ATWNetwork(Network):
	def __init__(self, networkSize):
		super().__init__(networkSize, ATWNode)

	def run(self):
		curr = self.initiator.right
		while curr != self.initiator:
			curr.begin()
			curr = curr.right
		super().run()


class ATWMessage(Message):
	def __init__(self):
		self.id = None
		self.type = self.INFO
		self.delay = 0

	def log(self):
		return "<ID%d, T%d, D%d>" % (self.id, self.type, self.delay)


class ATWNode(Node):
	minDelay = 2
	maxDelay = 10

	def __init__(self):
		super().__init__()
		delattr(self, 'left')
		self.ids = []

	def log(self):
		return "(%d, S%d, Q%d)" % (self.id, self.state, len(self.messageQueue))

	def sendMessage(self, message):
		super()._sendMessage(message, self.right)

	def processMessageQueue(self:Node):
		if not self.messageQueue:
			return
		else:
			for m in self.messageQueue:
				m.delay -= 1
				log.debug("Node %17s | SEE      | %-17s" % (self.log(), m.log()))  ##

			m = self.messageQueue[0]
			if m.delay <= 0:
				m = self.messageQueue.pop(0)
				self.processMessage(m)

	def processMessage(self, message):
		log.debug("Node %17s | PROCESS  | %-17s" %(self.log(), message.log()))
		if self.state == self.SLEEPING:
			self.state = self.AWAKE
		self.ids.append(message.id)
		if message.id == self.id:
			if self.id == min(self.ids):
				self.state = self.LEADER
				return
			else:
				self.state = self.FOLLOWER
				return

		else:
			message.delay = randint(self.minDelay, self.maxDelay)
			log.debug("Node %17s | TRANSMIT | %-17s | to node %s" % (self.log(), message.log(), self.right.log()))
			self.sendMessage(message)

	def begin(self):
		self.state = self.INITIATOR
		m = ATWMessage()
		m.id = self.id
		m.type = ATWMessage.INFO
		m.delay = randint(self.minDelay, self.maxDelay)
		log.debug("Node %17s | TRANSMIT | %-17s | to node %s" % (self.log(), m.log(), self.right.log()))
		self.sendMessage(m)

if __name__ == "__main__":
	print('starting')

	networkSize = 10
	net = ATWNetwork(networkSize)
	net.setIds()
	net.showTopology()
	net.initiator.begin = ATWNode.begin
	net.run()
	print(net.getcomplexity())

	print('done')