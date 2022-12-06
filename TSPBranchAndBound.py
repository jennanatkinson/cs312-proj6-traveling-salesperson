#!/usr/bin/python3

from TSPClasses import *
import heapq
import copy
import time

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

class BranchAndBound:

  def __init__(self):
    pass

  def solve( self, time_allowance=60.0 ): # Best Case: O(n^2 * b^n), worst case: O(n!) up to 60 seconds
    results = {} # O(1)
    cities = self._scenario.getCities() # O(1)
    ncities = len(cities) # O(1)
    ## Get initial BSSF using defaultRandomTour
    bssf = self.defaultRandomTour(time_allowance)['solution'] # O(n)
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
    solution, maxSize, totalStates, prunedStates, bssfUpdates = BranchAndBound.findBSSF(self, heap, bssf, start_time, time_allowance) # n^2 < O() < n! OR 60 seconds
    
    end_time = time.time()
    results['cost'] = solution.cost
    results['time'] = end_time - start_time
    results['count'] = bssfUpdates
    results['solution'] = solution
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
      currState.lowBound += BranchAndBound.reduceMatrix(currState.redCostMatrix) # O(n^2)
      
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

  def reduceMatrix(redCostMatrix): # O(n^2)
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