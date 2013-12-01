__author__ = 'ashwin'

from os import listdir as ls
from pickle import load
from pprint import pprint
from numpy import std as stdev, mean
from scipy import stats as CI

import operator
import math


def gatherResults():
    answer = {}
    #for savefilename in (f for f in ls('.') if f.endswith('.pkl')):
    for savefilename in ["Stages.pkl"]:
        with open(savefilename, 'rb') as savefile:
            comp = load(savefile)
            for proto, stats in comp.items():
                if proto not in answer:
                    answer[proto] = stats
                else:
                    for n, stat in stats.items():
                        answer[proto][n] = stat
    return answer


def getStats(rawResults:dict):
    answer = {}
    alpha = 0.95
    for k, stats in rawResults.items():
        if k not in answer:
            answer[k] = {}
        for n, counts in stats.items():
            std, se = stdev(counts), CI.sem(counts)
            conf = se * CI.t._ppf((1+alpha)/2, len(counts)-1)
            answer[k][n] = (mean(counts), conf)
    return answer

def compClasses():
    with open('n2.stats', 'w') as outfile:
        outfile.write("n\tn^2\n")
        for i in (n*10**pow for pow in range(1,6) for n in range(1,6)):
            outfile.write("%d\t%d\n" %(i, i**2))

    with open('nlogn.stats', 'w') as outfile:
        outfile.write("n\tnlogn\n")
        for i in (n*10**pow for pow in range(1,6) for n in range(1,6)):
            outfile.write("%d\t%d\n" %(i, i*math.log(i, 2)))

def writeout(stats):
    for proto in stats:
        print("processing", proto)
        with open(proto + '.stats', 'w') as outfile:
            outfile.write("#n\tLower\tMean\tUpper\n")
            for n, (mean, conf) in sorted(stats[proto].items(), key=operator.itemgetter(0)):
                outfile.write("%s\n" %'\t'.join(str(i) for i in (n, mean-conf, mean, mean+conf)))


if __name__ == "__main__":
    print("starting")
    results = getStats(gatherResults())
    pprint(results)
    writeout(results)
    #compClasses()
    print('done')