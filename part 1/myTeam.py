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
import game
from util import nearestPoint

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

    self.myFood = []

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

    "I N I T I A L  F O O D  A S S I G N M E N T S "


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

    '''
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
    '''
    myFood = foodList
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      distances = [self.getMazeDistance(myPos, food) for food in myFood]
      distances.sort()
      minDistance =  distances[0]
      features['distanceToFood'] = minDistance

      '''
      if len(distances) > 2:
           features['distanceToFood'] +=  .5 * distances[-3]
    '''

      '''
      if self.top and self.quandrantTop.contains(myPos):  #can't be just on off, needs to be a function
           features['inQuad'] = self.quandrantTop.center[1] + self.quandrantTop.height / 2 - myPos[1]

      if not self.top and self.quandrantBottom.contains(myPos):
           features['inQuad'] =  myPos[1] - self.quandrantBottom.center[1] - self.quandrantTop.height / 2
      '''
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

    unvisited = {}
    '''
    for el in fg:
        unvisited.update({el: el})
    '''
    unvisited = OrderedDict((el, el) for el in fg)

    farDist = 0
    test = []
    farCoord = unvisited.keys()[0]
    print "Position: ", pos, "Far Distance testing with", farCoord

    while unvisited:
        node = distanceFn(pos, unvisited.keys()[0], gameState)
        #print "node as ", node
        for el in node:
            #print "first traveled as", el
            if  el in fg: #foodGrid[el[0]][el[1]]: #was there originally food there? O(1) #TODO use dict instead of list
              try:
                  unvisited.pop(el)
              except KeyError:
                  "print already visited, ", el
        tmp = len(node)
        #should remove self
        #print tmp
        if tmp > farDist:
              test += [tmp]
              farDist = tmp - 1 #includes start and end length
              farCoord = node[-1]
              farId = fg.index(farCoord)

    ####this bit finds the true two farthest
    unvisitedX = OrderedDict((el, el) for el in fg)
    farNeighDist = 0

    unvisitedX.pop(farCoord)

    while unvisitedX:
        node = distanceFn(farCoord, unvisitedX.keys()[-1],gameState)
        #print "node as ", node
        for el in node:
            #print "first traveled as", el
            if el in fg:    #foodGrid[el[0]][el[1]]: #was there originally food there? O(1) #TODO use dict instead of list
              try:
                  unvisitedX.pop(el)
              except KeyError:
                  "print already visited, ", el
        tmp = len(node)  #this has all the states
        #should remove self
        #print tmp
        if tmp > farNeighDist:
              test += [tmp]
              farNeighDist = tmp - 1
              farNeighCoord = node[-1]

    #farNeigh, farNeighDist = g.getVertex(fg[farId]).getFarthestNeighborInfo()
    '''
    res = farDist
    '''
    #print "Tested maze distances:", test
    #print "Farthest Food dot at : ", fg[farId]#, "graph: ", g
    ##print "displaying the max manhattan distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "displaying the max maze distance to neighbor of the farthest dot from pacman:", farNeighDist
    #print "Distance between ", pos, "and ", fg[farId], "is ", farDist
    '''
    if farNeighDist > farDist:  #might always be true
       res = farNeighDist
       #print "Thus we can update the graph from", farDist, "to ", farNeighDist
    '''
    nextDot = distanceFn(pos, farNeighCoord, gameState)
    backdst = len(back) - 1
    #what about farNeigh + dist(pac, farNeigh)
    print "farthest dist to neigh: ", farNeighDist
    print "pacman distance distance from farthest neigh: ", backdst

    return backdst + farNeighDist