import copy

from TSPClasses import *
import numpy as np


class CityNode:
    def __init__(self, index, prev, next):
        self.index = index
        self.prev = prev
        self.next = next


class CheapestInsertion:
    def __init__(self, cities):
        self.cities = cities
        self.results = {}
        self.count = 0
        self.bssf = None
        self.cost_matrix = None

    def solve(self, time_allowance=60.0):
        start_time = time.time()

        # Setup
        self.bssf = None  # TODO: replace with fastest implementation we just need something as it doesn't optimize/affect the algorithm
        self.cost_matrix = self.get_cost_matrix()

        # Find n tours (update bssf along the way) while time allows
        for start_city in self.cities:
            # Time check
            if time.time() - start_time >= time_allowance:
                break

            # All nodes outside tour that are still viable candidates
            candidates = dict()
            for city in self.cities:
                candidates[city._index] = True

            # Initialize the tour with start and closest neighbor
            tour = dict()
            tour[start_city._index] = CityNode(start_city._index, None, None)
            neighbor_index = self.find_nearest_city_index(tour, candidates)
            tour[start_city._index].prev = neighbor_index
            tour[start_city._index].next = neighbor_index
            tour[neighbor_index] = CityNode(neighbor_index, start_city._index, start_city._index)
            tour_cost = self.cost_matrix[start_city._index][neighbor_index] + self.cost_matrix[neighbor_index][
                start_city._index]

            # Remove starting two cities from candidate pool
            for city_index, city in tour.items():
                candidates.pop(city_index)

            # Safeguard incase nearest city can't be inserted or asymmetric edge funk
            local_candidates = copy.deepcopy(candidates)
            while len(tour) < len(self.cities) and time.time() - start_time < time_allowance:

                while local_candidates:
                    nearest_city_index = self.find_nearest_city_index(tour, local_candidates)
                    start_index, end_index, tour_cost = self.find_cheapest_insertion(tour, tour_cost, nearest_city_index)

                    if start_index is not None and end_index is not None:
                        tour_cost = self.insert(tour, tour_cost, nearest_city_index, start_index, end_index)
                        local_candidates.pop(nearest_city_index)
                        break
                    else:
                        # Candidate is not viable (only has one edge), look at next candidate
                        local_candidates.pop(nearest_city_index)

            # Found a solution (may not be bssf)
            self.count += 1

            # Update bssf
            if (self.bssf is None or tour_cost < self.bssf.cost) and len(tour) == len(self.cities):
                # Tour to list, store in bssf
                bssf_cities = [start_city]
                city_index = tour[start_city._index].next
                while city_index is not start_city._index:
                    bssf_cities.append(self.cities[city_index])
                    city_index = tour[city_index].next
                self.bssf = TSPSolution(bssf_cities)

        end_time = time.time()

        self.results['time'] = end_time - start_time
        self.results['optimal'] = True if self.results['time'] < time_allowance else False
        if self.bssf is not None:
            self.results['cost'] = self.bssf.cost
        else:
            self.results['cost'] = np.inf
        self.results['count'] = self.count
        self.results['solution'] = self.bssf
        return self.results

    # Fill in matrix with cost of each city to another city
    # Row = origin  |  Column = destination
    def get_cost_matrix(self):
        cost_matrix = np.empty(shape=(len(self.cities), len(self.cities)))  # O(n^2)
        for i in range(len(self.cities)):  # O(n^2)
            city_a = self.cities[i]
            for j in range(len(self.cities)):
                city_b = self.cities[j]
                cost_matrix[i][j] = city_a.costTo(city_b)
        return cost_matrix

    def initialize_tour(self, start_index, unvisited):
        tour = {}  # Dictionary { origin_index : dest_index }

        dest_index, outbound_cost = self.find_closest_point(start_index)

        # Dead-end check (start city is not connected at all)
        if outbound_cost == np.inf:
            return None, np.inf

        inbound_cost = self.cost_matrix[dest_index][start_index]

        # Dead-end check (candidate has no viable paths)
        if inbound_cost == np.inf:  # TODO: if asymmetric edge, it should techoncally go to next best candidate
            return None, np.inf

        tour[start_index] = CityNode(start_index, dest_index, dest_index)
        tour[dest_index] = CityNode(dest_index, start_index, start_index)

        tour_cost = outbound_cost + inbound_cost
        return tour, tour_cost

    def find_closest_point(self, origin_index, candidates):
        min_candidate = None
        min_cost = np.inf

        for candidate in candidates:

            curr_cost = self.cost_matrix[origin_index][candidate]
            if curr_cost < min_cost:
                min_candidate = candidate
                min_cost = curr_cost

        return min_candidate, min_cost

    def find_nearest_city_index(self, tour: dict, candidates: dict):
        nearest_city_index = None
        min_cost = np.inf
        for city_index, city in tour.items():
            for candidate_index in candidates:
                cost = self.cost_matrix[city.index][candidate_index]
                if cost < min_cost:
                    nearest_city_index = candidate_index
                    min_cost = cost
        return nearest_city_index

    def find_cheapest_insertion(self, tour, tour_cost, candidate_index):
        min_start_index = None
        min_end_index = None
        min_cost = np.inf

        for start_index, start in tour.items():
            end_index = tour[start.next].index
            connection_cost = self.cost_matrix[start_index][candidate_index] + self.cost_matrix[candidate_index][end_index]
            cost = (tour_cost - self.cost_matrix[start_index][end_index]) + connection_cost
            if cost < min_cost:
                min_start_index = start_index
                min_end_index = end_index
                min_cost = cost
        return min_start_index, min_end_index, min_cost

    def insert(self, tour, tour_cost, candidate_index, start_index, end_index):
        tour[candidate_index] = CityNode(candidate_index, start_index, end_index)
        tour[start_index].next = candidate_index
        tour[end_index].prev = candidate_index
        tour_cost -= self.cost_matrix[start_index][end_index]
        tour_cost += self.cost_matrix[start_index][candidate_index]
        tour_cost += self.cost_matrix[candidate_index][end_index]
        return tour_cost
