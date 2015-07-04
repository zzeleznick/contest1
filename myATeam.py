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
import game
from util import nearestPoint
import time


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent'):
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

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

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
    #note: could be oriented top-bottom or left-right
    #first need to find orientation, and split the map
    #for our purposes assume that a width  > height --> l/r
    #this might make undue assumptions that we start on the same side as our other teammmate,

    #alternatively : def getFood(self, gameState): and find out how to divide
    '''
    if gameState.data.layout.width > gameState.data.layout.height:
        self.lr = True
    else:
        self.lr = False
    ''' ##currently this is always true

    "G A M E  K E Y  L O C A T I O N S  D E T E R M I N A T I O N"
    if self.red: #and self.lr:
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


    "Q U A D R A N T  D E T E R M I N A T I O N"
    self.quandrantBottom = Rectangle((leftEdge, 0), (rightEdge, gameState.data.layout.height / 2))
    self.quandrantTop = Rectangle((leftEdge, gameState.data.layout.height / 2), (rightEdge, gameState.data.layout.height -1 ))

    "Q U A D R A N T  A S S I G N M E N T"
    pos = gameState.getAgentState(self.index).getPosition()


    #self.friend = min(3 + int(not self.red), 4 - self.index + 2 * int(not self.red))
    #nope, was agent 2 and red
    #assume 1 and 2 are red, and the layout / help are dumb
    #self.friend =  min(3 + int(not self.red), 3 - self.index + 4 * int(not self.red))
    #nope, this was 1, and 2, but 1 was blue for some reason
    #red is 0,2 derp....
    #help file conflicts
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

    self.myFood = sorted(self.initFood, key = lambda el: el[1])


    '''
    if self.top:
        self.myFood = self.myFood[len(self.myFood)/2: len(self.myFood)]
    else:
        self.myFood = self.myFood[0:len(self.myFood)/2]

    for el in self.initFood:
        if self.quandrantBottom.contains(el):
            print "Food is in Bottom Quadrant at ", el
            if not self.top:
                self.myFood += [el]
        elif self.quandrantTop.contains(el):
            print "Food is in Top Quadrant at ", el
            if self.top:
                 self.myFood += [el]
        else:
            print "Food is in neither quadrant at ", el
            self.myFood += [el]
    '''
    "I N I T I A L  F O O D  A S S I G N M E N T S "
    self.nextDist, self.nextDot, self.farDot = findFood(pos, self.myFood, gameState, distanceFn = self.getMazeDistance)  # use self.getMazeDistance
    # distance heuristic, nextDot, farDot
    self.getPosition = gameState.getAgentState(self.index).getPosition
    #self.atGoalState =  lambda gs: len(self.getFood(gs).asList()) == 0 ##revised at end

    #check to make sure my friend's next dot is not the same as mine
    #might just do a simple calc, and mini-max
    #self.myFood = sorted(self.myFood, key = lambda el: self.getMazeDistance(self.farDot, el), reverse=True)

    #self.closeQ, self.farQ = findFoodQ(pos, self.myFood, gameState, distanceFn = self.getMazeDistance)
    #self.friendCloseQ, self.friendFarQ = findFoodQ(friendPos, self.myFood, gameState, distanceFn = self.getMazeDistance)

    #self.closeQ = findClosestFoodQ(self.safeSpaces[-int(self.top)], self.myFood, gameState, distanceFn = self.getMazeDistance)
    #self.friendCloseQ = findClosestFoodQ(self.safeSpaces[-int(not self.top)], self.myFood, gameState, distanceFn = self.getMazeDistance)
    self.myFoodDic = {}
    self.hisFoodDic = {}
    [self.myFoodDic.update({el: self.getMazeDistance(self.safeSpaces[-int(self.top)], el)}) for el in self.initFood]
    [self.hisFoodDic.update({el: self.getMazeDistance(self.safeSpaces[-int(not self.top)], el)}) for el in self.initFood]

    maxDist = 0
    dotToRemove = self.myFood[-1]

    for el in self.myFoodDic.keys():
        dist = self.myFoodDic[el]
        if dist > maxDist:
            dotToRemove = el
            maxDist = dist
        if el in self.hisFoodDic:
            if self.hisFoodDic[el] < self.myFoodDic[el]:
                self.myFoodDic.pop(el)

    try:
        self.myFoodDic.pop(dotToRemove)
    except:
        print "Dot", (dotToRemove), "already removed"

    print "REMOVED DOT" , dotToRemove, "at distance", maxDist
    self.myFood = self.myFoodDic.keys()
    print "MY Food is", self.myFood
    #still should remove far dot
    '''
    while len(self.closeQ.heap) > 2:
        mine = self.closeQ.pop()
        his =  self.friendCloseQ.pop()
        self.myFoodDic.update({mine[0]: mine[1]})  #tuple of food coord, distance
        self.hisFoodDic.update({his[0]: his[1]})
        if his in self.myFoodDic:
            if his[1] < self.myFoodDic[his]:
                self.myFoodDic.pop(his)

        if mine in self.hisFoodDic:
            if mine[1] < self.hisFoodDic[mine]:
                self.hisFoodDic.pop(mine)

    self.myFood = self.myFoodDic.keys()

    self.hisFood = self.hisFoodDic.keys()
    '''

    start = time.time()
    self.moves = aStarSearch(self, gameState, heuristic = baseHeuristic) # alternateStart = self.safeSpaces[-int(self.top)])
    print 'eval time for moves: %.4f' % (time.time() - start)
    print "Optimal Moves: ", self.moves

    "D E B U G G I N G"
    print "Coloring the bottom quadrant corners red"
    self.debugDraw([(leftEdge,0), (rightEdge, gameState.data.layout.height / 2)], [1,0,0], clear=False)

    print "Coloring the top quadrant green"
    self.debugDraw([(leftEdge,gameState.data.layout.height / 2), (rightEdge, gameState.data.layout.height - 1)], [0,1,0], clear=False)

    print "Coloring my safe column white"
    self.debugDraw([(self.safeColumn, el) for el in xrange(0, gameState.data.layout.height)], [1,1,1], clear=False)

    print "Coloring my safe spaces", self.safeSpaces, "blue"
    self.debugDraw(self.safeSpaces, [0,0,1], clear=False)


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    while self.moves:
        if self.getFood(gameState).asList() <=2:
            moves = None
            break
        move = self.moves[0]
        self.moves = self.moves[1:]
        print "Using predetermined move:", move
        return move

    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    #foodLeft = len(gameState.getRedFood().asList())  #this looks off
    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      print "Time to go home! ", foodLeft, "dots remaining"
      pos = gameState.getAgentState(self.index).getPosition()
      localbestDist = 9999
      dest = self.start
      bestDest = dest
      dist = self.getMazeDistance(dest,pos)

      for el in xrange(-2,4):
        try:
          idx = self.safeSpaces.index((self.safeColumn, pos[1] + el))
          dest = self.safeSpaces[idx]
          dist = self.getMazeDistance(dest,pos)
          #print "possible destination at", dest
        except ValueError:
            print "X: ", (self.safeColumn, pos[1] + el), "not valid destination"
        print "Current destination to check at ", dest, "at dist:", dist

        if dist < localbestDist:
          localbestDist = dist
          bestDest = dest

      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        #dist = self.getMazeDistance(self.start,pos2)
        dist = self.getMazeDistance(bestDest,pos2)

        if dist < bestDist:
              bestAction = action
              bestDist = dist

      print "Found optimal safe space at", bestDest , "with dist", bestDist, "coloring spot now"
      print "Agent ", self.index, "Going", bestAction, "\n"
      self.debugDraw([bestDest], [1,1,0], clear=False)

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

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)#self.getScore(successor)
    myFood = []

    for el in foodList:
        if self.quandrantTop.contains(el) and not self.top:
          continue
          #myFood += [el]
        elif self.quandrantBottom.contains(el) and self.top:
          continue
          #myFood += [el]
        else:
          myFood += [el]
    # Compute distance to the nearest food
    if len(myFood) <= len(foodList) / 5 + 2:
        myFood = foodList

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      distances = [self.getMazeDistance(myPos, food) for food in myFood]
      distances.sort()
      minDistance =  distances[0]


      features['distanceToFood'] = minDistance
      if len(distances) > 1:
           features['distanceToFood'] += .5 * distances[-2]

      if self.top and self.quandrantTop.contains(myPos):  #can't be just on off, needs to be a function
           features['inQuad'] = self.quandrantTop.center[1] + self.quandrantTop.height / 2 - myPos[1]

      if not self.top and self.quandrantBottom.contains(myPos):
           features['inQuad'] =  myPos[1] - self.quandrantBottom.center[1] - self.quandrantTop.height / 2

      if action == Directions.STOP: features['stop'] = 1
      rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]

      if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'stop': -500, 'reverse': -1}#'inQuad': -.25} #500 fails for alley and office

class Rectangle():
    def __init__(self, xy1, xy2):
        self.height = abs(xy2[1] - xy1[1])
        self.width  = abs(xy2[0] - xy1[0])
        self.center = (float(xy2[0] + xy1[0])/2, float(xy2[1] + xy1[1])/2)
    def area(self):
        return self.height * self.width
    def contains(self, point):
        wx = self.center[0] - float(self.width)/2 <= point[0] and  self.center[0] + float(self.width)/2 >= point[0]
        wy = self.center[1] - float(self.height)/2 <= point[1] and  self.center[1] + float(self.height)/2 >= point[1]
        return wx and wy

def euc(xy1,xy2):
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

def man(xy1, xy2):
     return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
'''
def debugDraw(self, cells, color, clear=False):
Draws a colored box on each of the cells you specify. If clear is True, will clear all old drawings before drawing on the specified cells. This is useful for debugging the locations that your code works with. color: list of RGB values between 0 and 1 (i.e. [1,0,0] for red) cells: list of game positions to draw on (i.e. [(20,5), (3,22)])
'''


def findFood(pos, myFood, gameState, distanceFn = man):  # use self.getMazeDistance

    from collections import OrderedDict

    fg = myFood
    print "fg as: ", fg
    if len(fg) == 0:
        return 0
    elif len(fg) == 1:
        return man(pos, fg[0])

    unvisited = OrderedDict((el, el) for el in fg)

    farDist = 0
    farCoord = unvisited.keys()[0]

    print "Position: ", pos, "Far Distance testing with", farCoord

    while unvisited:
        dot = unvisited.keys()[0]
        dist = distanceFn(pos, dot)
        unvisited.pop(dot)
        if dist > farDist:
              farDist = dist
              farDot = dot
              farId = fg.index(farCoord)

    ####this bit finds the true two farthest
    unvisitedX = OrderedDict((el, el) for el in fg)
    farNeighDist = 0

    unvisitedX.pop(farCoord)

    while unvisitedX:
        dotX = unvisitedX.keys()[-1]
        dist = distanceFn(farDot, dotX)
        unvisitedX.pop(dotX)
        if dist > farNeighDist:
              farNeighDist = dist
              nextDot = dotX

    #print "Tested maze distances:", test
    #print "Farthest Food dot at : ", fg[farId]
    ##print "displaying the max manhattan distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "displaying the max maze distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "Distance between ", pos, "and ", fg[farId], "is ", farDist

    closeDist = distanceFn(pos, nextDot)

    print "pacman's distance to farthest dot (ignored): ", farDist
    print "farthest distance between two dots relative to pacman: ", farNeighDist
    print "Next dot to eat:", nextDot, "at distance:", closeDist
    return [farNeighDist, nextDot, farDot]


def findFoodQ(pos, myFood, gameState, distanceFn = man):  # use self.getMazeDistance
    '''
    Returns two Priority Queues of Dots and Distances
    [nextDotQ, farDotQ]
    [ [((1,2), 4)...], [((12,10), 30)...]
    '''

    from collections import OrderedDict

    fg = myFood
    print "fg as: ", fg
    if len(fg) == 0:
        return [0] * 3
    elif len(fg) == 1:
        return [ [(fg[0], man(fg[0], pos))], [(fg[0], man(fg[0], pos))] ]

    unvisited = OrderedDict((el, el) for el in fg)

    farDist = 0
    farCoord = unvisited.keys()[0]
    farDotQ = util.PriorityQueue()

    print "Position: ", pos, "Far Distance testing with", farCoord

    while unvisited:
        dot = unvisited.keys()[0]
        dist = distanceFn(pos, dot)
        unvisited.pop(dot)
        farDotQ.push((dot, dist), float(1)/(dist+1))
        if dist > farDist:
              farDist = dist
              farDot = dot
              farId = fg.index(farCoord)

    ####this bit finds the true two farthest
    unvisitedX = OrderedDict((el, el) for el in fg)
    farNeighDist = 0
    closeDotQ = util.PriorityQueue()
    unvisitedX.pop(farCoord)

    while unvisitedX:
        dotX = unvisitedX.keys()[-1]
        dist = distanceFn(farDot, dotX)
        unvisitedX.pop(dotX)
        closeDotQ.push((dotX, dist), float(1)/(dist+1))
        if dist > farNeighDist:
              farNeighDist = dist
              nextDot = dotX


    #print "Tested maze distances:", test
    #print "Farthest Food dot at : ", fg[farId]
    ##print "displaying the max manhattan distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "displaying the max maze distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "Distance between ", pos, "and ", fg[farId], "is ", farDist

    closeDist = distanceFn(pos, nextDot)

    print "pacman's distance to farthest dot (ignored): ", farDist
    print "farthest distance between two dots relative to pacman: ", farNeighDist
    print "Next dot to eat:", nextDot, "at distance:", closeDist
    return [closeDotQ, farDotQ]


def findClosestFoodQ(pos, myFood, gameState, distanceFn = man):  # use self.getMazeDistance
    '''
    Returns Priority Queue of closest dots
    [farDotQ]
    [ [((1,2), 4)...], [((12,10), 30)...]
    '''

    from collections import OrderedDict

    fg = myFood
    print "fg as: ", fg
    if len(fg) == 0:
        return [0] * 3
    elif len(fg) == 1:
        return [ [(fg[0], man(fg[0], pos))] ]

    unvisited = OrderedDict((el, el) for el in fg)

    farDist = 0
    farCoord = unvisited.keys()[0]
    closeDotQ = util.PriorityQueue()

    print "Position: ", pos, "Far Distance testing with", farCoord

    while unvisited:
        dot = unvisited.keys()[0]
        dist = distanceFn(pos, dot)
        unvisited.pop(dot)
        closeDotQ.push((dot, dist), float(1)/(dist+1))
        if dist > farDist:
              farDist = dist
              farDot = dot
              farId = fg.index(farCoord)


    print "pacman's distance to farthest dot (ignored): ", farDist
    return closeDotQ
'''

def baseHeuristic(node, myFood, gameState, distanceFn =  ReflexCaptureAgent.getMazeDistance):
    dis, close, far = findFood(node.getLastState(), myFood, gameState, distanceFn)
    return dis
'''

def baseHeuristic(node, myFood, gameState, distanceFn = 1):
    print "Passed in", myFood
    if not myFood:
        return 0

    unvisited = {}
    for el in myFood:
      unvisited.update({el: False})

    for visit in node.getStates():
        if visit in unvisited:
            print "Found dot:", visit
            unvisited.pop(visit)

    print "Visited:", node.getStates()

    return len(unvisited)

def aStarSearch(agent, gameState, heuristic = baseHeuristic, alternateStart = False):
    """Search the node that has the lowest combined cost and heuristic first."""
    if not alternateStart:
       start = agent.getPosition()
    else:
       start = alternateStart
    closed = {}
    closed2 = {}
    closed3 = {}
    fringe = util.PriorityQueue()
    fringe.push(Node([start], []), 0) #PriorityQueue.push(item, priority)

    while True:
        if fringe.isEmpty():
            print "Fringe is empty"
            return None
        node = fringe.pop()
        state = node.getLastState()
        "Why can't I use is node in closed???"

        key = state
        if state.__class__ == dict:
            key = stateToTuple(state)
        #print state
        if agentAtGoalState(agent, gameState, node.getStates(), fg = agent.myFood): #agent.atGoalState(gameState):
          print "reached cutoff of less than", len(agent.initFood) / 5, "food"
          return node.getDir()

        if key not in closed or node.hCost < closed[key]:
            closed.update({key: node.hCost})
            actions = gameState.getLegalActions(agent.index)
            #sucs = [ Actions.directionToVector(action) for action in actions ]
            #sucs = zip(sucs.getAgentPosition(agent.index), actions)
            #sucs = agent.getSuccessors(state)
            sucs = getSuccessorsAlt(gameState, state)
            #print "walls at", gameState.data.layout.walls.asList()
            #print "Possible moves: ", sucs
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            for child in sucs:
                actionList = node.getDir() + [ child[1] ]
                modnode = node.addNodeImmutable( child[0], child[1], getCostOfActions(gameState, start, actionList) )
                #addNode will add the new action and state, and then recalculate input cost
                #the getCost() of the returned node will be updated
                #h = heuristic(modnode.getLastState(), agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                h = heuristic(modnode, agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                g = modnode.getCost()
                modnode.hCost = h
                print "Heuristic cost at", h, "; Step cost at", g, "from ", start, "\n"
                fringe.push(modnode, h + g )

        elif (node.states[-2], node.states[-1]) not in closed2 or node.hCost < closed2[(node.states[-2], node.states[-1])] :
            closed2.update({(node.states[-2], node.states[-1]): node.hCost})
            actions = gameState.getLegalActions(agent.index)
            #sucs = [ Actions.directionToVector(action) for action in actions ]
            #sucs = zip(sucs.getAgentPosition(agent.index), actions)
            #sucs = agent.getSuccessors(state)
            sucs = getSuccessorsAlt(gameState, state)
            #print "walls at", gameState.data.layout.walls.asList()
            #print "Possible moves: ", sucs
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            for child in sucs:
                actionList = node.getDir() + [ child[1] ]
                modnode = node.addNodeImmutable( child[0], child[1], getCostOfActions(gameState, start, actionList) )
                #addNode will add the new action and state, and then recalculate input cost
                #the getCost() of the returned node will be updated
                #h = heuristic(modnode.getLastState(), agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                h = heuristic(modnode, agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                g = modnode.getCost()
                modnode.hCost = h
                print "Heuristic cost at", h, "; Step cost at", g, "from ", start, "\n"
                fringe.push(modnode, h + g )

        elif (node.states[-3], node.states[-2],node.states[-1]) not in closed3 or node.hCost< closed3[(node.states[-3], node.states[-2],node.states[-1])]:
            closed3.update({(node.states[-3], node.states[-2], node.states[-1]): node.hCost})
            actions = gameState.getLegalActions(agent.index)
            #sucs = [ Actions.directionToVector(action) for action in actions ]
            #sucs = zip(sucs.getAgentPosition(agent.index), actions)
            #sucs = agent.getSuccessors(state)
            sucs = getSuccessorsAlt(gameState, state)
            #print "walls at", gameState.data.layout.walls.asList()
            #print "Possible moves: ", sucs
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            for child in sucs:
                actionList = node.getDir() + [ child[1] ]
                modnode = node.addNodeImmutable( child[0], child[1], getCostOfActions(gameState, start, actionList) )
                #addNode will add the new action and state, and then recalculate input cost
                #the getCost() of the returned node will be updated
                #h = heuristic(modnode.getLastState(), agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                h = heuristic(modnode, agent.myFood, gameState, distanceFn = agent.getMazeDistance)
                g = modnode.getCost()
                modnode.hCost = h
                print "Heuristic cost at", h, "; Step cost at", g, "from ", start, "\n"
                fringe.push(modnode, h + g )

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
            if gameState.data.layout.walls[x][y]: return 999999
            cost += 1 #self.costFn((x,y))
        return cost


class Node:
    def __init__(self, states =[], directions = [], cost = 0):
        """
        :param states: an array containing objects of state
        :param directions: an array containing North, East, South, West, or Stop directions
        :param cost: an integer representing the cost of directions
        :return: a node
        """
        self.states = states
        self.directions = directions
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

    def addDir(self, direction):
        self.directions += [direction]

    def sillyCost(actions):
        return 1

    def addNodeImmutable(self, state, dir, cost ):
        s = self.states[:]
        d = self.directions[:]
        c = self.cost
        output = Node(s,d, c)
        #for lists if you reference one list to a second, the second is a pointer, not a copy, use slice for lists
        #dir = getCorrespondingMove(self.getLastState(), state)
        output.addState(state)
        output.addDir(dir)
        #print output.getDir()
        output.cost = cost
        return output

def agentAtGoalState(agent, gameState, positions, fg = None):
    if not fg:
        fg = agent.getFood(gameState).asList()
    unvisited = {}
    for el in fg:
      unvisited.update({el: False})

    for visit in positions:
        if visit in unvisited:
            unvisited.pop(visit)

    #return len(unvisited) == 0
    #print "There are", len(unvisited), "dots remaining", "cutoff is ", len(agent.initFood) / 5
    return len(unvisited) < len(agent.initFood) / 5 + 1



def stateToTuple(dict):
    """
    :param dict: a dictionary with key value pairs
    :return: values in the dictionary as a tuple

    NOTE state is currently passed in as [{'visited': [False, False, False, False], 'pos': (5, 1)}]
    """
    val = dict.values()
    if not val:
        print "Dictionary Length is 0"
        return None
    res = tuple(val[0])
    for i in xrange(1, len(val)):
        tmp = tuple(val[i])
        res = tuple((res, tmp))
    return res


