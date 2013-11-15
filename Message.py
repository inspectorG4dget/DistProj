__author__ = 'ashwin'

from Node import Node

class Message:
	INFO = 0
	LEADER = 1
	def __init__(self):
		self.delay = 0
		self.type = None

	def log(self):
		pass