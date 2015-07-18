# curTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

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
    self.debugging = True
    self.stationaryTolerance = random.randint(6,16)

    "G A M E  K E Y  L O C A T I O N S  D E T E R M I N A T I O N"
    if self.red:
        leftEdge = gameState.data.layout.width / 2
        rightEdge =  gameState.data.layout.width - 2
        self.safeColumn = leftEdge - 2
        self.opSafeColumn = leftEdge + 2
    else:
        leftEdge = 1
        rightEdge = gameState.data.layout.width / 2
        self.safeColumn = rightEdge + 2
        self.opSafeColumn = rightEdge - 2

    self.safeSpaces = []
    self.opSafeSpaces = []
    for h in xrange(1,gameState.data.layout.height-1):
        if not gameState.data.layout.isWall((self.safeColumn, h)):
               self.safeSpaces += [(self.safeColumn, h)]
        if not gameState.data.layout.isWall((self.opSafeColumn, h)):
               self.opSafeSpaces += [(self.opSafeColumn, h)]

    print "Coloring my safe column white"
    self.debugDraw([(self.safeColumn, el) for el in xrange(0, gameState.data.layout.height)], [1,1,1], clear=False)

    print "Coloring my safe spaces", self.safeSpaces, "blue"
    self.debugDraw(self.safeSpaces, [0,0,1], clear=False)

  def findHome(self, pos, gameState):
      '''
      :param gameState:
      :param pos: position
      :return: The distance to closest safe space
      '''
      distToSafe = 9999
      dest = self.start
      bestDest = dest
      distToSafe = self.getMazeDistance(dest,pos)

      for space in self.safeSpaces:
        dist = self.getMazeDistance(space,pos)
        #print "Current destination to check at ", dest, "at dist:", dist
        if dist < distToSafe:
          distToSafe = dist
          bestDest = dest

      return distToSafe
      #print "Found optimal safe space at", bestDest , "with dist", bestDist, "coloring spot now"
      #print "Agent ", self.index, "Going", bestAction, "\n"
      #self.debugDraw([bestDest], [1,1,0], clear=False)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    foodLeft = len(self.getFood(gameState).asList())
    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)  #returns a configuration (direction, position
        pos2 = successor.getAgentPosition(self.index)
        dist = self.findHome(self, pos2, gameState)
        #self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction


    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    reversedAction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if reversedAction in bestActions:
        print "Hmmm"

    if len(bestActions) > 1:
        for action in bestActions:
            if action != Directions.STOP:
                return action
            else:
                if self.debugging:
                    print "Agent", self.index, "thinks stop is a good idea from pos", gameState.getAgentPosition(self.index)
                #if gameState.o
    if len(bestActions) == 1:
        #if bestActions[0] == Directions.STOP:
        if len(self.observationHistory) > self.stationaryTolerance:
            stationary = [False for i in xrange(1,self.stationaryTolerance) \
            if self.observationHistory[-i].getAgentPosition(self.index) != gameState.getAgentPosition(self.index)]

            if not False in stationary:
              #have we been staring at an offensive player head to head?
              self.stationaryTolerance = random.randint(6,16)  #reset tolerance and return move
              if not self.red and Directions.EAST in actions:
                  return Directions.EAST
              elif self.red and Directions.WEST in actions:
                  return Directions.WEST
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

  def trappedOpponent(self, pos, invaders, gameState):
    '''
    Returns true if this agent is closer to all of the opponent's safe spaces
    :param pos: our position
    :param invaders: invading enemies (a list)
    :param gameState:
    :return:
    '''
    ## assume at most we will be 6 away from the ghost we are trying to trap, and only count the closer one for now
    if len(invaders) == 0:
        return False  #should not be called otherwise

    closerInvader = invaders[0]
    sep = self.getMazeDistance(pos, closerInvader.getPosition())
    if self.getMazeDistance(pos, invaders[-1].getPosition()) < sep:
         closerInvader = invaders[-1]
         sep = self.getMazeDistance(pos, closerInvader.getPosition())

    #dest = closerInvader.start
    opPos = closerInvader.getPosition()
    #dist = self.getMazeDistance(dest, opPos)

    if self.debugging:
            print "* Agent ", self.index, "Examining if we are trapping an invader"
    for space in self.opSafeSpaces:
        if self.getMazeDistance(pos,space) >= self.getMazeDistance(opPos,space):
            return False
    if self.debugging:
            print "** Agent ", self.index, "Believes we have trapped opp located  at", opPos
    return True

  def trapped(self, pos, trapper, gameState):
    '''
    Returns true if this agent is closer to all of the opponent's safe spaces
    :param pos: our position
    :param trapper: identity of the opponent who is trapping us
    :param gameState:
    '''
    ## assume at most we will be 6 away from the ghost we are trying to trap, and only count the closer one for now
    opPos = trapper.getPosition()
    sep = self.getMazeDistance(pos, opPos)

    if self.debugging:
            print "* Agent ", self.index, "Examining if we have been trapped by enemy"
    for space in self.safeSpaces:
        if self.getMazeDistance(pos,space) < self.getMazeDistance(opPos,space):
            return False
    if self.debugging:
            print "** Agent ", self.index, "Believes we have been trapped opp located  at", opPos
    return True


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

    myPos = successor.getAgentState(self.index).getPosition()
    '''
    if action == Directions.STOP:
        features['actionPenalty'] = -.5
    '''
    numCarrying = gameState.getAgentState(self.index).numCarrying
    features['numCarrying'] = numCarrying

    distToSafe = self.findHome(myPos, gameState)
    features['distanceToSafe'] = distToSafe


    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None and successor.getAgentState(self.index).isPacman]
    features['ghostDistance'] = self.ghostsToFeatureScore(ghosts, myPos, action, gameState)

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance
    return features

  def ghostsToFeatureScore(self, ghosts, pos, action, gameState):
      '''
      Returns a score based on the distance from ghosts and current gameState
      :param ghosts: an array of enemies who are ghosts
      :param pos: our position
      :param gameState: the gamestate
      :return: a score
      '''
      ##assuming tight corridors, avoiding the ghost will be very tough
      '''
          .
        g. p .   g

        g

         .
        p


        g
         .|
         p|

      '''

      if len(ghosts) > 0:
         gtl = [(self.getMazeDistance(pos, a.getPosition()), a) for a in ghosts]
         if gtl[0][0] > gtl[-1][0]:
             tmp = gtl[0]
             gtl[0] = gtl[-1]
             gtl[-1] = tmp

         #GhostTupleList <- gtl (closest ghost that can hurt us
         closeGhost =  gtl[0][1]
         baseScore = min(-4 + gtl[0][0], 0)
         '''
             _____
             x_o._|

         '''
         oldPos = gameState.getAgentState(self.index).getPosition()

         if self.trapped(pos, closeGhost, gameState):
            #generally this is a very bad move
            baseScore -= 50
            if self.findHome(pos, gameState) < self.findHome(oldPos, gameState):
                baseScore += 1  #heading home
            else:
                # we are running away or stopping which seems futile
                pass
         else:
             if gtl[0][0] == 0:  #check to see if 1) ghost is scared  2) this is best option?
                 baseScore -= 100
             elif gtl[0][0] == 1:  #allow enemy to eat -- no!
                 baseScore -= 100
             elif gtl[0][0] <= 4:  #Here is the real challenge. Can we recognize our demise
                 pass
             else:   #ghost is 5 or more away
                 return 0

         if gtl[0][1].scaredTimer >= 5:
             # +.5 to head towards ghost if moving towards him from old pos
             if gtl[0][0] < self.getMazeDistance(oldPos, closeGhost):
               baseScore += .5

         return baseScore

      else:
          return 0


  def getWeights(self, gameState, action):
    weights = util.Counter()
    weights['successorScore'] = 100
    weights['distanceToFood'] = -1
    weights['actionPenalty'] = 1  #will prune stop from choose action


    '''
    # pac has eaten one dot and now must choose whether to eat more dots or return home
    # closest dot 3 away
    # safe is 3 away
    # ghost is 7 away from current pac
    # pac could go 3, eat the dot, ghost would be 4 away
    # chance that ghost blocks exit, or pac escapes depending on junction
    # would need to plan for worst case and recognize a cave
     ________
    | _____g_
    | |_____
    |p _.___|
    __|

     ________
    | _____g_
     p|____
    |  ____|
    _.|

    '''

    if gameState.getAgentState(self.index).numCarrying > 0:
        weights['distanceToSafe'] = -1  #changing from -1.5 for test
        weights['ghostDistance'] = 1 # default to feature score for ghostDistance; else keep at 0
    else:
        weights['ghostDistance'] = 1 # tried .5 and pac started running into ghosts
    return weights

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    #if myState.isPacman: features['onDefense'] = 0
    if self.red:
        if myPos > self.safeColumn:
            features['onDefense'] = 0
    else:
        if myPos < self.safeColumn:
            features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)

    if action == Directions.STOP: features['stop'] = 1

    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
      if gameState.getAgentState(self.index).scaredTimer >= 1:
          pass
          ## block other capsule? or just run away?

      ### Can I detect if I've trapped my opponent?
      if self.trappedOpponent(myPos, invaders, gameState):
          features['stop'] = -1  #100 point bonus (-1 * -100)
          ## NOTE: This also rewards trapping with an action like west since the bonus is activated
          ##  Suppose we have trapped opponent at 2 away, do we go left, down or stay?
          ##  We would want to minimize distance, and could go either way, but the second move matters greatly
          ##  Here, for b1 and b2, we can only get our bonus if we block the exit
          ##  Moving towards the exit will also reduce our distance (win)
          '''
          case a.  (Our turn)
           _____
          | o __
          |x |

          case b1.
           _____
          |o  __
          | x|

          case b2.
           _____
          |x  __
          | o|


          '''

    else:  #allow reverse when there are invaders at no penalty
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        capsules = self.getCapsulesYouAreDefending(gameState)
        if len(capsules) > 0:
            dists = [self.getMazeDistance(myPos, c) for c in capsules]
            features['capsuleDistance'] = min(dists)
            if action == Directions.STOP: features['stop'] = 0 ##allow squatting


    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'capsuleDistance': -10, 'stop': -100, 'reverse': -2}


'''
          BIG QUESTION:
             If pacman is pinned, should he move towards closest path to home or try a different path?

          case 1a.
          ___________
          1_g___p____|  pacman is trapped. pacman should proceed towards safe space
                        CLOSE EXIT

          case 1b.
          __
          1 |_______    pacman has close exit blocked (1), but he can get to exit 2 faster than ghost
          |_g_p__  |    Risky move to go close if ghost is behaving optimally, however could backtrack if ghost is not pursuing
           ______| |    FAR EXIT
          2________|

          case 1c.
          __
           1|_______    pacman has close exit blocked (1), and he cannot get to exit 2 faster than ghost
            g_p__  |    Could go towards ghost and exit, could try to wait it out at the halfway point
           |_____| |
          _2_______|    ???

          **Becomes more complex with 2 ghosts**

          case 2a.
          ___________
          1_g___p__g_|  pacman is trapped. pacman should proceed towards the exit and die
                        CLOSE EXIT

          case b.
          __
          1 |_______    pacman has close exit blocked (1) by close ghost, he can get to exit 2 faster than close ghost
          |_g_p__  |    but the far exit is blocked by the far ghost
           ______|g|    If the far ghost or close ghost is not acting optimally, small chance of escape
          2________|    Should go towards a non-pursuing ghost or exit, branch point also big factor
                        *** Also if capsule accessible ***
                        ** Set a flag for isTrapped **
                        EXIT


          When does pacman decide to face defeat vs attempt run away?
          1. Pacman should find his closest safe space.  <-- ideally escape route (safe space -> path)
          2. If the ghost is blocking that escape route (e.g. ghost is closer): find next closest escape route
          2b. Check if capsule in range

               ?????

'''