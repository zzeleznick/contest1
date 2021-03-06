# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util

from game import Directions
from game import Actions
from util import nearestPoint
import itertools
import copy
"""
print list(itertools.product([1,2,3], [4,5,6]))
[(1, 4), (1, 5), (1, 6),
(2, 4), (2, 5), (2, 6),
(3, 4), (3, 5), (3, 6)]
"""


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    "G A M E  K E Y  L O C A T I O N S  D E T E R M I N A T I O N"
    if self.red:
        leftEdge = gameState.data.layout.width / 2
        rightEdge =  gameState.data.layout.width - 2 #don't need the last wall
        self.safeColumn = leftEdge - 2 # -1 doesn't always seem to work
    else:
        leftEdge = 1
        rightEdge = gameState.data.layout.width / 2
        self.safeColumn = rightEdge + 2

    self.safeSpaces = []
    for h in xrange(1,gameState.data.layout.height-1):
        if not gameState.data.layout.isWall((self.safeColumn, h)):
               self.safeSpaces += [(self.safeColumn, h)]


    "S T A T E  A S S I G N M E N T"
    pos = gameState.getAgentState(self.index).getPosition()
    self.friend =  min(2 + int(not self.red), 2 - self.index + 2 * int(not self.red))
    friendPos = gameState.getAgentState(self.friend).getPosition()
    opps = [gameState.getAgentState(el).getPosition() for el in [1 - int(not self.red), 3 - int(not self.red)] ]

    print "I am agent", self.index, "at position ", pos
    #print "agent 0:", gameState.getAgentState(0).getPosition()
    print "My friend agent", self.friend, "is at position ", friendPos
    print "My first enemy agent is at position ", opps[0]
    print "My second enemy agent is at position ", opps[1]

    self.top = False
    self.undecided = False

    if pos[1] > friendPos[1]:
        print "My friend is lower on the map, and I will take top Quad"
        self.top = True
    elif pos[1] < friendPos[1]:
        print "My friend is higher on the map, and I will take bottom Quad"
    else:
        self.undecided = True

    "F O O D  A S S I G N M E N T"
    self.initFood = self.getFood(gameState).asList()
    self.myFood = self.initFood[:]  #this is will be updated during our A* Search for theoretical consumption


    "I N I T I A L  F O O D  A S S I G N M E N T S "
    start = time.time()
    ourMoves = aStarSearch(self, gameState, heuristic = baseHeuristic, alternateStart = ( self.safeSpaces[-int(self.top)], self.safeSpaces[-int(not self.top)]) )
    self.moves = ourMoves[0]

    print 'eval time for moves: %.4f' % (time.time() - start)
    print "Optimal Moves: ", self.moves


    "D E B U G G I N G"
    print "Coloring my safe column white"
    self.debugDraw([(self.safeColumn, el) for el in xrange(0, gameState.data.layout.height)], [1,1,1], clear=False)

    print "Coloring my safe spaces", self.safeSpaces, "blue"
    self.debugDraw(self.safeSpaces, [0,0,1], clear=False)



  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    #actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    #values = [self.evaluate(gameState, a) for a in actions]  #no evaluation currently
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    #return random.choice(actions)
    while self.moves:
        move = self.moves[0]
        self.moves = self.moves[1:]
        print "Using predetermined move:", move
        return move



def euc(xy1,xy2):
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

def man(xy1, xy2):
     return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
'''
def debugDraw(self, cells, color, clear=False):
Draws a colored box on each of the cells you specify. If clear is True, will clear all old drawings before drawing on the specified cells. This is useful for debugging the locations that your code works with. color: list of RGB values between 0 and 1 (i.e. [1,0,0] for red) cells: list of game positions to draw on (i.e. [(20,5), (3,22)])
'''

class Node:
    def __init__(self, states = [], directions = [ [], [] ], cost = 0):
        """
        :param states: an array containing tuples of position and food remaining
        :param directions: an array of two lists containing North, East, South, West, or Stop directions for both agents
        :param cost: an integer representing the cost of directions
        :return: a node
        """
        self.states = states  # [ ((1,2),(1,1)), 20), ... ]
        self.directions = directions  #[ ['North' ], ['North'] ]
        self.cost = cost
        self.hCost = 0

    def getLastState(self):
        return self.states[-1]

    def getStates(self):
        return self.states

    def getDir(self):
        return self.directions

    def getCost(self):
        return self.cost

    def addState(self, state):
        self.states += [state]

    def addDir(self, newDirection, playerID):  #0 for first, or 1 for second  ['N', 'S']
        self.directions[playerID] += [newDirection]
        print "My moves as player", playerID, ":", self.directions[playerID]

    def sillyCost(actions):
        return 1

    def addNodeImmutable(self, state, dir, cost ): #['North', 'West']
        s = self.states[:]
        print "current stored directions: ", self.directions[:]
        print "new directions: ", dir
        d = copy.deepcopy(self.directions)
        #can't use shallow copy e.g. copy.copy  or [:] for lists in list
        c = self.cost
        output = Node(s,d, c)
        #for lists if you reference one list to a second, the second is a pointer, not a copy, use slice for lists
        output.addState(state)
        output.addDir(dir[0], 0)
        output.addDir(dir[1], 1)
        #print output.getDir()
        output.cost = cost
        return output

def agentsAtGoalState(agent, gameState, positions, fg = None):
    if not fg:
        fg = agent.getFood(gameState).asList()
    unvisited = {}
    for el in fg:
      unvisited.update({el: False})

    for visit in positions:
        if visit in unvisited:
            unvisited.pop(visit)


    myPos = gameState.getAgentState(agent.index).getPosition()
    friendPos = gameState.getAgentState(agent.friend).getPosition()

    if agent.red:
        meHome = myPos[0] <= agent.safeColumn
        friendHome = friendPos[0] <= agent.safeColumn

    else:
        meHome = myPos[0] >= agent.safeColumn
        friendHome = friendPos[0] >= agent.safeColumn

    #return len(unvisited) == 0
    #print "There are", len(unvisited), "dots remaining", "cutoff is ", len(agent.initFood) / 5

    return len(unvisited) <=2 and meHome and friendHome

def getSuccessorsAlt(gameState, pos):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = pos
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not gameState.data.layout.walls[nextx][nexty]:
              nextState = (nextx, nexty)
              cost = 1 #self.costFn(nextState)
              successors.append( ( nextState, action, cost) )
        return successors

def getCostOfActions(gameState, pos, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        if actions == None: return 999999
        x,y = pos
        cost = 0
        print "ACTIONS Performed: ", actions
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            print "Checking", (x,y)
            if gameState.data.layout.walls[x][y]: print "Wall at", (x, y); return 999999
            cost += 1 #self.costFn((x,y))
        return cost


def baseHeuristic(node, myFood, gameState, distanceFn = 1):
    print "Passed in", myFood
    if not myFood:
        return 0
    allPositions = []
    # [ ( ((x,y), (x2,y2)), 10 ), ( ((x3,y3), (x4,y4)), 9 ) ...
    for tup in node.getStates():
        allPositions += [ tup[0][0] ]
        allPositions += [ tup[0][1] ]

    unvisited = {}
    for el in myFood:
      unvisited.update({el: False})

    for visit in allPositions:
        if visit in unvisited:
            print "Found dot:", visit
            unvisited.pop(visit)

    print "Visited:", allPositions

    return len(unvisited)

def aStarSearch(agent, gameState, heuristic = baseHeuristic, alternateStart = False):
    """Search the node that has the lowest combined cost and heuristic first."""
    if not alternateStart:
       myStart = gameState.getAgentState(agent.index).getPosition()
       friendStart = gameState.getAgentState(agent.friend).getPosition()

    else:
       myStart = alternateStart[0]
       friendStart = alternateStart[1]

    closed = {}

    initNumFood = len(agent.getFood(gameState).asList())


    fringe = util.PriorityQueue()
    init = Node( [ ((myStart, friendStart),initNumFood )], [ [],[] ], 0)
    init.hCost = initNumFood
    fringe.push(init, init.hCost) #PriorityQueue.push(item, priority)

    while True:
        if fringe.isEmpty():
            print "Fringe is empty"
            return None
        node = fringe.pop()
        state = node.getLastState()
        print "State passed as", state
        allPositions = []
         # [ ( ((x,y), (x2,y2)), 10 ), ( ((x3,y3), (x4,y4)), 9 ) ...
        for tup in node.getStates():
            allPositions += [ tup[0] ]

        if agentsAtGoalState(agent, gameState, allPositions, fg = agent.myFood): #TODO Resolve Redundancy in Goal State and Heuristic
          print "reached goal!"
          return node.getDir()

        if state not in closed:
            print "Unvisited:", state
            closed.update({state: node.hCost})
            #state -> ( ( (x,y), (x2,y2) ), 10 )
            myPos = state[0][0]
            friendPos = state[0][1]
            #curNumFood = state[1]
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            mySucs = getSuccessorsAlt(gameState, myPos)
            friendSucs = getSuccessorsAlt(gameState, friendPos)

            myNextPositions, myPotentialActions = [], []
            for tup in mySucs:
                myNextPositions += [ tup[0] ]
                myPotentialActions +=  [ tup[1] ]

            friendNextPositions, friendPotentialActions = [], []
            for tup in friendSucs:
                friendNextPositions += [ tup[0] ]
                friendPotentialActions += [ tup[1] ]


            allActionPairs = list(itertools.product( myPotentialActions, friendPotentialActions))
            #>>> zz =['N', 'S']
            #>>> zzz = ['W', 'N', 'S', 'E']
            #>>> z = list(itertools.product(zz, zzz))
            #>>> z
            #[('N', 'W'), ('N', 'N'), ('N', 'S'), ('N', 'E'), ('S', 'W'), ('S', 'N'), ('S', 'S'), ('S', 'E')]
            #print "walls at", gameState.data.layout.walls.asList()

            for child in allActionPairs:  #
                print "Action Pair:", child
                myActionList = node.getDir()[0] + [ child[0] ]
                friendActonList = node.getDir()[1] + [ child[1] ]

                print "my next action", child[0]
                print "friend next action", child[1]
                dx, dy = Actions.directionToVector(child[0])
                myNextPos = (int(myPos[0] + dx), int(myPos[1] + dy))
                fdx, fdy = Actions.directionToVector(child[1])
                friendNextPos = (int(friendPos[0] + fdx), int(friendPos[1] + fdy))
                #note that the food encoding in the state of each node will be that of it's parent

                modnode = node.addNodeImmutable( ((myNextPos, friendNextPos), node.hCost ), (child[0], child[1]), getCostOfActions(gameState, myStart,  myActionList) + getCostOfActions(gameState, friendStart,  friendActonList) )
                #addNode will add the new action and state, and then recalculate input cost
                #the getCost() of the returned node will be updated
                #h = heuristic(modnode.getLastState(), agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                h = heuristic(modnode, agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                g = modnode.getCost()
                modnode.hCost = h
                print "Heuristic cost at", h, "; Step cost at", g, "from ", myPos, "and ", friendPos
                print "Intended Destinations: ", myNextPos, "and ", friendNextPos, "\n"
                fringe.push(modnode, h + g )
