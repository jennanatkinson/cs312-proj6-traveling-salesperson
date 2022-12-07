import math
import signal
import sys
from Proj5GUI import Proj5GUI
from TSPSolver import TSPSolver

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtWidgets import *
	from PyQt5.QtGui import *
	from PyQt5.QtCore import *
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtGui import *
	from PyQt4.QtCore import *
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

# Test standard asserts for an algorithm and given inputs
def run_test(testFunc, size:int, seed:int, difficulty:str, timeLimit:int, expectedCost:int):
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  app = QApplication(sys.argv)
  w = Proj5GUI()
  w.generateNetwork(size=str(size), seed=str(seed), diff=difficulty)
  w.solver.setupWithScenario(w._scenario)
  max_time = float(timeLimit)

  results = testFunc(w.solver, max_time)

  assert(results['cost'] <= expectedCost)
  assert(results['solution'] != None)
  assert(len(results['solution'].route) == size)

  # Assert that all items are only in the city once
  citySet = set()
  for city in results['solution'].route:
    assert(not (city in citySet))
    citySet.add(city)

def test_should_solve_greedy_easy_three():
  run_test(TSPSolver.greedy, 3, 20, "Easy", 60, 4159)

# NOTE: For fancy, all the cost numbers are the optimal greedy solution
# Our algorithm should find the optimal greedy, if not better
def test_should_solve_fancy_easy_three():
  run_test(TSPSolver.fancy, 3, 20, "Easy", 60, 4159)

def test_should_solve_fancy_easy_ten():
  run_test(TSPSolver.fancy, 10, 431, "Easy", 60, 7242)

def test_should_solve_fancy_normal_ten():
  run_test(TSPSolver.fancy, 10, 850, "Normal", 60, 8247)

def test_should_solve_fancy_hard_det_three():
  run_test(TSPSolver.fancy, 3, 969, "Hard (Deterministic)", 60, 3880)

def test_should_solve_fancy_hard_det_ten():
  run_test(TSPSolver.fancy, 10, 135, "Hard (Deterministic)", 60, 7483)