import math
import signal
import sys
from Proj5GUI import Proj5GUI

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


def test_should_solve_easy_small_greedy():
  signal.signal(signal.SIGINT, signal.SIG_DFL)

  app = QApplication(sys.argv)
  w = Proj5GUI()
  w.diffDropDown.setCurrentIndex(4) # Hard (Deterministic)
  w.generateNetwork(size='3', seed='20', diff='Easy')
  w.solver.setupWithScenario(w._scenario)
  max_time = float(60)

  results = w.solver.greedy(max_time)

  assert(results['cost'] != math.inf)
  assert(results['cost'] == 4159)
  assert(results['time'] < 60)
  assert(results['count'] == 3)
  assert(results['solution'] != None)