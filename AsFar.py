__author__ = 'ashwin'

from Network import *
from Node import *
from Message import *
from random import randint

class AsFarMessage(Message):
	def __init__(self):
		self.id = None
		self.type = super().INFO


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

	def processMessage(self:Node, message:AsFarMessage):
		print("Node %d (state %d) is processing message %d (type %d)" %(self.id, self.state, message.id, message.type))  ##
		if message.id == self.id:  # algorithm terminates
			if self.state != self.LEADER:
				if message.type != message.LEADER:
					self.state = self.LEADER
					self.messageQueue = []

					m = AsFarMessage()
					m.type = m.LEADER
					m.id = self.id
					m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
					print("Node %d (state %d) transmits message %d (type %d) to Node %d" % (self.id, self.state, m.id, m.type, self.right.id))  ##
					self.right.messageQueue.append(m)
					self.sentMessages += 1
				else:
					self.messageQueue = []

		elif message.type == message.LEADER:
			self.messageQueue = []
			self.state = self.FOLLOWER
			print("Node %d (state %d) transmits message %d (type %d) to Node %d" % (self.id, self.state, message.id, message.type, self.right.id))  ##
			self.right.messageQueue.append(message)
			self.sentMessages += 1

		elif message.id < self.id:
			message.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
			print("Node %d (state %d) transmits message %d (type %d) to Node %d" % (self.id, self.state, message.id, message.type, self.right.id))  ##
			self.right.messageQueue.append(message)
			self.sentMessages += 1

	def processMessageQueue(self:Node):
		if not self.messageQueue:
			return
		else:
			for m in self.messageQueue:
				m.delay -= 1
				print("Node %d (state %d) saw message %d (type %d) (delay %d)" %(self.id, self.state, m.id, m.type, m.delay))  ##

			m = self.messageQueue[0]
			if m.delay <= 0:
				m = self.messageQueue.pop(0)
				self.processMessage(m)

	def begin(self):
		self.state = self.INITIATOR
		m = Message()
		m.id = self.id
		m.type = AsFarMessage.INFO
		m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
		print("Node %d (state %d) transmits message %d (type %d) to Node %d" % (self.id, self.state, m.id, m.type, self.right.id))  ##
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
