__author__ = 'ashwin'


def addConstants(names):
	def adder(cls):
		for i, name in enumerate(names): setattr(cls, name.upper(), i)
		return cls

	return adder

@addConstants("sleeping awake processing leader follower")
class Node:

	def __init__(self):
		self.sentMessages = 0
		self.right = None
		self.left = None
		self.state = None

	def onReceive(self, message):
		pass

	def changeMessage(self, message):
		pass

class Message:
	def __init__(self):
		self.distance = 0
		self.payload = None
		self.stage = 0
