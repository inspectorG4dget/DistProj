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


    def __init__(self):
        self.id = None
        self.type = super().INFO
        self.dir = 2 # 2 means send from Right, 3 from Left

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

    def __init__(self):
        super().__init__()
        self.messageQueueLeft = [] # Only for Left messages
        """:type : list[Message]"""
        #self.messageQueueRight= [] # Only for Right messages
        """:type : list[Message]"""
        self.processedMsg = 0 # 0 means processed right queue, 1 means processed left queue
        self.stage = 0
        self.fail = False

    def log(self):
        return "(%d, State%d, Queue%d, QueueLeft%d, Stage%d)" % (
        self.id, self.state, len(self.messageQueue), len(self.messageQueueLeft), self.stage)

    def _sendMessageLeft(self, message, destination):
        destination.messageQueueLeft.append(message)
        print(str(self.id) + " is sending to left destination Node " + str(destination.id))
        #print("Node %d's Right is %d, left is %d" %(self.id, self.right.id, self.left.id))
        self.sentMessages += 1

    def sendStageLeft(self, message):
        self._sendMessageLeft(message, self.left)

    #def processMessage(self:Node, message:StageMessage, messageLeft:StageMessage):
    def processMessage(self:Node, message:StageMessage): # message can be from left or right
    #log.debug("Node %17s | PROCESS  | %-17s" %(self.log(), message.log()))  ##

        print("-" * 60)
        print("Message queue for node %s" % self.log())
        print("-" * 30 + "Right")
        for m in self.messageQueue:
            print(m.log())
        print("-" * 30 + "Left")
        for mLeft in self.messageQueueLeft:
            print(mLeft.log())
        print("-" * 30)

        #if len(self.messageQueueRight) >= 1:
        #    message = self.messageQueueRight.pop(0)
        #if message.id == self.id:  # algorithm terminates
        if self.state != StageNode.LEADER and message.type == message.LEADER: #if received LEADER's msg
            #m = self.messageQueue.pop(0) # no need as following will clean the queue
            print("Node id " + str(self.id) + " is processing Leader's notice! ")
            self.messageQueue = []
            self.messageQueueLeft = []
            #self.messageQueueRight = []
            self.state = self.FOLLOWER
            #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
            self.sendRight(message) # Leader notification forward

        elif self.state == StageNode.CANDIDATE: # candidates processing # algorithm terminates,
            #if self.state != self.LEADER:
            if (message):
                if message.type != message.LEADER:
                    if message.id == self.id:
                    #Check the termination condition
                        self.state = self.LEADER
                        self.messageQueue = []
                        self.messageQueueLeft = []

                        m = StageMessage()
                        m.type = m.LEADER
                        m.id = self.id
                        m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                        m.stage = self.stage
                        #log.info("Node %17s | TRANSMIT | %-17s | to Right Node %03d" % (self.log(), m.log(), self.right.id))  ##
                        print("Node id " + str(self.id) + " is Leader!")
                        self.sendRight(m) # Leader notification


            elif (self.messageQueueLeft) and self.messageQueueLeft[0].type != message.LEADER and self.messageQueueLeft[0].id == self.id:
            #Check the termination condition

                self.state = self.LEADER
                self.messageQueue = []
                self.messageQueueLeft = []

                m = StageMessage()
                m.type = m.LEADER
                m.id = self.id
                m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
                m.stage = self.stage
                #log.info("Node %17s | TRANSMIT | %-17s | to Right Node %03d" % (self.log(), m.log(), self.right.id))  ##
                print("Node id " + str(self.id) + " is Leader!")
                self.sendRight(m) # Leader notification
            #else:
            #   self.messageQueue = []
            #   self.messageQueueLeft = []
            #self.messageQueueRight = []

            #if message and self.id < self.messageQueue[0].id: # become waiting to process another side, don't need send msg now, set processedMsg to ...
            #    m = self.messageQueue.pop(0)
            #    self.state = StageNode.WAITING
            #    self.processedMsg = 0
            #    print("Candidate Node id " + str(self.id) + " is processing Node " + str(
            #        message.id) + " and became Waiting! ")
            #elif self.id >= self.messageQueue[0].id: # failed, set state to WAITING for processing.
            #    m = self.messageQueue.pop(0)
            #    self.fail = True
            #    self.state = StageNode.WAITING
            #    self.processedMsg = 0
            #    print("Node id " + str(self.id) + " is failed by Right Node " + str(message.id))
            if self.id < message.id: # become waiting to process another side, don't need send msg now, set processedMsg ...
                # 3 steps: Pop msg / set node to Waiting / set processedMsg to 0 or 1
                self.state = StageNode.WAITING
                if message.dir == 2 :
                    m = self.messageQueue.pop(0)
                    self.processedMsg = 0
                    print("Candidate Node id " + str(self.id) + " is processing Node " + str(message.id) + " and became Waiting! ")
                elif message.dir == 3:
                    m = self.messageQueueLeft.pop(0)
                    self.processedMsg = 1
                    print("Candidate Node id " + str(self.id) + " is processing Left Node " + str(message.id) + " and became Waiting! ")
            else: # failed, set state to WAITING for processing.
                # 3 steps: Pop msg / set node to Waiting / set processedMsg to 0 or 1/ set self.fail
                self.fail = True
                self.state = StageNode.WAITING
                if message.dir == 2 :
                    m = self.messageQueue.pop(0)
                    self.processedMsg = 0
                    print("Node id " + str(self.id) + " is failed by Right Node " + str(message.id))
                elif message.dir == 3:
                    m = self.messageQueueLeft.pop(0)
                    self.processedMsg = 1
                    print("Candidate Node id " + str(self.id) + " is processing Left Node " + str(message.id) + " and became Waiting! ")

        elif self.state == StageNode.DEFEATED: # DEFEATED node only forward.
            print("Defeated Node id " + str(self.id) + " is forwarding! ")
            # steps: forward in two sides one time, pop messages which have been processed in 2 queues
            if message.dir == 2: # check if it is sent from right
                m = self.messageQueue.pop(0)
                self.sendRight(message) # forward to right if from my left neighbour
                if self.messageQueueLeft: # sent right, then check left
                    messageLeft = self.messageQueueLeft.pop(0)
                    if messageLeft.dir == 2:
                        self.sendRight(messageLeft)
                    else:
                        self.sendStageLeft(messageLeft)
            else:
                self.sendStageLeft(message) # forward to left if sent from left neighbour
                messageLeft = self.messageQueueLeft.pop(0)
                if self.messageQueue: # sent left, then check right
                    m = self.messageQueue.pop(0)
                    if messageLeft.dir == 2:
                        self.sendRight(m)
                    else:
                        self.sendStageLeft(m)

        elif self.state == StageNode.WAITING: # TODO set waiting later
            if self.processedMsg == 0: # processed right, message from left, then process
                #remove message.dir ==3 because: elif self.processedMsg == 0 and message.dir ==2: # 2 sent to 3's right before 3 processed previous left msg
                if self.messageQueueLeft:
                    messageLeft = self.messageQueueLeft.pop(0)
                    if (not self.fail) and self.id < messageLeft.id: # waiting processing
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
                        print("Waiting Node id " + str(self.id) + " is processing Left Node " + str(messageLeft.id))
                    else: # Defeated, set state.
                        self.state = self.DEFEATED
                        print("Waiting Node id " + str(self.id) + " is DEFEATED!")
                else:
                    return
            #elif self.processedMsg == 0 and message.dir ==2: # 2 sent to 3's right before 3 processed previous left msg
            #    if self.messageQueueLeft:
            #        messageLeft = self.messageQueueLeft.pop(0)
            #        if (not self.fail) and self.id < messageLeft.id: # waiting processing
            #            self.stage += 1
            #            m = StageMessage()
            #            m.type = self.CANDIDATE
            #            m.id = self.id
            #            m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
            #            m.stage = self.stage
            #            self.sendRight(m)
            #            message = clone(m)
            #            message.dir = 3
            #            self.sendStageLeft(message)
            #            print("Waiting Node id " + str(self.id) + " is processing Left Node " + str(messageLeft.id))
            #        else: # Defeated, set state.
            #            self.state = self.DEFEATED
            #            print("Waiting Node id " + str(self.id) + " is DEFEATED!")
            #    else:
            #        return
            elif self.processedMsg == 1: # processed Left, message from right, then process  TODO set this later
                if self.messageQueue:
                    mRight = self.messageQueue.pop(0)
                    if (not self.fail) and self.id < mRight.id: # waiting processing
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
                        print("Waiting Node id " + str(self.id) + " is processing Right Node " + str(message.id))
                    else: # Defeated, set state.
                        self.state = self.DEFEATED
                        print("Waiting Node id " + str(self.id) + " is DEFEATED!")
                else:
                    return

        else: # Initialization, processing..
            # decide whether there are 2 messages from left and right. TODO need check later
            message.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
            #log.info("Node %17s | TRANSMIT | %-17s | to Node %03d" % (self.log(), message.log(), self.right.id))  ##
            print("last else")
            if self.state == StageNode.INITIATOR: # For Initiators, need process first compare here or it will miss these messages
                self.state = StageNode.CANDIDATE
        #m = StageMessage()
        #m.type = StageNode.CANDIDATE
        #m.id = self.id
        #m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
        #m.stage = self.stage
        #self.sendRight(m)
        #message = clone(m)
        #message.dir = 3
        #self.sendStageLeft(message)
        #print("Initiator Node id " + str(self.id) + " sent left msgs! Right already sent in begin!" )
        #self.state == StageNode.CANDIDATE # candidates processing
        #print("message id is "+ str(message.id))
        #if self.id < message.id: # become waiting to process another side, don't need send msg now, set processedMsg to ...
        #    self.state = StageNode.WAITING
        #    self.processedMsg = 0
        #    print("Candidate Node id " + str(self.id) + " is processing Node " +str(message.id) + " and became Waiting! ")
        #else: # failed, set state to WAITING for processing.
        #    self.fail = True
        #    self.state = StageNode.WAITING
        #    self.processedMsg = 0
        #    print("Node id " + str(self.id) + " is failed by Right Node " +str(message.id))

    def processMessageQueue(self:Node):
        #m = self.messageQueue[0]
        #self.processMessage(m)
        if not self.messageQueue :
            if not self.messageQueueLeft:
                print("if not self.messageQueue :")
                return
            else:
                mleft = self.messageQueueLeft[0]
                self.processMessage(mleft)
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
                self.processMessage(m)

    def begin(self):
        self.state = self.INITIATOR
        if self.state == StageNode.INITIATOR: # For Initiators, need process first compare here or it will miss these messages
            self.state = StageNode.CANDIDATE
            print("Node %d is changed to Candidate from initiator." % self.id)
        m = StageMessage()
        m.id = self.id
        m.type = StageMessage.INFO
        m.delay = 0 #randint(StageNode.minDelay, StageNode.maxDelay)
        self.sendRight(m)
        message = clone(m)
        message.dir = 3
        self.sendStageLeft(message)


if __name__ == "__main__":
    print("starting")

    networkSize = 3
    net = StageNetwork(networkSize)
    net.setIds()
    net.showTopology()
    net.initiator.begin = StageNode.begin
    net.run()
    print(net.getcomplexity())

    print("done")
