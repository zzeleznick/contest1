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
from game import Directions, Actions
import game
from util import nearestPoint
from capture import AgentRules

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
    self.debugging = False
    self.stationaryTolerance = random.randint(6,16)
    self.depth = 6
    self.bestFood = None
    self.bestFoodDist = 0

    "G A M E  K E Y  L O C A T I O N S  D E T E R M I N A T I O N"
    if self.red:
        leftEdge = gameState.data.layout.width / 2
        rightEdge =  gameState.data.layout.width - 2
        self.safeColumn = leftEdge - 1
        self.opSafeColumn = leftEdge
    else:
        leftEdge = 1
        rightEdge = gameState.data.layout.width / 2
        self.safeColumn = rightEdge
        self.opSafeColumn = rightEdge - 1

    self.safeSpaces = []
    self.opSafeSpaces = []
    for h in xrange(1,gameState.data.layout.height-1):
        if not gameState.data.layout.isWall((self.safeColumn, h)):
               self.safeSpaces += [(self.safeColumn, h)]
        if not gameState.data.layout.isWall((self.opSafeColumn, h)):
               self.opSafeSpaces += [(self.opSafeColumn, h)]

    if self.debugging:
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

      for space in self.safeSpaces:
        dist = self.getMazeDistance(space,pos)
        #print "Current destination to check at ", dest, "at dist:", dist
        if dist < distToSafe:
          distToSafe = dist

      return distToSafe
      #print "Found optimal safe space at", bestDest , "with dist", bestDist, "coloring spot now"
      #print "Agent ", self.index, "Going", bestAction, "\n"
      #self.debugDraw([bestDest], [1,1,0], clear=False)

  def maxValues(self, state, action, minAgentId, depth, FIRST_CALL = False):
        if depth > self.depth:
        #if state.isWin() or state.isLose() or depth > self.depth:
            return self.evaluate(state, action, minAgentId)
        if FIRST_CALL: actions = [action]
        else: actions = state.getLegalActions(self.index)
        nextActionStatePairs = [ (state.generateSuccessor(self.index, a), a) for a in actions]
        #I suppose generate successor really does udate the gameboard...
        return max( [ self.minValues(s[0], s[1], minAgentId, depth + 1) for s in nextActionStatePairs] )


  def minValues(self, state, action, minAgentId, depth):
        if depth > self.depth:
        #if state.isWin() or state.isLose() or depth > self.depth:
            return self.evaluate(state, action, 7)  #since False == 0

        goodPos = state.getAgentPosition(self.index)
        opPos = state.getAgentPosition(minAgentId)
        sep = self.getMazeDistance(goodPos, opPos )
        if sep > 10:
            bestActions = [ random.choice(state.getLegalActions(minAgentId)) ]

        else:
            actions = state.getLegalActions(minAgentId)
            dist = 999
            bestActions = []
            for option in actions:
                nextGame = state.generateSuccessor(minAgentId, option)
                nextOpPos = nextGame.getAgentPosition(minAgentId)
                resgoodPos = nextGame.getAgentPosition(minAgentId)
                if self.getMazeDistance(goodPos, nextOpPos) < sep or resgoodPos == self.start:
                    bestActions += [option]

        if len(bestActions) == 0: #ooponent can only move away or die
            bestActions = [ random.choice(state.getLegalActions(minAgentId)) ]

        nextActionStatePairs = []
        nextActionStatePairs += [ (state.generateSuccessor(minAgentId, a), a) for a in bestActions]

        distancesToMe = [ (self.getMazeDistance(goodPos, ns[0].getAgentPosition(minAgentId)), ns) for ns in nextActionStatePairs]
        minDist = min(distancesToMe)[0]
        return min( [ self.maxValues(s[1][0], s[1][1], minAgentId, depth + 1) for s in distancesToMe if s[0] == minDist] )


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    foodLeft = self.getFood(gameState).asList()
    pos = gameState.getAgentState(self.index).getPosition()
    bestAction = random.choice(actions)
    if len(foodLeft) <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)  #returns a configuration (direction, position
        pos2 = successor.getAgentPosition(self.index)
        dist = self.findHome(pos2, gameState)
        if pos2 == self.start:
            dist += 900 #don't get killed!
            print "I am would have killed myself with action", action, "from position", gameState.getAgentPosition(self.index)
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None] #and successor.getAgentState(self.index).isPacman]
        try:
            minDistance = min([self.getMazeDistance(pos2, g.getPosition()) for g in ghosts])
        except:
            minDistance = 2
        if action == Directions.STOP:
            dist += .5

        if minDistance <= 1:
            dist += 100 #don't get killed!
            print "I am at risk to kill myself with action", action, "from position", gameState.getAgentPosition(self.index)
        if dist < bestDist:
          bestAction = action
          bestDist = dist

      return bestAction

    if self.getState() == 'OFFENSE':
        bestScore = -9999
        bestAction = actions[0]
        pos = gameState.getAgentPosition(self.index)
        enemyDists = [(self.getMazeDistance(pos, gameState.getAgentState(i).getPosition()), i) for i in self.getOpponents(gameState)]
        minDist, minAgentId = min(enemyDists)
        if minDist <= 4:
            for action in actions:
                score = self.maxValues(gameState, action, minAgentId, 0, FIRST_CALL = True)
                if score > bestScore:
                    bestScore = score
                    bestAction = action

            return bestAction
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    reversedAction = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if reversedAction in bestActions:
        if self.debugging:
            print "Hmmm. multiple best moves says", self.index, "including reverse"
        '''  ________
        exit ___p___.   possible scenario

        '''
    if self.getState() == 'OFFENSE': print "BEST ACTIONS ", bestActions
    if len(bestActions) > 1:
        newBestAction = bestActions[0]
        dist = 9999
        bestScore = -9999
        for option in bestActions:
             nextConfig = self.getSuccessor(gameState, option)  #returns a configuration (direction, position
             nextPos = nextConfig.getAgentPosition(self.index)

             if self.getState() == 'DEFENSE':
                 distToSafe = self.findHome(nextPos,gameState)
                 foodList = self.getFoodYouAreDefending(nextConfig).asList()
                 if len(foodList) > 0: # This should always be True,  but better safe than sorry
                    foodDist = min([self.getMazeDistance(nextPos, food) for food in foodList])
                 if distToSafe + .75 *foodDist <= dist:   # at a junction (e.g. go north or east)
                    dist = distToSafe + .75 *foodDist
                    newBestAction = option

             elif self.getState() == 'OFFENSE': #junction between going home or getting food
                #enemyDists = [(self.getMazeDistance(nextPos, gameState.getAgentState(i).getPosition()), i) for i in self.getOpponents(gameState)]
                #minAgentId = min(enemyDists)[1]
                #score = self.maxValues(gameState, option, minAgentId, 0, FIRST_CALL = True)
                distToSafe = self.findHome(nextPos,gameState)
                lastPos = gameState.getAgentPosition(self.index)
                preDistToSafe = self.findHome(lastPos,gameState)
                if distToSafe <  preDistToSafe and nextConfig.getAgentState(self.index).numCarrying > 0:
                    newBestAction = option  #head home
                elif len(foodLeft) > 0: # This should always be True,  but better safe than sorry
                    towardsFood = False
                    for food in foodLeft:
                        if self.getMazeDistance(nextPos, food) < self.getMazeDistance(lastPos, food):
                            towardsFood = True
                            newBestAction = option
                            print "Heading towards Food on Tie with action", option
                            break

        if self.getState() == 'OFFENSE': print "Chose ", newBestAction, "\n"
        return newBestAction

    if len(bestActions) == 1:
        #if bestActions[0] == Directions.STOP:
        if len(self.observationHistory) > self.stationaryTolerance and (self.getState() == 'OFFENSE'):
            stationary = [False for i in xrange(1,self.stationaryTolerance) \
            if self.observationHistory[-i].getAgentPosition(self.index) != gameState.getAgentPosition(self.index)]

            if not False in stationary:
              #have we been staring at an offensive player head to head?
              self.stationaryTolerance = random.randint(6,16)  #reset tolerance and return move
              if not self.red and Directions.EAST in actions:
                  return Directions.EAST
              elif self.red and Directions.WEST in actions:
                  return Directions.WEST

            revLoop = True
            for i in xrange(2,self.stationaryTolerance):
                 if self.observationHistory[-i].getAgentState(self.index).configuration.direction != Directions.REVERSE[self.observationHistory[-i+1].getAgentState(self.index).configuration.direction]:
                   revLoop = False
                   break

            if revLoop == True:
              #have we been staring at an offensive player head to head?
              self.stationaryTolerance = random.randint(6,16)  #reset tolerance and return move
              capsuleProgress = 0
              bestAction = random.choice(actions)
              lastPos = gameState.getAgentPosition(self.index)
              states = [ gameState.generateSuccessor(self.index, a) for a in actions ]
              for i in xrange(len(states)):
                  capsules = self.getCapsules(states[i])
                  if len(capsules) > 0:
                    curCapDist = min([ self.getMazeDistance(states[i].getAgentPosition(self.index), c) for c in capsules ])
                    preCapDist =  min([ self.getMazeDistance(lastPos, c) for c in capsules ])
                    if curCapDist < preCapDist:
                        capsuleProgress = 1
                        bestAction = actions[i]
                  else:
                       bestAction = actions[i]
                       break

              if self.getState() == 'OFFENSE': print "Chose ", bestAction, "\n"
              return bestAction

    res = random.choice(bestActions)
    if self.getState() == 'OFFENSE':
        if len(bestActions) > 1:
            print "Randomly Chose ", res, "\n"
        else:
            print "Chose ", res, "\n"
    return res

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

  def checkDeath(self, agentState):  ##this needs to be fixed
      if agentState.configuration == agentState.start:
          return True
      else:
          return False

  def evaluate(self, gameState, action, MM_ID = False):  #MM_ID if passed from mini-max
    """
    Computes a linear combination of features and feature weights
    """
    #print "Passing in GS, action", action, "and EE", EID
    features = self.getFeatures(gameState, action, MM_ID)
    weights = self.getWeights(gameState, action)
    res = features * weights
    if self.getState() == 'OFFENSE': print "Result", res
    return res

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

    if closerInvader.numCarrying == 0:
        return False # just chase him?

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
  def getState(self):
      return 'OFFENSE'

  def getFeatures(self, gameState, action, MM_ID = False): #MM_ID: IF eval passed from gamestate
    features = util.Counter()

    if  MM_ID:
        print "Eval Passed from Minimax"
        #successor = gameState.generateSuccessor(EID, action)
        # #gamestate already updated from minimax
        successor = gameState

    else: successor = gameState.generateSuccessor(self.index, action)
          #self.getSuccessor(gameState, action)


    foodList = self.getFood(successor).asList()
    features['foodLeft'] = -len(foodList)#self.getScore(successor)
    myPos = successor.getAgentState(self.index).getPosition()
    lastGame = self.getCurrentObservation()
    lastPos = lastGame.getAgentState(self.index).getPosition()

    capsules = self.getCapsules(successor)
    features['capsuleBonus'] = 1000 - 500 * len(capsules)
    capsuleProgress = 0
    if len(capsules) > 0:
        curCapDist = min([ self.getMazeDistance(myPos, c) for c in capsules ])
        preCapDist =  min([ self.getMazeDistance(lastPos, c) for c in capsules ])
        capsuleProgress = int(curCapDist < preCapDist)
        if curCapDist <= 6:
            features['capsuleBonus'] +=(6 - curCapDist) * capsuleProgress

    numCarrying = successor.getAgentState(self.index).numCarrying
    features['numCarrying'] = numCarrying
    features['scoreChange'] = abs(successor.data.scoreChange) + numCarrying ** .8


    distToSafe = self.findHome(myPos, gameState)  #note gamestate not used in function
    features['distanceToSafe'] = distToSafe
    if distToSafe == 0 and not myPos == self.start:
        features['scoreChange'] += numCarrying

    oppID = self.getOpponents(successor)
    opp1Dead = self.checkDeath(successor.getAgentState(oppID[0]))
    opp2Dead =  self.checkDeath(successor.getAgentState(oppID[1]))
    dead = self.checkDeath(successor.getAgentState(self.index)) # essentially are we back at start position... :(

    if dead:
        print "i'm dead in this successor!"  #either through ghost or pacman
        features['death'] = -1000

    elif opp1Dead or opp2Dead:
         print "cool my opponent is dead in this successor!"
         features['death'] = 500

    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    protectors = [a for a in enemies if a.getPosition() != None]
    if len(protectors) > 0:
      dists = [(self.getMazeDistance(myPos, a.getPosition()), a) for a in protectors]
      closestDist, closestGhost = min(dists)
      farDist, farGhost = max(dists)
      preActionState = self.getCurrentObservation()
      if successor.getAgentState(self.index).scaredTimer >= 1:
          if closestDist <=1 and closestGhost.isPacman: #not dead immediately, but after move
             print "i'm scared! and he would be one away after my move!"
             features['death'] = -500

      if closestGhost.isPacman:
          closestGhost = farGhost
          closestDist = farDist

      if not closestGhost.isPacman and closestGhost.scaredTimer <= 10:
          baseScore = min(-8 + closestDist, 0)
          #istrapped would have been smooth
          if closestDist == 1:  #allow enemy to eat -- no!
                if closestGhost.scaredTimer >= 1:
                    print "my opponent is close to dead in this successor!"
                else:
                    print "i would be dead in this move towards opponent"
                    features['death'] = -500

          if closestDist <= 4 and len(successor.getLegalActions(self.index)) <= 2: #one direction and stop
                features['trapped'] = -300
                if len(gameState.getLegalActions(self.index)) >= 4 and closestDist > 3: #junction with 3 paths and stop
                    features['trapped'] = 0

          features['distanceToProtector'] =  baseScore

    flag = len(foodList) > 0

    if flag: # This should always be True,  but better safe than sorry
      bestFood = foodList[0]
      bestLead = -9999
      distToFood = 9999
      preSafeDist = self.findHome(lastPos, gameState)
      for food in foodList:
          myDist = self.getMazeDistance(myPos, food)

          proDist = self.getMazeDistance(closestGhost.getPosition(), food)
          if closestGhost.isPacman: proDist = 0
          if proDist - myDist > bestLead:
              bestLead = proDist - myDist
              foodDist = myDist
              bestFood = food
              preFoodDist = self.getMazeDistance(lastPos, food)
              foodProgress = myDist < preFoodDist
              if numCarrying > 0:
                  if myDist >= distToSafe and distToSafe < preSafeDist:
                      features['actionBonus'] += 1
                      if capsuleProgress: features['capsuleBonus'] += 1

                  elif myDist < distToSafe and myDist < preFoodDist:
                        features['actionBonus'] += 1
                        if capsuleProgress: features['capsuleBonus'] += 1

      features['splitDistToFood'] = -foodDist

    if not MM_ID or MM_ID == 7:  #successor state is same as gamestate
        if action == gameState.getAgentState(self.index).configuration.direction:
            if numCarrying == 0 and not foodProgress:
                pass # no bonus for reverse
            else:
                features['actionBonus'] += .5 #ugly encouragment for same direction
            #can encourage him to keep backing up away from food

        if action == Directions.STOP:
            features['actionBonus'] -= 50

    if self.getState() == "OFFENSE": print features, action
    return features


  def getWeights(self, gameState, action):
    weights = util.Counter()
    weights['foodLeft'] = 100
    weights['splitDistToFood'] = 1
    weights['actionBonus'] = 1  #will prune stop from choose action
    weights['scoreChange'] = 50
    weights['capsuleBonus'] = 1
    weights['trapped'] = 1
    weights['death'] = 1 #assigned in features

    if gameState.getAgentState(self.index).numCarrying > 0:
        weights['distanceToSafe'] = -1  #changing from -1.5 for test
        weights['distanceToProtector'] = 1 # default to feature score for ghostDistance; else keep at 0
    else:
        weights['distanceToProtector'] = 1 # tried .5 and pac started running into ghosts
    return weights

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  def getState(self):
      return 'DEFENSE'

  def getFeatures(self, gameState, action, EID = False):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if action == Directions.STOP: features['stop'] = 1
    #if myState.isPacman: features['onDefense'] = 0
    if self.red:
        if myPos[0] > self.safeColumn or myState.isPacman:
            features['onDefense'] = 0
    else:
        if myPos[0] < self.safeColumn or myState.isPacman:
            features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)

    enemyPos = [en.getPosition() for en in enemies if en.getPosition() != None]
    enemyDists = [self.getMazeDistance(myPos, opp) for opp in enemyPos]

    nearby = min(enemyDists)

    oppID = self.getOpponents(successor)
    opp1Dead = self.checkDeath(successor.getAgentState(oppID[0]))
    opp2Dead =  self.checkDeath(successor.getAgentState(oppID[1]))
    dead = self.checkDeath(successor.getAgentState(self.index)) # essentially are we back at start position... :(

    if dead:
        print "ME (DEFENSE) Considered ACTIVE suicide by going", action
        features['death'] = -1000

    elif nearby == 1:
        features['death'] = -800

    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      minDist = min(dists)
      features['invaderDistance'] = minDist
      if successor.getAgentState(self.index).scaredTimer >= 1:
          print "I AM SCARED, SAYS defense"
          if minDist == 1:
            features['death'] = -500 # really bad
            print "ME (DEFENSE) Considered PASSIVE suicide by going", action

      ### Can I detect if I've trapped my opponent?
      if self.trappedOpponent(myPos, invaders, gameState):
          features['stop'] = -1  #100 point bonus (-1 * -100)
    else:
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev: features['reverse'] = 1

        ourFood = self.getFoodYouAreDefending(gameState).asList()
        foodDists1 = [(self.getMazeDistance(enemies[0].getPosition(), food), food) for food in ourFood]
        foodDists2 = [(self.getMazeDistance(enemies[-1].getPosition(), food), food) for food in ourFood]

        fd1 = min(foodDists1)
        fd2 = min(foodDists2)
        if fd1 < fd2:
           closeFood = fd1[1]
        else:
           closeFood = fd2[1]

        features['foodDistance'] = self.getMazeDistance(myPos,closeFood)

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'foodDistance': -10, 'death': 1, 'capsuleDistance': -10, 'stop': -100, 'reverse': -2}
