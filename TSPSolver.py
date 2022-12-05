#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
  from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
  from PyQt4.QtCore import QLineF, QPointF
else:
  raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import copy

## Add class to hold state at any time
class TSPState:
  def __init__(self, lowBound, redCostMatrix, city, cities, depth, route):
    self.lowBound = lowBound
    self.redCostMatrix = redCostMatrix
    self.city = city
    self.cities = cities
    self.depth = depth
    self.route = route

  def __lt__(self, other):
    ## MULTIPLE OPTIONS....UNCOMMENT THE ONE YOU WANT
    return (self.lowBound / self.depth) < (other.lowBound / other.depth)
    #return (self.lowBound - (self.depth * 2 * len(self.cities))) < (other.lowBound - (other.depth * 2 * len(other.cities)))


class TSPSolver:
  def __init__( self, gui_view ):
    self._scenario = None

  def setupWithScenario( self, scenario ):
    self._scenario = scenario


  ''' <summary>
    This is the entry point for the default solver
    which just finds a valid random tour.  Note this could be used to find your
    initial BSSF.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of solution, 
    time spent to find solution, number of permutations tried during search, the 
    solution found, and three null values for fields not used for this 
    algorithm</returns> 
  '''
  
  def defaultRandomTour( self, time_allowance=60.0 ):
    results = {}
    cities = self._scenario.getCities()
    ncities = len(cities)
    foundTour = False
    count = 0
    bssf = None
    start_time = time.time()
    while not foundTour and time.time()-start_time < time_allowance:
      # create a random permutation
      perm = np.random.permutation( ncities )
      route = []
      # Now build the route using the random permutation
      for i in range( ncities ):
        route.append( cities[ perm[i] ] )
      bssf = TSPSolution(route)
      count += 1
      if bssf.cost < np.inf:
        # Found a valid route
        foundTour = True
    end_time = time.time()
    results['cost'] = bssf.cost if foundTour else math.inf
    results['time'] = end_time - start_time
    results['count'] = count
    results['soln'] = bssf
    results['max'] = None
    results['total'] = None
    results['pruned'] = None
    return results


  ''' <summary>
    This is the entry point for the greedy solver, which you must implement for 
    the group project (but it is probably a good idea to just do it for the branch-and
    bound project as a way to get your feet wet).  Note this could be used to find your
    initial BSSF.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of best solution, 
    time spent to find best solution, total number of solutions found, the best
    solution found, and three null values for fields not used for this 
    algorithm</returns> 
  '''

  # Returns the first greedy solution found, Time: O(x*n**2)
  def greedy(self, time_allowance=60.0, startCity=None):
    # Setup objects
    results = {}
    cities = self._scenario.getCities()
    foundTour = False
    count = 0
    solution = None
    # Add tracker for bestSolution
    bestSolution = None
    start_time = time.time()

    # Adding outer for loop to iterate through all cities as startCity
    # O(n**3)
    for startCity in cities:
      # Deleted previous startCity initialization
      # Add another timer check
      if time.time() - start_time >= time_allowance:
        break
      # No need for while loop anymore, we either find a solution or we don't
      unvisitedCitiesSet = set(cities)
      route = []
      currentCity = startCity

      # Build the route greedily, Time: O(n**2)
      for _ in range(len(cities)):
        greedyCost, nextCity = None, None
        # Iterate to find the smallest unvisited edge, Time: O(n)
        for unvisitedCity in unvisitedCitiesSet:
          cost = currentCity.costTo(unvisitedCity)
          # Save the smallest city (or any city, if none have been visited)
          if greedyCost == None or cost < greedyCost:
            greedyCost, nextCity = cost, unvisitedCity

        # Visit the smallest edge, Time: O(1)
        if nextCity != None:
          unvisitedCitiesSet.remove(nextCity)
          route.append(nextCity)
          currentCity = nextCity
        else:
          raise Exception("Unable to visit any city!!")
      
      solution = TSPSolution(route)
      
      if solution.cost < math.inf:
        # Found a valid route
        foundTour = True
        # Add logic for tracking bssf
        if bestSolution == None or solution.cost < bestSolution.cost: 
          count += 1
          bestSolution = solution

        # Removed old startCity changer

    # Return results
    end_time = time.time()
    # Change to bestSolution
    results['cost'] = bestSolution.cost if foundTour else math.inf
    results['time'] = end_time - start_time
    results['count'] = count
    results['soln'] = bestSolution
    results['max'], results['total'], results['pruned'] = None, None, None
    return results
  
  
  
  ''' <summary>
    This is the entry point for the branch-and-bound algorithm that you will implement
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of best solution, 
    time spent to find best solution, total number solutions found during search (does
    not include the initial BSSF), the best solution found, and three more ints: 
    max queue size, total number of states created, and number of pruned states.</returns> 
  '''
    
  def branchAndBound( self, time_allowance=60.0 ): # Best Case: O(n^2 * b^n), worst case: O(n!) up to 60 seconds
    results = {} # O(1)
    cities = self._scenario.getCities() # O(1)
    ncities = len(cities) # O(1)
    ## Get initial BSSF using defaultRandomTour
    bssf = self.defaultRandomTour(time_allowance)['soln'] # O(n)
    start_time = time.time() # O(1)

    redCostMatrix = {}
    indexes = []
    ## Create an initial reduced cost matrix:  Total = O(n^2)
    for row in range(ncities): # O(n)
      indexes.append(row) # O(1)
      for col in range(ncities): # O(n)
        redCostMatrix[(row,col)] = cities[row].costTo(cities[col]) # O(1)
    
    start = 0
    route = []
    route.append(start)
    ## Could start with any city, I just chose the first one
    state = TSPState(0, redCostMatrix, indexes.pop(start), indexes, 0, route)
    heap = []
    heap.append(state)
    ## Initialize a heap
    heapq.heapify(heap) # O(1)
    ## Pass to a prune and expand function
    soln, maxSize, totalStates, prunedStates, bssfUpdates = self.findBSSF(heap, bssf, start_time, time_allowance) # n^2 < O() < n! OR 60 seconds
    
    end_time = time.time()
    results['cost'] = soln.cost
    results['time'] = end_time - start_time
    results['count'] = bssfUpdates
    results['soln'] = soln
    results['max'] = maxSize
    results['total'] = totalStates
    results['pruned'] = prunedStates
    return results

  def findBSSF(self, heap, bssf, start_time, time_allowance): # n^2 * b^n < O() < n! OR 60 seconds
    ## Initialize trackers
    totalStates = 0
    prunedStates = 0
    maxSize = 0
    bssfUpdates = 0

    ## Infinite loop until time expiration or empty heap
    while True and time.time()-start_time < time_allowance: # O(b^n)
      ## Quick Exits
      if len(heap) == 0: # O(1)
        break

      ## Update maxSize
      if len(heap) > maxSize: # O(1)
        maxSize = len(heap)

      ## Get next state
      currState = heapq.heappop(heap) # O(log n)
      ## Immediately reduce and get a new lower bound
      currState.lowBound += self.reduceMatrix(currState.redCostMatrix) # O(n^2)
      
      ## Prune if not better than original
      if currState.lowBound >= bssf.cost: # O(1)
        prunedStates += 1
        continue
      ## Check if more edges before expansion
      elif not currState.cities: # O(n)
        route = []
        ## TSPSolution needs an array of cities, but I was just using their indexes
        for i in currState.route: # worst case O(n)
          route.append(self._scenario.getCities()[i])
        bssf = TSPSolution(route) # O(n)
        bssfUpdates += 1
        continue
      ## Expand now
      else:
        ## For each 'neighbor'
        for i in currState.cities: # worst case O(n)
          ## Having some timer issues so adding another check here
          if time.time()-start_time > time_allowance: # O(1)
            break
          ## Update matrix with infinities for next reduction
          redCostMatrix = copy.deepcopy(currState.redCostMatrix) # Forums state this is typically linear O(n)
          maxI = list(redCostMatrix.keys())[-1][0] + 1 # O(1)
          city = currState.city
          for row in range(maxI): # O(n)
            redCostMatrix[row, i] = math.inf
          for col in range(maxI): # O(n)
            redCostMatrix[city, col] = math.inf
          redCostMatrix[i, city] = math.inf
          lowBound = currState.lowBound + currState.redCostMatrix[currState.city, i]
          ## This was seriously breaking everything until I deep copied it
          cities = copy.deepcopy(currState.cities) # O(n)
          cities.remove(i)
          route = copy.deepcopy(currState.route)
          depth = len(route) + 1
          route.append(i)
          ## Create a new state to put into queue
          state = TSPState(lowBound, redCostMatrix, i, cities, depth, route)
          totalStates += 1
          heapq.heappush(heap, state) # O(log n)
    
    return bssf, maxSize, totalStates, prunedStates, bssfUpdates

  def reduceMatrix(self, redCostMatrix): # O(n^2)
    ## Initialize
    bound = 0
    maxI = list(redCostMatrix.keys())[-1][0] + 1

    ## Based on spec, reduce each row
    for row in range(maxI): # O(n^2)
      minVal = math.inf
      ## This finds the min value
      for col in range(maxI):
        if (redCostMatrix[row,col] < minVal):
          minVal = redCostMatrix[row,col]
      ## If it's a valid min
      if minVal > 0 and minVal != math.inf:
        ## Update bound and reduce each other value by the min
        bound += minVal
        for col in range(maxI):
          redCostMatrix[row,col] = redCostMatrix[row,col] - minVal

    ## Now reduce each column
    for col in range(maxI): # O(n^2)
      minVal = math.inf
      ## This finds the min value
      for row in range(maxI):
        if (redCostMatrix[row,col] < minVal):
          minVal = redCostMatrix[row,col]
      ## If it's a valid min
      if minVal > 0 and minVal != math.inf:
        ## Update bound and reduce each other value by the min
        bound += minVal
        for row in range(maxI):
          redCostMatrix[row,col] = redCostMatrix[row,col] - minVal

    return bound



  ''' <summary>
    This is the entry point for the algorithm you'll write for your group project.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of best solution, 
    time spent to find best solution, total number of solutions found during search, the 
    best solution found.  You may use the other three field however you like.
    algorithm</returns> 
  '''
    
  def fancy( self,time_allowance=60.0 ):
    pass
    



