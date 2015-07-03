'''
tree-Test.py

Experimenting with returning the max value of a tree search
Will eventually convert to mini-max, and then test pruning
'''
import time
def multCost(pos):
        return pos[0] * pos[1]

def successorCoords(pos):
      return [(pos[0] - 1, pos[1]),(pos[0] + 1, pos[1]), (pos[0], pos[1] - 1), (pos[0], pos[1] + 1) ]


class Node:
    def __init__(self, state = (0,0), parentState = None, depth = 0, parent = None, costFn = multCost ):
        """
        :param states: an array containing objects of state
        :param directions: an array containing North, East, South, West, or Stop directions
        :param cost: an integer representing the cost of directions
        :return: a node
        """
        self.state = state
        self.parentState = parentState # Todo Remove
        self.directions = None #directions Todo Fix

        self.costFn = costFn
        self.cost = self.costFn(state)

        self.parent = parent
        self.depth = depth
        self.children = None

    def getState(self):
        return self.state

    def getDir(self):
        return self.directions

    def getCost(self):
        return self.cost

    def setState(self, state):
        self.state = state

    def addDir(self, direction):
        self.directions += [direction]

    def addChildren(self):
        childStates = successorCoords(self.state)
        childNodes = [ Node(el, self.state, self.depth + 1, self) for el in childStates]
        self.children = childNodes

    def getChildren(self):
        if self.children:
            return self.children

    def getChildrenStates(self):
        if self.getChildren():
            return [child.getState() for child in self.getChildren()]

    '''
    def addNodeImmutable(self, state, dir, costfn = sillyCost ):
        s = self.states[:]
        d = self.directions[:]
        c = self.cost
        output = Node(s,d, c)
        #for lists if you reference one list to a second, the second is a pointer, not a copy, use slice for lists
        #dir = getCorrespondingMove(self.getLastState(), state)
        output.addState(state)
        output.addDir(dir)
        output.cost = costfn(output.getDir())
        return output
    '''

def sillyCost():
        return 0
class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0



def bfsMax(origin, maxDepth = 3):
    parent = Node(origin)
    #closed = []
    closed = {}
    fringe = Queue()
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
            tmp = node.getCost()
            if tmp > best:
                best = tmp
                bestDest = node
            continue
            #return node
        if node not in closed:
            #closed += [ node ]
            closed.update({node: node.getCost()})
            node.addChildren()
            expanded += 4
            for child in node.getChildren():
                #If this is start and we find a,b, we need to push start,a and start,b
                #note that get successors returns ((5,4) 'South', 1) --> direction encoded
                fringe.push(child)


if __name__ == '__main__':
    parent = Node((10,10))
    count = 0
    '''
    created = [ parent ]
    expanded = []
    while count < 3:
        for node in created:
            if node.getState() not in expanded:
               node.addChildren()
               count = node.depth + 1
               created += node.getChildren()
               #print "Created list as: ", [child.getState() for child in created]
               expanded.append(node)
    '''
    start = time.time()
    dest, val, expanded = bfsMax((10,10), 6)
    print "destination at", dest.getState(), "dist:", val, " with ", expanded, "nodes expanded."
    print 'eval time for bfs: %.4f' % (time.time() - start)

    #depth of 6 -> 2.8 seconds, 5460 nodes
    #depth of 6 -> .11 with dictionary
    #depth of 5 _. 1350 nodes


