from TSPClasses import *
import numpy as np

# Loops through each edge's cost and puts into a matrix
def init_cost_matrix(cities:list[City]):
	cost_matrix = np.empty(shape=(len(cities), len(cities)))  # O(n^2)
	for i in range(len(cities)):  # O(n^2)
		city_a = cities[i]
		for j in range(len(cities)):
			city_b = cities[j]
			cost_matrix[i][j] = city_a.costTo(city_b)
	return cost_matrix

# Linked list for City
class LinkedCityNode:
	def __init__(self, value:City, nextCity=None):
			self.value:City = value
			self.next:LinkedCityNode = nextCity

# Given a list of City objects, find a tour that visits all cities only once, using Cheapest Insertion
class CheapestInsertion:
	def __init__(self, startCity:City, cities:list[City], cost_matrix:list[list[int]]):
			self.cities:list[City] = cities #readOnly
			self.cost_matrix:list[list[int]] = cost_matrix #readOnly
			self.linked_route_root:LinkedCityNode = LinkedCityNode(startCity, None)
			self.cost_so_far:int = 0

			self.unvisited_cities_set:set[City] = set(self.cities)
			self.unvisited_cities_set.remove(self.linked_route_root.value)

	# Searches for a solution until all cities are visited, or impossible
	def find_solution(self, costBound:int) -> TSPSolution:
		while len(self.unvisited_cities_set) != 0:
			insert_cost = self.add_next_city()
			
			# If no insertion was possible, stop
			if insert_cost == np.inf:
				break

			# Check bound to stop searching for solutions
			# NOTE: cost_so_far is not an accurate cost of the route, does not do end -> start, but helps prune
			if self.cost_so_far >= costBound:
				return None

		return TSPSolution(self.build_route())

	# Transforms the linked list (LinkedCityNode) into an array of cities (list[City])
	def build_route(self) -> list:
		route = []
		node = self.linked_route_root
		while node != None:
			route.append(node.value)
			node = node.next
		return route
		
	# Finds the cheapest insertion node and point, and inserts it into the list
	# Returns the cost to insert
	def add_next_city(self) -> int:
		start_insert:LinkedCityNode = None
		city_obj_to_insert:City = None
		end_insert:LinkedCityNode = None
		min_insert_cost = np.inf
		city_in_route:LinkedCityNode = self.linked_route_root # start at beginning of route

		# Find cheapest city and way to insert in the route
		while city_in_route != None:
			for unvisited_city in self.unvisited_cities_set:
				
				# Calculate option of insert after end of tour
				if city_in_route.next == None:
					connect_cost = self.cost_matrix[city_in_route.value._index][unvisited_city._index]
					if connect_cost < min_insert_cost:
						min_insert_cost = connect_cost
						start_insert = city_in_route
						city_obj_to_insert = unvisited_city
						end_insert = None
				
				# Calculate option of insert between the cityInRoute and cityInRoute.next
				if city_in_route.next != None:
					connect_cost = self.cost_matrix[city_in_route.value._index][unvisited_city._index] + \
												self.cost_matrix[unvisited_city._index][city_in_route.next.value._index]
					if connect_cost < min_insert_cost:
						min_insert_cost = connect_cost
						start_insert = city_in_route
						city_obj_to_insert = unvisited_city
						end_insert = city_in_route.next
			
			city_in_route = city_in_route.next
		
		# If a city is able to be inserted somewhere in the route,
		if city_obj_to_insert != None:
			
			# Remove city from unvisited
			self.unvisited_cities_set.remove(city_obj_to_insert)

			# Add city to linked list and update running cost
			insert_link_node = LinkedCityNode(city_obj_to_insert, nextCity=end_insert)
			if start_insert != None:
				start_insert.next = insert_link_node
				self.cost_so_far += self.cost_matrix[start_insert.value._index][city_obj_to_insert._index]
			
			if end_insert != None:
				self.cost_so_far += self.cost_matrix[city_obj_to_insert._index][end_insert.value._index]
			
			if start_insert != None and end_insert != None:
				self.cost_so_far -= self.cost_matrix[start_insert.value._index][end_insert.value._index]

		return min_insert_cost

