#!/usr/bin/python
import sys, getopt
import pickle
import numpy as np

class RankDifference:
    """
    Given two input files of ranked terms, the class computes and outputs terms with least/largest term differences for both sets.
    """
    def __init__(self, fileA, fileB, debug=True, limit=20, listOnly=False):
        # store params
        self.fileA = fileA
        self.fileB = fileB
        self.debug = debug
        self.limit = limit
        self.listOnly = listOnly
        # init variables
        self.listA = list()
        self.listB = list()
        # perform initialization
        self.readLists()

    def readLists(self):
        """
        Read in both lists of ranked terms from the given input files.
        """
        # # read fileA
        # self.listA = [line.rstrip('\n') for line in open(self.fileA)]
        # # read fileB
        # self.listB = [line.rstrip('\n') for line in open(self.fileB)]

        # read fileA
        self.listA = self.fileA
        # read fileB
        self.listB = self.fileB

    def computeRankDifference(self):
        sizeA = len(self.listA)
        sizeB = len(self.listB)
        # list of all terms
        dictionary = list(set(self.listA) | set(self.listB))
        differences = list()
        for term in dictionary:
            try:
                rankA = self.listA.index(term) + 1
            except ValueError:
                rankA = sizeA # sizeA + 1 instead?
            try:
                rankB = self.listB.index(term)
            except ValueError:
                rankB = sizeB
            rankDiff = 1.0*rankA/sizeA - 1.0*rankB/sizeB # in [-1,1]
            differences.append((term, round(rankDiff, 2)))
        return sorted(differences, key=lambda i: i[1], reverse=True)[0:self.limit]


if __name__ == "__main__":
    with open('countryArtistsUL.pkl', 'rb') as f:
        countryArtistsUL = pickle.load(f)
    with open('topGlobal.pkl', 'rb') as f:
        topGlobal = pickle.load(f)
    # parse cmdline arguments
    fileA = list(np.argsort(countryArtistsUL[0]))[::-1][:10000]
    fileB = list(np.argsort(topGlobal))[:10000]
    listOnly = False
    numTerms = 20
    errorMsg = 'rank_difference.py -a <fileA> -b <fileB> [-l] [-n <numTerms>]'
    args = sys.argv[1:]
    try:
        opts, args = getopt.getopt(args,"ha:b:ln:",["fileA=","fileB=","listOnly","numTerms"])
    except getopt.GetoptError:
        print (errorMsg)
        sys.exit(2)
   
    for opt, arg in opts:
        if opt == '-h':
            print (errorMsg)
            sys.exit()
        elif opt in ("-a", "--fileA"):
            fileA = arg
        elif opt in ("-b", "--fileB"):
            fileB = arg
        elif opt in ("-l", "--listOnly"): # output only the list of descriptive terms for fileA 
            listOnly = True
        elif opt in ("-n", "--numTerms"):
            numTerms = int(arg)

    if fileA == '' or fileB == '':
        print (errorMsg)
        sys.exit()

    instance = RankDifference(fileA=fileA, fileB=fileB, listOnly=listOnly, limit=numTerms)
    instance.computeRankDifference()
