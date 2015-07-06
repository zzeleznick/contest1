# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint
import copy

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
    CaptureAgent.registerInitialState(self, gameState)

    "G A M E  K E Y  L O C A T I O N S  D E T E R M I N A T I O N"
    self.start = gameState.getAgentPosition(self.index)

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
    print "My friend agent", self.friend, "is at position ", friendPos
    print "My first enemy agent is at position ", opps[0]
    print "My second enemy agent is at position ", opps[1]

    '''
    Your initialization code goes here, if you need any.
    '''
    print "Coloring my safe spaces", self.safeSpaces, "blue"
    self.debugDraw(self.safeSpaces, [0,0,1], clear=False)

    self.counter = 0
    self.moves = []
    self.intendedCoords =[]
    self.best = None

    #new
    print "Using my sweet time to find next moves during init as agent", self.index
    self.best = self.ActionLoop(gameState, 140)
    self.moves =  self.best.getDir()
    self.counter = len(self.moves)
    self.cacheSize = len(self.moves)
    #new


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    if self.counter == 0: #-1:
            print "Calculating", self.cacheSize, "moves as player", self.index, "from ", gameState.getAgentPosition(self.index)
            print "Cached value"
            self.best =  self.ActionLoop(gameState, self.cacheSize)
            self.moves =  self.best.getDir()

            if not self.moves or len(self.moves) == 0:
              print "Tried to play move, but ran Out of Moves!!!"
              actions = gameState.getLegalActions(self.index)
              return random.choice(actions)

            self.intendedCoords =  self.best.state[0]
            self.counter = self.cacheSize
    try:
        move = self.moves[self.cacheSize - self.counter]
        self.counter -= 1
    except:
        print "Tried to access index", self.cacheSize - self.counter, "in list of length", len(self.moves)#, "more moves now generated"
        #print "Agent", self.index, "Defaulting to closest Agent Protocol"
        #self.counter = 9999
        #return calcMoves(self, gameState)

        #actions = gameState.getLegalActions(self.index)
        #self.counter = 0
        return self.chooseAction(gameState)
        #return random.choice(actions)
    print "On move ", self.cacheSize - self.counter, "as player", self.index, "going", move, "from", gameState.getAgentPosition(self.index)
    return move



  def evaluateScore(self, gameState, node):
     fg = self.getFood(gameState).asList()
     unvisited = {}
     for el in fg:
        unvisited.update({el: False})
     count = len(fg)
     myDists = []
     hisDists = []
     #print "len of fg", count
     for dot in fg:
        if dot in node.myVisits or dot in node.friendVisits:
            # print "Visited ", dot
            count -= 1
            unvisited.pop(dot)
        else:
            myDists +=  [self.getMazeDistance(node.getState()[0], dot) ]
            hisDists +=  [self.getMazeDistance(node.getState()[1], dot) ]

     if len(myDists) < 2:
         score = 0
     else:
         score = min(myDists)

     return unvisited, - len(unvisited) * 100 - len(node.myVisits) - score


  def ActionLoop(self, gameState, depth):
    maxDepth = depth
    start = time.time()
    levelDic = {}
    closed = {}
    expanded = 0
    popped = 0
    reborn = 0
    zobmies = 0
    killedZombies = 0
    fringe = util.PriorityQueue()
    root = Node((gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(self.friend).getPosition()), evalFn = self.evaluateScore, gameState = gameState)

    fringe.push(root, -root.getScore())  #least to greatest (use negative scores)
    while len(fringe.heap) != 0:
        node = fringe.pop()
        popped += 1
        if node.getState() not in closed:  #could do just the position? // 10,10 -> 11,10 -> 11,11 <- 10,11 <-  10,10  want to prune more
            if node.depth not in levelDic:
                levelDic.update({node.depth: node })
                if node.doomed:
                      node.doomed = False  #reborn!!!
                      print "Zombie found life. Reborn!"
                      reborn +=1
                      node.lives = root.lives

            elif node.depth in levelDic: #have we explored this depth already?
              if node.getScore() > levelDic[node.depth].getScore():
                  levelDic.update({node.depth: node })
                  if node.doomed:
                      node.doomed = False  #reborn!!!
                      reborn +=1
                      node.lives = root.lives

              else:
                #print "considered pruning here"
                '''
                node.doomed = True
                zobmies +=1
                if node.lives == 0:
                    #print "Zombie ", node.getState(), "Killed. | Better Score:", levelDic[node.depth].getState(), "| Depth:", node.depth
                    killedZombies +=1
                    continue
                '''
                continue
            closed.update({node.getState(): True})
            if node.depth == maxDepth:
                continue
            #node.addDoomedChildren(node.doomed)
            node.addChildren()
            expanded += 4
            for child in node.getChildren():
                fringe.push(child, - child.getScore())  #(e.g all food: 30 * -100, 28 * -100, would want to reverse)

    print '\neval time for pruned tree is: %.4f' % (time.time() - start)
    print 'Expanded Nodes: ', expanded
    print 'Popped Nodes from Fringe: ', popped
    print 'Allowed zombies to roam:' , zobmies
    print ' | Reborn:' , reborn, " | Killed:", killedZombies, " |", "Lives: ", root.lives, '|'
    try:
        #bestDeepNode = levelDic[maxDepth]
        nodes = levelDic.values()
        bestNodes = sorted(nodes, key = lambda node: node.getScore())
        bestDeepNode = bestNodes[-1]
        if not bestDeepNode.parent:
            try:
                bestDeepNode = bestNodes[-2]
            except:
                print "Root is max"
                return None
    except:
        print "Bad Optimization"
        #bestDeepNode = levelDic[max(levelDic.keys())]


    print 'Final Destination at ',  bestDeepNode.getState(), "of depth", bestDeepNode.depth, "with score",  bestDeepNode.getScore()
    print 'Optimal moves found to be: ',  bestDeepNode.getDir()
    print 'Friend moves found to be: ',  bestDeepNode.getFriendDir()
    coords = []
    hisCoords = []
    end =  bestDeepNode
    mine = 0
    while end:
        #print "Coords in Reverse"
         if mine % 2 == 0:
            coords =[end.state[0][0]] +  coords
         else:
             hisCoords =[end.state[0][1]] +  hisCoords
         mine += 1
         end = end.parent

    print "Coords Traveled as", self.index, coords
    print "Friend coords Traveled", hisCoords
    print "Number of Pellets Left", len(self.getFood(gameState).asList())
    firstMove = bestDeepNode.getDir()[0]
    print "Going ", firstMove, "towards ", bestDeepNode.getState(), "\n"
    #return firstMove
    return bestDeepNode


##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(gameState.getRedFood().asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}



class Node:
    def __init__(self, state, directions = None, parent = None, evalFn = None, gameState = None):
        """
        :param states: an array containing objects of state
        :param directions: an array containing North, East, South, West, or Stop directions
        :param cost: an integer representing the cost of directions
        :return: a node
        """

        self.state = state  #  ( (10,0), (11,0)  ) -- > ( ( (10,0), (11,0) ), food Remaining )
        #we should never need to revisit a square we have been to unless food was gained
        #paths do matter, we can compare costs of steps when relating cost
        #self.directions = directions  [ ['N', 'S'], ['S']]
        self.parent = parent

        if self.parent:
            self.depth = parent.depth + 1
            self.parentState = parent.state

            self.myVisits = copy.deepcopy(parent.myVisits)
            self.myVisits.update({state[0]: True})

            self.friendVisits = copy.deepcopy(parent.friendVisits)
            self.friendVisits.update({state[1]: True})

            if parent.myDirections:
                if not parent.friendDirections:
                    self.friendDirections =  [directions ]
                    self.myDirections = parent.myDirections

                elif len(parent.myDirections) >= len(parent.friendDirections):
                    self.friendDirections = parent.friendDirections + [directions]  #copy.deepcopy(parent.directions)
                    self.myDirections = parent.myDirections
                else:
                    self.myDirections = parent.myDirections + [directions]
                    self.friendDirections = parent.friendDirections
            else:
                    self.myDirections = [ directions ] #initialized for real this time for root node
                    self.friendDirections = []#None
        else:
            self.depth = 0
            self.parentState = None
            self.myDirections =  []  #defaulted to None for root node
            self.friendDirections = []#None
            self.myVisits = {state[0]: True}
            self.friendVisits = {state[1]: True}

        self.doomed = False
        self.lives = 10

        self.evalFn = evalFn
        #self.score = self.evalFn(gameState, state, self.directions)
        self.food, self.score = self.evalFn(gameState, self)

        self.state = (self.state, len(self.food)) # ( ( (10,0), (11,0) ), score )

        self.children = None

        self.gameState = gameState



    def getState(self):
        return self.state

    def getDir(self):
        return self.myDirections

    def getFriendDir(self):
        return self.friendDirections

    def getScore(self):
        return self.score


    def addChildren(self):
        if len(self.myDirections) == len(self.friendDirections):
            childStates = getSuccessorsAlt(self.gameState, self.state[0][0])
            #print "Possible child states for",  self.state[0][0], "are:", childStates
            childNodes = [ Node((el[0],self.state[0][1]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            self.children = childNodes

        else:
            childStates = getSuccessorsAlt(self.gameState, self.state[0][1])
            #print "Possible child states for",  self.state[0][1], "are:", childStates
            childNodes = [ Node((self.state[0][0], el[0]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            self.children = childNodes




    '''
    def addDoomedChildren(self, doomed = False):
        if self.firstActor:
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            childStates = getSuccessorsAlt(self.gameState, self.state[0][0])
            #print "Possible child states for",  self.state[0][0], "are:", childStates
            childNodes = [ Node((el[0],self.state[0][1]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            if doomed:
                for node in childNodes:
                    node.lives = node.parent.lives - 1
            self.children = childNodes
        else:
            childStates = getSuccessorsAlt(self.gameState, self.state[0][1])
            #print "Possible child states for",  self.state[0][1], "are:", childStates
            if self.depth == 139:
                print 'meh'
            childNodes = [ Node((self.state[0][0], el[0]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            for node in childNodes:
                node.lives= node.parent.lives - 1
            if doomed:
                for node in childNodes:
                    node.lives= node.parent.lives - 1
            self.children = childNodes
    '''
    def getChildren(self):
        if self.children:
            return self.children

    def getChildrenStates(self):
        if self.getChildren():
            return [child.getState() for child in self.getChildren()]

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
               cost = 1
               successors.append( ( nextState, action, cost) )
        return successors



