# myTeam.py
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
import random, time, util
from game import Directions, Actions
import game
from util import nearestPoint

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

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)
    states = [ gameState.generateSuccessor(self.index, action) for action in actions ]

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.betterEvaluationFunction(state) for state in states]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

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

  def betterEvaluationFunction(self, currentGameState):
        """
          Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
          evaluation function (question 5).

          DESCRIPTION: I gave subscores to different features of the gamestate where the total score
         ( successorScore ) = actionScore + foodLeftScore + foodDistScore +  ghostDistanceScore + capsuleScore + modifier
          The actionScore penalized stopping slightly to break ties on otherwise good options
          The foodLeftScore encourages PacMan to eat food
          The foodDistScore encourages PacMan to move closer to food
          The ghostDistanceScore encourages PacMan to avoid the ghosts if possible in pursuit of food
          The capsuleScore encourages PacMan to eat capsules
          The modifier is a scaled down version of the actual score to adjust for unexpected occurences
        """
        debug = False
        #print "I am running"
        myFood = self.getFood(currentGameState).asList()
        myCapsules = self.getCapsules(currentGameState)

        '''
        pos = currentGameState.getPacmanPosition()
        ghostStates = currentGameState.getGhostStates()
        ghostPositions = [ghost.configuration.getPosition() for ghost in ghostStates]
        scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
        '''
        myState = currentGameState.getAgentState(self.index)
        pos = myState.getPosition()

        # TODO FIX!
        enemies = [currentGameState.getAgentState(i) for i in self.getOpponents(currentGameState)]
        ghosts = [a for a in enemies if not a.isPacman and a.getPosition() != None]
        ghostPositions = [predictGhostMove(pos, ghost.getPosition()) for ghost in ghosts]

        actionScore = 0
        #direction = currentGameState.data.agentStates[self.index].getDirection()
        #if direction == Directions.STOP: actionScore = -50000  #stop keeps same direction
        '''
        if not agentMoved:
            actionScore = -200  #this also the last state -- if he stopped last time
        '''
        foodLeftScore = -100 * len(myFood)
        if len(myFood) == 0:
            foodDistScore = 0
        else:
            foodDists = [self.getMazeDistance(pos, food) for food in myFood]
            foodDists.sort()
            foodDistScore = - foodDists[0]

        minGhostDist = min([self.getMazeDistance(pos, ghost) for ghost in ghostPositions])
        g =  minGhostDist
        if g == 0:
            g = -500  #don't step on the ghost!
        elif g <= 2 :
            g = (4-g)*g
        elif g == 3:
            g = 6
        else:
            #g = .5*g
            g = 7

        ghostDistanceScore = g

        modifier = .5 * currentGameState.getScore()  #adjust for unplanned good actions
        capsuleScore = -400 * len(myCapsules)
        nearestGhostId = [ idx for idx in range(len(ghostPositions)) if self.getMazeDistance(pos, ghostPositions[idx]) ==  minGhostDist]
        if ghosts[nearestGhostId[0]].scaredTimer >= 5:
            ghostDistanceScore = 20 - 20 * ghostDistanceScore

        successorScore = actionScore + foodLeftScore + foodDistScore +  ghostDistanceScore + capsuleScore + modifier


       # newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        if debug:
          #print  "Successor GS:\n", successorGameState, "at New Position", newPos
          #print "Examining", direction, "with new Position", pos
          print  "Ghosts Positions:", ghostPositions # "with times", newScaredTimes
            ##how did ghost get to 0.0 ?
          print "| foodLeftScore: ", foodLeftScore, "| foodDistScore: ", foodDistScore, "| ghostDistanceScore:",\
              ghostDistanceScore, " | Total: ", successorScore, "\n"


        return  successorScore

def predictGhostMove(myPos, ghostPos):
    '''
    Returns the expected position of the ghost
    :param myPos:
    :param ghostPos:
    :return:
    '''
    moves = util.Counter()
    #r = random.random()  #where r is the degree of noise (randomness)
    #if optimal:
    if myPos[1] < ghostPos[1]:
        moves[Directions.SOUTH] = 1
        if myPos[0] < ghostPos[0]:
          moves[Directions.SOUTH] = .8
          moves[Directions.WEST] = .2
        elif myPos[0] > ghostPos[0]:
          moves[Directions.SOUTH] = .8
          moves[Directions.EAST] = .2

    elif myPos[1] > ghostPos[1]:
            moves[Directions.NORTH] = 1
            if myPos[0] < ghostPos[0]:
              moves[Directions.NORTH] = .8
              moves[Directions.WEST] = .2
            elif myPos[0] > ghostPos[0]:
              moves[Directions.NORTH] = .8
              moves[Directions.EAST] = .2


    elif myPos[1] == ghostPos[1]:
        if myPos[0] < ghostPos[0]:  #as just 1, THIS was having issues with the autograder
             moves[Directions.WEST] = .9
             moves[Directions.STOP] = .1
        elif myPos[0] > ghostPos[0]:
            moves[Directions.EAST] = 1
            moves[Directions.STOP] = .1
        else:
            moves[Directions.STOP] = 1

    #currently there is no check if ghost will move off the map or into a wall
    ## should just pick optimally for closer towards pac
    ## ghost might be using euc or man instead of maze distance though!!!
    move = util.chooseFromDistribution(moves)
    vector =  Actions.directionToVector(move)
    newPos = (ghostPos[0] + vector[0], ghostPos[1] + vector[1])
    return newPos
