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
		results['solution'] = bssf
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
		results['solution'] = bestSolution
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
		
	def branchAndBound( self, time_allowance=60.0 ):
		pass



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
		



