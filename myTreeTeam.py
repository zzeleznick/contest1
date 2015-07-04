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


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'TreeAgent', second = 'TreeAgent'):
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

class TreeAgent(CaptureAgent):
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
    print 'eval time for moves: %.4f' % (time.time() - start)


    "D E B U G G I N G"
    print "Coloring my safe column white"
    self.debugDraw([(self.safeColumn, el) for el in xrange(0, gameState.data.layout.height)], [1,1,1], clear=False)

    print "Coloring my safe spaces", self.safeSpaces, "blue"
    self.debugDraw(self.safeSpaces, [0,0,1], clear=False)


    ##self.getPosition = gameState.getAgentState(self.index).getPosition
    ##self.getFriendPosition = gameState.getAgentState(self.friend).getPosition
    self.counter = 0
    self.moves = []
    self.intendedCoords =[]
    self.best = None

  def evaluate(self, gameState, state, directions):
        fg = self.getFood(gameState).asList()
        #print "Passed in Directions: ", directions
        if not directions:
            return len(fg)

        unvisited = {}
        x,y =  gameState.getAgentState(self.index).getPosition() # self.getPosition() NONONONO This doesn't update auto
        myPositions = { (x,y): True }
        #print "Started at", (x, y)
        for action in directions[0]:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            myPositions.update({ (x,y) : True })

        x, y = gameState.getAgentState(self.friend).getPosition()
        hisPositions = { (x,y): True }
        #print "Started at", (x, y)
        for action in directions[1]:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            hisPositions.update({ (x,y) : True })

        for el in fg:
            unvisited.update({el: False})

        count = len(fg)
        #print "len of fg", count
        for dot in fg:
            if dot in myPositions or dot in hisPositions:
                #print "Visited ", dot
                count -= 1
                unvisited.pop(dot)

        '''
        if count <= 5:
            score = [self.getMazeDistance(state[0], dot) for dot in unvisited]
            homeDist = min ([self.getMazeDistance(state[0], space) for space in self.safeSpaces ])
            score = - (min(score) + homeDist) - count * 50 - 3 * len(myPositions)
            return score
        '''

        if count <= 2:
            homeDist = min ([self.getMazeDistance(state[0], space) for space in self.safeSpaces ])
            homeDist2 = min ([self.getMazeDistance(state[1], space) for space in self.safeSpaces ])
            score = - (homeDist + homeDist2) - 2 * len(myPositions)
            return score

        score = [self.getMazeDistance(state[0], dot) for dot in unvisited]
        score2 = [self.getMazeDistance(state[1], dot) for dot in unvisited]
        #print "Distances:", score
        #res = map(lambda x: count * x, score)
        #print "Food Left", count
        #return -min(res)
        res = - (min(score2) + min(score)) - count * 100 -  2* len(myPositions)
        #res = - (min(score)) - count * 100 - 3 * len(myPositions)
        return res
        #return - (count + len(myPositions) + len(hisPositions) )
        #return len(unvisited)

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
    if self.counter == 0:
        print "Calculating 60 moves ", "as player", self.index, "from ", gameState.getAgentPosition(self.index)
        print "Cached value"
        self.best =  self.ActionLoop(gameState)
        self.moves =  self.best.getDir()[1]
        if len(self.getFood(gameState).asList()) <= 2:
            print "plan terminated with", len(self.getFood(gameState).asList()), "dots left"

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
            for pos2, action, cost in getSuccessorsAlt(gameState, pos):
                dist = self.getMazeDistance(bestDest,pos2)
                if dist < bestDist:
                  bestAction = action
                  bestDist = dist

            print "Found optimal safe space at", bestDest , "with dist", bestDist, "coloring spot now"
            print "Agent ", self.index, "Going", bestAction, "\n"
            self.debugDraw([bestDest], [1,1,0], clear=False)
            return bestAction

        if not self.moves or len(self.moves) == 0:
            print "Tried to play move, but ran Out of Moves!!!"
            actions = gameState.getLegalActions(self.index)
            return random.choice(actions)
        self.intendedCoords =  self.best.state[0]
        self.counter = 60
    try:
        move = self.moves[60 - self.counter]
        self.counter -= 1
    except:
        print "Tried to access index", 60 - self.counter, "in list of length", len(self.moves), "more moves now generated"
        actions = gameState.getLegalActions(self.index)
        self.counter = 0
        return random.choice(actions)
    print "On move ", 60 - self.counter, "as player", self.index, "going", move, "from", gameState.getAgentPosition(self.index)
    return move




  def ActionLoop(self, gameState):
    maxDepth = 100
    start = time.time()
    levelDic = {}
    closed = {}
    expanded = 0
    popped = 0
    reborn = 0
    zobmies = 0
    killedZombies = 0
    fringe = util.PriorityQueue()
    root = Node((gameState.getAgentState(self.index).getPosition(), gameState.getAgentState(self.friend).getPosition()), evalFn = self.evaluate, gameState = gameState)

    fringe.push(root, -root.getScore())  #least to greatest (use negative scores)
    while len(fringe.heap) != 0:
        node = fringe.pop()
        popped += 1
        if node.getState() not in closed:  #could do just the position? // 10,10 -> 11,10 -> 11,11 <- 10,11 <-  10,10  want to prune more
            if node.depth not in levelDic:
                levelDic.update({node.depth: node })
            elif node.depth in levelDic: #have we explored this depth already?
              if node.getScore() > levelDic[node.depth].getScore():
                  levelDic.update({node.depth: node })
                  if node.doomed:
                      node.doomed = False  #reborn!!!
                      reborn +=1
                      node.lives = root.lives
              else:
                #print "considered pruning here"
                node.doomed = True
                zobmies +=1
                if node.lives == 0:
                    killedZombies +=1
                    continue

            closed.update({node.getState(): True})
            if node.depth == maxDepth:
                continue
            node.addDoomedChildren(node.doomed)
            expanded += 4
            for child in node.getChildren():
                fringe.push(child, -child.getScore())

    print '\neval time for pruned tree is: %.4f' % (time.time() - start)
    print 'Expanded Nodes: ', expanded
    print 'Popped Nodes from Fringe: ', popped
    print 'Allowed zombies to roam:' , zobmies
    print ' | Reborn:' , reborn, " | Killed:", killedZombies, " |", "Lives: ", root.lives, '|'
    try:
        #bestDeepNode = levelDic[maxDepth]
        nodes = levelDic.values()
        bestNodes = sorted(nodes, key = lambda node: node.getScore())
        best = bestNodes[-1]
        if not best.parent:
            try:
                bestDeepNode = bestNodes[-2]
            except:
                print "Root is max"
                return None
    except:
        print "Bad Optimization"
        bestDeepNode = levelDic[max(levelDic.keys())]


    print 'Final Destination at ',  bestDeepNode.getState(), "of depth", bestDeepNode.depth, "with score",  bestDeepNode.getScore()
    print 'Optimal moves found to be: ',  bestDeepNode.getDir()
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

    firstMove = bestDeepNode.getDir()[1][0]
    print "Going ", firstMove, "towards ", bestDeepNode.getState()
    #return firstMove
    return bestDeepNode


class Node:
    def __init__(self, state, directions = None, parent = None, evalFn = None, gameState = None):
        """
        :param states: an array containing objects of state
        :param directions: an array containing North, East, South, West, or Stop directions
        :param cost: an integer representing the cost of directions
        :return: a node
        """

        self.state = state  #  ( (10,0), (11,0)  ) -- > ( ( (10,0), (11,0) ), score )
        #self.directions = directions  [ ['N', 'S'], ['S']]
        self.parent = parent

        if self.parent:
            self.depth = parent.depth + 1
            self.firstActor = self.depth % 2 == 0
            self.parentState = parent.state
            if parent.directions:
                self.directions = copy.deepcopy(parent.directions)
                if self.firstActor:
                    self.directions[0] +=  [ directions ]
                else:
                    self.directions[1] +=  [ directions ]
            else:
                self.directions = [ [] , [directions] ]
        else:
            self.depth = 0
            self.firstActor = True
            self.parentState = None
            self.directions =  directions


        self.doomed = False
        self.lives = 7

        self.evalFn = evalFn
        self.score = self.evalFn(gameState, state, self.directions)
        self.state = (self.state, self.score) # ( ( (10,0), (11,0) ), score )

        self.children = None

        self.gameState = gameState


    def getState(self):
        return self.state

    def getDir(self):
        return self.directions

    def getScore(self):
        return self.score

    def addDir(self, direction):
        self.directions += [direction]

    def addChildren(self):
        if self.firstActor:
            #note that get successors returns ((5,4) 'South', 1) --> direction encoded
            childStates = getSuccessorsAlt(self.gameState, self.state[0][0])
            #print "Possible child states for",  self.state[0][0], "are:", childStates
            childNodes = [ Node((el[0],self.state[0][1]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            self.children = childNodes
        else:
            childStates = getSuccessorsAlt(self.gameState, self.state[0][1])
            #print "Possible child states for",  self.state[0][1], "are:", childStates
            childNodes = [ Node((self.state[0][0], el[0]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            self.children = childNodes

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
            childNodes = [ Node((self.state[0][0], el[0]), el[1], self, self.evalFn, self.gameState) for el in childStates]
            for node in childNodes:
                node.lives= node.parent.lives - 1
            if doomed:
                for node in childNodes:
                    node.lives= node.parent.lives - 1
            self.children = childNodes



    def getChildren(self):
        if self.children:
            return self.children

    def getChildrenStates(self):
        if self.getChildren():
            return [child.getState() for child in self.getChildren()]



def agentsAtGoalState(agent, gameState, positions, fg = None):
    if not fg:
        fg = agent.getFood(gameState).asList()
    unvisited = {}
    for el in fg:
      unvisited.update({el: False})

    for visit in positions:
        if visit in unvisited:
            unvisited.pop(visit)


    myPos = gameState.getAgentState(agent.index).oition()
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
              cost = 1
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

'''
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
'''
'''
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

'''
def euc(xy1,xy2):
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

def man(xy1, xy2):
     return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
'''
def debugDraw(self, cells, color, clear=False):
Draws a colored box on each of the cells you specify. If clear is True, will clear all old drawings before drawing on the specified cells. This is useful for debugging the locations that your code works with. color: list of RGB values between 0 and 1 (i.e. [1,0,0] for red) cells: list of game positions to draw on (i.e. [(20,5), (3,22)])
'''