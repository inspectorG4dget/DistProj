__author__ = 'ashwin'


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

    def log(self):
        pass

    def _sendMessage(self, message, destination):
        destination.messageQueue.append(message)
        #print(str(self.id) + " is sending to destination Node " + str(destination.id))
        self.sentMessages += 1

    def sendLeft(self, message):
        self._sendMessage(message, self.left)

    def sendRight(self, message):
        self._sendMessage(message, self.right)