__author__ = 'ashwin'

from Network import *
from Node import *
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
		#print("Node %d is processing message %d" %(self.id, message.id))  ##
		if message.id == self.id:  # algorithm terminates
			if message.type != message.LEADER:
				self.state = AsFarNode.LEADER
				self.messageQueue = []

				m = AsFarMessage()
				m.type = AsFarMessage.LEADER
				m.id = self.id
				m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
				self.right.messageQueue.append(m)
				self.sentMessages += 1

		elif message.type == AsFarMessage.LEADER:
			self.messageQueue = []
			self.state = AsFarNode.FOLLOWER
			self.right.messageQueue.append(message)
			self.sentMessages += 1

		elif message.id < self.id:
			message.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
			self.right.messageQueue.append(message)
			self.sentMessages += 1

	def processMessageQueue(self:Node):
		if not self.messageQueue:
			return
		else:
			for m in self.messageQueue:
				#print("Node %d saw message %d (delay %d)" %(self.id, m.id, m.delay))  ##
				m.delay -= 1

			m = self.messageQueue[0]
			if m.delay <= 0:
				m = self.messageQueue.pop(0)
				self.processMessage(m)

	def begin(self):
		m = Message()
		m.id = self.id
		m.type = AsFarMessage.INFO
		m.delay = randint(AsFarNode.minDelay, AsFarNode.maxDelay)
		self.right.messageQueue.append(m)

if __name__ == "__main__":
	print("starting")

	N = AsFarNetwork
	networkSize = 50
	net = AsFarNetwork(networkSize)
	net.setIds()
	net.showTopology()
	net.initiator.begin = AsFarNode.begin
	net.run()
	print(net.getcomplexity())

	print("done")
