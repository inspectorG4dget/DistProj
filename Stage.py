__author__ = 'mandy'

from Node import *
from Network import *
from Message import *
from random import randint
from copy import deepcopy as clone

import logging

log = logging.getLogger("Stages")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s | %(levelname)-8s | %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class StageMessage(Message):
        dir = 2 # 2 means send from Right, 3 from Left

        def __init__(self):
                self.id = None
                self.type = super().INFO

        def log(self):
                return "<ID%d, Type%d, Delay%d, Dir%d>" % (self.id, self.type, self.delay, self.dir)


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
        maxDelay = 0

        CANDIDATE = 6
        WAITING = 7
        DEFEATED = 8

        stage = 0

        messageQueueLeft = [] # Only for Left messages
        """:type : list[Message]"""

        def __init__(self):
                super().__init__()

        def log(self):
                return "(%d, State%d, Queue%d, QueueLeft%d, Stage%d)" % (self.id, self.state, len(self.messageQueue), len(self.messageQueueLeft), self.stage)

        def _sendMessageLeft(self, message, destination):
            destination.messageQueueLeft.append(message)
            print(str(self.id)+" is sending to destination Node "+str(destination.id))
            print("Node %d's Right is %d, left is %d" %(self.id, self.right.id, self.left.id))
            self.sentMessages += 1

        def sendStageLeft(self, message):
            self._sendMessageLeft(message, self.left)

        #def send2Sides(self, message):
        #        self.sendRight(message)
        #        message = clone(message)
        #        self.sendLeft(message)

        #def processMessage(self:Node, message:StageMessage, messageLeft:StageMessage):
        def processMessage(self:Node, message:StageMessage):
                #log.debug("Node %17s | PROCESS  | %-17s" %(self.log(), message.log()))  ##

                print("-"*60)
                print("Message queue for node %s" %self.log())
                print("-"*30+"Right")
                for m in self.messageQueue:
                        print(m.log())
                print("-"*30+"Left")
                for mLeft in self.messageQueueLeft:
                    print(mLeft.log())
                print("-"*30)

##                print("Node id " + str(self.id) + " self.messageQueue: ")
##                for p in self.messageQueue:
##                        print(p)
##                print("Node id " + str(self.id) + " end of self.messageQueue: ")
                if message.id == self.id:  # algorithm terminates
                        if self.state != self.LEADER:
                                if message.type != message.LEADER:
                                        self.state = self.LEADER
                                        self.messageQueue = []

                                        m = StageMessage()
                                        m.type = m.LEADER
                                        m.id = self.id
                                        m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                                        m.stage = self.stage
                                        #log.info("Node %17s | TRANSMIT | %-17s | to Right Node %03d" % (self.log(), m.log(), self.right.id))  ##
                                        print("Node id " + str(self.id) + " is Leader!")
                                        self.sendRight(m) # Leader notification
                                else:
                                        self.messageQueue = []

                elif message.type == message.LEADER: #if received LEADER's msg
                        print("Node id " + str(self.id) + " is processing Leader's notice! " )
                        self.messageQueue = []
                        self.state = self.FOLLOWER
                        #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
                        self.sendRight(message) # Leader notification forward

                elif self.state == self.DEFEATED: # DEFEATED node only forward.
                        print("Defeated Node id " + str(self.id) + " is forwarding! " )
                        if message.dir == 2: # check if it is sent from right
                                self.sendRight(message) # forward to right if from my left neighbour
                        else:
                                self.sendStageLeft(message) # forward to left if sent from left neighbour

                else: # Initialization, processing..
                        #if self.messageQueue[
                        #        0].SENTFROMRIGHT + message.SENTFROMRIGHT == 1: # decide whether there are 2 messages from left and right. TODO need check later
                        message.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                                #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
                        if self.state == 0: # For Initiators
                            self.state = self.CANDIDATE
                            m = StageMessage()
                            m.type = self.CANDIDATE
                            m.id = self.id
                            m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                            m.stage = self.stage
                            #self.sendRight(m)
                            message = clone(m)
                            message.dir = 3
                            self.sendStageLeft(message)
                            print("Initiator Node id " + str(self.id) + " sent 2 msgs! " )
                        elif len(self.messageQueueLeft) >= 1:
                            messageLeft = self.messageQueueLeft.pop(0)
                            if self.state == 6 and self.id < message.id and self.id < messageLeft.id: # candidates processing
                                self.stage += 1
                                m = StageMessage()
                                m.type = self.CANDIDATE
                                m.id = self.id
                                m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                                m.stage = self.stage
                                self.sendRight(m)
                                message = clone(m)
                                message.dir = 3
                                self.sendStageLeft(message)
                                print("Candidate Node id " + str(self.id) + " is processing Node " +str(message.id) + " and Node " + str(messageLeft.id))
                            else: # Defeated, set state.
                                self.state = self.DEFEATED
                                print("Node id " + str(self.id) + " is DEFEATED!")

        def processMessageQueue(self:Node):
                if not self.messageQueue :
                    print("if not self.messageQueue :")
                    return
                #elif not self.messageQueueLeft:
                #    print("if self.messageQueueLeft :")
                #    return
                else:
                        for m in self.messageQueue:
                                m.delay -= 1
                                #log.debug("Node %17s | SEE      | %-17s" %(self.log(), m.log()))  ##

                        #for mleft in self.messageQueueLeft:
                        #    mleft.delay -= 1

                        m = self.messageQueue[0]
                        if m.delay <= 0:
                                m = self.messageQueue.pop(0)
                                #mleft = self.messageQueueLeft.pop(0)
                                self.processMessage(m)

        def begin(self):
                self.state = self.INITIATOR
                m = StageMessage()
                m.id = self.id
                m.type = StageMessage.INFO
                m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                self.sendRight(m)
                #self.sendLeft(m)


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
