__author__ = 'mandy'

from Node import *
from Network import *
from Message import *
from random import randint
"""
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s | %(levelname)-8s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
"""
class StageMessage(Message):
    SENTFROMRIGHT = 0

    def __init__(self):
        self.id = None
        self.type = super().INFO

    def log(self):
        return "<ID%d, T%d, D%d>" %(self.id, self.type, self.delay)

class StageNetwork(Network):
	def __init__(self, networkSize):
		super().__init__(networkSize, StageNode)

	def run(self):
		curr = self.initiator.right
		while curr != self.initiator:
			curr.begin()
			curr = curr.right
		super().run()

class StageNode(Node):
    """
        Time Delay can be set here.
    """
    minDelay = 0
    maxDelay = 1

    CANDIDATE = 6
    WAITING = 7
    DEFEATED = 8

    stage = 0

    def __init__(self):
        super().__init__()

    def log(self):
        return "(%d, S%d, Q%d)" %(self.id, self.state, len(self.messageQueue))

    def sendRight(self, message):
        super().sendRight(message)

    def sendLeft(self, message):
        super().sendLeft(message)

    def send2Sides(self, message):
        self.sendRight(message)
        self.sendLeft(message)

    def processMessage(self:Node, message:StageMessage):
        #log.debug("Node %17s | PROCESS  | %-17s" %(self.log(), message.log()))  ##

        print("Node id "+str(self.id) + " self.messageQueue: ")
        for p in self.messageQueue:
            print(p)
        print("Node id "+str(self.id) + " end of self.messageQueue: ")
        if message.id == self.id:  # algorithm terminates
            if self.state != self.LEADER:
                if message.type != message.LEADER:
                    self.state = self.LEADER
                    self.messageQueue = []

                    m = StageMessage()
                    m.type = m.LEADER
                    m.id = self.id
                    m.delay = randint(StageNode.minDelay, StageNode.maxDelay)
                    m.stage = self.stage
                    #log.info("Node %17s | TRANSMIT | %-17s | to Right Node %03d" % (self.log(), m.log(), self.right.id))  ##
                    print("Node id "+str(self.id) + " is Leader!")
                    self.sendRight(m) # Leader notification
                else:
                    self.messageQueue = []

        elif message.type == message.LEADER:
            self.messageQueue = []
            self.state = self.FOLLOWER
            #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
            self.sendRight(message) # Leader notification forward

        elif self.state == self.DEFEATED:
            if message.SENTFROMRIGHT == 1: # check if it is sent from right
                self.sendLeft(message) # forward to left if sent from right
            else:
                self.sendRight(message) # forward to right if sent from left

        elif self.messageQueue:
            if self.messageQueue[0].SENTFROMRIGHT + message.SENTFROMRIGHT == 1: # decide whether there are 2 messages from left and right. TODO need check later
                message.delay = randint(StageNode.minDelay, StageNode.maxDelay)
                #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
                if self.id < min(message.id, self.messageQueue[0].id):
                    self.stage += 1
                    m = StageMessage()
                    m.type = m.CANDIDATE
                    m.id = self.id
                    m.delay = randint(StageNode.minDelay, StageNode.maxDelay)
                    m.stage = self.stage
                    self.send2Sides(m) #send in both sides, TODO how to set SENTFROMRIGHT
                else:
                    self.state = self.DEFEATED
                    print("Node id "+str(self.id) + " is DEFEATED!")

    def processMessageQueue(self:Node):
        if not self.messageQueue:
            return
        else:
            for m in self.messageQueue:
                m.delay -= 1
                #log.debug("Node %17s | SEE      | %-17s" %(self.log(), m.log()))  ##

            m = self.messageQueue[0]
            if m.delay <= 0:
                m = self.messageQueue.pop(0)
                self.processMessage(m)

    def begin(self):
        self.state = self.INITIATOR
        m = StageMessage()
        m.id = self.id
        m.type = StageMessage.INFO
        m.delay = randint(StageNode.minDelay, StageNode.maxDelay)
        self.sendRight(m)
        self.sendLeft(m)

if __name__ == "__main__":
	print("starting")

	networkSize = 5
	net = StageNetwork(networkSize)
	net.setIds()
	net.showTopology()
	net.initiator.begin = StageNode.begin
	net.run()
	print(net.getcomplexity())

	print("done")