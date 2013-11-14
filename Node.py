__author__ = 'ashwin'


def addConstants(names):
	def adder(cls):
		for i, name in enumerate(names): setattr(cls, name.upper(), i)
		return cls

	return adder

#@addConstants("sleeping awake processing leader follower initiator")
class Node:

	INITIATOR = 0
	SLEEPING = 1
	AWAKE = 2
	PROCESSING = 3
	LEADER = 4
	FOLLOWER = 5

	def __init__(self):
		self.sentMessages = 0
		self.right = None
		""":type : Node"""
		self.left = None
		""":type : Node"""
		self.state = None
		self.messageQueue = []
		""":type : list[Message]"""
		self.id = 0

	def onReceive(self, message):
		pass

	def changeMessage(self, message):
		pass

	def processMessage(self, message):
		pass

	def processMessageQueue(self):
		pass

	def begin(self):
		pass