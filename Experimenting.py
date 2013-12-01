__author__ = 'ashwin'

from ControlledDistance import CDNode, CDNetwork
from AsFar import AsFarNode, AsFarNetwork
from AllTheWay import ATWNode, ATWNetwork
from multiprocessing import Process
from os import listdir as ls
from functools import partial

import pickle
import sys

def runProto(proto, nodetype, numNodes, numTrials):
	answer = []
	for _t in range(numTrials):
		print(_t, end=' ')
		sys.stdout.flush()
		net = proto(numNodes)
		net.setIds()
		net.initiator.begin = nodetype.begin
		net.run()
		complexity = net.getcomplexity()
		answer.append(complexity)
	print('')
	return answer


def runAllProtos(protos, nodes, numTrials):
	answer = {}
	for proto, nodeType in protos.items():
		pname = proto(nodes[0]).__class__
		pname = str(pname).rstrip(">").rsplit('.')[1].strip("'")
		print('-'*30, "Running", pname)
		if pname not in answer:
			answer[pname] = {}

		for numNodes in nodes:
			print('tesing with %d nodes' %numNodes)
			answer[pname][numNodes] = runProto(proto, nodeType, numNodes, numTrials)

	return answer

def RCD():
	protos = {
		CDNetwork: CDNode,
	}
	nodes = [i * 10 ** pow for pow in range(1, 4) for i in range(1, 6)]
	numTrials = 30
	for numNodes in nodes:
		if 'CD%d.pkl' %numNodes not in ls('.'):
			results = runAllProtos(protos, [numNodes], numTrials)
			with open('CD%d.pkl' %numNodes, 'wb') as logfile:
				pickle.dump(results, logfile)

def RAF():
	protos = {
		AsFarNetwork: AsFarNode,
	}
	nodes = [i * 10 ** pow for pow in range(1, 4) for i in range(1, 6)]
	numTrials = 30
	for numNodes in nodes:
		if 'AF%d.pkl' %numNodes not in ls('.'):
			results = runAllProtos(protos, [numNodes], numTrials)
			with open('AF%d.pkl' %numNodes, 'wb') as logfile:
				pickle.dump(results, logfile)

def RAW(nodes):
	protos = {
		ATWNetwork: ATWNode,
	}
	#nodes = [i * 10 ** pow for pow in range(1, 4) for i in range(1, 6)]
	numTrials = 30
	for numNodes in nodes:
		if 'ATW%d.pkl' % numNodes not in ls('.'):
			results = runAllProtos(protos, [numNodes], numTrials)
			with open('ATW%d.pkl' %numNodes, 'wb') as logfile:
				pickle.dump(results, logfile)

if __name__ == "__main__":
	print('starting')
	#protos = {
	#		CDNetwork: CDNode,
	#		AsFarNetwork: AsFarNode,
	#		ATWNetwork: ATWNode,
	#}
	#nodes = [i*10**pow for pow in range(1,7) for i in range(1,6)]
	#numTrials = 30
	#results = runAllProtos(protos, nodes, numTrials)
	#with open('datafile', 'w') as logfile:
	#	pickle.dump(results, logfile)

	p1 = Process(target=partial(RAW, [1000]))
	p2 = Process(target=partial(RAW, [2000]))
	p3 = Process(target=partial(RAW, [3000]))
	p4 = Process(target=partial(RAW, [4000]))
	p5 = Process(target=partial(RAW, [5000]))
	#p2 = Process(target=RAF)
	#p3 = Process(target=RAW)
	p1.start()
	p2.start()
	p3.start()
	p4.start()
	p5.start()
	p1.join()
	p2.join()
	p3.join()
	p4.join()
	p5.join()

	print('done')