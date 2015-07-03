'''
tree-Test.py

Experimenting with returning the max value of a tree search
Will eventually convert to mini-max, and then test pruning
'''
import time
import util
def evaluateMult(pos):
        return pos[0] * pos[1]

def evaluateMultWithTime(state): #( (10, 10), 2 )
        return state[0][0] * state[0][1] - state[1]


def successorCoords(pos):
      return [(pos[0] - 1, pos[1]),(pos[0] + 1, pos[1]), (pos[0], pos[1] - 1), (pos[0], pos[1] + 1) ]


class Node:
    def __init__(self, state = (0,0), parentState = None, depth = 0, parent = None, evalFn = evaluateMult ):
        """
        :param states: an array containing objects of state
        :param directions: an array containing North, East, South, West, or Stop directions
        :param cost: an integer representing the cost of directions
        :return: a node
        """
        self.state = state
        self.parentState = parentState # Todo Remove
        self.directions = None #directions Todo Fix

        self.evalFn = evalFn
        self.score = self.evalFn(state)

        self.parent = parent
        self.depth = depth
        self.children = None

    def getState(self):
        return self.state

    def getDir(self):
        return self.directions

    def getScore(self):
        return self.score

    def setState(self, state):
        self.state = state

    def addDir(self, direction):
        self.directions += [direction]

    def addChildren(self, evalFn = evaluateMult):
        if self.state[0].__class__ == tuple:
            childStates = successorCoords(self.state[0])
            childNodes = [ Node((el,self.state[1] + 1 ), self.state, self.depth + 1, self, evalFn) for el in childStates]  #still storing parent states idk why I am
            self.children = childNodes
        else:
            childStates = successorCoords(self.state)
            childNodes = [ Node(el, self.state, self.depth + 1, self) for el in childStates]
            self.children = childNodes

    def getChildren(self):
        if self.children:
            return self.children

    def getChildrenStates(self):
        if self.getChildren():
            return [child.getState() for child in self.getChildren()]

def sillyCost():
        return 0



def bfsMax(origin, maxDepth = 3):
    parent = Node(origin)
    #closed = []
    closed = {}
    fringe = util.Queue()
    fringe.push(parent)
    bestDest = None
    best = 0
    expanded = 0
    while True:
        if fringe.isEmpty():
           #print "Fringe is empty"
           return bestDest, best, expanded
        node = fringe.pop()
        if node.depth == maxDepth: #problem.isGoalState(node.getLastState()):
            tmp = node.getScore()
            if tmp > best:
                best = tmp
                bestDest = node
            continue
            #return node
        if node not in closed:
            #closed += [ node ]
            closed.update({node: node.getScore()})
            node.addChildren()
            expanded += 4
            for child in node.getChildren():
                #If this is start and we find a,b, we need to push start,a and start,b
                #note that get successors returns ((5,4) 'South', 1) --> direction encoded
                fringe.push(child)


if __name__ == '__main__':
    parent = Node((10,10))
    count = 0
    start = time.time()
    dest, val, expanded = bfsMax((10,10), 6)
    print "destination at", dest.getState(), "dist:", val, " with ", expanded, "nodes expanded."
    print 'eval time for bfs: %.4f' % (time.time() - start)

    maxDepth = 100
    start2 = time.time()
    levelDic = {}
    closed = {}
    expanded = 0
    fringe = util.PriorityQueue()
    root = Node(((10,10), 0), evalFn = evaluateMultWithTime)

    fringe.push(root, -root.getScore())  #least to greatest (use negative scores)
    while len(fringe.heap) != 0:
        node = fringe.pop()
        if node.getState() not in closed:  #could do just the position? // 10,10 -> 11,10 -> 11,11 <- 10,11 <-  10,10  want to prune more
            if node.depth in levelDic: #have we explored this depth already?
                if node.getScore() < levelDic[node.depth].getScore():
                    continue

            levelDic.update({node.depth: node })
            closed.update({node.getState(): True})
            if node.depth == maxDepth:
                continue
            node.addChildren(evalFn = evaluateMultWithTime)
            expanded += 4
            for child in node.getChildren():
                fringe.push(child, -child.getScore())

    print '\neval time for pruned tree is: %.4f' % (time.time() - start2)
    print 'Expanded Nodes: ', expanded
    print 'Final Destination at ', levelDic[maxDepth].getState()



    #depth of 6 -> 2.8 seconds, 5460 nodes
    #depth of 6 -> .11 with dictionary
    #depth of 5 _. 1350 nodes


